---
title: Gin的FileFromFS无限重定向问题
date: '2025-08-19T14:49:43+08:00'
tags: 
- go
categories: 
- 问题
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Gin的FileFromFS无限重定向问题

## 问题

在用Gin+React构建SPA应用时，想把React的构建产物直接通过`//go:embed`嵌入到go应用。结果出现了无限重定向的问题：

```bash
[GIN-debug] GET    /                         --> main.d (3 handlers)
[GIN-debug] [WARNING] You trusted all proxies, this is NOT safe. We recommend you to set a value.
Please check https://pkg.go.dev/github.com/gin-gonic/gin#readme-don-t-trust-all-proxies for details.
[GIN-debug] Listening and serving HTTP on :8080
[GIN] 2025/08/19 - 16:44:29 | 301 |            0s |             ::1 | GET      "/"
[GIN] 2025/08/19 - 16:44:31 | 301 |            0s |             ::1 | GET      "/"
[GIN] 2025/08/19 - 16:44:31 | 301 |            0s |             ::1 | GET      "/"
[GIN] 2025/08/19 - 16:44:31 | 301 |            0s |             ::1 | GET      "/"
[GIN] 2025/08/19 - 16:44:31 | 301 |            0s |             ::1 | GET      "/"
```

这个问题直接卡了我两天，以为是自己哪写错了，把各个AI问了个遍都改不对，怎么都没想到是gin框架的问题。要是一开始就去翻下issue就好了，有点过度依赖AI和信任流行库了。

## 解析

在使用`gin.context.FileFromFS`是，会将URL路径替换为文件路径。而标准库的`serveFile`在处理路径时如果有`/index.html`后缀会重定向会`/`路由。如果是从`/`路由获取`index.html`，就会导致无限循环重定向。

如下是一个复现问题的最小示例：

```go
package main

import (
    "embed"
    "io/fs"
    "net/http"

    "github.com/gin-gonic/gin"
)

func main() {
    run()
}

func run() {
    r := gin.Default()
    r.GET("/", d)
    r.Run(":8080")
}

//go:embed all:web
var embedFS embed.FS

// transfer embed.FS to http.FileSystem
func getHttpFS(targetPath string) http.FileSystem {
    fsys, err := fs.Sub(embedFS, targetPath)
    if err != nil {
        return nil
    }
    return http.FS(fsys)
}

func d(c *gin.Context) {
    c.FileFromFS("index.html", getHttpFS("web"))
}

```

阅读源码进行调试，可以看到urlpath的变化：

1. **/ -> index.html**

    ```go
    // github.com/gin-gonic/gin@v1.10.1
    // context.go
    // #L1078-L087

    // FileFromFS writes the specified file from http.FileSystem into the body stream in an efficient way.
    func (c *Context) FileFromFS(filepath string, fs http.FileSystem) {
        defer func(old string) {
            c.Request.URL.Path = old
        }(c.Request.URL.Path)

        c.Request.URL.Path = filepath // "/" -> "index.html"

        http.FileServer(fs).ServeHTTP(c.Writer, c.Request)
    }
    ```

2. **index.html -> /index.html**

    ```go
    // go1.23.0
    // http
    // fs.go
    // #L980-L987

    func (f *fileHandler) ServeHTTP(w ResponseWriter, r *Request) {
        upath := r.URL.Path
        if !strings.HasPrefix(upath, "/") {
            upath = "/" + upath
            r.URL.Path = upath // "index.html" -> "/index.html"
        }
        serveFile(w, r, f.root, path.Clean(upath), true)
    }

    ```

3. **/index.html -> /**

```go
// go1.23.0
// http
// fs.go
// #L673-L683

// name is '/'-separated, not filepath.Separator.
func serveFile(w ResponseWriter, r *Request, fs FileSystem, name string, redirect bool) {
    const indexPage = "/index.html"

    // redirect .../index.html to .../
    // can't use Redirect() because that would make the path absolute,
    // which would be a problem running under StripPrefix
    if strings.HasSuffix(r.URL.Path, indexPage) {
        localRedirect(w, r, "./") // "/index.html" -> "/"
        return
    }
```

## 解决方法

可以写一个专门的方法获取`index.html`，直接实现`serveFile`的逻辑，绕过`FileFromFS`。

```go

func d(c *gin.Context) {
    // c.FileFromFS("index.html", getHttpFS("web"))
    indexFromFS(c, "index.html", getHttpFS("web"))
}

func indexFromFS(c *gin.Context, path string, fs http.FileSystem) {
    file, err := fs.Open(path)
    if err != nil {
        log.Printf("file not found: %s, error: %v", path, err)
        c.AbortWithStatus(404)
        return
    }
    defer file.Close()

    stat, err := file.Stat()
    if err != nil {
        log.Printf("file stat error: %s, error: %v", path, err)
        c.AbortWithStatus(404)
        return
    }

    c.Header("Content-Type", "text/html")

    http.ServeContent(c.Writer, c.Request, path, stat.ModTime(), file)
}
```

gin的issues有更多相关讨论：[#3696](https://github.com/gin-gonic/gin/issues/3696) [#2654](https://github.com/gin-gonic/gin/issues/2654)
