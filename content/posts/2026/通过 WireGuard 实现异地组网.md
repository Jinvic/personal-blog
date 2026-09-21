---
title: 通过WireGuard实现异地组网
date: '2026-06-03T09:11:17+08:00'
lastnod: '2026-09-21T10:41:00+08:00'
tags: 
- Linux
categories: 
- 问题
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 通过WireGuard实现异地组网

## 背景

最近 ssh 和 RustDesk 突然不可用，分别报错`kex_exchange_identification: read: Connection reset` 和 `os error 10054`，疑似被防火墙或 DPI（Deep Packet Inspection 深度包检测）阻断。于是用 WireGuard 搭建加密隧道来绕过。

后来发现这套组网方式很通用，不止能解决 ssh/RustDesk 被阻断的问题，还能用于异地内网互通、多机互联等场景。本文整理成一份通用指南，方便日后重新组网时快速查阅。

## 适用场景

- 多台异地机器需要互相访问内网服务
- 某些服务被防火墙/DPI 阻断，需要加密隧道绕过
- 需要把分散的机器组成一个虚拟内网
- 需要一台云服务器作为中转或跳板

## 前置条件

- 一台有公网 IP 的服务器（作为服务端/中转节点）
- 若干台需要组网的客户端（可以在 NAT 后）
- 服务商安全组放行 WireGuard 的 UDP 端口

## 拓扑选型

WireGuard 组网有两种常见拓扑，选哪种取决于需求。

### 星型拓扑（Hub-and-Spoke）

所有客户端只和服务端建立 Peer，客户端之间的流量由服务端转发。

```txt
        服务端 (10.0.0.1)
        /        |        \
       /         |         \
客户端A       客户端B      客户端C
(10.0.0.100) (10.0.0.101) (10.0.0.102)
```

**优点：**

- 配置简单，客户端只需配一个 Peer
- 加客户端方便，只改服务端
- 适合客户端在 NAT 后、无法互相直连的场景

**缺点：**

- 所有流量经过服务端，带宽和延迟受服务端限制
- 服务端单点故障

**适用：** 客户端数量少、客户端在 NAT 后、不想维护复杂配置。

### 全网状拓扑（Mesh）

每个节点都和其他节点直接建立 Peer，流量点对点直连，不经过中转。

```txt
        节点A (10.0.0.100)
        /        \
       /          \
节点B (10.0.0.101) — 节点C (10.0.0.102)
```

**优点：**

- 流量直连，延迟低，不占中转带宽
- 没有单点故障
- 适合节点都有公网 IP 或能互相直连的场景

**缺点：**

- 每个节点要配其他所有节点的 Peer，配置量随节点数平方增长
- 加节点要改所有节点的配置
- 节点在 NAT 后时，直连可能失败，需要 fallback

**适用：** 节点数量少、节点有公网 IP、追求低延迟。

### 混合拓扑

部分节点直连，部分节点通过中转。比如我之前的场景：

- 物理机1 直连服务器 2、4、5（全网状）
- 物理机1 和物理机2 通过服务器 2 中转（星型）

混合拓扑灵活但配置复杂，建议需求明确时再用。

### 选型建议

| 场景                          | 推荐拓扑 |
| ----------------------------- | -------- |
| 客户端在 NAT 后，无法互相直连 | 星型     |
| 客户端数量多，想集中管理      | 星型     |
| 节点都有公网 IP，追求低延迟   | 全网状   |
| 节点数量少（< 5），追求简单   | 星型     |
| 节点数量少，追求性能          | 全网状   |
| 需求混合                      | 混合     |

## 服务端配置

### 1. 安装

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install wireguard wireguard-tools iptables -y
```

### 2. 生成密钥对

```bash
sudo mkdir -p /etc/wireguard
cd /etc/wireguard

# 生成私钥
wg genkey | sudo tee server_private.key
sudo chmod 600 server_private.key

# 生成公钥
sudo cat server_private.key | wg pubkey | sudo tee server_public.key

# 查看公钥（给客户端配置用）
sudo cat server_public.key
```

### 3. 开启 IP 转发

星型拓扑下服务端要转发客户端之间的流量，必须开启 IP 转发。

```bash
# 临时生效
sudo sysctl -w net.ipv4.ip_forward=1

# 永久生效
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

### 4. 创建 wg0.conf

#### 星型拓扑服务端配置

```conf
[Interface]
# 服务器私钥
PrivateKey = <服务器私钥>

# 服务器的 WireGuard 内网 IP
Address = 10.0.0.1/32

# 监听端口（UDP）
ListenPort = 51820

# 可选：MTU 设置（避免分片问题）
MTU = 1420

# 开启 IP 转发 + FORWARD 放行（星型拓扑必须）
PostUp = sysctl -w net.ipv4.ip_forward=1
PostUp = iptables -I FORWARD 1 -i wg0 -j ACCEPT
PostUp = iptables -I FORWARD 1 -o wg0 -j ACCEPT
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -o wg0 -j ACCEPT

[Peer]
# 客户端 A 的公钥
PublicKey = <客户端A公钥>
# 分配给客户端 A 的内网 IP
AllowedIPs = 10.0.0.100/32
# 保持连接
PersistentKeepalive = 25

[Peer]
# 客户端 B 的公钥
PublicKey = <客户端B公钥>
AllowedIPs = 10.0.0.101/32
PersistentKeepalive = 25

[Peer]
# 客户端 C 的公钥
PublicKey = <客户端C公钥>
AllowedIPs = 10.0.0.102/32
PersistentKeepalive = 25
```

每个客户端一个 `[Peer]` 段，`AllowedIPs` 用各自的 `/32`。

#### 全网状拓扑服务端配置

全网状拓扑下，服务端也是其中一个节点，和其他节点直连。服务端不需要转发，所以不需要 FORWARD 规则。

```conf
[Interface]
PrivateKey = <服务器私钥>
Address = 10.0.0.1/32
ListenPort = 51820
MTU = 1420

[Peer]
# 节点 A
PublicKey = <节点A公钥>
AllowedIPs = 10.0.0.100/32
Endpoint = <节点A公网IP>:<节点A端口>
PersistentKeepalive = 25

[Peer]
# 节点 B
PublicKey = <节点B公钥>
AllowedIPs = 10.0.0.101/32
Endpoint = <节点B公网IP>:<节点B端口>
PersistentKeepalive = 25
```

注意全网状下每个 Peer 都要写 `Endpoint`，因为要直连。

### 5. 防火墙和安全组

- 服务商安全组：开放 `UDP 51820`
- 服务端系统防火墙：放行 `51820/udp`

  ```bash
  sudo ufw allow 51820/udp
  # 如果 ufw 已启用，还要放行 wg0 接口
  sudo ufw allow in on wg0
  sudo ufw allow out on wg0
  ```

### 6. 启动并设置开机自启

```bash
sudo systemctl enable wg-quick@wg0
sudo wg-quick up wg0

# 查看状态
sudo wg show
sudo ip route show | grep wg0

# 停止
# sudo wg-quick down wg0
```

星型拓扑下，启动后应该看到每个客户端的 `/32` 路由：

```bash
ip route show | grep wg0
# 10.0.0.100 dev wg0 scope link
# 10.0.0.101 dev wg0 scope link
# 10.0.0.102 dev wg0 scope link
```

## 客户端配置

### 星型拓扑客户端配置

客户端只和服务端建 Peer，`AllowedIPs` 写整个网段，让所有 `10.0.0.x` 的流量都走服务端。

```conf
[Interface]
# 客户端私钥
PrivateKey = <客户端私钥>
# 客户端的 WireGuard 内网 IP
Address = 10.0.0.100/32

[Peer]
# 服务端公钥
PublicKey = <服务器公钥>
# 服务端公网 IP 和端口
Endpoint = <服务器公网IP>:51820
# 所有 10.0.0.x 都走隧道，由服务端转发
AllowedIPs = 10.0.0.0/24
# 保持连接
PersistentKeepalive = 25
```

### 全网状拓扑客户端配置

每个客户端要配其他所有节点的 Peer，`AllowedIPs` 用对方的 `/32`，并写 `Endpoint`。

以节点 A（`10.0.0.100`）为例：

```conf
[Interface]
PrivateKey = <节点A私钥>
Address = 10.0.0.100/32
ListenPort = 51820
MTU = 1420

[Peer]
# 服务端
PublicKey = <服务器公钥>
AllowedIPs = 10.0.0.1/32
Endpoint = <服务器公网IP>:51820
PersistentKeepalive = 25

[Peer]
# 节点 B
PublicKey = <节点B公钥>
AllowedIPs = 10.0.0.101/32
Endpoint = <节点B公网IP>:51820
PersistentKeepalive = 25

[Peer]
# 节点 C
PublicKey = <节点C公钥>
AllowedIPs = 10.0.0.102/32
Endpoint = <节点C公网IP>:51820
PersistentKeepalive = 25
```

节点 B、C 同理，各配其他节点的 Peer。

### Windows 客户端

在 [官网](https://www.wireguard.com/install/) 下载安装，打开后选择
*新建隧道 -> 新建空隧道*，自动生成密钥对，将公钥填入服务端配置。

### 放行 Windows 防火墙

**这一步很关键，不做的话服务端 ping 不通客户端，客户端之间也互 ping 不通。**

先查 WireGuard 接口的实际名称。一般为 wg 客户端配置的隧道名，但确认一下比较保险：

```powershell
Get-NetAdapter | Where-Object { $_.InterfaceDescription -like "*WireGuard*" } |
  Format-Table Name, InterfaceDescription, Status -AutoSize
```

然后用实际名称放行来自 wg 网段的入站流量：

```powershell
New-NetFirewallRule `
  -DisplayName "Allow WireGuard Subnet In" `
  -Direction Inbound `
  -RemoteAddress 10.0.0.0/24 `
  -Action Allow `
  -InterfaceAlias "<实际接口名>"
```

如果不想指定接口，可以去掉 `-InterfaceAlias`，直接按源地址放行：

```powershell
New-NetFirewallRule `
  -DisplayName "Allow WireGuard Subnet In" `
  -Direction Inbound `
  -RemoteAddress 10.0.0.0/24 `
  -Action Allow `
  -Profile Any
```

放行后确保防火墙处于开启状态：

```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### Linux 客户端

```conf
[Interface]
PrivateKey = <客户端私钥>
Address = 10.0.0.100/32

[Peer]
PublicKey = <服务器公钥>
Endpoint = <服务器公网IP>:51820
AllowedIPs = 10.0.0.0/24
PersistentKeepalive = 25
```

Linux 客户端一般不需要额外防火墙配置，但如果用了 `ufw` 或 `firewalld`，同样要放行 wg0 接口的入站。

## 拓扑切换

如果需要从星型切到全网状，或反过来，按下面步骤操作。

### 星型 → 全网状

1. 服务端：为每个 Peer 补上 `Endpoint`（对方的公网 IP 和端口）
2. 服务端：去掉 `PostUp`/`PostDown` 里的 FORWARD 规则（不再需要转发）
3. 客户端：为其他每个客户端补一个 `[Peer]` 段，写 `Endpoint` 和 `/32` 的 `AllowedIPs`
4. 客户端：把原来指向服务端的 `AllowedIPs = 10.0.0.0/24` 改为只写服务端和其他节点的 `/32`
5. 重启所有节点的 WireGuard

### 全网状 → 星型

1. 服务端：加上 `PostUp`/`PostDown` 的 FORWARD 规则
2. 服务端：去掉每个 Peer 的 `Endpoint`（或保留也行，星型下不必须）
3. 客户端：删掉其他客户端的 `[Peer]` 段，只保留服务端
4. 客户端：把 `AllowedIPs` 改为 `10.0.0.0/24`
5. 重启所有节点的 WireGuard

### 切换时的注意事项

- 切换前先 `wg-quick down`，改完配置再 `wg-quick up`
- 如果同一个客户端上同时运行多个隧道，注意网段和密钥不要冲突
- 全网状下如果某个节点在 NAT 后，直连可能失败，需要额外的 NAT 穿透方案（如 STUN、中继）

## 测试

```bash
# 服务端 ping 客户端
ping -I 10.0.0.1 10.0.0.100

# 客户端 ping 服务端
ping 10.0.0.1

# 客户端之间互 ping
ping 10.0.0.101
```

## RustDesk / ssh 场景

WireGuard 隧道建立后，被阻断的服务可以通过隧道访问。以 RustDesk 为例：

### 场景 1：RustDesk 服务端在 wg 网内

如果 RustDesk 的 hbbs/hbbr 也在某个 wg 节点上，客户端直接连它的 wg 内网 IP：

```txt
RustDesk ID Server: 10.0.0.1
RustDesk Relay Server: 10.0.0.1
```

这种方式最干净，所有流量都走加密隧道，DPI 看不到。

### 场景 2：RustDesk 服务端在公网

如果 RustDesk 服务端在公网，但连接被 DPI 阻断，可以把 RustDesk 服务端的公网 IP 也加入 `AllowedIPs`，让去往它的流量走隧道：

```conf
AllowedIPs = 10.0.0.0/24, <RustDesk服务器公网IP>/32
```

这样客户端访问 RustDesk 服务端时，流量先到 wg 服务端，再由服务端转发出去。注意服务端需要做 NAT（MASQUERADE），否则回包路由不对：

```conf
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```

ssh 同理，把 ssh 服务端的 IP 加入 `AllowedIPs` 即可。

## 故障排查清单

按顺序排查：

- [ ] 服务端 `sudo wg show` 显示 `latest handshake`，且 `transfer` 在增长
- [ ] 服务端 `sysctl net.ipv4.ip_forward` 返回 1（星型拓扑必须）
- [ ] 服务端 `ip route show | grep wg0` 有各客户端的 `/32` 路由
- [ ] 服务端 `iptables -L FORWARD -n -v` 有 wg0 的 ACCEPT 规则（星型拓扑必须）
- [ ] 云服务商安全组开放 `UDP 51820`
- [ ] 服务端系统防火墙放行 `51820/udp` 和 `wg0` 接口
- [ ] 客户端 `AllowedIPs` 包含需要访问的网段
- [ ] 客户端 `Address` 用 `/32`，不是 `/24`
- [ ] **Windows 客户端已放行来自 `10.0.0.0/24` 的入站流量**
- [ ] 客户端能 `ping 10.0.0.1`
- [ ] 服务端能 `ping -I 10.0.0.1 <客户端IP>`
- [ ] 客户端之间能互 ping

### 抓包定位

如果还是不通，按这个顺序抓包：

```bash
# 服务端：看 ICMP 是否从 wg0 发出、是否有回包
sudo tcpdump -i wg0 -n icmp

# 服务端：看加密 UDP 包是否发出
sudo tcpdump -i eth0 -n udp port 51820
```

Windows 客户端：

```powershell
pktmon start --etw -c --comp nics
# 复现问题
pktmon stop
pktmon format pktmon.etl -o pktmon.txt
```

在输出里搜 `wireguard.sys`，看 ICMP 是否到达接口、是否有回包。如果只有 Rx 没有 Tx，基本就是 Windows 防火墙拦截。

## 常见坑

1. **服务端 `Address` 用 `/24`**：会导致 on-link 路由覆盖 Peer 路由，转发行为异常。用 `/32`。
2. **客户端 `Address` 用 `/24`**：Windows 上会添加 on-link 路由，导致流量不走隧道。用 `/32`。
3. **忘了开 IP 转发**：星型拓扑下客户端之间必然不通。`sysctl -w net.ipv4.ip_forward=1`。
4. **忘了放行 FORWARD**：同上，服务端不会转发。加 iptables 规则。
5. **Windows 防火墙拦截入站 ICMP**：服务端 ping 不通客户端，客户端之间也互 ping 不通。放行 `10.0.0.0/24`。
6. **接口名混淆**：`wg show` 显示的接口名和 Windows 网络适配器名不一定一致。用 `Get-NetAdapter` 查实际名称。
7. **`AllowedIPs` 只写服务端 `/32`**：客户端只能访问服务端，访问不了其他客户端。星型用 `10.0.0.0/24`。
8. **服务端只配了一个 Peer**：多客户端场景下每个客户端一个 `[Peer]` 段。
9. **全网状下忘了写 `Endpoint`**：不写就无法直连，流量会走默认路由。
10. **同一客户端上多个隧道共用密钥和网段**：会导致 endpoint 抖动、同 IP 绑两个接口。要么用不同密钥和网段，要么保证同一时刻只激活一个。

## 参考

- [WireGuard 官网](https://www.wireguard.com/)
- [WireGuard 安装](https://www.wireguard.com/install/)
