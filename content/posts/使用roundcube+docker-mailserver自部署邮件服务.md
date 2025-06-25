---
title: 使用roundcube+docker-mailserver自部署邮件服务
date: '2025-02-07T13:57:54+08:00'
tags: []
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

我是直接在1Panel的应用市场装的Roundcube，不过默认配置有点问题我改了下端口，如下：

|Key|Value|
|---|---|
|IMAP 服务器| mail.jinvic.top|
|IMAP 端口| 993|
|SMTP 服务器| mail.jinvic.top|
|SMTP 端口| 465|

IMAP登录时还需要手动指定SSL/TLS加密方式，我不清楚环境变量怎么改就直接改的配置文件`./data/config/config.docker.inc.php`，缺点是每次重启都会重置。

```txt
$config['imap_host'] = 'ssl://mail.jinvic.top:993';
$config['smtp_host'] = 'ssl://mail.jinvic.top:465';
$config['username_domain'] = 'jinvic.top';
```

`username_domain`是可选项，配置后如`jinvic@jinvic.top`登录时就可以直接用jinvic作为用户名了，比较方便。

至于SSL/TLS配置，我没有在roundcube里配，而是在反向代理至roundcube服务时加了https配置，实测没有问题。

完成如上配置后就可以登录roundcube客户端访问docker-mailserver服务器，进行收发邮件操作了。

**250624更新**:

在1panel商店安装的roundcube只能使用1panel商店安装的mysql。就个人使用来说单独装个mysql还是太笨重了。为了切换到sqlite还是换成了自部署。参考[官方示例](https://github.com/roundcube/roundcubemail-docker/blob/master/examples/docker-compose-simple.yaml)改改就行。这里给出一个配置示例：

```yml
services:
  roundcube:
    image: roundcube/roundcubemail:latest
    container_name: roundcube
    environment:
      ROUNDCUBEMAIL_DEFAULT_HOST: "ssl://mail.jinvic.top"
      ROUNDCUBEMAIL_DEFAULT_PORT: "993"
      ROUNDCUBEMAIL_SMTP_SERVER: "ssl://mail.jinvic.top"
      ROUNDCUBEMAIL_SMTP_PORT: "465"
      ROUNDCUBEMAIL_USERNAME_DOMAIN: "jinvic.top"
      # ROUNDCUBEMAIL_REQUEST_PATH:
      # ROUNDCUBEMAIL_PLUGINS:
      # ROUNDCUBEMAIL_INSTALL_PLUGINS:
      # ROUNDCUBEMAIL_SKIN:
      # ROUNDCUBEMAIL_UPLOAD_MAX_FILESIZE:
      # ROUNDCUBEMAIL_SPELLCHECK_URI:
      # ROUNDCUBEMAIL_ASPELL_DICTS:

      ROUNDCUBE_DB_TYPE: "sqlite"
      ROUNDCUBE_DB_NAME: "/var/roundcube/db/roundcube.sqlite"
    volumes:
      - ./www:/var/www/html
      - ./data/config:/var/roundcube/config
      - ./data/db:/var/roundcube/db
    ports:
      - "12078:80"
    restart: always
```
