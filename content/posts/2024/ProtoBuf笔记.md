---
title: ProtoBuf笔记
date: '2024-11-04T13:31:35+08:00'
tags:
- Go
- Protobuf
categories:
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# ProtoBuf笔记

[官方文档](https://protobuf.dev/)
[中文文档](https://protobuf.com.cn/)

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

## 语法简记

说是不要抄文档，但语法部分还是当备忘录抄一下。毕竟平时用的不多老忘。抄一下主要的部分。

### 字段基数

- `optional`: 显示指定字段是否可选。如果没有这个标记，将无法区分字段**未设置**还是**设置了零值**。对于Go语言，使用了`optional`后字段类型将**变成指针**，同时提供`HasXxx()`方法判断是否设置，`GetXxx()`方法安全获取值（未设置返回零值）。
- `repeated`: 此字段可以重复零次或多次，重复值的顺序将被保留。**相当于数组/列表。**
- `map`: 键值对字段类型。相当于repeated字段的一种语法糖。即如下两种写法是基本是等价的，区别是map序列化后顺序不会保留。

    ```protobuf
    // map
    message Test1 {
        map<string, int32> g = 7;
    }

    // repeated
    message Test2 {
        message g_Entry {
            string key = 1;
            int32 value = 2;
        }
        repeated g_Entry g = 7;
    }
    ```

### 注释格式

- 优先使用 C/C++/Java 风格的行尾注释 `//`，放在 .proto 代码元素的前一行。
- 也接受 C 风格的内联/多行注释 `/* ... */`。
  - 使用多行注释时，推荐使用 `*` 作为边距行。

```protobuf
/**
 * SearchRequest represents a search query, with pagination options to
 * indicate which results to include in the response.
 */
message SearchRequest {
  string query = 1;

  // Which page number do we want?
  int32 page_number = 2;

  // Number of results to return per page.
  int32 results_per_page = 3;
}
```

### 删除字段

删除字段后建议**保留字段编号和字段名**。重用字段编号可能会导致严重问题，而重用旧字段名通常是安全的，但仍建议保留。示例如下：

```protobuf
message Foo {
  reserved 2, 15, 9 to 11, 40 to max;;
  reserved "foo", "bar";
}
```

### 标量类型

protobuf中提供的标量类型如下：

| Proto 类型 | 说明                                                                              |
| ---------- | --------------------------------------------------------------------------------- |
| double     | 使用 IEEE 754 双精度格式。                                                        |
| float      | 使用 IEEE 754 单精度格式。                                                        |
| int32      | 使用可变长度编码。对于编码负数效率低下——如果你的字段可能包含负值，请改用 sint32。 |
| int64      | 使用可变长度编码。对于编码负数效率低下——如果你的字段可能包含负值，请改用 sint64。 |
| uint32     | 使用可变长度编码。                                                                |
| uint64     | 使用可变长度编码。                                                                |
| sint32     | 使用可变长度编码。有符号整数值。这些比常规的 int32 更高效地编码负数。             |
| sint64     | 使用可变长度编码。有符号整数值。这些比常规的 int64 更高效地编码负数。             |
| fixed32    | 总是四个字节。如果值经常大于 228，比 uint32 更高效。                              |
| fixed64    | 总是八个字节。如果值经常大于 256，比 uint64 更高效。                              |
| sfixed32   | 总是四个字节。                                                                    |
| sfixed64   | 总是八个字节。                                                                    |
| bool       |                                                                                   |
| string     | 字符串必须始终包含 UTF-8 编码或 7 位 ASCII 文本，且长度不能超过 232。             |
| bytes      | 可包含任意字节序列，长度不超过 232。                                              |

### 字段默认值

- 对于字符串，默认值是空字符串。
- 对于字节，默认值是空字节。
- 对于布尔值，默认值是 false。
- 对于数值类型，默认值是零。
- 对于消息字段，该字段未设置。其确切值取决于语言。详情请参阅[生成的代码指南](https://protobuf.com.cn/reference/)。
- 对于枚举，默认值是第一个定义的枚举值，它必须为 0。请参阅[枚举默认值](https://protobuf.com.cn/programming-guides/proto3/#enum-default)。
- 对于 repeated 字段，默认值是空的（通常是相应语言中的空列表）。
- 对于 map 字段，默认值是空的（通常是相应语言中的空 map）。

### 枚举相关

可以使用`enum`定义枚举值。示例如下：

```protobuf
enum BookStatus {
  option allow_alias = true;
  BOOK_STATUS_UNSPECIFIED = 0;
  BOOK_STATUS_AVAILABLE = 1;
  BOOK_STATUS_ONSHELF = 1;
  BOOK_STATUS_UNAVAILABLE = 2;
  BOOK_STATUS_OFFSHELF = 2;
}

message Book {
  int64 id = 1;
  string title = 2;
  string author = 3;
  BookStatus status = 4;
}
```

需要注意的是，枚举定义中定义的**第一个值必须为零**，并且应该命名为`ENUM_TYPE_NAME_UNSPECIFIED`或`ENUM_TYPE_NAME_UNKNOWN`。这是因为

- 必须有一个零值，以便我们可以将 0 用作数字默认值。
- 零值需要是第一个元素，以便与 proto2 语义兼容，其中除非明确指定了不同的值，否则第一个枚举值是默认值。

可以将 `allow_alias` 选项设置为 `true`来运行别名。

### Oneof

oneof 中的所有字段共享内存，并且一次最多只能设置一个字段。果设置了多个值，则由 proto 中的顺序决定的最后一个设置的值将覆盖所有先前的值。

```protobuf
message SampleMessage {
  oneof test_oneof {
    string name = 4;
    SubMessage sub_message = 9;
  }
}
```

### 定义服务

如果想将的消息类型与 RPC（远程过程调用）系统一起使用，您可以在 .proto 文件中定义一个 RPC 服务接口，protocol buffer 编译器将以选择的语言生成服务接口代码和存根 (stub)。

```protobuf
service SearchService {
  rpc Search(SearchRequest) returns (SearchResponse);
}
```

## 知名类型

提供了标量类型以外的预定义类型，位于`google.protobuf`包，源码在`protocolbuffers/protobuf`的[src/google/protobuf](https://github.com/protocolbuffers/protobuf/tree/main/src/google/protobuf)目录下。

### 选择指南

| 场景                   | 推荐类型                             |
| ---------------------- | ------------------------------------ |
| 需要精确时间点         | `Timestamp`                          |
| 需要时间间隔           | `Duration`                           |
| 需要表示空响应         | `Empty`                              |
| 需要区分 0/null/未设置 | 包装类型（Int32Value 等）            |
| 需要动态 JSON 数据     | `Struct`                             |
| 需要部分更新           | `FieldMask`                          |
| 需要动态类型           | `Any`                                |
| 需要二进制数据         | `bytes`                              |
| 不需要值区分           | 直接使用基础类型（int32, string 等） |

### Struct/Any/Value比较

| 特性         | **Struct**       | **Any**              | **Value**        |
| ------------ | ---------------- | -------------------- | ---------------- |
| **本质**     | JSON 对象        | 类型擦除的消息       | JSON 值          |
| **数据格式** | Map + 动态类型   | 任意 Protobuf 消息   | 任意 JSON 类型   |
| **类型安全** | 弱（运行时检查） | 强（需显式类型 URL） | 弱（运行时检查） |
| **跨语言**   | JSON 兼容        | Protobuf 消息        | JSON 兼容        |
| **典型用途** | 动态配置、元数据 | 插件系统、多态       | 任意值存储       |

选择的关键在于：是需要存储 JSON 数据（用 Struct/Value），还是需要存储类型安全的 Protobuf 消息（用 Any）。

### XxxValue

这些包装类型主要用于兼容proto2，解决未设置和设置为默认值的问题。proto3中加入了`optional`，就不需要用到包装类型了。

### Duration

Duration 表示一个带符号的固定长度时间跨度，以秒和纳秒分辨率的秒分数表示。它独立于任何日历以及“天”或“月”等概念。它与 Timestamp 相关，因为两个 Timestamp 值之间的差是 Duration，并且可以从 Timestamp 中添加或减去。范围大约为 ±10,000 年。

### Timestamp

Timestamp 表示一个独立于任何时区或日历的时间点，以 UTC 纪元时间中的秒和纳秒分辨率的秒分数表示。Timestamp 类型以 RFC 3339 格式编码为字符串：“{year}-{month}-{day}T{hour}:{min}:{sec}[.{frac_sec}]Z”。

| 字段名  | Type  | 描述                                                                                                                    |
| ------- | ----- | ----------------------------------------------------------------------------------------------------------------------- |
| seconds | int64 | 自 Unix 纪元 1970-01-01T00:00:00Z 以来 UTC 时间的秒数。必须在 0001-01-01T00:00:00Z 到 9999-12-31T23:59:59Z 之间（含）。 |
| nanos   | int32 | 纳秒分辨率的非负小数秒。带有小数的负秒值仍必须具有向前计时的非负纳秒值。必须在 0 到 999,999,999 之间（含）。            |

### FieldMask

FieldMask 表示一组符号字段路径。该字段掩码用于指定应由获取操作返回（一个 *投影*）或由更新操作修改的字段子集。字段掩码也有自定义的 JSON 编码（见下文）。

```txt
// 字段掩码
paths: "f.a"
paths: "f.b.d"

// 应用前
f {
  a : 22
  b {
    d : 1
    x : 2
  }
  y : 13
}
z: 8

// 应用后
f {
  a : 22
  b {
    d : 1
  }
}

```

代码示例：

```protobuf
// protobuf
mask {
  paths: "user.display_name"
  paths: "photo"
}
```

```json
// json
{
  mask: "user.displayName,photo"
}
```

| 字段名 | Type   | 描述             |
| ------ | ------ | ---------------- |
| paths  | string | 字段掩码路径集。 |

### Any

Any 包含一个任意序列化消息以及描述序列化消息类型的 URL。

```protobuf
package google.profile;
message Person {
  string first_name = 1;
  string last_name = 2;
}
```

```json
{
  "@type": "type.googleapis.com/google.profile.Person",
  "firstName": <string>,
  "lastName": <string>
}
```

| 字段名   | Type   | 描述                                              |
| -------- | ------ | ------------------------------------------------- |
| type_url | string | 一个 URL/资源名称，其内容描述了序列化消息的类型。 |
| value    | bytes  | 必须是上述指定类型的有效序列化数据。              |

### Struct

Struct 表示一个结构化数据值，由映射到动态类型值的字段组成。在某些语言中，Struct 可能由原生表示支持。

| 字段名 | Type               | 描述               |
| ------ | ------------------ | ------------------ |
| fields | map<string, Value> | 动态类型值的映射。 |

### Value

Value 表示一个动态类型的值，可以是 null、数字、字符串、布尔值、递归结构体值或值列表。值的生成者应设置其中一种变体，缺少任何变体表示错误。

Value 的 JSON 表示是 JSON 值。

Value为联合字段，以下只有一个：

| 字段名       | Type      | 描述                   |
| ------------ | --------- | ---------------------- |
| null_value   | NullValue | 表示一个空值。         |
| number_value | double    | 表示一个双精度值。     |
| string_value | string    | 表示一个字符串值。     |
| bool_value   | bool      | 表示一个布尔值。       |
| struct_value | Struct    | 表示一个结构化值。     |
| list_value   | ListValue | 表示一个重复的 Value。 |

### ListValue

ListValue 是一个包含重复值字段的包装器。

ListValue 的 JSON 表示是 JSON 数组。

| 字段名 | Type  | 描述                   |
| ------ | ----- | ---------------------- |
| values | Value | 动态类型值的重复字段。 |

### NullValue

NullValue 是一个单例枚举，表示 Value 类型联合的空值。

NullValue 的 JSON 表示是 JSON null。

| 枚举值     | 描述   |
| ---------- | ------ |
| NULL_VALUE | 空值。 |

## 参数校验

对于原生protoc生态，可以使用`protoc-gen-validate`([PGV](https://github.com/bufbuild/protoc-gen-validate))插件。而对于新项目/[buf](https://buf.build/docs/cli/)生态，更推荐使用[protovalidate](https://protovalidate.com/about/)，支持[CEL](https://cel.dev/?hl=zh-cn)表达式，有着更完善强大的验证功能。可以在[CEL by Example](https://celbyexample.com/)快速学习了解cel在protovalidate中的使用。
