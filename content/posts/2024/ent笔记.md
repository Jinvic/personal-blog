---
title: ent笔记
date: '2024-11-07T14:41:18+08:00'
tags:
- Go
categories:
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# ent笔记

## 概述

>ent 是一个 Go 的实体框架 (ORM)。 ent 可以使用 Go 代码轻松地定义任何数据模型或图结构；schema配置由 entc (ent codegen) 验证，这种配置生成了一个地道的静态类型的 API ，使开发人员能够富有生产性和幸福感。 它支持 MySQL, MariaDB, PostgreSQL, SQLite 和 Gremlin图数据库。

简单来说，ent是Facebook团队开源的一个Go语言ORM框架，类似于Java的Hibernate，Python的SQLAlchemy，Go的GORM等。相比于gorm，ent的特点是专注于使用dsl写schema，关联和约束都写在 Go 代码，而不是结构标签，并用cli工具自动生成和验证代码，以及同样支持从schema构造迁移数据库结构，用户只需要管理好schema就行。缺点是学习成本和上手难度较高，需要理解学习它的schema概念和dls语法，以及面对复杂需求框架生成的代码可能不够灵活有时需要自定义方法。

~~ent[官方文档](https://entgo.io/zh/docs/getting-started)里的中文和没有差不多。这里贴一个民间翻译的[中文文档](https://ent.ryansu.tech/#/zh-cn/getting-started)。~~

> 241107: 才注意到ent主页挂着支持以色列的横幅，在开源项目中宣扬政治主张实在有点恶心了。
> 241114: 中文支持很差，甚至文档进度都不同步，建议看英文文档。为了封装硬生生搞了个语法子集出来，很多功能都无法实现。文档既少又烂，查资料全靠issue。两个字：**快跑**

## 快速入门

ent使用需要go环境，可以安装go后设置go项目:

```bash
go mod <projectname>
```

### 安装ent

```bash
go get entgo.io/ent/cmd/ent
```

使用`ent -h`查看是否安装成功。如果提示找不到可以使用如下命令代替ent命令：

```bash
go run entgo.io/ent/cmd/ent
```

或者使用go install添加到%GOPATH/bin目录：

```bash
go install entgo.io/ent/cmd/ent
```

### 初始化ent目录

```bash
ent new
```

目录如下：

```bash
.
└── ent
    ├── generate.go
    └── schema
```

### 创建实体

```bash
ent new <entityname>
```

可以使用如上命令同时创建多个实体。它们将被创建在schema目录下。假设我们创建了一个User实体（**首字母必须大写**）`ent new User`：

```bash
.
└── ent
    ├── generate.go
    └── schema
        └── user.go
```

代码如下：

```go

package schema

import "entgo.io/ent"

// User holds the schema definition for the User entity.
type User struct {
    ent.Schema
}

// Fields of the User.
func (User) Fields() []ent.Field {
    return nil
}

// Edges of the User.
func (User) Edges() []ent.Edge {
    return nil
}
```

其中Fields和Edges方法分别定义了实体的字段和关联关系。

#### 添加字段

直接修改各实体`Fields`方法的返回值即可。例如，我们给User实体添加age和name字段：

```go
// Fields of the User.
func (User) Fields() []ent.Field {
 return []ent.Field{
  field.Int("age").
   Positive(),
  field.String("name").
   Default("unknown"),
 }
}
```

#### 添加边（Relation）

直接修改各实体`Edges`方法的返回值即可。例如，我们给User实体添加一个一对多关系到Car：

```go
// Edges of the User.
func (User) Edges() []ent.Edge {
 return []ent.Edge{
  edge.To("cars", Car.Type),
 }
}
```

这时如果我们查看数据库模式，会发现Car实体对应的cars表多了一列`user_cars`，作为外键约束指向User实体的id。

#### 添加逆边（BackRef）

```go
// Edges of the Car.
func (Car) Edges() []ent.Edge {
 return []ent.Edge{
  // 创建一个名为 "owner" 的 `User` 反向边
  // 并关联到 "cars" 边 (在 用户 结构中)
  // 并显式的使用 `Ref` 方法。
  edge.From("owner", User.Type).
   Ref("cars").
   // 设置边为唯一确保每辆车都只有一个拥有者
   Unique(),
 }
}
```

如上代码创建了`cars`边的逆边`owner`。这时如果我们查看数据库模式，会发现并没有新增约束，因为这只是对原边的反向引用。

我们可以通过`Unique`方法来设置边的唯一性，从而设置一对一，一对多或多对多关系。
如果是多对多关系将建立一个新的映射表来反映关联关系。

### 生成代码

```bash
ent generate ./ent/schema
```

或者：

```bash
go generate ./ent
```

生成代码后目录如下：

```bash
.
└── ent
    ├── client.go
    ├── ent.go
    ├── enttest
    │   └── enttest.go
    ├── generate.go
    ├── hook
    │   └── hook.go
    ├── migrate
    │   ├── migrate.go
    │   └── schema.go
    ├── mutation.go
    ├── predicate
    │   └── predicate.go
    ├── runtime
    │   └── runtime.go
    ├── runtime.go
    ├── schema
    │   └── user.go
    ├── tx.go
    ├── user            # user
    │   ├── user.go
    │   └── where.go        
    ├── user.go         # user
    ├── user_create.go  # user
    ├── user_delete.go  # user
    ├── user_query.go   # user
    └── user_update.go  # user
```

其中，user文件夹及user开头的文件属于User实体，其他的文件则是通用的。

在编写好schema和生成代码后，就可以使用ent的client进行数据库操作了。

### 连接数据库

ent支持多种数据库，包括MySQL、PostgreSQL、SQLite等。可以使用`ent.Open()`建立一个数据库链接并返回客户端：

```go

// func ent.Open(driverName string, dataSourceName string, options ...ent.Option) (*ent.Client, error)

client, err := ent.Open("mysql", "username:password@tcp(127.0.0.1:3306)/entdemo")
defer client.Close()
```

### 创建&迁移数据库模式

可以使用`ent.Client.Schema.Create()`方法创建数据库模式：

```go
// func (s *Schema) Create(ctx context.Context, opts ...schema.MigrateOption) error

err := client.Schema.Create(context.Background())
```

## 其他工具

### SQL转entgo

[SQL转entgo](https://old.printlove.cn/tools/sql2ent)

这个在线工具可以将sql直接转换成entgo的schema。

### entimport

[blog](https://entgo.io/zh/blog/2021/10/11/generating-ent-schemas-from-existing-sql-databases/)
[github](https://github.com/ariga/entimport)

这个工具可以将数据库中现有的表结构转换成entgo的schema。

### protoc-gen-ent

[blog](https://entgo.io/blog/2021/05/04/announcing-schema-imports/)
[github](https://github.com/ent/contrib/tree/master/entproto/cmd/protoc-gen-ent)

这个工具可以将protobuf文件转换成entgo的schema。
