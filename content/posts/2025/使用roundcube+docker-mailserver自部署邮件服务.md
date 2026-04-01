---
title: 使用roundcube+docker-mailserver自部署邮件服务
date: '2025-02-07T13:57:54+08:00'
tags:
- Docker
categories:
- 自部署
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 使用roundcube+docker-mailserver自部署邮件服务

在做一个开源项目的邮件通知功能，本来用smtp发个邮件就行，不知怎么的就捣鼓着就开始自建邮件服务器了。不过用自己的域名实现邮件服务很酷不是吗？

## 参考

**教程**：

- [1Panel 自建邮局 - Docker Mailserver](https://www.anye.xyz/archives/itwz2wfX)
- [Usage - Docker Mailserver](https://docker-mailserver.github.io/docker-mailserver/latest/usage/)

**工具**：

- [smtp发信测试](https://ll00.cn/Mail/index.html)
- [MX ToolBox](https://mxtoolbox.com/SuperTool.aspx)

## 邮件服务器 Docker Mailserver

本来是打算在应用商店直接部署的，但不知道为什么总报错安装失败，就自己用docker-composer部署了。

### 证书申请

首先要实现SSL/TLS安全连接你必须有个证书，申请证书的过程略，1Panel本身的证书功能就很方便了。申请好的证书别忘了**推送到本地目录**，记下这个路径之后要用到。

### DNS配置

要让别人能找到你的邮件服务器地址需要配置DNS，配置项很多我也不是很懂，详情可以参考开头的文章。这里以我的域名`jinvic.top`为例：

|域名|记录类型|记录值|备注|
|---:|---|---|---|
|jinvic.top|MX|10 mail.jinvic.top|改成你自己的域名|
|email.jinvic.top|A|<你的服务器公网ip>||
|jinvic.top|TXT|"v=spf1 mx -all"|SPF 记录|
|_dmarc.jinvic.top|TXT|"v=DMARC1; p=reject; adkim=s; aspf=s"|DMARC 记录|
|mail._domainkey.jinvic.top|TXT|<稍后生成>|DKIM 记录|

### 开放端口

DMS用到的端口有`25,143,465,587,993`这些，全部在防火墙开放一下。如果用到是服务商提供的云服务器，记得配置下安全组规则。

### 部署DMS

在准备好的工作目录下，通过如下命令获取docker-compose和.env文件：

```bash
DMS_GITHUB_URL="https://raw.githubusercontent.com/docker-mailserver/docker-mailserver/master"
wget "${DMS_GITHUB_URL}/compose.yaml"
wget "${DMS_GITHUB_URL}/mailserver.env"
```

compose.yaml中如下内容需要自主配置：

- `hostname`：改成你自己的域名，即DNS中A记录配置的域名，如`email.jinvic.top`，注意不能是`jinvic.top`。
- `volumes`: 将你的证书路径挂载进去，配环境变量用

如下是我的compose.yaml示例：

```yaml
services:
  mailserver:
    image: ghcr.io/docker-mailserver/docker-mailserver:latest
    container_name: mailserver
    # Provide the FQDN of your mail server here (Your DNS MX record should point to this value)
    hostname: mail.jinvic.top
    env_file: mailserver.env
    # More information about the mail-server ports:
    # https://docker-mailserver.github.io/docker-mailserver/latest/config/security/understanding-the-ports/
    ports:
      - "25:25"    # SMTP  (explicit TLS => STARTTLS, Authentication is DISABLED => use port 465/587 instead)
      - "143:143"  # IMAP4 (explicit TLS => STARTTLS)
      - "465:465"  # ESMTP (implicit TLS)
      - "587:587"  # ESMTP (explicit TLS => STARTTLS)
      - "993:993"  # IMAP4 (implicit TLS)
    volumes:
      - ./docker-data/dms/mail-data/:/var/mail/
      - ./docker-data/dms/mail-state/:/var/mail-state/
      - ./docker-data/dms/mail-logs/:/var/log/mail/
      - ./docker-data/dms/config/:/tmp/docker-mailserver/
      - /cert/jinvic.top:/cert/jinvic.top:ro
    restart: always
    stop_grace_period: 1m
    # Uncomment if using `ENABLE_FAIL2BAN=1`:
    # cap_add:
    #   - NET_ADMIN
    healthcheck:
      test: "ss --listening --tcp | grep -P 'LISTEN.+:smtp' || exit 1"
      timeout: 3s
      retries: 0
```

mailserver.env中如下内容需要自主配置：

- `SSL_TYPE`：设置为`manual`
- `SSL_CERT_PATH` 和 `SSL_KEY_PATH`：映射的证书路径
- `POSTMASTER_ADDRESS`：非必选，邮件服务器的管理员邮箱地址

示例：

```env
SSL_TYPE=manual
SSL_CERT_PATH=/cert/jinvic.top/fullchain.pem
SSL_KEY_PATH=/cert/jinvic.top/privkey.pem
POSTMASTER_ADDRESS=jinvic@jinvic.top
```

配置完成后，使用`docker-compose up -d`启动服务。

### 容器内配置

通过`docker exec -ti <CONTAINER NAME> /bin/sh`启动容器内终端。

- **创建用户**： `setup email add jinvic@jinvic.top`
    之后会让你输入密码。之后就可以用这套账密登录roundcube了。
- **生成DKIM**：`setup config dkim`
    将括号内文本写入DNS（见 [DNS配置](#dns配置)）。

## 邮件客户端 Roundcube

### 安装配置

在1panel商店安装的roundcube只能使用1panel商店安装的mysql。就个人使用来说单独装个mysql还是太笨重了。为了切换到sqlite还是换成了自部署。相关配置项可以看看[dockerhub](https://hub.docker.com/r/roundcube/roundcubemail)页面，docker compose 文件参考[官方示例](https://github.com/roundcube/roundcubemail-docker/blob/master/examples/docker-compose-simple.yaml)改改就行。这里给出自用配置：

```yml
services:
  roundcube:
    image: roundcube/roundcubemail:latest-apache
    container_name: roundcube
    environment:
      # ROUNDCUBEMAIL_DEFAULT_HOST: "ssl://mail.jinvic.top"
      ROUNDCUBEMAIL_DEFAULT_HOST: "ssl://mailserver"
      ROUNDCUBEMAIL_DEFAULT_PORT: "993"
      # ROUNDCUBEMAIL_SMTP_SERVER: "ssl://mail.jinvic.top"
      ROUNDCUBEMAIL_SMTP_SERVER: "ssl://mailserver"
      ROUNDCUBEMAIL_SMTP_PORT: "465"
      ROUNDCUBEMAIL_USERNAME_DOMAIN: "jinvic.top"
      # ROUNDCUBEMAIL_REQUEST_PATH:
      # ROUNDCUBEMAIL_PLUGINS:
      # ROUNDCUBEMAIL_INSTALL_PLUGINS:
      # ROUNDCUBEMAIL_SKIN:
      # ROUNDCUBEMAIL_UPLOAD_MAX_FILESIZE:
      # ROUNDCUBEMAIL_SPELLCHECK_URI:
      # ROUNDCUBEMAIL_ASPELL_DICTS:

      ROUNDCUBEMAIL_DB_TYPE: "sqlite"
      ROUNDCUBEMAIL_DB_NAME: "roundcube"
    volumes:
      - ./www:/var/www/html
      - ./data/config:/var/roundcube/config
      - ./data/db:/var/roundcube/db
    ports:
      - "12078:80"
    restart: always
    networks:
      - mail_network

networks:
  mail_network:
    external: true
```

可以看到，我添加了一个docker网络方便容器间通信。在外部创建`mail_network`并在mailserver的docker compose文件中也添加相关配置即可。

### 登录失败

在尝试登录时，可能遇到登录失败，控制台报错如下：

```bash
/?_task=login:1  POST https://email.jinvic.top/?_task=login 401 (Unauthorized)
```

容器日志报错如下：

```bash
IMAP Error: Login failed for jinvic@jinvic.top against mailserver from 172.28.0.1. Could not connect to ssl://mailserver:993: Unknown reason
```

提示连接到mailserver失败了。但使用openssl连接又是正常的：

```bash
openssl s_client -connect mailserver:993 -crlf
...
* OK [CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE LITERAL+ AUTH=PLAIN AUTH=LOGIN] Dovecot (Debian) ready.
```

说明Roundcube 的 PHP 环境无法通过 fsockopen 或 stream_socket_client 建立 SSL 连接到 mailserver:993。

可能是因为我的证书来自Let's Encrypt。为了解决这个问题，可以强制禁用证书验证。毕竟我是通过docker内部网络进行通信的。

在`./data/config`下创建`config.local.inc.php`并写入：

```php
<?php

// /var/roundcube/config/config.local.inc.php

// ------------------------------
// 修复：IMAP/SMTP SSL 连接失败
// ------------------------------
$config['imap_conn_options'] = array(
    'ssl' => array(
        'verify_peer'      => false,
        'verify_peer_name' => false,
        'allow_self_signed' => true,
    ),
);
$config['smtp_conn_options'] = array(
    'ssl' => array(
        'verify_peer'      => false,
        'verify_peer_name' => false,
        'allow_self_signed' => true,
    ),
);

// ------------------------------
// 调试配置（可选）
// ------------------------------
// $config['debug_level'] = 5;
// $config['log_driver'] = 'stdout';
// $config['log_logins'] = true;
// $config['smtp_log'] = true;

// ------------------------------
// 其他安全和用户体验设置
// ------------------------------
// $config['des_key'] = 'your-secret-key-change-this-1234567890'; // 生成一个随机密钥
// $config['product_name'] = 'My Webmail';
// $config['temp_dir'] = '/tmp/roundcube-temp';
```

记得确认一下是否正确挂载到了`/var/roundcube/config/`。

## QQ邮箱代收发配置

虽然部署了RoundCube能用于登录邮箱，但需要主动登录检查是否收到新邮件有些麻烦。可以尝试与已有的通知功能绑定。我尝试的是QQ邮箱的代收发服务。

QQ邮箱的收件服务不使用imap，而是pop3。docker-mailserver默认不启用这个功能，需要修改配置文件：

```env
# Enables POP3 service
# - **0** => Disabled
# - 1     => Enabled
ENABLE_POP3=1
```

至于pop3和smtp子域名，我懒得配这么多就统一用`mail.jinvic.top`了，只要A记录指向你服务器的IP地址就行。虽然这样的做法并不规范。

## 无法发信处理

> [!NOTE]
> 经测试，QQ邮箱可以正常接收公网IP发信，无需配置第三方smtp

如果你尝试向Google，outlook等常用邮箱发信，可能会被退回，伴随如下提示：

```txt
outlook-com.olc.protection.outlook.com[52.101.41.20] said: 550 5.7.1
    Service unavailable, Client host [1.92.158.23] blocked using Spamhaus. To
    request removal from this list see
    https://www.spamhaus.org/query/ip/1.92.158.23 (AS3130). [Name=Protocol
    Filter Agent][AGT=PFA][MxId=11BBA0D9B700029C]
    [SJ5PEPF000001E9.namprd05.prod.outlook.com 2025-08-07T01:59:44.262Z
    08DDD06CE15C1A45] (in reply to MAIL FROM command)
```

说明ip被Spamhaus禁用了。查询得知类型为 **PBL**（Policy Block List）。进一步了解得知绝大多数的公网IP默认都在 PBL 上，因为这些 IP 不是专用于邮件服务的“静态 MX IP”。

解决方法是使用第三方smtp中继服务（smtp reply service）。

本来想试试刚刚配置的QQ邮箱代发，但还是被退回了。直接使用QQ邮箱发送好像就没问题。其他国外的第三方代理整起来也挺麻烦的。

另一种解决方法是直接申请解封。

在刚刚的提示中有着查询网址`https://www.spamhaus.org/query/ip/1.92.158.23`，在这个页面也可以操作申请解封。填入自己的邮箱，Spamhaus 将向邮箱发送一封验证邮件，点击邮件中的验证链接就行。

```txt
Removal successful.
Your removal request for 1.92.158.23 has been processed. Please allow some time for servers around the world to update their data.

Please note that the resource will be re-listed if malicious activity is detected in the future.
```

需要注意如果进行恶意活动被检测到会被重新封禁为**SBL**或**XBL**类型，到时候可能就不是一封验证邮件的事了。

## 评分测试

可以使用邮箱评分网站，如[mailgenius](https://www.mailgenius.com)对邮件服务器进行评分，查看哪些地方有问题。

我在检查时也发现了一些问题：

> The Mail Server IP Address that your email was received from does not have a Reverse DNS pointer (PTR) record that resolves to the correct received-from Mail Server domain.

提示我没有设置PTR记录。我使用的是华为云的DNS解析，直接在控制台添加反向解析就行。添加完成后通过`dig -x <ip> +short`命令验证：

```bash
dig -x 1.92.158.23 +short
mail.jinvic.top.
```

此外还有一些小问题，影响不大就没管。例如top这个TLD不够受信任，我买top域名就是为了便宜，而且迁移也麻烦。以及没有BIMI记录，这个主要是给大公司做品牌推广用的。我一个个人用户也不需要。
