---
title: 在1Panel环境下部署Mox邮件服务器
date: '2026-04-03T09:00:02+08:00'
tags: 
- Docker
categories: 
- 自部署
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 在1Panel环境下部署Mox邮件服务器

> Mox is a modern full-featured open source secure mail server for low-maintenance self-hosted email.

[mox](https://github.com/mjl-/mox)是一个现代功能齐全的开源安全邮件服务器，适用于低维护的自托管电子邮件。我之前也使用过[docker-mailserver](https://github.com/docker-mailserver/docker-mailserver)，但它作为生产级的邮件服务器内存占用太大，有200-300M左右。相比之下，mox就显得轻量多了，只有20-30M。作为个人使用，当然是占用越低越好。而且mox自带一个开箱即用的Webmail，不用再额外部署[Roundcube](https://github.com/roundcube/roundcubemail)之类的邮件客户端。

## 开放端口配置

邮件服务用到的端口有`143,25,443,587,993`等。在你的服务器防火墙上开放这些端口。同时，也别忘了在云服务商的安全组（防火墙）中放行这些端口。

## docker部署初始化

官方推荐在专门的服务器上使用二进制部署。但我没有条件专门为它租用一台服务器，就选择docker部署到现有服务器上，和其他应用并行使用。在已有服务的服务器上部署mox最大的问题是其默认使用的80/443端口已被`OpenResty`等占用，需要更改一些配置，比较繁琐。

如下是官方的`docker compose`文件示例。

```yml
# Before launching mox, run the quickstart to create config files for running as
# user the mox user (create it on the host system first, e.g. "useradd -d $PWD mox"):
#
# mkdir config data web
# docker-compose run mox mox quickstart you@yourdomain.example $(id -u mox)
#
# note: if you are running quickstart on a different machine than you will deploy
# mox to, use the "quickstart -hostname ..." flag.
#
# After following the quickstart instructions you can start mox:
#
# docker-compose up
#
#
# If you want to run "mox localserve", you could start it like this:
#
# docker run \
#     -p 127.0.0.1:25:1025 \
#     -p 127.0.0.1:465:1465 \
#     -p 127.0.0.1:587:1587 \
#     -p 127.0.0.1:993:1993 \
#     -p 127.0.0.1:143:1143 \
#     -p 127.0.0.1:443:1443 \
#     -p 127.0.0.1:80:1080 \
#     r.xmox.nl/mox:latest mox localserve -ip 0.0.0.0
#
# The -ip flag ensures connections to the published ports make it to mox, and it
# prevents listening on ::1 (IPv6 is not enabled in docker by default).

services:
  mox:
    # Replace "latest" with the version you want to run, see https://r.xmox.nl/r/mox/.
    # Include the @sha256:... digest to ensure you get the listed image.
    image: r.xmox.nl/mox:latest
    container_name: mox
    environment:
      - MOX_DOCKER=yes # Quickstart won't try to write systemd service file.
    # Mox needs host networking because it needs access to the IPs of the
    # machine, and the IPs of incoming connections for spam filtering.
    network_mode: 'host'
    volumes:
      - ./config:/mox/config:z
      - ./data:/mox/data:z
      # web is optional but recommended to bind in, useful for serving static files with
      # the webserver.
      - ./web:/mox/web:z
      # 挂载 1Panel 的证书目录
      - /cert:/mox/certs:ro
    working_dir: /mox
    restart: on-failure
    healthcheck:
      test: netstat -nlt | grep ':25 '
      interval: 1s
      timeout: 1s
      retries: 10
```

需要注意的是，必须使用 `host` 网络模式，否则垃圾邮件过滤和限流功能会失效（所有连接源 IP 会变成 Docker 网关 IP）。

这里我额外添加了一个`/cert:/mox/certs:ro`挂载，用于将1Panel的证书挂载进去使用。由于mox的默认使用场景是在无其他服务的裸机上运行，所以会使用`Let's Encrypt`自动申请证书。但我们已有1Panel进行证书和反代管理，就集成到mox中，禁用ACME并使用现有的证书。具体配置会在下面详细论述。

可以看到`docker-compose.yml`开头的注释已经给出了初始化流程。`mox quickstart`的用法如下：

```bash
usage: mox quickstart [-skipdial] [-existing-webserver] [-hostname host] user@domain [user | uid]
-existing-webserver
        use if a webserver is already running, so mox won't listen on port 80 and 443; you'll have to provide tls certificates/keys, and configure the existing webserver as reverse proxy, forwarding requests to mox.
-hostname string
        hostname mox will run on, by default the hostname of the machine quickstart runs on; if specified, the IPs for the hostname are configured for the public listener
-skipdial
        skip check for outgoing smtp (port 25) connectivity or for domain age with rdap
```

我们运行如下命令：

```bash
docker-compose run mox mox quickstart -existing-webserver -skipdial -hostname mail.yourdomain.com user@yourdomain.com $(id -u)
```

这里的`$(id -u)`是获取当前用户的 UID，而不是`$(id -u mox)`。示例命令的`$(id -u mox)`是在宿主机创建了`mox`系统用户的情况下。如果没有创建，可以省略或使用当前用户id。

我们启用了`-existing-webserver`和`-skipdial`选项。前者是因为我们是部署在1Panel环境，80/443端口已被`OpenResty`占用。后者是因为部署在腾讯云服务器上，而国内大厂基本都禁用了25端口的出方向，避免被滥用发垃圾邮件。虽然可以尝试申请解封，但比较麻烦。我还是选择通过resend进行smtp中继。如果你也和我一样选择中继方案，或者暂时没有外发邮件的需求，强烈建议启用 `-skipdial`来避免`mox quickstart`因无法连接外部 25 端口而报错。或者如果是更宽松的提供商，可以直接使用25端口发信，则不必启用该选项。

运行命令后如果没问题会输出大段日志内容，结尾是：

```log
Enjoy!

(output is also written to quickstart.log)
```

由于容器内的工作目录没有挂载到宿主机，`quickstart.log`在容器停止后会丢失。建议在终端输出后立即**手动复制保存**其中的关键信息，包括初始密码、管理员密码和DNS配置。

## DNS配置

`quickstart.log`提供了大量DNS配置，需要在DNS服务商处进行配置。其中，`A`、`MX`、`SPF`、`DKIM`和`DMARC`记录是保证邮件能够基本收发和通过反垃圾检测的核心记录，必须配置。其余记录（如`MTA-STS`、`TLSRPT`、`SRV`等）可以增强安全性和便利性，强烈建议一并加上。

| 类型  | 主机名                              | 值                                                             |
| ----- | ----------------------------------- | -------------------------------------------------------------- |
| A     | `mail.yourdomain.com`               | `服务器公网 IP`                                                |
| MX    | `yourdomain.com`                    | `10 mail.yourdomain.com`                                       |
| TXT   | `mail.yourdomain.com`               | `v=spf1 a -all`                                                |
| TXT   | `yourdomain.com`                    | `v=spf1 ip4:x.x.x.x mx ~all`                                   |
| TXT   | `_dmarc.yourdomain.com`             | `v=DMARC1;p=reject;rua=mailto:dmarcreports@yourdomain.com!10m` |
| TXT   | `2026a._domainkey.yourdomain.com`   | DKIM 公钥                                                      |
| TXT   | `2026b._domainkey.yourdomain.com`   | DKIM 公钥（备用）                                              |
| TXT   | `_smtp._tls.yourdomain.com`         | `v=TLSRPTv1; rua=mailto:tlsreports@yourdomain.com`             |
| TXT   | `_mta-sts.yourdomain.com`           | `v=STSv1; id=20260403T000000`                                  |
| CNAME | `mta-sts.yourdomain.com`            | `mail.yourdomain.com`                                          |
| CNAME | `autoconfig.yourdomain.com`         | `mail.yourdomain.com`                                          |
| SRV   | `_autodiscover._tcp.yourdomain.com` | `0 1 443 mail.yourdomain.com`                                  |
| SRV   | `_imaps._tcp.yourdomain.com`        | `0 1 993 mail.yourdomain.com`                                  |
| SRV   | `_submissions._tcp.yourdomain.com`  | `0 1 465 mail.yourdomain.com`                                  |
| SRV   | `_imap._tcp.yourdomain.com`         | `0 0 0 .`（禁用）                                              |
| SRV   | `_submission._tcp.yourdomain.com`   | `0 0 0 .`（禁用）                                              |
| SRV   | `_pop3._tcp.yourdomain.com`         | `0 0 0 .`（禁用）                                              |
| SRV   | `_pop3s._tcp.yourdomain.com`        | `0 0 0 .`（禁用）                                              |

如上配置项仅作示例，具体得查看你自己的日志文件。

### 关于 DNSSEC

日志中可能还有如下提示：

```log
WARNING: It looks like the DNS resolvers configured on your system do not verify DNSSEC...

...

NOTE: It looks like the DNS records of your domain (zone) are not DNSSEC-signed.
```

说明DNS解析器未启用`DNSSEC`验证，以及域名未启用`DNSSEC`签名。`DNSSEC`虽然可以增强安全性，但对于自建邮件服务器**不是必须的**。不配置`DNSSEC`会导致`DANE`无法使用，不过影响极小，因为主流邮件服务都不支持`DANE`。

我的DNS服务商为腾讯云，其中`DNSSEC`为付费功能，就跳过这一步了。如果你的DNS服务商免费提供`DNSSEC`服务，可以尝试了解并配置。

## 修改IP配置

`mox quickstart` 通过 DNS 查询域名 `mail.yourdomain.com` 来获取 IP 地址，然后将其写入配置。但在云服务器环境中，公网 IP 不在本地接口上，导致 Mox 无法绑定。我们需要修改`mox.conf`，直接监听所有IP：

```yml
Listeners:
	public:

		# Use 0.0.0.0 to listen on all IPv4 and/or :: to listen on all IPv6 addresses, but
		# it is better to explicitly specify the IPs you want to use for email, as mox
		# will make sure outgoing connections will only be made from one of those IPs. If
		# both outgoing IPv4 and IPv6 connectivity is possible, and only one family has
		# explicitly configured addresses, both address families are still used for
		# outgoing connections. Use the "direct" transport to limit address families for
		# outgoing connections.
		IPs:
      - 0.0.0.0
      - ::
```

## 证书配置

我是使用1Panel管理证书，输出到`/cert`目录：

```bash
$ ls /cert/
fullchain.pem  privkey.pem
```

所以在`docker-compose.yml`挂载的`/cert`目录，这个根据你自己的情况调整。

```yml
services:
  mox:
    volumes:
      - ./config:/mox/config:z
      - ./data:/mox/data:z
      - ./web:/mox/web:z
      # 挂载 1Panel 的证书目录
      - /cert:/mox/certs:ro
```

在`config/mox.conf`中配置证书。

需要注意mox使用的`sconf`严格要求使用制表符`\t`（tab）排版，不能使用空格。

```yml
# Listeners are groups of IP addresses and services enabled on those IP addresses,
# such as SMTP/IMAP or internal endpoints for administration or Prometheus
# metrics. All listeners with SMTP/IMAP services enabled will serve all configured
# domains. If the listener is named 'public', it will get a few helpful additional
# configuration checks, for acme automatic tls certificates and monitoring of ips
# in dnsbls if those are configured.
Listeners:
	public:
		TLS:
			# Keys and certificates to use for this listener. The files are opened by the
			# privileged root process and passed to the unprivileged mox process, so no
			# special permissions are required on the files. If the private key will not be
			# replaced when refreshing certificates, also consider adding the private key to
			# HostPrivateKeyFiles and configuring DANE TLSA DNS records. (optional)
			KeyCerts:
				-

					# Certificate including intermediate CA certificates, in PEM format.
					CertFile: /mox/certs/fullchain.pem

					# Private key for certificate, in PEM format. PKCS8 is recommended, but PKCS1 and
					# EC private keys are recognized as well.
					KeyFile: /mox/certs/privkey.pem
```

由于我的是泛域名证书，只用配置一个就行。如果是单域名证书需要为`mail.yourdomain.com`，`mta-sts.yourdomain.com`和`autoconfig.yourdomain.com`都配置证书。

### 证书重载

我是使用1Panel管理证书，证书文件保存在宿主机的`/cert`目录下。虽然自动续签后会推送到本地目录进行更新，但Mox不支持自动重载证书，需要重启进程才能加载新证书。一种解决方式是添加crontab定时任务，比较简单就不赘述了。另一种比较优雅的方式是使用1Panel的钩子脚本，在**证书 - 编辑**中勾选**申请证书后执行脚本**，cd到你的docker目录并执行重启命令：

```bash
cd your-mox-docker-workspace && sudo docker compose restart mox
```

## 反向代理配置

观察`mox.conf`可以发现，启用`-existing-webserver`后mox将大部分服务都放在了`1080`端口，而`AutoconfigHTTPS`和`MTASTSHTTPS`服务在`81`端口。我们配置反向代理时，将`main.yourdomain.com`转发至`1080`端口，`autoconfig.yourdomain.com`和`mta-sts.yourdomain.com`转发至`81`端口。记得配置https证书。

配置完成后，可以通过`https://mail.yourdomain.com/`访问**账号管理**页面，`https://mail.yourdomain.com/webmail/`访问**Webmail**页面。密码在之前的`quickstart.log`中。

我们不能直接通过域名`https://mail.yourdomain.com/admin/`访问**管理后台**页面，因为mox为了安全只允许从本地访问。可以使用`ssh`访问服务器并通过`-L`进行本地端口转发来访问管理后台页面：

```bash
ssh -L 8080:localhost:80 you@yourmachine
```

然后在你的本地机器上访问localhost:80就行。

如果你觉得ssh太麻烦，也可以在1Panel中为`/admin/`路径单独配置反向代理，将后端域名由`$host`改为`localhost`，强制mox认为请求来自本地，就可以通过`https://mail.yourdomain.com/admin/`访问了。

## SMTP中继配置

由于国内各大云服务商基本都封禁25端口的出方向，避免被滥用发垃圾邮件。而申请解封又比较麻烦，所以我选择了SMTP中继的方式，让有资质的第三方服务商为你转发邮件。如果你的服务器的25端口可用，可以直接跳过这一节。

我选择的服务商为[Resend](https://resend.com/)，在Resend配置域名和获取API Key，具体配置方法不在此赘述。然后在`mox.conf`配置Transports：

```yml
# Transport are mechanisms for delivering messages. Transports can be referenced
# from Routes in accounts, domains and the global configuration. There is always
# an implicit/fallback delivery transport doing direct delivery with SMTP from the
# outgoing message queue. Transports are typically only configured when using
# smarthosts, i.e. when delivering through another SMTP server. Zero or one
# transport methods must be set in a transport, never multiple. When using an
# external party to send email for a domain, keep in mind you may have to add
# their IP address to your domain's SPF record, and possibly additional DKIM
# records. (optional)
Transports:
	Resend:
		# Submission SMTP over a TLS connection to submit email to a remote queue.
		# (optional)
		Submissions:
			# Host name to connect to and for verifying its TLS certificate.
			Host: smtp.resend.com

			# If set, authentication credentials for the remote server. (optional)
			Auth:
				Username: resend
				Password: your_api_key
				Mechanisms:
					# Allowed authentication mechanisms. Defaults to SCRAM-SHA-256-PLUS,
					# SCRAM-SHA-256, SCRAM-SHA-1-PLUS, SCRAM-SHA-1, CRAM-MD5. Not included by default:
					# PLAIN. Specify the strongest mechanism known to be implemented by the server to
					# prevent mechanism downgrade attacks. (optional)

					- PLAIN
```

需要注意的是，mox的默认认证机制是`SCRAM-SHA-256-PLUS`等，但Resend只支持简单的 `PLAIN`/`LOGIN`，所以需要修改`Mechanisms`。由于mox通过`465`端口（SMTPS）连接 Resend，整个连接从一开始就是TLS加密的，所以`PLAIN`认证也是安全的。

`mox.conf`中的Transports配置完成后，再在`domain.conf`中配置Routes。使用刚刚定义的Resend作为Transport:

```yml
# Domains for which email is accepted. For internationalized domains, use their
# IDNA names in UTF-8.
Domains:
	yourdomain.com:

		# Routes for delivering outgoing messages through the queue. Each delivery attempt
		# evaluates account routes, these domain routes and finally global routes. The
		# transport of the first matching route is used in the delivery attempt. If no
		# routes match, which is the default with no configured routes, messages are
		# delivered directly from the queue. (optional)
		Routes:
			-

				# Matches if the envelope from domain matches one of the configured domains, or if
				# the list is empty. If a domain starts with a dot, prefixes of the domain also
				# match. (optional)
				# FromDomain: #
				#  - #

				# Like FromDomain, but matching against the envelope to domain. (optional)
				# ToDomain: #
				#  - #

				# Matches if at least this many deliveries have already been attempted. This can
				# be used to attempt sending through a smarthost when direct delivery has failed
				# for several times. (optional)
				# MinimumAttempts: 0 #
        # use resend transport configured in mox.conf
				Transport: Resend
```

配置完成后，重启mox尝试发信。

## 总结

至此，一个轻量、现代且完全自主掌控的邮件服务器就部署完成了。现在，你拥有了一个资源占用极低（约 30M 内存）、自带 Webmail 的全功能邮箱系统。既可用于日常通信，也可作为深入理解电子邮件协议的实践练习。自建邮件服务的路途虽然略显曲折，但当发出第一封签着自己域名的邮件时，那份掌控感和成就感是无可替代的。
