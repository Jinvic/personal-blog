---
title: Grpc实践练习
date: '2026-03-31T10:34:13+08:00'
tags: 
categories: 
draft: true
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Grpc实践练习

参考：

- [grpc-go](https://grpc.org.cn/docs/languages/go/)
- [protobuf](https://protobuf.dev/overview/)
- [buf](https://buf.build/docs/cli/)

grpc相关的内容都十分繁琐，虽然看还是能看懂但自己写就抓瞎了。所以做一个项目边练边学尝试融会贯通所学内容。

## 项目结构

项目结构没有什么最佳实践之类，按自己喜欢的来就行。主要protobuf有一套自己的包机制，和go混在一起容易混淆。搞清楚`package`和`option go_package`等配置就怎么写都行。

```bash
./
├── Readme.md
├── api/
│   ├── book/
│   │   └── v1/
│   │       └── book.proto
│   └── common/
│       └── v1/
│           └── types.proto
├── buf.gen.yaml
├── buf.yaml
├── go.mod
└── go.sum
```

## buf

[Buf CLI](https://buf.build/docs/cli/)是一个protobuf构建工具，可以帮助简化配置。安装可查看[教程](https://buf.build/docs/cli/installation/)，在此不再赘述。

### buf.yaml

运行`buf config init`将初始化一个`buf.yaml`文件，内容如下：

```yml
# For details on buf.yaml configuration, visit https://buf.build/docs/configuration/v2/buf-yaml
version: v2
lint:
  use:
    - STANDARD
breaking:
  use:
    - FILE
```

此时需要手动添加`modules`来指定需要处理的proto文件，例如：

```yml
version: v2
modules:
  - path: api
```

另两个选项分别为`lint`和`breaking`分别用于设置**静态代码分析策略**和**破坏性更改检测规则**，保持默认就行。详细配置可以参考[文档](https://buf.build/docs/configuration/v2/buf-yaml).可以分别使用`buf lint`命令和`buf breaking`命令来进行代码检查和破坏性变更检测。

配置完成后可以使用`buf build`检查是否有问题。

### buf.gen.yaml

如果不使用`buf cli`，可以直接在proto文件中配置`option go_package`，然后运行如下命令来生成stub文件:

```bash
protoc \
  --proto_path=./api \
  --go_out=./api \
  --go_opt=paths=source_relative \
  --go-grpc_out=./api \
  --go-grpc_opt=paths=source_relative \
  api/book/v1/book.proto \
  api/common/v1/types.proto
```

这套方法肉眼可见的复杂。而`buf.gen.yaml`就是将配置项写到文件中从而简化配置。

`buf.gen.yaml`没有默认内容，我直接给出一个示例进行讲解。更多配置可以查看[文档](https://buf.build/docs/configuration/v2/buf-gen-yaml)。

```yml
version: v2
managed:
  enabled: true
  override:
    - file_option: go_package
      path: book/v1
      value: bookstore/api/book/v1;bookv1
    - file_option: go_package
      path: common/v1
      value: bookstore/api/common/v1;commonv1
plugins:
  - remote: buf.build/protocolbuffers/go
    out: api
    opt:
      - paths=source_relative
  - remote: buf.build/grpc/go
    out: api
    opt:
      - paths=source_relative
inputs:
  - directory: api

```

- `managed`：托管模式。可以将文件和字段`option`统一定义在`buf.gen.yaml`中而不是在每个proto文件中都写一遍。例如我的配置就等价于`option go_package = "bookstore/api/book/v1;bookv1";`。更多配置项参见[文档](https://buf.build/docs/generate/managed-mode)。
  如果需要覆写多个文件的option使用`managed mode`会很方便，但为单个文件专门反而增加了复杂度。此外，虽然启用`managed mode`后原proto文件中可以不写相关option，但还是建议也写上保持对原生protoc的兼容等。
- `plugins`：使用插件。这里的`remote`指的是托管在`BSR`([Buf Schema Registry](https://buf.build/plugins))上的远程插件。也可以使用protoc的内置插件和本地插件。例如使用本地插件的示例如下：

  ```yml
    - local: protoc-gen-go
      out: api/bookstore/v1
      opt:
        - paths=source_relative
    - local: protoc-gen-go-grpc
      out: api/bookstore/v1
      opt:
        - paths=source_relative
  ```

  如上配置等价于`protoc --go_out=api/bookstore/v1 --go_opt=paths=source_relative --go-grpc_out=api/bookstore/v1 --go-grpc_opt=paths=source_relative`，可以看出就相当于把冗长的命令参数写到配置文件中来简化配置。
- `inputs`：输入列表，这个很好理解。这个配置是可选的，默认行为就是查找所有proto文件。具体可用参数参见[文档](https://buf.build/docs/configuration/v2/buf-gen-yaml/#inputs)。

配置完成后可以使用`buf generate`生成go的stub代码。
