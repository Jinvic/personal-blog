---
title: Go使用pdfcpu操作pdf文件
date: '2025-08-27T14:28:24+08:00'
tags: 
- Go
categories: 
- 知识点
draft: true
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Go使用pdfcpu操作pdf文件

最近有一个新需求是移除pdf的logo和部分文本，也就了解了一下用go操作pdf。[unidoc/unipdf](https://github.com/unidoc/unipdf)这个库好像功能最强大，但是商业化使用需要授权，开源库里也是混淆代码。最后选用的是[pdfcpu/pdfcpu]，能够一定程度上处理pdf，但仍不能实现我对需求，只能借助这个库的现有功能手动写了。

## 删除图片

首先是移除logo，通过`pdfcpu images list -p=1 .\test.pdf`可以看到pdf内的图片信息：

```bash
pdfcpu images list -p=1 .\test.pdf

.\test.pdf:
1 images available (11 KB)
Page │ Obj# │ Id   │ Type  SoftMask ImgMask │ Width │ Height │ ColorSpace Comp bpc Interp │  Size │ Filters
━━━━━┿━━━━━━┿━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━━━━
1 │   13 │ img1 │ image    *             │   735 │    160 │     CalRGB    3   8        │ 11 KB │ FlateDecode
```

不过pdfcpu并没有提供主动删除图片的方式。通过解析处理图片的相关方法可以了解到图片相关信息存在`ctx.XRefTable.Table`中，这是一个`map[int]*model.XRefTableEntry`类型的映射。再结合上面得到的图片信息，从中删除logo图片的对象id就行。

```go
func DeleteObjFromPdf(rs io.ReadSeeker, w io.Writer, objNr int) error {
    if rs == nil {
        return errors.New("pdfcpu: Optimize: missing rs")
    }

    conf := model.NewDefaultConfiguration()

    ctx, err := api.ReadValidateAndOptimize(rs, conf)
    if err != nil {
        return err
    }

    delete(ctx.XRefTable.Table, objNr)

    if err = api.WriteContext(ctx, w); err != nil {
        return err
    }

    return nil
}
```

## 提取内容流

至于删除文本，我原本想的是提取原始内容流，删除相应文本后再写回去：

```go
func RemoveTextFromPage(ctx *model.Context, pageNum int, textToRemove string) error {
    // 提取原始内容流
    r, err := pdfcpu.ExtractPageContent(ctx, pageNum)
    if err != nil || r == nil {
        return err
    }

    data, err := io.ReadAll(r)
    if err != nil {
        return err
    }

    // TODO： 删除特定文本

    // TODO： 写回ctx

    return nil
}
```

## 添加图章

但解析出来的的内容流太复杂，我又不懂pdf语法，只好退而求其次，用一个纯色图章遮住目标文本凑合用:

```go
func hideTextWithStamp(rs io.ReadSeeker, w io.Writer) error {
    text := " "
    descs := []string{
        "fillc:white",
        "bgcolor:white",
        "pos:c",
        "off:0 250",
        "points:36",
        "scale:1 abs",
        "ma:8 250",
        "rot:0.0",
    }
    desc := strings.Join(descs, ",")
    onTop := true
    update := false
    wm, err := api.TextWatermark(text, desc, onTop, update, types.POINTS)
    if err != nil {
        return err
    }
    selectedPages := []string{"1"}
    if err := api.AddWatermarks(rs, w, selectedPages, wm, nil); err != nil {
        return err
    }
    return nil
}
```

就这样，勉强算是解决了这个需求。感觉进阶的话可以了解一下pdf语法，再尝试去手动编辑内容流。
