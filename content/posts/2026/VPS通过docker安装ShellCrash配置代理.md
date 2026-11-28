---
title: VPS通过docker安装ShellCrash配置代理
date: '2026-11-28T16:59:32+08:00'
tags: 
- Linux
categories: 
- 自部署
draft: true
hiddenFromHomePage: false
hiddenFromSearch: false
---

# VPS通过docker安装ShellCrash配置代理

部署了Navidrome听歌，为了性能直接没有选择rclone挂载对象存储用云服务器的本地硬盘当音乐库。又陆续部署了[codetta](https://github.com/gavndev/codetta)管理元数据和[yubal](https://github.com/guillevc/yubal)下歌。使用yubal时发现从Youtube Music下载需要代理，但已经搭好了一堆东西再迁移到海外服务器比较麻烦，就使用[ShellCrash](https://github.com/juewuy/ShellCrash)便捷部署代理。

## docker部署

```yaml
services:
  shellcrash:
    image: juewuy/shellcrash:latest
    container_name: shellcrash
    restart: unless-stopped
    ports:
      - "7890:7890"
      - "9999:9999"
    cap_add:
      - NET_ADMIN
      - NET_RAW
      - SYS_ADMIN
    devices:
      - /dev/net/tun:/dev/net/tun
    volumes:
      - ./data/configs:/etc/ShellCrash/configs
      - ./data/yamls:/etc/ShellCrash/yamls
      - ./data/jsons:/etc/ShellCrash/jsons
    networks:
      - proxy

networks:
  proxy:
    external: true
    name: proxy
```

`port`要配两个端口，`7890`是代理端口，`9999`是UI面板端口。

`cap_add`添加一些权限，不添加权限启动服务时会有一些权限不足的报错：

```txt
Operation not permitted (you must be root)
netlink: Error: cache initialization failed: Operation not permitted
```

`devices`可选，如果用TUN模式需要配置，否则不配也行。

`networks`可选，我是建了一个专门的docker网络供不同容器通信。

**关于持久化**：官方示例使用的是命名卷，我个人习惯挂载到./data，直接挂载会有问题，本地空文件夹会遮盖镜像中已有文件。我的处理是建一个临时镜像把这些文件复制出来。也可以按官方示例使用挂载卷。

```bash
mkdir data
sudo docker run -d --name shellcrash-tmp juewuy/shellcrash:latest
sleep 5
sudo docker cp shellcrash-tmp:/etc/ShellCrash/configs ./data/
sudo docker cp shellcrash-tmp:/etc/ShellCrash/yamls   ./data/
sudo docker cp shellcrash-tmp:/etc/ShellCrash/jsons   ./data/
sudo docker rm -f shellcrash-tmp
```

最后`sudo docker compose up -d`启动容器。

## 配置

需要exec到容器内使用命令行工具交互配置。exec到容器内部后，可以随时使用`crash`命令启动配置工具。

```bash
sudo docker exec -it shellcrash sh -l
```

```txt

```
