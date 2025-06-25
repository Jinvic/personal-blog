---
title: Kratos 快速入门实践
date: '2024-11-11T20:50:17+08:00'
tags:
- Go
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Kratos 快速入门实践

## 前言

kratos[官方文档](https://go-kratos.dev/docs/getting-started/start)的快速入门主打一个跑起来就算成功，基本没什么内容。本文将基于官方文档快速入门，结合自己的实践，详细说明如何在kratos框架中开发一个新功能。

## 项目结构

如下是 Kratos 的一个典型的 Go 项目布局，也差不多是我们使用`kratos new .`创建新项目时的默认布局：

```bash
application
|____api
| |____helloworld
| | |____v1
| | |____errors
|____cmd
| |____helloworld
|____configs
|____internal
| |____conf
| |____data
| |____biz
| |____service
| |____server
|____test
|____pkg
|____go.mod
|____go.sum
|____LICENSE
|____README.md
```

简单来说，要开发一个新功能就是`api->[service-biz-data]<-ent`的流程。其中`api`层定义外部接口，`service`层负责与外部接口对接，`biz`层负责业务逻辑，`data`层与底层数据操作对接，`ent`层实现数据库定义与操作。

## api层

首先在`api/helloworld/v1`中定义protobuf文件，并使用 `kratos proto client .\api\helloworld\v1\test.proto` 生成go代码。

```proto
// api/helloworld/v1/test.proto
syntax = "proto3";

package api.helloworld.v1;

import "google/api/annotations.proto";

option go_package = "helloworld/api/helloworld/v1;v1";

// The test service definition.
service Test {
  rpc GetTest(GetTestRequest) returns (GetTestReply) {
    option (google.api.http) = {
      get: "/test/{id}"
    };
  };
}

message GetTestRequest {
  string id = 1;
}
message GetTestReply {
  string field1 = 1;
  string field2 = 2;
}
```

然后可以通过`kratos proto server .\api\helloworld\v1\test.proto -t internal/service`在`internal\service`下生成对应的service文件，这里实现了`pb.TestServer`接口。

```go
// internal/service/test.go
package service

import (
 "context"

 pb "helloworld/api/helloworld/v1"
)

type TestService struct {
 pb.UnimplementedTestServer
}

func NewTestService() *TestService {
 return &TestService{}
}

func (s *TestService) GetTest(ctx context.Context, req *pb.GetTestRequest) (*pb.GetTestReply, error) {
 return &pb.GetTestReply{}, nil
}
```

对外的部分就完成了，这是从外部接口到内部逻辑的步骤。

接下来，我们从最底层的数据库开始，由内向外实现到service层。

## ent层

首先是ent框架的schema定义，在`internal/data/ent/schema`下定义ent的schema文件。
关于ent的语法，在此不再赘述。

```go
// internal/data/ent/schema/test.go
package schema

import (
 "entgo.io/ent"
 "entgo.io/ent/dialect"
 "entgo.io/ent/schema/field"
)

// Test holds the schema definition for the Test entity.
type Test struct {
 ent.Schema
}

// Fields of the Test.
func (Test) Fields() []ent.Field {

 return []ent.Field{

  field.Int32("id").SchemaType(map[string]string{
   dialect.MySQL: "int(10)UNSIGNED", // Override MySQL.
  }).NonNegative().Unique(),

  field.String("field1").SchemaType(map[string]string{
   dialect.MySQL: "varchar(50)", // Override MySQL.
  }),

  field.String("field2").SchemaType(map[string]string{
   dialect.MySQL: "varchar(50)", // Override MySQL.
  }),
 }

}

// Edges of the Test.
func (Test) Edges() []ent.Edge {
 return nil
}
```

在完成schema定义后，就可以使用ent工具生成用户操作数据库的相关代码。

```bash
ent generate ./internal/data/ent/schema
```

在`internal/data/data.go`中实现客户端并装载到Data结构体中,这样就把数据库操作和内部逻辑连接了起来。

```go
// internal/data/data.go
package data

import (
    ...
    _ "github.com/go-sql-driver/mysql" // mysql driver
)

// Data .
type Data struct {
 // TODO wrapped database client
 db *ent.Client
}

// NewData .
func NewData(c *conf.Data, logger log.Logger) (*Data, func(), error) {
 cleanup := func() {
  log.NewHelper(logger).Info("closing the data resources")
 }
 return &Data{
  db: NewEntClient(c, logger),
 }, cleanup, nil
}

// NewEntClient .
func NewEntClient(c *conf.Data, logger log.Logger) *ent.Client {
 client, err := ent.Open(c.Database.Driver, c.Database.Source)
 if err != nil {
  log.NewHelper(logger).Fatal(err)
 }
 return client
}
```

别忘了在`configs/config.yaml`中修改数据库配置。

```yaml
data:   
  database:
    driver: mysql
    source: root:123456@tcp(127.0.0.1:3306)/test?parseTime=True&loc=Local
```

完成api层和ent层后，程序内外的连接就完成了，接下来就是实现程序内部的逻辑。

## data层

在`internal/data/test.go`中实现数据库操作，这里让`testRepo`实现`GetTest`方法，即实现`biz.TestRepo`接口。

```go
// internal/data/test.go
package data

type testRepo struct {
 data *Data
 log  *log.Helper
}

func (r *testRepo) GetTest(ctx context.Context, id int32) (*biz.Test, error) {
 test, err := r.data.db.Test.Query().Where(test.IDEQ(id)).Only(ctx)
 if err != nil {
  return nil, err
 }
 return &biz.Test{
  Id:     test.ID,
  Field1: test.Field1,
  Field2: test.Field2,
 }, nil
}

```

## biz层

在`internal/biz/test.go`中实现业务逻辑，这里因为逻辑很简单，直接调用data层方法就行。

```go
// internal/biz/test.go
package biz

type Test struct {
 Id     int32
 Field1 string
 Field2 string
}

type TestRepo interface {
 GetTest(context.Context, int32) (*Test, error)
}

type TestUsecase struct {
 repo TestRepo
 log  *log.Helper
}

// // GetTest search and return the Test.
func (uc *TestUsecase) GetTest(ctx context.Context, id int32) (*Test, error) {
 return uc.repo.GetTest(ctx, id)
}
```

## service层

最后，将`TestUsecase`装载到`internal/service/test.go`中，这样service层就完成了。

```go
// internal/service/test.go
package service

type TestService struct {
 pb.UnimplementedTestServer
 uc *biz.TestUsecase
}

func (s *TestService) GetTest(ctx context.Context, req *pb.GetTestRequest) (*pb.GetTestReply, error) {
 id, err := strconv.Atoi(req.Id)
 if err != nil {
  return nil, err
 }
 test, err := s.uc.GetTest(ctx, int32(id))
 if err != nil {
  return nil, err
 }
 return &pb.GetTestReply{
  Field1: test.Field1,
  Field2: test.Field2,
 }, nil
}
```

## 依赖注入

最后，我们实现每一层的构造函数，并使用`wire`进行依赖注入。

```go
// internal/servece/test.go
package service

func NewTestService(
 uc *biz.TestUsecase,
) *TestService {
 return &TestService{
  uc: uc,
 }
}
// internal/servece/service.go
package service

import "github.com/google/wire"

// ProviderSet is service providers.
var ProviderSet = wire.NewSet(NewGreeterService, NewTestService)

// internal/biz/test.go
package biz

// NewTestUsecase new a Test usecase.
func NewTestUsecase(repo TestRepo, logger log.Logger) *TestUsecase {
 return &TestUsecase{repo: repo, log: log.NewHelper(logger)}
}

// internal/biz/biz.go
package biz

import "github.com/google/wire"

// ProviderSet is biz providers.
var ProviderSet = wire.NewSet(NewGreeterUsecase, NewTestUsecase)

// internal/data/test.go
package data

// NewTestRepo .
func NewTestRepo(data *Data, logger log.Logger) biz.TestRepo {
 return &testRepo{
  data: data,
  log:  log.NewHelper(logger),
 }
}

// internal/data/data.go
package data

import (
    ...
    "github.com/google/wire"
)

// ProviderSet is data providers.
var ProviderSet = wire.NewSet(NewData, NewGreeterRepo, NewTestRepo)

// internal/server/http.go
package server

// NewHTTPServer new an HTTP server.
func NewHTTPServer(c *conf.Server, greeter *service.GreeterService, test *service.TestService, logger log.Logger) *http.Server {
 var opts = []http.ServerOption{
  http.Middleware(
   recovery.Recovery(),
  ),
 }
 if c.Http.Network != "" {
  opts = append(opts, http.Network(c.Http.Network))
 }
 if c.Http.Addr != "" {
  opts = append(opts, http.Address(c.Http.Addr))
 }
 if c.Http.Timeout != nil {
  opts = append(opts, http.Timeout(c.Http.Timeout.AsDuration()))
 }
 srv := http.NewServer(opts...)
 v1.RegisterGreeterHTTPServer(srv, greeter)
 v1.RegisterTestHTTPServer(srv, test)
 return srv
}

// internal/server/grpc.go
package server

// NewGRPCServer new a gRPC server.
func NewGRPCServer(c *conf.Server, greeter *service.GreeterService, test *service.TestService, logger log.Logger) *grpc.Server {
 var opts = []grpc.ServerOption{
  grpc.Middleware(
   recovery.Recovery(),
  ),
 }
 if c.Grpc.Network != "" {
  opts = append(opts, grpc.Network(c.Grpc.Network))
 }
 if c.Grpc.Addr != "" {
  opts = append(opts, grpc.Address(c.Grpc.Addr))
 }
 if c.Grpc.Timeout != nil {
  opts = append(opts, grpc.Timeout(c.Grpc.Timeout.AsDuration()))
 }
 srv := grpc.NewServer(opts...)
 v1.RegisterGreeterServer(srv, greeter)
 v1.RegisterTestServer(srv, test)
 return srv
}
```

使用`go generate ./...`命令更新依赖注入代码后就可以启动服务了。

## 总结

通过以上步骤，我们完成了从proto文件到最终可运行的服务的整个过程，包括proto文件生成、ent层、data层、biz层、service层以及依赖注入。至于其他内容如`cmd`和`internal/conf`文件夹下的内容，在创建项目时已经生成好了不需要过多改动在此便不再赘述，有需要可以自行修改。
