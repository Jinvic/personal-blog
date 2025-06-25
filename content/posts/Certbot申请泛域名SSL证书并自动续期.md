---
title: Certbot申请泛域名SSL证书并自动续期
date: '2024-12-11T17:15:32+08:00'
tags:
- 服务器
- Linux
- Web
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Certbot申请泛域名SSL证书与自动续期

参考：[使用 Let’s Encrypt 免费申请泛域名 SSL 证书，并实现自动续期](https://www.cnblogs.com/michaelshen/p/18538178)

本来不打算写这篇的，原教程已经很详细了。不过他使用的腾讯云，在自动续期这块有个cli工具可以用。而我用的华为云只能调api，所以还是得自己摸索下顺便记录。

## 安装 Certbot

虽然很想用包管理器，但官网都只用snap和pip安装，为了保险还是用到snap。

```bash
sudo snap install --classic certbot #安装Certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot #创建一个符号链接，确保可以执行certbot命令（相当于快捷方式）
```

## 域名验证&证书生成

Certbot需要验证你申请证书的域名是否确实属于你。具体流程就是给你个随机字符串让你解析到固定域名它再来验证。

```bash
sudo certbot certonly --manual --preferred-challenges dns -d *.example.com -d example.com
```

记得替换你的邮箱和域名。然后他会请求你的邮箱用于紧急更新和安全提醒。

![pic1](/post-images/Certbot申请泛域名SSL证书并自动续期/1.png)

然后是两次确认。第一次是服务条款选是，第二次是问能不能给你邮箱发广告邮件，可以选否。

![pic2](/post-images/Certbot申请泛域名SSL证书并自动续期/2.png)

接着就是给你一串字符串去解析到对应域名。例如我就是将那一串解析到`_acme-challenge.jinvic.top`。具体解析方法看你的DNS服务商，重点是**记录类型**要选`TXT`。

![pic3](/post-images/Certbot申请泛域名SSL证书并自动续期/3.png)

添加解析完成后稍等一会再继续。你也可以在[这里](https://toolbox.googleapps.com/apps/dig/#TXT/)验证解析是否成功。

验证成功后就会自动生成证书，并告诉你证书所在目录和过期时间。

![pic4](/post-images/Certbot申请泛域名SSL证书并自动续期/4.png)

## nginx配置证书

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
 
    location / {
        return 301 https://$host$request_uri;
    }
}
 
server {
    listen 443 ssl;
    server_name example.com www.example.com;
 
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
 
    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}
```

## 自动续期

内容有点多，新开了个项目：[Jinvic/certbot-huaweicloud](https://github.com/Jinvic/certbot-huaweicloud)。用这个项目生成供certbot钩子运行的程序。

```bash
certbot renew --manual --preferred-challenges=dns \
--manual-auth-hook /path/to/project/bin/certbot -use auth \
--manual-cleanup-hook /path/to/project/bin/certbot -use cleanup \
--deploy-hook "sudo nginx -s reload"
```

- `/path/to/project/bin/certbot` 为你编译生成的程序路径。
- `sudo nginx -s reload` 用于重新加载配置nginx配置。

编辑生成的程序需要读取配置文件。cd到项目目录或者将配置文件`.env`放到程序同一目录再执行上述命令。
