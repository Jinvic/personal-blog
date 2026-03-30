---
title: Multirepo微服务项目迁移记录
date: '2026-03-30T10:44:01+08:00'
tags: 
categories:
- 开发
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Multirepo微服务项目迁移记录

工作需求需要对一个200+仓库的multirepo微服务项目迁移到另一个git仓库和k8s集群，迁移时也总结了一些简单的经验踩坑及工作流，在这里记录一下。

## git仓库迁移

相比于pull到本地再push到新git仓库，一个更简便的方法是直接在gitlab实例中导入。我的迁移路径是[GitLab 社区版 v17.7.7](https://gitlab.com/gitlab-org/gitlab-foss/-/tags/v17.7.7)到[GitLab 企业版 v15.2.2-ee](https://gitlab.com/gitlab-org/gitlab/-/tags/v15.2.2-ee)。其实源实例类型和版本倒无所谓，主要是目标实例是否支持相关功能。我使用的`v15.2.2-ee`可以按照`New project > Import project > Repository by URL`直接从git链接导入。同时，从私有实例导出时一般需要配置用户名和密码（访问令牌）。我使用的`v17.7.7`可以在`用户设置 > 访问令牌`中配置。

## 梳理依赖关系

比起毫无头绪地蒙头就干，我更建议先梳理一下依赖关系，优先迁移不依赖其他服务的仓库。具体操作就是先找一个最复杂使用最频繁的仓库（我这是题库客户端接口的api仓库），然后梳理其调用的其他服务（一般写在配置文件中）和直接依赖（在go.mod）中。然后再梳理依赖的依赖关系。这样自顶向下注意出一个依赖图。

需要注意存在循环依赖的可能。其中服务调用的循环依赖不用过于关心，一般在迁移时没有流量流入，不会调用其他服务。如果有初始化/定时任务之类调用了暂未迁移的服务接口，可以暂时让这个服务保持挂掉的状态，等那个服务也迁移了再重启。

而直接依赖的循环依赖比较麻烦。常见情况是A有一个旧版，B依赖了A的旧版本，A的新版本又依赖B导致循环依赖。由于我迁移的这些项目都使用了`go vendor`管理依赖，一个取巧的办法是直接从vendor中将依赖移到项目根目录下，即`vendor/gitlab.old.com/otherrepo`->`pkg/otherrepo`,再全局替换一下包路径，这样就实现了依赖的解耦。反正go.mod里version也是定死的，这个项目作为一个仅维护的老项目也很少会再更新代码，不用费力维护依赖关系。

## 逐个迁移服务

终于到正片了。这里我将分不同commit介绍。实践中我基本也是这么操作的。

### build: 更新依赖

如下几个步骤我一般合并在一个commit中完成，主要目的就是让项目指向新git仓库并能够正常跑起来。

#### 替换git仓库链接

例如原gitlab实例为`gitlab.old.com`，仓库名为`gitlab.old.com/project/reponame`。新gitlab实例为`gitlab.new.com/proj/reponame`。因为项目名一般不会变更，直接全局替换`gitlab.old.com/project`为`gitlab.new.com/proj`就行。

#### 私有模块配置

虽然大部分私有仓库的依赖我都会通过如上的方法，将其从vendor目录移到项目根目录实现依赖解耦。但一些比较简单的依赖关系和基础库我并不会这么处理，所以go.mod中还是会有私有gitlab实例的库。所以需要配置`GOPRIVATE`和`GONOSUMDB`，这样`go mod`才能正常下载和校验私有库。

#### 其他依赖问题

除了私有仓库，可能还有一些其他问题，例如部分依赖仓库已经删除/删标签导致拉取不到等等。大部分都可以通过从vendor移出解决，也可以自行检索相关信息寻找其他解决方法。例如我有一些仓库依赖`github.com/qiniu/api.v7`这个库，而新版本的go不支持这个格式，检查其github仓库就提供了解决方法，全局替换为`github.com/qiniu/go-sdk/v7`即可。

#### 更新vendor目录

最后`go mod tidy`和`go vendor`更新依赖，确认没问题就行。

### conf: 修改配置文件

新集群的服务域名/访问路径/数据库配置可能都有变更，需要再检查一遍配置文件进行确认。确认完成后本地运行一下试试能不能跑起来。此外，别忘了备份一份旧配置文件。

### ci: 迁移ci配置

> **注意**：以下内容高度客制化仅作记录。ci流程这种东西各个项目都不一样。

新旧集群很可能有着不同的部署工作流。与其在旧ci上大刀阔斧地改造，我更喜欢套用新的工作流再修改适配。

我迁移的这个项目，旧集群ci只有个gitlab-ci，而新集群则是将配置文件和k8s配置都放在仓库中，任何修改都可以在仓库中进行再通过gitlab-ci将修改应用到k8s。

#### .gitlab-ci.yml

主要是服务名和端口的配置。此外，不同项目使用的配置文件名也可能不同，有的是`app.conf`有的是`config.yml`，需要检查以下是否正确。

#### dockerfile

主要是更换拉取的docker镜像地址。两个镜像仓库有的镜像都不同，有的镜像就换私有，没有的就换公有。例如我迁移时旧集群用的私有alpine镜像预装了时区数据，换成公共镜像后要加一句`RUN apk add --no-cache tzdata`之类。

#### k8s.yml

k8s配置比较复杂，但大部分都是通用的，主要注意几点：

1. **启动命令**。有些的直接运行，有些要加参数。

    ```yml
        containers:
        - name: ---APP_NAME---
          command:
            - /app/---APP_NAME---
    ```

2. **Ingress配置**。有些服务的子路径和服务名不一致，需要进行校对，不一致的手动修改。

    ```yml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
    namespace: ---NAMESPACE---
    name: ---APP_NAME---ingress
    annotations:
        nginx.ingress.kubernetes.io/use-regex: "true"
        nginx.ingress.kubernetes.io/rewrite-target: /$1
    spec:
    tls:
        - hosts:
            - api.example.com
        secretName: ssl
    rules:
        - host: api.example.com
        http:
            paths:
            - backend:
                service:
                    name: ---APP_NAME---
                    port:
                    number: ---PORT---
                path: /---APP_NAME---/(.*)
                pathType: ImplementationSpecific
    ```

3. **定时任务**。包括任务名，cron表达式，启动命令，挂载数据卷之类。

    ```yml
    apiVersion: batch/v1
    kind: CronJob
    metadata:
    namespace: ---NAMESPACE---
    name: cron-job-name
    labels:
        app: ---APP_NAME---
    spec:
    schedule: "*/5 * * * *"
    concurrencyPolicy: Forbid
    successfulJobsHistoryLimit: 3
    failedJobsHistoryLimit: 1
    jobTemplate:
        spec:
        ttlSecondsAfterFinished: 86400
        activeDeadlineSeconds: 600
        backoffLimit: 6
        template:
            spec:
            containers:
                - name: cron-job-name
                image: "---IMAGE---"
                imagePullPolicy: Always
                command: ["/app/jobset"]
                args: ["arg1", "arg2"]
                env:
                    - name: aliyun_logs_---APP_NAME----log
                    value: stdout
                resources:
                    requests:
                    cpu: 50m
                    memory: 64Mi
                    limits:
                    cpu: 100m
                    memory: 128Mi
                terminationMessagePath: /dev/termination-log
                terminationMessagePolicy: File
                volumeMounts:
                    - mountPath: /etc/localtime
                    name: volume-localtime
                    - mountPath: /app/conf
                    name: config
                    readOnly: true
            restartPolicy: Never
            volumes:
                - name: volume-localtime
                hostPath:
                    path: /etc/localtime
                    type: File
                - name: config
                configMap:
                    name: ---CONFIG_MAP_NAME---
                    defaultMode: 420
    ```

### feat: 添加健康检查

在`/health`路由添加一个简单的健康检查接口，并在k8s配置中设置探针：

```yml
    startupProbe:
        httpGet:
            path: /health
            port: ---PORT---
        failureThreshold: 60
        periodSeconds: 2
    livenessProbe:
        httpGet:
            path: /health
            port: ---PORT---
        failureThreshold: 3
        periodSeconds: 10
    readinessProbe:
        httpGet:
            path: /health
            port: ---PORT---
        initialDelaySeconds: 1
        periodSeconds: 5
```

## 检查服务是否可用

因为配置了探针，只需要直接查看服务状态就行。如果有问题检查日志或者pod事件找原因。

## 总结

这次迁移需要动代码的部分比较少，大部分时间都是在配ci调ci，十分枯燥。只有在部署后有问题时才需要去看代码解决问题。感觉完全可以整理成一个skill交给ai做，但虽然上面讲的轻松，实际迁移问题还是有很多细节问题各个项目都不一样，没办法整理出来就都略过了。ai弄出了问题还得自己处理，最后还是自己慢慢做磨时间。
