---
title: Linux配置ClashMeta内核
date: '2024-12-20T11:33:14+08:00'
tags:
- Linux
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Linux配置ClashMeta内核

> 配置项没弄好，换 ~~数据删除~~ <!-- [ShellCrash](https://github.com/juewuy/ShellCrash/tree/dev) --> 解决了，感觉前面的工作都白干了。但写都写了还是发篇博客。

## 安装homebrew

使用`homebrew`安装mihomo。注意：`homebrew`不建议使用root用户直接安装，建议新创建一个用户再添加到sudo用户组。例如创建新用户`brew`:

```bash
sudo useradd brew
sudo passwd brew # 设置新用户的密码
sudo usermod -aG sudo brew
```

完成后使用新用户账号密码登录，可以使用`groups`命令检查用户是否属于sudo组。

使用如下命令安装`homebrew`：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

如果出现如下报错：

```txt
Error: Failed to install Homebrew Portable Ruby and cannot find another Ruby 3.3!
If there's no Homebrew Portable Ruby available for your processor:
- install Ruby 3.3 with your system package manager (or rbenv/ruby-build)
- make it first in your PATH
- try again
```

提示说找不到适合你的处理器架构的Ruby 3.3版本，需要自已装一个ruby，安装方法不在此赘述。我是在wsl上出现这个问题的，云服务器上没有出现。

安装Homebrew成功后，需要手动将其添加到PATH路径：

```bash
echo 'export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

然后使用`brew -v`验证homebrew是否能够正常使用。

## 安装mihomo

使用homebrew可以很方便地安装mihomo：

`homebrew install mihomo`

安装完成后提示信息如下：

```text
You need to customize /home/linuxbrew/.linuxbrew/etc/mihomo/config.yaml.

To start mihomo now and restart at login:
  brew services start mihomo
Or, if you don't want/need a background service you can just run:
  /home/linuxbrew/.linuxbrew/opt/mihomo/bin/mihomo -d /home/linuxbrew/.linuxbrew/etc/mihomo
```

提示你配置文件创建在`/home/linuxbrew/.linuxbrew/etc/mihomo/config.yaml`。有需要可以参考[文档](https://wiki.metacubex.one/config/)进行修改。

如下是一些使用`homebrew services`操作mihomo的命令：

```bash
brew services start mihomo      # 启动服务
brew services stop mihomo       # 停止服务
brew services list              # 查看服务状态
brew services restart mihomo·   # 重启服务
```

**【可选】：** 个人比较喜欢用[just](https://just.systems/man/zh/%E8%AF%B4%E6%98%8E.html)管理命令。`.justfile`文件如下：

```text
start:
    brew services start mihomo
stop:
    brew services stop mihomo
list:
    brew services list
restart:
    brew services restart mihomo

alias st:=start
alias sp:=stop
alias li:=list
alias re:=restart
```

## 用户界面

完全靠参数也不方便，我们先来配置ui界面。可选的面板有yacd,metacubexd等。

~~数据删除~~

<!-- - [metacubexd](https://github.com/MetaCubeX/metacubexd/archive/refs/heads/gh-pages.zip)
- [Yacd-meta](https://github.com/MetaCubeX/Yacd-meta/archive/refs/heads/gh-pages.zip)
- [Razord-meta](https://github.com/MetaCubeX/Razord-meta/archive/refs/heads/gh-pages.zip) -->

下载压缩包并解压。然后往配置文件中添加如下内容：

```yaml
external-controller: 0.0.0.0:9090# RESTful API 监听地址
secret: your_secret # `Authorization:Bearer ${secret}`  # 设置登录面板的密码
external-ui: /home/brew/mihomo/metacubexd-gh-pages/     # 换成你压缩包解压出来的文件夹的地址
```

端口按需求改，地址换成你自己的，保存后重启服务。在防火墙和安全组开放相关端口后，访问`http://<你的服务器ip>:9093/ui`即可登录面板。

## 代理配置

见 ~~数据删除~~ <!-- [subconverter](https://github.com/tindy2013/subconverter/tree/master) --> 。
更方便的用法是使用现成的客户端，如 ~~数据删除~~ <!-- clash for windows --> ，~~数据删除~~ <!-- clash verge rev -->。

## https配置

虽然注释写着要配置tls的证书路径，但实测只要反向代理时配了证书，配置项里写一下https的端口就行。
如果不进行反向代理直接通过ip和端口号访问才需要在设置里配证书路径。

```yaml
# 直接通过ip访问还需要配置证书
tls:
  certificate: string # 证书 PEM 格式，或者 证书的路径
  private-key: string # 证书对应的私钥 PEM 格式，或者私钥路径
# 反向代理只需要配置https端口
external-controller-tls: 0.0.0.0:9443 # RESTful API HTTPS 监听地址，需要配置 tls 部分配置文件
```
