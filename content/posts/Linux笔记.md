---
title: Linux笔记
date: '2024-11-02T13:31:03+08:00'
tags:
- Linux
- 笔记
draft: true
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Linux笔记

@[TOC]

本来最开始学Linux时用VMware装了个ubuntu镜像，但用起来卡卡的。虽然最开始时冲着图像界面去的，但后来发现用命令行操作更常用。于是又装了个WSL2学习命令行操作。而且挂载磁盘也比VMware方便。官方文档也很详细，中文支持很好，所以学习起来也很方便。
这里记一下使用过程中遇到的一些问题。

## 常用命令

并没打算搞个命令大全之类的，只是记一下最常用且有用的几个。用多了随时添，没必要整一大堆跟背单词一样。

- ls 列出目录中的文件
- cd 更改当前目录
- pwd 打印当前工作目录
- cat 显示文件的内容
- rm 删除文件
- find 在目录层次结构中搜索文件
- whereis 在特定目录中查找符合条件的文件
- sudo 以超级用户身份执行命令
- touch 创建文件/修改文件属性
- nohup 在系统后台不挂断地运行命令
- hostname -I 获取ip地址，用户访问wsl中启动的服务

- nano 编辑器，对没linux基础的我来说比vim好用
- htop 交互式进程查看器，支持鼠标操作

## 部分应用安装

只是做个集合整理，避免每次重装时一个个去翻文档和官网。

### 安装vfox

[来源](https://vfox.lhan.me/zh-hans/guides/quick-start.html)

**安装vfox**：

apt安装命令：

```bash
echo "deb [trusted=yes] https://apt.fury.io/versionfox/ /" | sudo tee /etc/apt/sources.list.d/versionfox.list
 sudo apt-get update
 sudo apt-get install vfox
```

**挂载vfox到Shell**：

```bash
echo 'eval "$(vfox activate bash)"' >> ~/.bashrc
```

### 安装make

这里使用vfox安装并进行版本管理。
同时作个vfox安装应用教程。

``` bash
# 添加插件
vfox add make
# 查看所有可用版本
# vfox search make
# 安装最新版本
vfox install make@latest
# 设置使用版本
vfox use -g make
```

其中作用域参数有`-p -g -s`三种，分别表示项目，全局，会话。详情略。

### 安装protobuf

[来源](https://grpc.org.cn/docs/protoc-installation/)

虽然vfox提供了unofficial的protobuf插件，但好像有bug安装不了，还是用apt了。

```bash
sudo apt install -y protobuf-compiler
```

如果要进行go开发，还需要额外安装插件：

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
```

### 安装go

还是使用vfox，见上[安装make](#安装make)。

不要忘了更新path，虽然好像不加这行也能在其他目录调用。可能vfox时默认加的：

```bash
export PATH="$PATH:$(go env GOPATH)/bin"
```

如果要进行grpc开发，还需要安装对应插件：

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

## WSL2重装系统

有种说法是再ubuntu的应用设置中选择重置，亲测无效。

后来又找到别的方法。输入`wsl.exe --unregister Ubuntu`，再`wsl --install`就能重新注册用户了。

后续流程按官方的[最佳实践](https://learn.microsoft.com/zh-cn/windows/wsl/setup/environment)来就行。

## WSL2配置代理

1. 如clash等代理软件打开Allow LAN（允许局域网链接）选项
2. 在wsl中，使用 `cd~` 进入用户目录
3. 编辑`.bashrc`文件，在末尾添加如下内容：

   ```bash
   hostip=$(ip route show | grep -i default | awk '{ print $3}')
    export https_proxy="http://${hostip}:7890"
    export http_proxy="http://${hostip}:7890"
    export all_proxy="socks5://${hostip}:7890"
   ```

4. 保存退出，执行 `source ~/.bashrc` 使配置生效
5. 使用`wget www.google.com`测试是否成功

我看很多教程获取ip地址都用的
`cat /etc/resolv.conf |grep -oP '(?<=nameserver\ ).*'`
可我看[官方教程](https://learn.microsoft.com/zh-cn/windows/wsl/networking#default-networking-mode-nat)是
`ip route show | grep -i default | awk '{ print $3}'`
也不知道为什么，反正我用前一个不行后一个行。

## Linux安装homebrew

虽然[Homebrew官网](https://brew.sh/zh-cn/)上就一句话：

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

但如果你真的直接把这行代码复制粘贴到终端，大概率看到如下报错：

```text
Error: Failed to install Homebrew Portable Ruby and cannot find another Ruby 3.3!
If there's no Homebrew Portable Ruby available for your processor:
- install Ruby 3.3 with your system package manager (or rbenv/ruby-build)
- make it first in your PATH
- try again
```

提示说找不到适合你的处理器架构的Ruby 3.3版本，所以我们需要先安装一个Ruby 3.3版本。这里顺便推荐一个版本管理工具[vfox](https://vfox.lhan.me/zh-hans/)。

安装Ruby后再安装Homebrew，在茫茫的返回中你找到一行：

`==> Installation successful!`

但是当你再次输入`brew -v`命令时，却提示`command not found`。再看一眼发现了在这行上面还有个报错：

```text
Warning: /home/linuxbrew/.linuxbrew/bin is not in your PATH.
  Instructions on how to configure your shell for Homebrew
  can be found in the 'Next steps' section below.
```

这是因为Homebrew的安装路径不在你的PATH环境变量中，所以需要手动添加。

```bash
echo 'export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

执行如上命令将homebrew添加到path。这时再执行`brew -v`就能看到版本号了。

## 用户管理

当然可以一个root打天下。但我还是想为不同用途分下多用户。记一下用户操作。

**新建用户**：`useradd 选项 用户名`。可选项如下：

- `-c` comment 指定一段注释性描述。
- `-d` 目录 指定用户主目录，如果此目录不存在，则同时使用-m选项，可以创建主目录。
- `-g` 用户组 指定用户所属的用户组。
- `-G` 用户组，用户组 指定用户所属的附加组。
- `-s` Shell文件 指定用户的登录Shell。
- `-u` 用户号 指定用户的用户号，如果同时有-o选项，则可以重复使用其他用户的标识号。

推荐操作：`sudo useradd -m username -s /bin/bash -g sudo`，创建用户的同时新建主目录并设置bash。

**删除用户**：`userdel 选项 用户名`。推荐操作`userdel -r username`，`-r`选项将连主目录一起删除。

**修改用户**：`usermod 选项 用户名`。选项同上。

**修改密码**：`passwd 选项 用户名`。可选项如下：

- `-l` 锁定口令，即禁用账号。
- `-u` 口令解锁。
- `-d` 使账号无口令。
- `-f` 强迫用户下次登录时修改口令。

**查看用户组**：`group username`或`id username`
