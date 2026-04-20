---
title: Grpc实践练习
date: '2026-03-31T10:34:13+08:00'
tags: 
- Go
- Protobuf
categories:
- 开发 
draft: true
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Grpc实践练习

参考：

- [buf](https://buf.build/docs/cli/)
- [protobuf EN](https://protobuf.dev/overview/)
- [protobuf CN](https://protobuf.com.cn/overview/)
- [grpc-go EN](https://grpc.io/docs/languages/go/)
- [grpc-go CN](https://grpc.org.cn/docs/languages/go/)
- [grpcurl](https://github.com/fullstorydev/grpcurl)
- [protovalidate](https://protovalidate.com/about/)
- [CEL by Example](https://celbyexample.com/)
- [go-grpc-middleware](https://github.com/grpc-ecosystem/go-grpc-middleware)
- [grpc-gateway](https://github.com/grpc-ecosystem/grpc-gateway)

grpc相关的内容都十分繁琐，虽然看还是能看懂但自己写就抓瞎了。所以做一个项目边练边学尝试融会贯通所学内容。

## 项目结构

项目结构没有什么最佳实践之类，按自己喜欢的来就行。

protobuf有一套自己的包机制，和go混在一起容易混淆。搞清楚`package`和`option go_package`等配置就放哪都行。

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
├── buf.lock
├── buf.yaml
├── cmd/
│   ├── client/
│   └── server/
│       └── book/
│           └── main.go
├── go.mod
├── go.sum
└── internal/
    ├── client/
    └── server/
        └── book/
            ├── model/
            │   ├── biz/
            │   │   └── book.go
            │   └── db/
            │       └── book.go
            ├── repo/
            │   ├── book.go
            │   └── converter.go
            ├── server/
            │   ├── di.go
            │   └── server.go
            ├── service/
            │   ├── book.go
            │   └── converter.go
            └── usecase/
                └── book.go
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
  如果需要覆写多个文件的option使用`managed mode`会很方便，但为少数文件专门使用反而增加了复杂度。此外，虽然启用`managed mode`后原proto文件中可以不写相关option，但还是建议也写上保持对原生protoc的兼容等。
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

## protobuf

protobuf的详细语法可以查阅[文档](https://protobuf.dev/programming-guides/proto3/)和[protobuf笔记](https://blog.jinvic.top/protobuf%E7%AC%94%E8%AE%B0/#%E8%AF%AD%E6%B3%95%E7%AE%80%E8%AE%B0)，在次不再赘述。

这里只是结合目录结构和部分代码进行简单讲解。

```bash
./api/
├── book/
│   └── v1/
│       └── book.proto
└── common/
    └── v1/
        └── types.proto
```

```protobuf
// api/book/v1/book.proto
syntax = "proto3";

package book.v1;

import "common/v1/types.proto";
import "google/protobuf/field_mask.proto";
import "google/protobuf/struct.proto";
import "google/protobuf/timestamp.proto";

option go_package = "bookstore/api/book/v1;bookv1";

service BookService {
  rpc GetBook(GetBookRequest) returns (GetBookResponse);
  rpc CreateBook(CreateBookRequest) returns (CreateBookResponse);
  rpc ListBooks(ListBooksRequest) returns (ListBooksResponse);
  rpc UpdateBook(UpdateBookRequest) returns (UpdateBookResponse);
  rpc DeleteBook(DeleteBookRequest) returns (DeleteBookResponse);
}

message GetBookRequest {
  int64 id = 1;
}

message GetBookResponse {
  common.v1.Book book = 1;
}

message CreateBookRequest {
  common.v1.Book book = 1;
}

message CreateBookResponse {
  common.v1.Book book = 1;
}

message ListBooksRequest {
  int32 page_number = 1;
  int32 page_size = 2;
  repeated common.v1.OrderBy order_by = 3;
  map<string, google.protobuf.Value> filter = 4;
}

message ListBooksResponse {
  repeated common.v1.Book books = 1;
  int32 total_count = 2;
  int32 page_number = 3;
  int32 page_size = 4;
}

message UpdateBookRequest {
  common.v1.Book book = 1;
  google.protobuf.FieldMask update_mask = 2;
}

message UpdateBookResponse {
  common.v1.Book book = 1;
}

message DeleteBookRequest {
  int64 id = 1;
}

message DeleteBookResponse {
  int64 id = 1;
  google.protobuf.Timestamp deleted_at = 2;
}

```

```protobuf
// api/common/v1/types.proto
syntax = "proto3";

package common.v1;

import "google/protobuf/timestamp.proto";

option go_package = "bookstore/api/common/v1;commonv1";

enum BookStatus {
  BOOK_STATUS_UNSPECIFIED = 0;
  BOOK_STATUS_AVAILABLE = 1; // 可用
  BOOK_STATUS_UNAVAILABLE = 2; // 不可用
  BOOK_STATUS_BORROWED = 3; // 借出
  BOOK_STATUS_LOST = 4; // 丢失
  BOOK_STATUS_RESERVED = 6; // 预约
}

message Book {
  int64 id = 1;
  BookStatus status = 2;
  google.protobuf.Timestamp created_at = 3;
  google.protobuf.Timestamp updated_at = 4;
  google.protobuf.Timestamp deleted_at = 5;
  string title = 6;
  string author = 7;
  double price = 8;
  string isbn = 9;
  string publisher = 10;
  google.protobuf.Timestamp published_at = 11;
}

message OrderBy {
  string field = 1;
  bool ascending = 2;
}

```

`package`是proto之间互相引用的包名。可以注意到`book.proto`从`types.proto`引用`Book`时就是`common.v1.Book`。

`import`用于引入其他proto文件，可以是本地文件也可以是从其他地方引入。例如`book.proto`的`import "common/v1/types.proto";`就是本地proto，`import "google/protobuf/struct.proto";`就是`google/protobuf`里的proto。需要注意的是，即使是同一目录下的不同文件在引用时也需要显式`import`，这点和Go的默认行为并不一致。

这里我们在引入`google/protobuf`的相关文件时不需要显式声明依赖，是因为`google/protobuf`是内置在`protobuf`中的，相当与标准库。而在引入其他第三方库时，往往需要手动安装（protoc）或显式声明（buf cli）。

`option`之前有讲过，是语言特定的一些定义选项。

`service`和`message`分别定义rpc服务和消息结构体，`repeated`和`enum`定义数组和枚举，语法都比较简单。

## gRPC服务端

关于proto部分，在之前已经介绍地差不多了。现在我们来看看如何在go中实现gorc服务端并用上之前的proto stub。

如下是我规划的项目结构，按照`server → service → usecase → repo`进行分层：

```bash
./
├── api/
├── cmd/
│   ├── client/
│   └── server/
│       └── book/ # 入口
└── internal/
    ├── client/
    └── server/
        └── book/
            ├── model/
            │   ├── biz/ # 业务层模型
            │   └── db/  # 数据库模型
            ├── repo/    # 数据仓库层
            ├── server/  # gRPC server
            ├── service/ # gRPC 服务实现
            └── usecase/ # 用例层
```

首先我们要实现在proto中定义的服务，如下：

```go
// internal/server/book/service/book.go
type BookService struct {
  bookv1.UnimplementedBookServiceServer
  bu *usecase.BookUsecase
}

func NewBookService(bu *usecase.BookUsecase) *BookService {
  return &BookService{bu: bu}
}

func (s *BookService) GetBook(ctx context.Context, req *bookv1.GetBookRequest) (*bookv1.GetBookResponse, error) {
  bizBook, err := s.bu.GetBook(ctx, req.Id)
  if err != nil {
    return nil, status.Errorf(codes.Internal, "failed to get book: %v", err)
  }

  return &bookv1.GetBookResponse{Book: BizToV1Book(bizBook)}, nil
}

func (s *BookService) CreateBook(ctx context.Context, req *bookv1.CreateBookRequest) (*bookv1.CreateBookResponse, error) {
  // ...
}

func (s *BookService) ListBooks(ctx context.Context, req *bookv1.ListBooksRequest) (*bookv1.ListBooksResponse, error) {
  // ...
}

func (s *BookService) UpdateBook(ctx context.Context, req *bookv1.UpdateBookRequest) (*bookv1.UpdateBookResponse, error) {
  // ...
}

func (s *BookService) DeleteBook(ctx context.Context, req *bookv1.DeleteBookRequest) (*bookv1.DeleteBookResponse, error) {
  // ...
}
```

我们需要自行定义一个结构体，嵌入protobuf生成的stub代码中的`UnimplementedXXXServer`结构体，并实现相关方法。这就相当于handler或controller层了。

然后我们启动gprc服务。此处的依赖注入实现较简略仅作示例。生产环境可以换成`wire`或`dig`。

```go
// internal/server/book/server/server.go
type BookServer struct {
  port int
}

func NewBookServer(port int) *BookServer {
  return &BookServer{port: port}
}

func (s *BookServer) Run(ctx context.Context) error {

  lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.port))
  if err != nil {
    return fmt.Errorf("failed to listen: %w", err)
  }
  defer lis.Close()

  grpcServer := grpc.NewServer()
  bookv1.RegisterBookServiceServer(grpcServer, BuildBookService())

  go func() {
    <-ctx.Done()
    log.Println("shutting down server...")
    grpcServer.GracefulStop()
  }()

  log.Printf("server listening at port %d", s.port)
  if err := grpcServer.Serve(lis); err != nil {
    if err == grpc.ErrServerStopped {
      log.Println("server stopped")
      return nil
    }
    return fmt.Errorf("failed to serve: %w", err)
  }
  return nil
}

func BuildBookService() *service.BookService {
  br := repo.NewBookRepository()
  bu := usecase.NewBookUsecase(br)
  return service.NewBookService(bu)
}
```

总结流程，首先使用`net.Listen()`监听一个端口，然后用`grpc.NewServer()`声明一个`grpc.Server`类型的grpc服务，使用stub代码中的`RegisterBookServiceServer()`方法将你自定义的结构体注册到这个grpc服务中，最后用`grpc.Server.Serve()`在监听器上提供服务。

继续往项目里填充crud代码，运行`go run cmd/server/book/main.go`就可以启动这个服务了。

## grpcurl

要测试启动的grpc服务是否可用，可以实现一个客户端，也可以使用[grpcurl](https://github.com/fullstorydev/grpcurl)这个工具。就简单测试而言直接使用`grpcurl`就行。

```bash
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
```

### 启用反射服务

由于grpc使用protobuf的二进制编码，而不是json那种自描述的文本编码，所以我们需要提供proto文件或者反射服务，让客户端了解服务列表、方法列表、消息定义等。通常完整客户端都是和服务端共用相同的proto文件，而我们为了调试方便使用`grpcurl`时就启用反射服务。

可以使用`google.golang.org/grpc/reflection`包将`grpc.Server`注册到反射服务中：

```go
import "google.golang.org/grpc/reflection"

func (s *BookServer) Run(ctx context.Context) error {
  // ...

  grpcServer := grpc.NewServer()
  reflection.Register(grpcServer) // new
  bookv1.RegisterBookServiceServer(grpcServer, BuildBookService())

  // ...
}
```

反射服务在收到查询请求时，会**实时查询**`grpc.Server`中已注册的所有服务，而不是快照注册时的服务列表，所以注册反射服务和注册业务服务的顺序没有影响。

### grpcurl基础用法

现在我们可以通过`grpcurl`调用grpc服务了，用法为：`grpcurl [flags] [address] [list|describe] [symbol]`。

```bash
-plaintext
      Use plain-text HTTP/2 when connecting to server (no TLS).
```

由于我们实现的服务端没有启用证书，所以我们`grpcurl`测试时的所有命令都要添加`-plaintext`选项来进行明文通讯。生产环境应该启用tls加密。

可以使用`list`查看服务和方法列表：

```bash
$ grpcurl -plaintext localhost:8081 list
book.v1.BookService
grpc.reflection.v1.ServerReflection
grpc.reflection.v1alpha.ServerReflection

$ grpcurl -plaintext localhost:8081 list book.v1.BookService
book.v1.BookService.CreateBook
book.v1.BookService.DeleteBook
book.v1.BookService.GetBook
book.v1.BookService.ListBooks
book.v1.BookService.UpdateBook
```

可以使用`describe`查看服务和方法列表：

```bash
$ grpcurl -plaintext localhost:8081 describe book.v1.BookService
book.v1.BookService is a service:
service BookService {
  rpc CreateBook ( .book.v1.CreateBookRequest ) returns ( .book.v1.CreateBookResponse );
  rpc DeleteBook ( .book.v1.DeleteBookRequest ) returns ( .book.v1.DeleteBookResponse );
  rpc GetBook ( .book.v1.GetBookRequest ) returns ( .book.v1.GetBookResponse );
  rpc ListBooks ( .book.v1.ListBooksRequest ) returns ( .book.v1.ListBooksResponse );
  rpc UpdateBook ( .book.v1.UpdateBookRequest ) returns ( .book.v1.UpdateBookResponse );
}

$ grpcurl -plaintext localhost:8081 describe book.v1.BookService.GetBook
book.v1.BookService.GetBook is a method:
rpc GetBook ( .book.v1.GetBookRequest ) returns ( .book.v1.GetBookResponse );

$ grpcurl -plaintext localhost:8081 describe .book.v1.GetBookResponse                           
book.v1.GetBookResponse is a message:
message GetBookResponse {
  .common.v1.Book book = 1;
}

$ grpcurl -plaintext localhost:8081 describe .common.v1.Book
common.v1.Book is a message:
message Book {
  int64 id = 1;
  .common.v1.BookStatus status = 2;
  .google.protobuf.Timestamp created_at = 3;
  .google.protobuf.Timestamp updated_at = 4;
  .google.protobuf.Timestamp deleted_at = 5;
  string title = 6;
  string author = 7;
  double price = 8;
  string isbn = 9;
  string publisher = 10;
  .google.protobuf.Timestamp published_at = 11;
}
```

最后是调用方法，可以通过`-d`标志传入一个json字符串作为输入参数。如果传入`@`字符则是从标准输入读取json作为参数，一般用于复杂json输入，也可用于测试流方法。

```bash
$ grpcurl -plaintext -d '{"id":1}' localhost:8081 book.v1.BookService/GetBook
{
  "book": {
    "id": "1",
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "price": 10.99,
    "isbn": "978-0-7432-1967-1",
    "publisher": "Scribner",
    "publishedAt": "2026-04-16T01:47:46.470161300Z"
  }
}

# linux
$ grpcurl -plaintext -d @ localhost:8081 book.v1.BookService/GetBook <<EOM
{"id": 1}
EOM
{
  "book": {
    "id": "1",
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "price": 10.99,
    "isbn": "978-0-7432-1967-1",
    "publisher": "Scribner",
    "publishedAt": "2026-04-16T01:47:11.511262700Z"
  }
}
```

```pwsh
# windows(Powershell)
> @"
{"id": 1}
"@ | grpcurl -plaintext -d '@' localhost:8081 book.v1.BookService/GetBook
{
  "book": {
    "id": "1",
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "price": 10.99,
    "isbn": "978-0-7432-1967-1",
    "publisher": "Scribner",
    "publishedAt": "2026-04-16T02:02:47.932611Z"
  }
}
```

## grpc客户端

除了使用grpcurl直接测试grpc服务，还需要实现grpc客户端供微服务之间互相调用。如下是一个实现示例：

```go
// internal/client/book/client.go
type Client struct {
  bookv1.BookServiceClient
  conn *grpc.ClientConn
}

func NewClient(host string, port int) (*Client, error) {
  serverAddr := fmt.Sprintf("%s:%d", host, port)

  opts := []grpc.DialOption{
    grpc.WithTransportCredentials(insecure.NewCredentials()),
  }
  conn, err := grpc.NewClient(serverAddr, opts...)
  if err != nil {
    return nil, fmt.Errorf("failed to create client: %w", err)
  }
  return &Client{
    BookServiceClient: bookv1.NewBookServiceClient(conn),
    conn:              conn,
  }, nil
}

func (c *Client) Close() error {
  return c.conn.Close()
}

func (c *Client) GetBook(ctx context.Context, id int64) (*commonv1.Book, error) {
  resp, err := c.BookServiceClient.GetBook(ctx, &bookv1.GetBookRequest{Id: id})
  if err != nil {
    return nil, fmt.Errorf("failed to get book: %w", err)
  }
  return resp.Book, nil
}

// ...
```

逻辑还是比较清晰的。首先确认服务地址`serverAddr`，然后处理连接选项`opts`。这里我们使用的`grpc.WithTransportCredentials(insecure.NewCredentials())`，因为服务端没有启用tls加密。通过`grpc.NewClient()`获取到一个grpc连接`conn`，再通过`bookv1.NewBookServiceClient()`创建book服务的客户端。需要注意的是，要将`conn`变量保存下来用于关闭连接。最后我们为客户端实现各个方法就行。

## 流式rpc

除了常规的请求-响应，grpc还支持各种流式rpc方法，包括客户端流，服务端流和双向流等。让我们为各种流式方法设计业务场景并尝试实现：

- 客户端流：批量导入
- 服务端流：批量导出
- 双向流：心跳检测

### protobuf定义流

在protobuf中，要启用流特性，需要在声明方法时添加`stream`关键字进行标识：

```protobuf
service BookService {
  rpc GetBook(GetBookRequest) returns (GetBookResponse);
  rpc CreateBook(CreateBookRequest) returns (CreateBookResponse);
  rpc ListBooks(ListBooksRequest) returns (ListBooksResponse);
  rpc UpdateBook(UpdateBookRequest) returns (UpdateBookResponse);
  rpc DeleteBook(DeleteBookRequest) returns (DeleteBookResponse);
  // new
  rpc BatchImportBooks(stream BatchImportBooksRequest) returns (BatchImportBooksResponse);
  rpc BatchExportBooks(BatchExportBooksRequest) returns (stream BatchExportBooksResponse);
  rpc HeartBeat(stream HeartBeatRequest) returns (stream HeartBeatResponse);
}


message BatchImportBooksRequest {
  common.v1.Book book = 1;
}

message BatchImportBooksResponse {
  int32 total = 1;
  int32 success = 2;
  repeated string error_messages = 3;
}

message BatchExportBooksRequest {
  repeated int64 book_ids = 1;
}

message BatchExportBooksResponse {
  int64 book_id = 1;
  common.v1.Book book = 2;
  string error_message = 3;
}

message HeartBeatRequest {
  // 1: ping, 2: pong
  common.v1.HeartBeatType type = 1;
  int64 sent_at = 2;
}

message HeartBeatResponse {
  // 1: ping, 2: pong
  common.v1.HeartBeatType type = 1;
  int64 sent_at = 2;
  int64 received_at = 3;
}

enum HeartBeatType {
  HEART_BEAT_TYPE_UNSPECIFIED = 0;
  HEART_BEAT_TYPE_PING = 1; // 心跳请求
  HEART_BEAT_TYPE_PONG = 2; // 心跳响应
}
```

### 流式rpc服务端实现

然后是三个方法的服务端go实现，方法签名如下：

```go
func (s *BookService) BatchImportBooks(stream bookv1.BookService_BatchImportBooksServer) error
func (s *BookService) BatchExportBooks(req *bookv1.BatchExportBooksRequest, stream bookv1.BookService_BatchExportBooksServer) error
func (s *BookService) HeartBeat(stream bookv1.BookService_HeartBeatServer) error
```

可以看到，它使用`服务名_方法名Server`取代了原来的`request`和`response`。查看定义可以发现请求和响应被封装到了对应的流接口中：

```go
type BookService_BatchImportBooksServer = grpc.ClientStreamingServer[BatchImportBooksRequest, BatchImportBooksResponse]
type BookService_BatchExportBooksServer = grpc.ServerStreamingServer[BatchExportBooksResponse]
type BookService_HeartBeatServer = grpc.BidiStreamingServer[HeartBeatRequest, HeartBeatResponse]
```

查看接口定义，可以看到它们各自定义了`Send()`和`Recv()`等相关方法用于发送和接收消息。

```go
type ServerStreamingServer[Res any] interface {
  Send(*Res) error
  ServerStream
}

type ClientStreamingServer[Req any, Res any] interface {
  Recv() (*Req, error)
  SendAndClose(*Res) error
  ServerStream
}

type BidiStreamingServer[Req any, Res any] interface {
  Recv() (*Req, error)
  Send(*Res) error
  ServerStream
}
```

需要注意的是，这些方法都**不是并发安全**的。因为对于绝大多数简单的、顺序处理的流，一个内置的`sync.Mutex`会带来不必要的性能损耗。同时gRPC的设计者也希望开发者明确地规划发送和接收的角色权限。所以如果在多个goroutine中都有调用同一个方法，需要自行设计同步机制。例如使用一个专用的goroutine来执行所有的`Send()`或`Recv()`操作，或者使用`sync.Mutex`进行保护。

按照由易到难的顺序，我们依次实现服务端流，客户端流和双向流。

首先是服务端流，只有一次输入，分多次输出结果：

```go
func (s *BookService) BatchExportBooks(req *bookv1.BatchExportBooksRequest, stream bookv1.BookService_BatchExportBooksServer) error {
  for _, bookId := range req.BookIds {
    book, err := s.bu.GetBook(stream.Context(), bookId)
    if err != nil {
      if sendErr := stream.Send(&bookv1.BatchExportBooksResponse{
        BookId:       bookId,
        ErrorMessage: fmt.Sprintf("failed to get book %s: %v", book.Title, err),
      }); sendErr != nil {
        return status.Errorf(codes.Internal, "failed to send response: %v", sendErr)
      }
      continue
    }
    if err := stream.Send(&bookv1.BatchExportBooksResponse{Book: BizToV1Book(book)}); err != nil {
      return status.Errorf(codes.Internal, "failed to send response: %v", err)
    }
  }
  return nil
}
```

然后是客户端流，多次输入直到流关闭，最后一次性输出结果。

```go
func (s *BookService) BatchImportBooks(stream bookv1.BookService_BatchImportBooksServer) error {
  var total int32
  var success int32
  var errorMessages []string
  for {
    req, err := stream.Recv()
    if err == io.EOF {
      break
    }
    if err != nil {
      return status.Errorf(codes.Internal, "failed to receive request: %v", err)
    }
    bizBook := V1ToBizBook(req.Book)
    _, err = s.bu.CreateBook(stream.Context(), bizBook)
    if err != nil {
      errorMessages = append(errorMessages, fmt.Sprintf("failed to create book %s: %v", bizBook.Title, err))
    } else {
      success++
    }
    total++

  }
  return stream.SendAndClose(&bookv1.BatchImportBooksResponse{
    Total:         total,
    Success:       success,
    ErrorMessages: errorMessages,
  })
}
```

最后是双向流，双方都随时可以进行输入输出：

```go
func (s *BookService) HeartBeat(stream bookv1.BookService_HeartBeatServer) error {
  sendCh := make(chan *bookv1.HeartBeatResponse, 10)
  done := make(chan struct{})
  defer close(done)

  // 发送消息到客户端
  sender := func() {
    for {
      select {
      case msg, ok := <-sendCh:
        if !ok {
          return
        }
        if err := stream.Send(msg); err != nil {
          log.Printf("failed to send message: %v", err)
          return
        }
        log.Println("sent message:", msg.Type)
      case <-done:
        log.Println("sender goroutine stopped")
        return
      case <-stream.Context().Done():
        log.Println("client disconnected, stopping sender goroutine")
        return
      }
    }
  }

  // 定时发送心跳消息
  ticker := func() {
    jitter := time.Duration(rand.Intn(10)) * time.Second
    ticker := time.NewTicker(1*time.Minute + jitter)
    defer ticker.Stop()

    for {
      select {
      case <-ticker.C:
        sendCh <- &bookv1.HeartBeatResponse{
          Type:   commonv1.HeartBeatType_HEART_BEAT_TYPE_PING,
          SentAt: time.Now().UnixMilli(),
        }
      case <-done:
        log.Println("ticker goroutine stopped")
        return
      case <-stream.Context().Done():
        log.Println("client disconnected, stopping ticker goroutine")
        return
      }
    }
  }

  // 接收客户端的心跳消息
  receiver := func() error {
    for {
      req, err := stream.Recv()
      if err == io.EOF {
        break
      }
      if err != nil {
        return status.Errorf(codes.Internal, "failed to receive request: %v", err)
      }

      switch req.Type {
      case commonv1.HeartBeatType_HEART_BEAT_TYPE_PING:
        sendCh <- &bookv1.HeartBeatResponse{
          Type:   commonv1.HeartBeatType_HEART_BEAT_TYPE_PONG,
          SentAt: req.SentAt,
        }
      case commonv1.HeartBeatType_HEART_BEAT_TYPE_PONG:
        receivedAt := time.Now().UnixMilli()
        log.Println("received pong, latency:", receivedAt-req.SentAt)
      default:
        log.Println("received unknown heart beat type")
        return status.Errorf(codes.InvalidArgument, "unknown heart beat type: %v", req.Type)
      }
    }
    return nil
  }

  go ticker()
  go sender()
  return receiver()
}
```

### 流式rpc客户端实现

然后我们尝试实现客户端。流式rpc的服务端和客户端实现差不多，都是操作一个流对象通过`Send()`和`Recv()`等相关方法收发信息。

客户端的各种流接口定义如下：

```go
type ServerStreamingClient[Res any] interface {
  Recv() (*Res, error)
  ClientStream
}
type ClientStreamingClient[Req any, Res any] interface {
  Send(*Req) error
  CloseAndRecv() (*Res, error)
  ClientStream
}
type BidiStreamingClient[Req any, Res any] interface {
  Send(*Req) error
  Recv() (*Res, error)
  ClientStream
}

```

和服务端流接口一样，这些方法也**不是并发安全**的，需要自行设计同步机制。

具体实现如下：

**服务端流**：

```go
func (c *Client) BatchExportBooks(ctx context.Context, bookIds []int64) ([]*commonv1.Book, []string, error) {
  req := &bookv1.BatchExportBooksRequest{BookIds: bookIds}
  stream, err := c.BookServiceClient.BatchExportBooks(ctx, req)
  if err != nil {
    return nil, nil, fmt.Errorf("failed to export books: %w", err)
  }

  books := make([]*commonv1.Book, 0)
  errorMessages := make([]string, 0)
  for {
    resp, err := stream.Recv()
    if err == io.EOF {
      break
    }
    if err != nil {
      return nil, nil, fmt.Errorf("failed to receive response: %w", err)
    }
    if resp.ErrorMessage != "" {
      errorMessages = append(errorMessages, fmt.Sprintf("failed to export book with ID %d: %s", resp.BookId, resp.ErrorMessage))
      continue
    }
    books = append(books, resp.Book)
  }
  return books, errorMessages, nil
}
```

**客户端流**：

```go
func (c *Client) BatchImportBooks(ctx context.Context, books []*commonv1.Book) (*bookv1.BatchImportBooksResponse, error) {
  stream, err := c.BookServiceClient.BatchImportBooks(ctx)
  if err != nil {
    return nil, fmt.Errorf("failed to import books: %w", err)
  }
  for _, book := range books {
    err := stream.Send(&bookv1.BatchImportBooksRequest{Book: book})
    if err != nil {
      return nil, fmt.Errorf("failed to send request: %w", err)
    }
  }
  resp, err := stream.CloseAndRecv()
  if err != nil {
    return nil, fmt.Errorf("failed to close stream: %w", err)
  }
  return resp, nil
}
```

**双向流**：

```go
func (c *Client) HeartBeat(ctx context.Context) error {
  stream, err := c.BookServiceClient.HeartBeat(ctx)
  if err != nil {
    return fmt.Errorf("failed to create heart beat stream: %w", err)
  }

  sendCh := make(chan *bookv1.HeartBeatRequest, 10)
  done := make(chan struct{})
  defer close(done)

  // 发送消息到服务端
  sender := func() {
    for {
      select {
      case msg, ok := <-sendCh:
        if !ok {
          return
        }
        if err := stream.Send(msg); err != nil {
          log.Printf("failed to send message: %v", err)
          return
        }
        log.Println("sent message:", msg.Type)
      case <-done:
        log.Println("sender goroutine stopped")
        return
      case <-stream.Context().Done():
        log.Println("client disconnected, stopping sender goroutine")
        return
      }
    }
  }

  // 定时发送心跳消息
  ticker := func() {
    jitter := time.Duration(rand.Intn(10)) * time.Second
    ticker := time.NewTicker(1*time.Minute + jitter)
    defer ticker.Stop()

    for {
      select {
      case <-ticker.C:
        sendCh <- &bookv1.HeartBeatRequest{
          Type:   commonv1.HeartBeatType_HEART_BEAT_TYPE_PING,
          SentAt: time.Now().UnixMilli(),
        }
      case <-done:
        log.Println("ticker goroutine stopped")
        return
      case <-stream.Context().Done():
        log.Println("client disconnected, stopping ticker goroutine")
        return
      }
    }
  }

  // 接收服务端的心跳消息
  receiver := func() error {
    for {
      req, err := stream.Recv()
      if err == io.EOF {
        break
      }
      if err != nil {
        return status.Errorf(codes.Internal, "failed to receive request: %v", err)
      }

      switch req.Type {
      case commonv1.HeartBeatType_HEART_BEAT_TYPE_PING:
        sendCh <- &bookv1.HeartBeatRequest{
          Type:   commonv1.HeartBeatType_HEART_BEAT_TYPE_PONG,
          SentAt: req.SentAt,
        }
      case commonv1.HeartBeatType_HEART_BEAT_TYPE_PONG:
        receivedAt := time.Now().UnixMilli()
        log.Println("received pong, latency:", receivedAt-req.SentAt)
      default:
        log.Println("received unknown heart beat type")
        return status.Errorf(codes.InvalidArgument, "unknown heart beat type: %v", req.Type)
      }
    }
    return nil
  }

  go ticker()
  go sender()
  return receiver()
}
```

## 参数校验

protobuf原生不提供参数校验功能，需要引入第三方的插件（[protoc-gen-validate](https://github.com/bufbuild/protoc-gen-validate)）或者库（[protovalidate](https://github.com/bufbuild/protovalidate)）。这里我们选择`protovalidate`。

`protovalidate`的详细语法在此不作赘述，可以查阅[文档](https://protovalidate.com/about/)进行了解。这里只简单介绍如何导入依赖和简单使用。

首先要在`buf.yaml`中添加依赖，并执行`buf dep update`更新依赖：

```yml
version: v2
modules:
  - path: api
deps:
  - buf.build/bufbuild/protovalidate # new
lint:
  use:
    - STANDARD
breaking:
  use:
    - FILE
```

在proto文件中通过`import buf/validate/validate.proto`引入依赖，就可以添加验证规则了。添加验证后的`book.proto`部分代码如下：

```protobuf
message GetBookRequest {
  int64 id = 1 [(buf.validate.field).int64.gte = 1];
}

message CreateBookRequest {
  common.v1.Book book = 1 [(buf.validate.field).cel = {
    id: "create_book.required_fields"
    message: "title and author are required"
    expression:
      "this.title != ''"
      "&& this.author != ''"
  }];
}

message ListBooksRequest {
  optional int32 page_number = 1 [(buf.validate.field).int32.gte = 1];
  optional int32 page_size = 2 [(buf.validate.field).int32.gte = 1];
  repeated common.v1.OrderBy order_by = 3;
  map<string, google.protobuf.Value> filter = 4;
}

message UpdateBookRequest {
  common.v1.Book book = 1 [(buf.validate.field).cel = {
    id: "update_book.required_fields"
    message: "id is required"
    expression: "this.id > 0"
  }];
  google.protobuf.FieldMask update_mask = 2;
}
```

可以看到，既可以直接为字段设置简单的验证规则，也可以使用cel表达式设置更为复杂的验证规则。

要在go中执行参数校验，需要安装`buf.build/go/protovalidate`依赖。

```bash
go get buf.build/go/protovalidate@latest
```

可以直接使用`protovalidate.Validate()`方法验证proto转换的结构体：

```go
// internal/server/book/service/book.go
func (s *BookService) GetBook(ctx context.Context, req *bookv1.GetBookRequest) (*bookv1.GetBookResponse, error) {
  protovalidate.Validate(req) // new
  bizBook, err := s.bu.GetBook(ctx, req.Id)
  if err != nil {
    return nil, status.Errorf(codes.Internal, "failed to get book: %v", err)
  }

  return &bookv1.GetBookResponse{Book: BizToV1Book(bizBook)}, nil
}
```

而对`gRPC`项目，则可以将`protovalidate`注册为拦截器：

```go
// internal/server/book/server/server.go
func (s *BookServer) Run(ctx context.Context) error {
  // ...
  validator, err := protovalidate.New()
  if err != nil {
    return fmt.Errorf("failed to create validator: %w", err)
  }

  interceptor := func(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
    if err := validator.Validate(req.(proto.Message)); err != nil {
      return nil, status.Errorf(codes.InvalidArgument, "invalid request: %v", err)
    }
    return handler(ctx, req)
  }

  grpcServer := grpc.NewServer(grpc.UnaryInterceptor(interceptor))
  // ...
}
```

### 扩展：gRPC校验方案演进史

```mermaid
timeline
title gRPC校验方案演进史
section 2017-2019 
方案A：go-proto-validators
: 早期方案，需生成代码<br>与 go-grpc-middleware 配合
section 2019-2023 
方案B：protoc-gen-validate (PGV)
: 成为事实标准<br>规则更丰富，生成代码成熟
section 2023-Now 
方案C：protovalidate
: Buf 官方推出<br>无代码生成，性能更强
```

- 方案A：`go-proto-validators` (较老，生态渐微)
  - **规则定义**：在 `.proto` 中使用 `(validator.field)` 选项。
  - **校验执行**：通过 `protoc` 插件 **生成** Go代码，代码中包含 `Validate()` 方法。
  - **gRPC集成**：需要手动调用 `msg.Validate()`，或使用 `go-grpc-middleware/validator` 拦截器自动调用。
  - **当前状态**：**维护少，不推荐新项目**。作者 `mwitkow` 已停止主动维护，且对最新 `protobuf` API 支持不佳。
- 方案B：`protoc-gen-validate` (PGV) (主流，但正被取代)
  - **规则定义**：在 `.proto` 中使用 `(validate.rules)` 选项。
  - **校验执行**：通过 `protoc` 插件 **生成** Go代码，代码中包含 `ValidateAll()` 等方法。
  - **gRPC集成**：同方案A，可手动调用或使用 `go-grpc-middleware/validator` 拦截器。
  - **当前状态**：**非常成熟，大量项目在用**。但依赖代码生成，且已被更优的方案C挑战。
- 方案C：`protovalidate` (Buf出品，现代推荐)
  - **规则定义**：在 `.proto` 中使用 `(buf.validate.field)` 选项 (更丰富的规则集)。
  - **校验执行**：**无需代码生成**。在运行时动态读取 `.proto` 中的规则并执行校验。提供 `protovalidate.Validate(msg)` 函数。
  - **gRPC集成**：可手动调用，或使用 `go-grpc-middleware/protovalidate` 包中的拦截器。
  - **当前状态**：**未来方向**。Buf 公司官方维护，性能好，不污染生成的代码。

**总结**：

- 老方案：在proto里写规则 → 生成 Validate() 方法 → 用 go-grpc-middleware 的拦截器自动调用。
- 新方案：在proto里写规则 → 直接调用 protovalidate.Validate() 或它的拦截器。

## 拦截器

既然上一节提到了拦截器，这一节就展开讲讲。拦截器其实就相当于其他地方的“中间件”（middleware）概念，用于在rpc调用前后执行特定操作。

客户端和服务端拦截器不同，一元和流式rpc的拦截器也不同，两两组合遍有四种拦截器：

```go
type UnaryClientInterceptor func(ctx context.Context, method string, req, reply any, cc *ClientConn, invoker UnaryInvoker, opts ...CallOption) error
type StreamClientInterceptor func(ctx context.Context, desc *StreamDesc, cc *ClientConn, method string, streamer Streamer, opts ...CallOption) (ClientStream, error)
type UnaryServerInterceptor func(ctx context.Context, req any, info *UnaryServerInfo, handler UnaryHandler) (resp any, err error)
type StreamServerInterceptor func(srv any, ss ServerStream, info *StreamServerInfo, handler StreamHandler) error
```

### 服务端一元rpc拦截器

我们先看看服务端一元rpc拦截器，使用示例同上节：

```go
// internal/server/book/server/server.go
func (s *BookServer) Run(ctx context.Context) error {
  // ...
  validator, err := protovalidate.New()
  if err != nil {
    return fmt.Errorf("failed to create validator: %w", err)
  }

  interceptor := func(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
    if err := validator.Validate(req.(proto.Message)); err != nil {
      return nil, status.Errorf(codes.InvalidArgument, "invalid request: %v", err)
    }
    return handler(ctx, req)
  }

  grpcServer := grpc.NewServer(grpc.UnaryInterceptor(interceptor))
  // ...
}
```

这里使用`grpc.UnaryInterceptor()`注册拦截器。需要注意的是该方法只能注册一个拦截器，所以如果有多个拦截器需要手动处理链式调用。不过grpc在`v1.28.0`中更新了`ChainUnaryInterceptor()`方法，可以直接链式注册多个拦截器，就不再需要手动处理了。两者的定义如下：

```go
func UnaryInterceptor(i UnaryServerInterceptor) ServerOption
func ChainUnaryInterceptor(interceptors ...UnaryServerInterceptor) ServerOption
```

拦截器全堆在server里太臃肿了，让我们更新项目结构，将拦截器统一放在统一目录下管理：

```bash
.\internal\server\common\/
└── interceptor/
    ├── initialize.go
    └── validator.go
```

除了手动定义拦截器，[go-grpc-middleware](https://github.com/grpc-ecosystem/go-grpc-middleware)中也提供了很多现成的拦截器可用。例如我们之前的验证拦截器就可以使用`protovalidate`这个子包：

```go
// internal/server/common/interceptor/initialize.go
package interceptor

func Initialize() error {
  if err := InitValidateInterceptor(); err != nil {
    return err
  }
  return nil
}

// internal/server/common/interceptor/validator.go
package interceptor

import (
  "buf.build/go/protovalidate"
  protovalidate_middleware "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/protovalidate"
  "google.golang.org/grpc"
)

var (
  validator protovalidate.Validator
)

func InitValidateInterceptor() error {
  var err error
  validator, err = protovalidate.New()
  if err != nil {
    return err
  }
  return nil
}

func ValidateUnaryInterceptor(opts ...protovalidate_middleware.Option) grpc.UnaryServerInterceptor {
  return protovalidate_middleware.UnaryServerInterceptor(validator, opts...)
}

func ValidateStreamInterceptor(opts ...protovalidate_middleware.Option) grpc.StreamServerInterceptor {
  return protovalidate_middleware.StreamServerInterceptor(validator, opts...)
}

// internal/server/book/server/server.go
func (s *BookServer) Run(ctx context.Context) error {
  // ...
  grpcServer := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
      interceptor.ValidateUnaryInterceptor(),
    ),
    grpc.ChainStreamInterceptor(
      interceptor.ValidateStreamInterceptor(),
    ),
  )
  // ...
}
```

### 客户端一元rpc拦截器

再是客户端一元rpc拦截器，例如超时控制就可以实现如下：

```go
func TimeoutInterceptor(timeout time.Duration) grpc.UnaryClientInterceptor {
  return func(ctx context.Context, method string, req, reply any, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
    timedCtx, cancel := context.WithTimeout(ctx, timeout)
    defer cancel()
    return invoker(timedCtx, method, req, reply, cc, opts...)
  }
}
```

`go-grpc-middleware`也封装好了超时控制和连接重试等客户端拦截器，我们可以直接集成到之前的客户端实现中：

```go
import(
  "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/retry"
  "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/timeout"
)

func NewClient(host string, port int) (*Client, error) {
  serverAddr := fmt.Sprintf("%s:%d", host, port)
  opts := []grpc.DialOption{
    grpc.WithTransportCredentials(insecure.NewCredentials()),
    // new
    grpc.WithChainUnaryInterceptor(
      timeout.UnaryClientInterceptor(5*time.Second),
      retry.UnaryClientInterceptor(
        retry.WithMax(3),
        retry.WithPerRetryTimeout(2*time.Second),
      ),
    ),
  }
  conn, err := grpc.NewClient(serverAddr, opts...)
  // ...
}
```

`go-grpc-middleware`中还有很多优秀的拦截器可用，感兴趣可以探索一下。

### 服务端流式rpc拦截器

### 客户端流式rpc拦截器
