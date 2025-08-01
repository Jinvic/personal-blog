---
title: 个人博客Gredia到Hugo迁移记录
date: '2025-06-26T09:27:00+08:00'
tags:
- 杂项
categories:
- 自部署
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 个人博客Gredia到Hugo迁移记录

参考：

- [Hugo中文文档](https://hugo.opendocs.io/getting-started/)
- [主题文档 - 基本概念 - Dolt](https://hugodoit.pages.dev/zh-cn/theme-documentation-basics/)

最开始打算写博客时选择Gredia，是因为可以一键部署到GitHub Pages，觉得很方便，不用自己建站搞服务器等。后来作者没继续做开源版了，搞了个付费订阅的闭源版。我其实并不反对这个商业化，只是看了看新增的功能没啥兴趣，就将就着继续用原来的版本了。

现在有了自己的服务器，也部署了不少东西。看着唯一一个飘零在外的博客，理所当然就想迁移回来自部署了。相比于已经停更的Gredia，也希望换一个更有活力的社区。了解一番后选择了hugo，一是go技术栈感觉比较亲切，二是安装和构建等确实也比较轻量和方便。三是之前用过mkdocs搭建文档站，对这种生成静态网站的工具还是比较熟悉的。

其实迁移本身并不麻烦，但还是水一篇博客。

## 元数据

如下是Gredia和Hugo的元数据对比：

```yaml

# Gredia
---
title: 'go依赖注入库 samber/do 笔记'
date: 2025-06-24 11:05:03
tags: [笔记,Go]
published: true
hideInList: false
feature: 
isTop: false
---

# Hugo
---
title: go依赖注入库 samber/do 笔记
date: '2025-06-24T11:05:03+08:00'
tags:
- Go
categories:
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

```

可以看到，两者的配置还是比较接近的。首先处理一下日期格式，tag格式好像改不改都行。
`published`和`draft`参数对应，`hideInList`在Hugo原生配置中似乎没有对应，和draft是一样的功能。不过我用的[Dolt](https://github.com/HEIGE-PCloud/DoIt)主题有`hiddenFromHomePage`和`hiddenFromSearch`两项正好对应。
`feature`和`isTop`两项没有对应，删除就行。

## 路由

在Gredia和Hugo中，都是直接使用文件名作为路由的。如果你之前的路由没什么问题可以不改。我之前是使用英文标题作路由，打算改成中文标题就改了下，注意路由中不能有空格和`/`等特殊字符，否则会进行截断。写脚本时注意下。

## TOC

TOC(Table of Contents)是我非常喜欢的一个功能。因为我习惯使用大量标题分隔文章内容，有一个侧边栏toc当目录就很方便。原来Gredia用的concise主题，在toc列表过长时不会自动滑动。Dolt主题的toc支持自动折叠，就不会有这个问题。

要启用toc，可以在配置文件中添加如下内容。注意不要使用静态目录，否则目录会在文章开头而不是侧边栏。

```toml
    # DoIt 新增 | 0.2.0 目录配置
    [params.page.toc]
      # 是否使用目录
      enable = true
      # DoIt 新增 | 0.2.9 是否保持使用文章前面的静态目录
      keepStatic = false
      # 是否使侧边目录自动折叠展开
      auto = true
```

## 摘要

Hugo支持自动提取文章前若干个字符作为摘要，或者手动写摘要，在列表页展示。我没有写摘要的习惯，所以直接关掉了这个功能。在配置项中将自动摘要长度设为0就行。

```toml
# 设置文章摘要长度
summaryLength = 0
```

## 图片

Gredia中图片链接的格式为`https://<host>/post-images/<title>/<pic>`，示例：

```markdown
![gridea主题页面](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic1.png)
```

Hugo中引用图片有页面包，assets和static三种方式，我选择了static方式，格式为`/<path>/<pic>`，示例：

```markdown
![gridea主题页面](/post-images/Gridea主题concise如何添加和修改live2d模型/pic1.png)
```

直接将Gredia的`post-images`文件夹放到`static`目录下，修改一下文件夹名，然后在文档中全文搜索替换就行。

## 评论

之前的评论系统是在Vercel上一件部署的Waline，也是因为可以无服务端一键部署很方便。不过后续基本没怎么管过。为了白嫖这个服务，Vercel这边搞下托管，LeanCloud那边搞下存储,想看一眼都要登好几个后端确实麻烦。现在评论系统也自建就方便多了。

之前用到Waline说实话样式不是很喜欢，只是因为兼容Gredia支持的Valine才用的。Github系列的评论系统往往有网络问题，最后在Artalk和Twikoo中选择了前者，前者功能更丰富些。

Dolt主题要启用评论系统，只需在配置文件中添加如下内容：

```toml
# Comment config
# 评论系统设置
[page.comment]
enable = true

# artalk comment config (https://artalk.js.org/guide/frontend/config.html)
# artalk comment 评论系统设置 (https://artalk.js.org/guide/frontend/config.html)
[page.comment.artalk]
enable = true
server = "https://comment.jinvic.top"
site = "Jinvic Blog"
lite = false
katex = false
lightbox = false
pageview = true
commentCount = true
```

server填自建的Artalk地址，site填网站名就行。

artalk部署后，需要在容器内执行命令创建管理员账户，之后就可以登录后台修改配置了。

```bash
docker exec -it artalk artalk admin
```

如果在本地调试时无法使用artalk，在artalk的可信域名中添加`http://localhost:1313`就行。

## 分析

Dolt主题自带很多常见的流量分析配置，在配置项中启用就行。我使用的是自部署的Umami：

```toml
# _default/params.toml

# Analytics config
# 网站分析配置
[analytics]
enable = true
[analytics.umami]
data_website_id = "..."
src = "..."
```
