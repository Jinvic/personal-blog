---
title: Go标准库中的errors包
date: '2025-08-07T14:37:36+08:00'
tags: 
- Go
categories: 
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Go标准库中的errors包

> [!Note]
> 本篇内容节选自[《Go语言高级编程》阅读笔记](/go语言高级编程阅读笔记)

参考：

- [Working with Errors in Go 1.13](https://go.dev/blog/go1.13-errors)
- [errors package - errors - Go Packages](https://pkg.go.dev/errors)

go官方在1.13已经加入了基础的包装特性。随着Go官方错误处理的改进，如`pkg/errors`之类的三方包基本不再活跃了。

既然如此，就简单了解一下官方errors包的新特性吧。

## Errors before Go 1.13

在1.13之前，标准库的错误只包括 `errors.New` 和 `fmt.Errorf` 两个方法。生成的错误只包括消息。

要检查错误是否存在以及错误类型，可以将其与nil或哨兵变量比较： `if err != nil {...}` ， `if err == ErrNotFound {...}`。

由于错误值是一个error接口类型，可以使用类型断言将其转换为具体类型：`if e, ok := err.(*NotFoundError); ok {...}`。

要在传递错误时添加信息，可以构造一个新错误，包含原先错误的文本：`fmt.Errorf("decompress %v: %v", name, err)`。

或者定义一个新的错误类型，其中包含底层错误，例如：

```go
type QueryError struct {
    Query string
    Err   error
}

if e, ok := err.(*QueryError); ok && e.Err == ErrPermission {
    // query failed because of a permission problem
}
```

Go 1.13 为 errors 和 fmt 标准库包引入了新特性，以简化处理包含其他错误的情况。

## The Unwrap method

Go 1.13 引入了一项惯例：一个包含其他错误的对象可以实现一个 `Unwrap` 方法返回底层错误。

如果 e1.Unwrap() 返回 e2 ，我们就说 e1 包装了 e2 ，并且你可以通过 e1 来获取 e2 。

例如对于如上`QueryError`结构体，我们可以实现如下`Unwrap` 方法来实现这一惯例：

```go
func (e *QueryError) Unwrap() error { return e.Err }
```

展开一个错误的结果本身可能也有一个 Unwrap 方法；我们称通过重复展开产生的错误序列为错误链。

## Wrapping errors with %w

如前所述，通常使用 fmt.Errorf 函数向错误添加额外信息。在 Go 1.13 中， fmt.Errorf 函数支持一个新的 %w 动词。当这个动词存在时， fmt.Errorf 返回的错误将有一个 Unwrap 方法，该方法返回 %w 的参数， %w 必须是一个错误。在其他所有方面， %w 与 %v 完全相同。

```go
if err != nil {
    // Return an error which unwraps to err.
    return fmt.Errorf("decompress %v: %w", name, err)
}
```

## Examining errors with Is and As

Go 1.13 的 `errors` 包添加了两个新的用于检查错误的功能： `Is` 和 `As` 。

errors.Is 函数比较一个错误和一个值。

```go
// Similar to:
//   if err == ErrNotFound { … }
if errors.Is(err, ErrNotFound) {
    // something wasn't found
}
```

As 函数测试一个错误是否为特定类型。

```go
// Similar to:
//   if e, ok := err.(*QueryError); ok { … }
var e *QueryError
// Note: *QueryError is the type of the error.
if errors.As(err, &e) {
    // err is a *QueryError, and e is set to the error's value
}
```

在简单情况下，两种表现类似于与哨兵函数比较和类型断言。在处理包装错误时，这些函数会考虑链中的所有错误。

`Combine multiple errors with Join`:

如果需要组合多个错误，通过`%w`嵌套包装比较麻烦。在Go 1.20中引入了`Join`方法，可以直接组合多个错误。

```go
import (
    "errors"
    "fmt"
)

func main() {
    err1 := errors.New("err1")
    err2 := errors.New("err2")
    err := errors.Join(err1, err2)
    fmt.Println(err)
    if errors.Is(err, err1) {
        fmt.Println("err is err1")
    }
    if errors.Is(err, err2) {
        fmt.Println("err is err2")
    }
}
```

如上，其返回值可以视为其中的任意一个方法。对于组合的nil错误将被丢弃，如果组合的错误都是nil将返回nil。

`Join`方法的返回值实现了`Unwrap() []error`方法，可以解包出一个错误切片。
