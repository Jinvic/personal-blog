---
title: Gridea主题concise如何添加和修改live2d模型
date: '2023-06-08T20:27:33+08:00'
tags:
- 杂项
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 前言

软件自带的主题感觉不是很好用，早就想换，但这个开源项目好像已经不再维护，主题页面`https://gridea.dev/themes`已经失效了，就暂且搁置了下来。
![gridea主题页面](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic1.png)
之后想起这回事又找了找，虽然官网的主题页面用不了了，但github上还是能找到不少为gridea做的主题的，挑挑拣拣一番，我相中了这个concise主题，[项目地址](https://github.com/NeedQuiet/Gridea-theme-concise)。
![concise主题预览1](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic2.png)
![concise主题预览2](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic3.png)
之后尝试改live2d，原项目的教程就几句话：
>参考了：[gridea-theme-fog](https://github.com/850552586/gridea-theme-fog)
>
>- 模型下载地址: [下载地址](https://gitee.com/ericam/live2d-widget-models)
>- 模型样式预览: [预览地址](https://blog.csdn.net/wang_123_zy/article/details/87181892)
>- 主题-自定义配置中目前可选2中模型：黑猫和白猫
>修改：可直接覆盖live2d/assets直接修改，
>添加：按照目前结构继续添加（要修改下载下来的目录文件结构，及对应的model.json里相关path）

感觉讲的比较简略，想弄好还是要摸索一番的，我就详细写一下记在这里避免忘记，如果以后自己要再改live2d模型就来看看。

# 模型的预览和下载

这个原readme里面写了地址：

- 模型下载地址: [下载地址](https://gitee.com/ericam/live2d-widget-models)
- 模型样式预览: [预览地址](https://blog.csdn.net/wang_123_zy/article/details/87181892)

我们先到预览里挑一个喜欢的模型，这里以miku为例：
![模型预览](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic4.png)
然后下载模型并解压，找到对应文件夹，进入`asserts`子文件夹，这就是我们的模型了：
![下载](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic5.png)
![模型所在文件夹](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic6.png)

# 将模型添加到gridea

首先我们要找到gridea的源文件路径，这个可以在客户端左下角找到：
![客户端左下角](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic7.png)
![源文件路径](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic8.png)
进到`themes/concise/assets/media/live2d/assets`目录下，我们需要将模型移到这个目录。不过不能简单拖过来，它们的目录结构有点不一样。
![模型路径](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic9.png)
两个json文件和moc子文件夹下的文件可以直接移动：
![json移动](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic10.png)
![moc移动](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic11.png)
在gridea这边的mtn目录下新建文件夹，以模型名字命名，再将下载的mtn文件夹内文件移到新建的文件夹内：
![mtn移动](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic12.png)
至此，我们就成功将模型添加到gridea了。

# 配置文件修改

由于添加模型时更改了目录结构，我们首先修改模型的配置文件。打开`assets`下的`miku.model.json`。这里可能是压缩成一行的代码，可以使用VScode的格式化方便查看，将`motion`项中的`mtn/`路径都修改为`mtn/miku/`就行。
![model.json修改前](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic13.png)
![model.json修改后](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic14.png)
之后我们要修改concise主题的配置文件，将新模型添加到选项中。在`themes/concise`目录下找到`config.json`，搜索“看板娘”，在这个项下按格式添加就行：
![config.json路径](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic15.png)
![添加选项](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic16.png)
重启gridea客户端，查看是否添加成功：
![查看结果1](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic17.png)
进入网页查看，头脚被截断了一部分：
![查看结果2](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic18.png)
在目录`themes/concise/templates/includes`下找到`live2d.ejs`，修改画布大小：
![live2d.ejs路径](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic19.png)

```javascript
<canvas id="live2d" width="240" height="250" class="live2d"></canvas>
```

修改为`width="200" height="300"`，现在能正常显示了：
![查看结果3](https://Jinvic.github.io//post-images/Gridea-theme-concise-how-to-add-and-change-live2d-model/pic20.png)

（完🙃）
