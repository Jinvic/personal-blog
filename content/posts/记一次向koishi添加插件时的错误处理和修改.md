---
title: 记一次向koishi添加插件时的错误处理和修改
date: '2025-01-08T16:48:06+08:00'
tags:
- 编程
- 杂项
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

给qq机器人绑osubot，用的[@tr4nce/osu-bot](https://github.com/Tsurumaki-Kokoro/koishi-plugin-osu-bot/tree/master)插件，需要[HitCircle API](https://github.com/Tsurumaki-Kokoro/HitCircle-API)作后端，就用docker装这个，3个多G的镜像，还好不怎么吃内存，我现在缺的就是内存。

跑HitCircle API时报错：

```bash
RuntimeError: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
```

因为mysql从8.0.3开始将默认的身份认证插件从mysql_native_password更改为caching_sha2_password，所以这里缺了个包。如果是手动部署直接在`requirements.txt`里加一行就行，但我用到是docker compose，只好在`docker-compose.yml`里加一行：

```yml
services:
  api_backend:
    command: sh -c "pip install cryptography && uvicorn main:app --host 0.0.0.0 --port 8900"
    image: tr4nce/hit-circle-api:latest
    ...
```

调试几次后又报错：`Error response from daemon: No such container:`，把新加的一行删了就好了。而且之后也没再报缺依赖。虽然不知道怎么回事但解决了就行吧。

关于redis，它本来是在`docker-compose.yml`又拉了一个redis镜像。我本来想换成宿主机的redis，但不能localhost直连，如果换公网ip因为它的镜像写死了不能用密码，我如果把本地redis改成无密码再暴露到公网风险太大，还是用的镜像。

即使是再同一个`docker-compose.yml`里，两个镜像也是各自独立的网络命名空间，不能localhost，得用服务名称作为主机名才行，即`redis:6379`。

别看搞这么麻烦，其实手动部署很简单就能解决，改下源码加个密码的配置项就行。这就是docker，部署起来确实方便，但遇到问题要改点啥也很麻烦。

然后插件本身也有点问题，因为它的命令全写的一级命令不好管理，我之后装其他bot还可能冲突，我就只好看看文档看看源码自己改一下。虽然对前端一窍不通，但和别的插件源码对照一下还是改好了，记一下怎么改：

首先再koishi安装目录下找到下载的插件，我这是`/koishi/data/node_modules/@tr4nce/koishi-plugin-osu-bot/lib`

在`index.js`里把一级指令改成二级指令，使用`/`或者`.`分隔，示例如下：

```typescript
// ctx.command('bind <username: text>', '绑定osu账号')
ctx.command('osu.bind <username: text>', '绑定osu账号')
```

然后在`locate/zh-CN.json`改下文档。这里建议copy一份[源码](https://github.com/Tsurumaki-Kokoro/koishi-plugin-osu-bot/blob/master/src/locales/zh-CN.yml)的yml改，改起来方便些:

```yml
// 更改前
commands:
  bind:
    description: 绑定你的 osu! 账号到你的 平台 账号
    ...

// 更改后
commands:
  // 添加一级指令
  osu:
    description: osu! 相关指令
    // 其余命令都向右缩进作为二级指令
    bind:
      description: 绑定你的 osu! 账号到你的 平台 账号
```

然后把yml转成json再压缩一下就行。
