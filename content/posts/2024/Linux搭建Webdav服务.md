---
title: Linux搭建Webdav服务
date: '2024-12-10T08:59:01+08:00'
tags:
- Linux
categories:
- 自部署
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Linux搭建webDav服务

一直都有一个文件存储传输同步共享的需求，但苦于没有太好的解决方案。qq不安全难预览还会改你压缩包后缀名，纯强盗逻辑逼着你用他家的垃圾产品生态。百度网盘则是众所周知的限速。虽然我有会员，但感觉还是更适合长期大容量存储而非短期临时的频繁存取，自带的同步空间也不好用只能同步固定文件夹。WPS倒是可以自选同步文件夹，但本来就不是做文件管理这行的使用体验极差，遇上个几百兆的pdf就歇菜了，连基础的文档服务都做不好感觉纯噱头。现在打算在服务器上自己搭一个服务，不想再受这些鸟气。

本次搭建webdav使用[hacdias/webdav](https://github.com/hacdias/webdav/)，教程参考readme文件和博客[使用docker搭建webdav应用](https://sunjx97.github.io/posts/cb46f731/)。

## webdav

首先准备一个专门的文件目录，用于放置配置文件和作为webdav的存储路径。这里我的路径是`service/webdav`。

### webdav安装配置

**webdav配置**：

在目录下新建文件`config.yml`，写入如下内容：

```yml
# 监听任意网卡，多网卡可指定对应ip
address: 0.0.0.0
port: 6065
auth: true
prefix: /
modify: true
rules: []

# 跨域设置 | 不是很懂
cors:
  enabled: true
  credentials: true
  allowed_headers:
    - Depth
  allowed_hosts:
    - http://localhost:6065
  allowed_methods:
    - GET
  exposed_headers:
    - Content-Length
    - Content-Range

# 用户信息，如果 auth 为 true 生效  
users:
  - username: admin
    password: admin
    # 配置自己的 webdav 访问范围，此例为 /data 内所有文件
    scope: /data
    # 配置用户权限 默认为R（只读）
    permissions: CRUD
```

其中port是docker容器内的端口，可以自行修改。cors跨域设置这块不是很懂。后面的用户信息记得改改用户名和密码，以及根据需求配置用户权限。

**docker配置**：

在目录下新建文件`docker-compose.yml`，写入如下内容：

```yml
services:
  webdav:
    image: hacdias/webdav
    container_name: webdav
    restart: always
    ports:
      - 6065:6065
    volumes:
      - ./data:/data
      - ./config.yml:/config.yml
```

其中port前部分改成你在服务器上要使用的端口，记得开放防火墙和安全组。后部分则是docker内端口，和配置文件保持一致。

volumes的路径我使用的相对路径，也可以根据需求自行修改。第一行是webdav的文件存储位置，第二行是你的配置文件位置。

### 启动&重启服务

配置项完成后，使用`sudo docker-compose up -d`启动服务。

如果你修改了配置文件，如添加用户或修改密码，可以使用`sudo docker-compose restart webdav`重启服务。

### webdav justfile

> just 为您提供一种保存和运行项目特有命令的便捷方式。

[just地址](https://github.com/casey/just)
[just文档](https://just.systems/man/zh/%E8%AF%B4%E6%98%8E.html)

webdav相关命令的justfile如下：

```yml .justfile
alias re := restart

run:
    sudo docker-compose up -d

restart:
    sudo docker-compose restart webdav

del:
    sudo rm -r data/
```

## alist

> alist: 一个支持多种存储的文件列表程序，使用 Gin 和 Solidjs。

搭了个webdav本来该到此为止的，但又发现一个alist好像挺有意思，见猎心喜搭来看看。我就说明明webdav很常用但教程相对偏少，原来都用的这个。相当于一个中间层，使用alist连接不支持webdev的文件存储方案（如百度网盘），就可以把alist当webdev连接了。

### alist 安装配置登录

我是使用的docker安装，直接使用官方提供的docker-compose：

```yml
services:
    alist:
        image: 'xhofe/alist:latest'
        container_name: alist
        volumes:
            - '/etc/alist:/opt/alist/data'
        ports:
            - '5244:5244'
        environment:
            - PUID=0
            - PGID=0
            - UMASK=022
        restart: unless-stopped
```

使用`sudo docker-compose up -d`启动服务。然后访问`<服务器地址>:5244`登录控制台。初始账号为`admin`，密码随机生成，通过`sudo docker logs alist`查看日志：

![pic1](/post-images/Linux搭建Webdav服务/pic1.png)

登录后记得修改密码。

### 连接存储

连接存储直接看[官方文档](https://alist.nn.ci/zh/guide/drivers/common.html)就行。

有一点需要注意，我连接自建的webdav时直接用`<ip>:<port>`报错：`first path segment in URL cannot contain colon`，需要加上`http(s)://`协议头。

### alist justfile

alist 相关命令的justfile如下：

```yml .justfile
alias re := restart
alias upd := update

run:
    sudo docker-compose up -d

restart:
    sudo docker-compose restart alist

update:
    sudo docker-compose pull | \
    sudo docker-compose up -d

log:
    sudo docker logs alist
```

## 客户端

### raidrive

可以使用[raidrive](https://www.raidrive.com/)将Webdav挂载到电脑盘。配置示例如下，依次填入你的服务器地址，配置中设置的端口号，账号密码：
![pic2](/post-images/Linux搭建Webdav服务/pic2.png)

**注意**：如果你在配置中没有设置tls，不要勾选"地址"旁边的"安全连接"复选框。

### davfs2

Lunux系统挂载webdav可以使用davfs2，参考[这篇文章](https://blog.lincloud.pro/archives/36.html)
