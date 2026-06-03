---
title: 通过WireGuard解决ssh和RustDesk被阻断问题
date: '2026-06-03T09:11:17+08:00'
tags: 
- Linux
categories: 
- 问题
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 通过WireGuard解决ssh和RustDesk被阻断问题

最近ssh和ruskdesk突然不可用，分别报错`kex_exchange_identification: read: Connection reset`和`os error 10054`，可能是被防火墙或者`DPI`（Deep Packet Inspection 深度包检测）阻断了。尝试配置WireGuard作为VPN加密来解决问题。

## 服务端配置

首先安装wireguard：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install wireguard wireguard-tools -y
```

生成服务端密钥对：

```bash
# 创建WireGuard配置目录
sudo mkdir -p /etc/wireguard
cd /etc/wireguard

# 生成私钥（服务器的私钥）
wg genkey | sudo tee server_private.key
sudo chmod 600 server_private.key

# 生成公钥
sudo cat server_private.key | wg pubkey | sudo tee server_public.key

# 查看并保存公钥（需要给客户端配置用）
sudo cat server_public.key
```

然后创建配置文件`wg0.conf`：

```conf
[Interface]
# 服务器的私钥（从server_private.key复制）
PrivateKey = <服务器私钥>

# 服务器的WireGuard内网IP（选择10.0.0.x网段）
Address = 10.0.0.2/24

# 监听端口（UDP）
ListenPort = 51820

# 可选：MTU设置（避免分片问题）
MTU = 1420

[Peer]
# 客户端的公钥（需要从客户端获取）
PublicKey = <客户端公钥>

# 允许客户端使用的内网IP（分配给它10.0.0.1）
AllowedIPs = 10.0.0.1/32

# 保持连接（对于NAT后的客户端很重要）
PersistentKeepalive = 25
```

在防火墙开放端口`51820`的udp协议。如果服务商有安全组配置，在安全组也开放端口。

最后设置服务为开机自启并启动服务：

```bash
# 设置为开机自启
sudo systemctl enable wg-quick@wg0

# 启动WireGuard接口
sudo wg-quick up wg0

# 查看状态
sudo wg show

# 停止WireGuard接口
# sudo wg-quick down wg0
```

## 客户端配置

在[官网](https://www.wireguard.com/install/)下载客户端，安装后打开，选择 *新建隧道 -> 新建空隧道*，就会自动生成密钥对，将公钥填入服务器配置。

客户端配置如下：

```conf
[Interface]
# 客户端的私钥（自动生成）
PrivateKey = <客户端私钥>
# 客户端的WireGuard内网IP（选择10.0.0.x网段）
Address = 10.0.0.1/24

[Peer]
# 服务器的公钥（从服务器获取）
PublicKey = <服务器的公钥>

# 服务器的公网IP和端口
Endpoint = <服务器的公网IP>:51820

# 允许的IP段（让发往RustDesk的流量走隧道）
AllowedIPs = 10.0.0.0/24

# 保持连接
PersistentKeepalive = 25
```

配置完成后，确保服务端启动了wg服务，然后就可以连接测试。此时ssh服务应该已经可用。

```bash
# 测试网络是否联通
ping 10.0.0.2

## 测试ssh服务是否可用
ssh root@10.0.0.2
```

## RustDesk配置

此时虽然ssh可用，但RustDesk仍不可用，需要进行额外配置。

打开客户端设置，在*网络 -> ID/中继服务器*中，修改ID服务器地址。

理论上这里修改为内网ip`10.0.0.2`就可用，但我测试时失败。我的解决方法是使用用一个域名`rustdesk.example.com`，配置DNS解析指向服务器的公网ip，同时在客户端修改host文件指向内网ip：

```bash
notepad C:\Windows\System32\drivers\etc\hosts
```

```txt
# 在文件末尾添加

10.0.0.2    rustdesk.example.com
```

然后修改客户端的ID服务器地址为`rustdesk.example.com`后连接成功。如果还是不行，也可以尝试在客户端显示指定中继服务器，或者服务端的hbbs通过`-r`选项指定中继。

## 故障排查清单

- [ ] 服务端 `sudo wg show` 显示 `latest handshake`
- [ ] 云服务商安全组开放 `UDP 51820`
- [ ] 客户端能 `ping 10.0.0.2`
- [ ] RustDesk 服务端运行：`docker logs rustdesk-hbbs`
- [ ] 防火墙开放 `21115-21119/tcp` 和 `21116/udp`
