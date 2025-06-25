---
title: ProtoBuf笔记
date: '2024-11-04T13:31:35+08:00'
tags:
- Go
categories:
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# ProtoBuf笔记

[官方文档](https://protobuf.com.cn/)

尽量少抄文档吧。。。感觉抄文档的笔记没有一点意义，真要查些什么都直接查文档了。

## 概述

### 什么是ProtoBuf？

> **定义**：Protocol Buffers 是一种与语言无关、与平台无关的可扩展机制，用于序列化结构化数据。

看起来有点懵，举个例子。我们随便定义一个结构体，在不同语言中定义方法是不同的：

```c
struct Person
{
    char name[50];
    int age;
};
```

```c++

struct Person {
    std::string name;
    int age;
};
```

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

```go
type Person struct {
    Name string
    Age  int
}
```

而protobuf提供了一种通用的定义方式，它可以通过工具转换成任意一种语言。

```protobuf
message Person {
  string name = 1;
  int32 age = 2;
}
```

### protobuf有什么用？

protobuf本质上是一种序列化技术。什么是序列化？这里不扯定义，简单粗暴地说，就是把数据转换成另一种更方便更通用的形式，方便进行存储和传输。你在程序里有个结构体，你可以把它当参数在这个程序里面传来传去。但如果你要把它存到磁盘，可能就得存一个txt或json，这个过程你就可以理解为序列化。你用另一个程序把这个txt或json读到程序里的结构体，然后就可以自由操作这个结构体了，这个过程就可以理解为反序列化。上面讲的是存储，而传输也是一样的道理。json就是序列化技术之一，而protobuf也是类似的。而相比json的轻量级标记，protobuf则有着更接近编程语言的语法和工具链支持。

protobuf常用于跨语言，跨项目的通信协议和数据存储，如RPC等。具体什么是RPC这里不予赘述。

## protobuf-go开发

protobuf生成go代码时，需要使用 `go_package` 选项指定生成代码的包的导入路径。包名为最后一个路径组件。如下，包名为`tutorialpb`。

```proto
option go_package = "github.com/protocolbuffers/protobuf/examples/go/tutorialpb";
```

使用protobuf生成go代码，需要额外安装插件`protoc-gen-go`，如果是gRPC开发还需安装`protoc-gen-go-grpc`：

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

编译器插件 `protoc-gen-go` 将安装在 `$GOBIN` 中，默认为 `$GOPATH/bin`。 需要将其添加到`$PATH` 中，以便协议编译器 `protoc` 能够找到它。

**Linux添加PATH**：

```bash
export PATH="$PATH:$(go env GOPATH)/bin"
```

编译命令中使用`--go_out`和`--go-grpc_out`指定输出目录。

```bash
protoc --go_out=proto --go-grpc_out=proto .\proto\test.proto
```
