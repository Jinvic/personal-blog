---
title: BMP图片格式和读取【C++/Python】
date: '2023-05-23T00:09:37+08:00'
tags:
- C/C++
- Python
categories:
- 开发
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

<!-- more -->
<!-- # 前言
人工智能课程的最后一个实验，感觉还是有点难度。加上我基本没有相关知识的储备，就顺手写个博客当学习笔记了。

首先，神经网络的部分不谈，人脸识别这块首先你要会处理图片吧。上学期倒是开过一门数字图像处理，但很可惜我没选所以这块我是完全不会的，就从这部分开始学吧。

使用数据集为YALE数据集。该是由耶鲁大学计算视觉与扼制中心创立,包括15位志愿者，每个人有11张不同姿势、光照和表情的图片，共计165张图片,图片均为80*100像素的BMP格式图像。我们将整个数据库分为两个部分，每个人的前5幅图片作为网络的训练使用，后6副图片作为测试使用。

# 图像读入和处理
因为数据集全为BMP格式的图片，所以只需要了解如何处理BMP格式的图片就行了。在使用现成库和自己手撸轮子之间我选择了后者，因为应用域很窄，就这次做实验用一下，专门搞个opencv这种太麻烦。但前期准备时发现了一个轻量级的图像处理库[stb_image](https://github.com/nothings/stb/tree/master)，暂且码住备用。 -->
# 前言

这篇文章的标题本来是《人工智能实验-基于三层BP神经网络的人脸识别》这样看起来就高大上的标题的，结果做了一半，室友告诉我这个实验允许用python，而且C++求梯度时有求导什么的不好写balabala。。。（其实只是公式推导，最后推出来的要用的公式并不复杂）加上期末考试将近确实确实缺时间，只好转python化身调包侠交差。至于做了一半的C程序和文章，还是有点舍不得，只好从里面拆一块勉强成形的部分出来，变成了现在这个小肚鸡肠的标题，残念。

~~如果你按下F12，还能从注释里找到点原文章的残骸~~

我刚开始做的时候用的C++，然后理所当然去拿rgb值了。之后做python看到用PIL包一句话的事，羡慕嫉妒恨。C++其实也有很多第三方库，但安装啊文档啊用法啊这些都是问题，有什么疑惑也没地问。社区环境不如java和python这些，大佬不屑于用萌新用不明白，于是大家都自己造轮子，轮子越造越多却没几个能传播到大家都用的地步。闲话到此为止，先讲讲如何用C++读取图片rgb值，python放最后面。

# BMP图像文件格式

了解BMP的格式我主要参考了这篇文章[BMP图片的文件结构](https://blog.csdn.net/weixin_43673589/article/details/104849486)。这篇介绍得相对独立，不需要什么前置知识。此外，为了更完善的代码支持，我引入了`wingdi.h`这个头文件。这是 Windows 平台上的一个头文件，其中定义了一些图形设备接口（GDI）相关的结构体、常量和函数。同时定义好了一些可用于处理BMP的结构体和函数，这样就不用自己写一遍了。但我发现使用这个头文件里的定义时我的IDE的自动补全和错误检查之类都变得很慢，不知道是不是引入这个头文件引起的，之后可能把相关代码修改一下单独拿出来。

言归正传，`wingdi.h`头文件是有着官方文档可用的。仅用于处理BMP格式的话，看这几个就够了：

* [wingdi.h 标头](https://learn.microsoft.com/zh-cn/windows/win32/api/wingdi/#structures)：相当于目录，主要在#structures下找定义好的结构体。
* [BITMAP 结构 (wingdi.h)](https://learn.microsoft.com/zh-cn/windows/win32/api/wingdi/ns-wingdi-bitmap)：BMP结构体，如果觉得他定义的这个不好用也可以自己写一个。我就有点想换了，void*每次用都要强转。。。
* [BITMAPFILEHEADER structure (wingdi.h)](https://learn.microsoft.com/zh-cn/windows/win32/api/wingdi/ns-wingdi-bitmapfileheader)：文件头结构体，不知道为什么这个页面没中文，不过也没几个字无所谓。
* [BITMAPINFOHEADER 结构 (wingdi.h)](https://learn.microsoft.com/zh-cn/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader)：信息头结构体，重要的信息都在这里。
* [RGBQUAD 结构 (wingdi.h)](https://learn.microsoft.com/zh-cn/windows/win32/api/wingdi/ns-wingdi-rgbquad)颜色表结构体。

参考资料列完，就来简单讲讲BMP的文件格式吧。大致可分为4个部分：位图文件头（Bitmap File Header）、位图信息头（Bitmap Info Header）、颜色表（Color Map）和位图数据（即图像数据，Data Bits或Data Body）。

文件头和信息头的结构就不具体介绍了，看上面的文档就行。颜色表是一个可选项，不一定有。主要取决于信息头中一个叫`biBitCount`的参数，它指定每个像素的位数 (bpp) ，取值有1、4、8、24、32几种。首先我们要知道，像素的颜色通常有r、g、b三个值确定，每个值的长度都是8位，加起来就是24位。于是，如果biBitCount为24的话，它直接就能存下rgb值了，也就不需要颜色表。至于32位，个人猜测是加了一个alpha值，也就是透明度，之前做滑块验证码时Java的bufferimage就是这样的。不过BMP是不是也这样我也不确定，没查资料。

回到正题，24位是没有颜色表的。那么颜色表是干什么的呢？就是当biBitCount小于24时，每个像素的位数存不下rgb值，这时就需要一个额外的表来保存可选的rgb值，而位图数据存的是这张表的索引。举个例子，假设一张BMP图的biBitCount值为8，那么在文件头和信息头后就是一个大小为2^8=256的颜色表。之后再是位图数据。对于这张图的每个像素，他首先在位图数据中得到一个8位的值，然后以这个值作为索引到颜色表里去找对应的颜色。同理，biBitCount值为1颜色表就只有2种颜色，值为4就是16种颜色。

# BMP图像RGB值读入和处理

写一个读入函数，定义如下

```C++
bool readBMP(const char *filename, BITMAP *bmp)
```

filename我准备外部用std::string类型，方便修改，传入时就用std::string.c_str()；BITMAP是`wingdi.h`中定义的结构体，主要注意成员bmBits，这是指向位图位值位置的指针。

首先用ifstream打开文件后，读掉文件头和信息头：

```C++
    // 二进制读方式打开指定的图像文件
    std::ifstream file(filename, std::ios::binary);
    // 位图文件头结构变量
    BITMAPFILEHEADER file_head;
    file.read((char *)&file_head, sizeof(BITMAPFILEHEADER));
    // 位图信息头结构变量
    BITMAPINFOHEADER info_head;
    file.read((char *)&info_head, sizeof(BITMAPINFOHEADER));
```

根据文件头和信息头的内容，进行标识符校验和部分成员赋值：

```C++
    // 检查文件标识符
    if (file_head.bfType != 0x4d42)
    {
        std::cerr << "Invalid BMP file: " << filename << std::endl;
        return false;
    }
    // 处理固定值
    bmp->bmType = 0;
    bmp->bmPlanes = 1;
    // 获取图像宽度和高度
    bmp->bmWidth = info_head.biWidth;
    bmp->bmHeight = info_head.biHeight;
```

到了处理位图数据的部分，数据集的图片都是8位256色的图，但做神经网络时存三个rgb值对我们没有意义，还需要额外空间去存颜色表。所以我们这里直接转成32位bpp，用`wingdi.h`中的`RGB(r,g,b)`宏把三个值合成一个。其实就是按位拼起来，自己写一个也行。不过有现成的我也懒得写了。
同时为了兼容性，还是要判断一下原图的bpp是否为8的，然后决定是否读掉颜色表以及转32位操作。这里我想删掉的，毕竟要做兼容性其实应该把1,4,32全做一下，暂时就这样吧。

```C++
// 每个像素的位数，转换成32位的颜色值
    bmp->bmBitsPixel = 32;
    // 灰度图像有颜色表，且颜色表表项为256
    RGBQUAD *color_table;
    if (info_head.biBitCount == 8)
    {
        // 申请颜色表所需要的空间，读颜色表进内存
        color_table = new RGBQUAD[256];
        file.read((char *)color_table, sizeof(RGBQUAD) * 256);
    }

    // 计算每个扫描行中的字节数
    bmp->bmWidthBytes = info_head.biWidth * info_head.biBitCount / 8 + 3 / 4 * 4;
    DWORD biSizeImage = bmp->bmWidthBytes * bmp->bmHeight;
    // 申请位图数据所需要的空间
    char *bmBits = new char[biSizeImage];
    // 读取图像数据
    file.read((char *)bmBits, biSizeImage);
    // 将数据存入结构体BITMAP中
    if (info_head.biBitCount == 8)
    {
        bmp->bmBits = new COLORREF[biSizeImage];
        for (int i = 0; i < biSizeImage; i++)
            ((COLORREF *)(bmp->bmBits))[i] = RGB(color_table[bmBits[i]].rgbRed,
                                                 color_table[bmBits[i]].rgbGreen,
                                                 color_table[bmBits[i]].rgbBlue);
        delete[] color_table;
    }
    else
        bmp->bmBits = bmBits;
```

<!-- # BP神经网络
图像处理的部分做完了。现在我们需要处理的数据就从图片变成数组了，回到了我们熟悉的领域，可以专注搞算法了。 -->
# 完整代码

```C++
// 读入BMP图像
bool readBMP(const char *filename, BITMAP *bmp)
{
    // 二进制读方式打开指定的图像文件
    std::ifstream file(filename, std::ios::binary);
    if (!file)
    {
        std::cerr << "Failed to open BMP file: " << filename << std::endl;
        return false;
    }

    // 位图文件头结构变量
    BITMAPFILEHEADER file_head;
    file.read((char *)&file_head, sizeof(BITMAPFILEHEADER));
    // 位图信息头结构变量
    BITMAPINFOHEADER info_head;
    file.read((char *)&info_head, sizeof(BITMAPINFOHEADER));

    // 检查文件标识符
    if (file_head.bfType != 0x4d42)
    {
        std::cerr << "Invalid BMP file: " << filename << std::endl;
        return false;
    }

    // 处理固定值
    bmp->bmType = 0;
    bmp->bmPlanes = 1;
    // 获取图像宽度和高度
    bmp->bmWidth = info_head.biWidth;
    bmp->bmHeight = info_head.biHeight;
    // 每个像素的位数，转换成32位的颜色值
    bmp->bmBitsPixel = 32;
    // 灰度图像有颜色表，且颜色表表项为256
    RGBQUAD *color_table;
    if (info_head.biBitCount == 8)
    {
        // 申请颜色表所需要的空间，读颜色表进内存
        color_table = new RGBQUAD[256];
        file.read((char *)color_table, sizeof(RGBQUAD) * 256);
    }

    // 计算每个扫描行中的字节数
    bmp->bmWidthBytes = (info_head.biWidth * info_head.biBitCount / 8 + 3) / 4 * 4;
    DWORD biSizeImage = bmp->bmWidthBytes * bmp->bmHeight;
    // 申请位图数据所需要的空间
    char *bmBits = new char[biSizeImage];
    // 读取图像数据
    file.read((char *)bmBits, biSizeImage);
    // 将数据存入结构体BITMAP中
    if (info_head.biBitCount == 8)
    {
        bmp->bmBits = new COLORREF[biSizeImage];
        for (int i = 0; i < biSizeImage; i++)
            ((COLORREF *)(bmp->bmBits))[i] = RGB(color_table[bmBits[i]].rgbRed,
                                                 color_table[bmBits[i]].rgbGreen,
                                                 color_table[bmBits[i]].rgbBlue);
        delete[] color_table;
    }
    else
        bmp->bmBits = bmBits;

    if (!file)
    {
        std::cerr << "Error reading BMP file: " << filename << std::endl;
        return false;
    }

    return true;
}
```

顺手放个测试函数：

```C++
void readBMP_test(void)
{
    BITMAP bmp;
    std::string filename = "1.BMP";
    readBMP(filename.c_str(), &bmp);
    std::cout << bmp.bmWidth << " " << bmp.bmHeight << '\n';
    // std::cout << ((COLORREF *)(bmp.bmBits))[0] << " " << ((COLORREF *)(bmp.bmBits))[bmp.bmWidth * bmp.bmHeight - 1] << '\n';
    for (int i = 0; i < bmp.bmWidth * bmp.bmHeight; i++)
    {
        std::cout << ((COLORREF *)(bmp.bmBits))[i] << '\n';
    }
}
```

# Python

python也可以像上文那样一个个读字节把头文件什么的全读掉，但我没有深入了解和尝试实现。
放个博客在这：[BMP文件分析及用python读取](https://blog.csdn.net/qq_43409114/article/details/104538619)
另一种方法就是使用Python中的Pillow（PIL）库。Pillow库是Python Imaging Library（PIL）的分支，它支持多种图像文件格式。
示例代码如下：

```Python
from PIL import Image

# 打开 BMP 图像文件
with Image.open('image.bmp') as img:
    # 获取图像的 RGB 像素数据
    rgb_img = img.convert('RGB')
    width, height = rgb_img.size
    
    # 遍历图像的每一个像素点，并获取其 RGB 值
    for y in range(height):
        for x in range(width):
            r, g, b = rgb_img.getpixel((x, y))
            print(f"Pixel({x}, {y}) - R: {r}, G: {g}, B: {b}")
```

顺便一提，也可以不把rgb值拿出来直接用`np.array()`转为数组用来训练。因为我的数据集是8位灰度图像，还需要用`image.convert(L)`将图像转换为灰度模式。最后用`flatten()`方法降维一维。
关于`image.convert()`函数，可以看[这篇博客](https://blog.csdn.net/wzk4869/article/details/126082728)。
示例代码如下：

```Python
from PIL import Image
import numpy as np

# 读入BMP图像并转换为灰度模式
img = Image.open('image.bmp').convert('L')

# 转换为NumPy数组
img_data = np.array(img)

# 将图像数据展平并添加到列表中
X.append(img_data.flatten())
```
