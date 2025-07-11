---
title: go消息队列库 RabbitMQ 笔记
date: '2025-06-11T10:52:43+08:00'
tags:
- Go
categories:
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---
# go消息队列库 RabbitMQ 笔记

`github.com/rabbitmq/amqp091-go`

参考：

- [go库文档](https://pkg.go.dev/github.com/rabbitmq/amqp091-go)
- [AMQP 0-9-1 模型详解](https://rabbitmq.cn/tutorials/amqp-concepts)
- [中文文档](https://www.rabbitmq.cn/tutorials/tutorial-one-go)
- [英文文档](https://rabbitmq.com/tutorials/tutorial-four-go)

---

[TOC]

---

`amqp091-go` 是RabiitMQ提供的官方go库。

## 基本概念

- **连接（Connection）**：客户端与 RabbitMQ 节点之间的 TCP 连接。
- **通道（Channel）**：在连接之上建立的轻量级通信路径，用于发送和接收消息。
- **队列（Queue）**：存储消息的实际容器。
- **交换机（Exchange）**：负责接收生产者发布的消息，并根据一定的规则将消息路由到一个或多个队列。
- **发布者（Publisher）**：向交换机发送消息的应用程序。
- **消费者（Consumer）**：从队列中接收消息并进行处理的应用程序。

```mermaid
---
config:
  layout: dagre
---
flowchart LR
    Client["Client"] -- Dail --> Connection["Connection"]
    Connection -- TCPConnection --> Server["Server"]
    Conn["Connection"] --> Ch1["Channel1"] & Ch2["Channel2"]
    Ch1 -- PublishMessage --> Publisher["Publisher"]
    Ch2 -- ConsumeMessages --> Consumer["Consumer"]
    P["Publisher"] -- publish --> E["Exchange"]
    E -- Binding --> Q["Quene"]
    C["Consumer"] -- Listening --> Q
    Q -- Consume --> C

```

## 连接

### 建立连接

直接使用`Dial()`方法建立连接。

```go
func Dial(url string) (*Connection, error)

// e.g.
conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
defer conn.Close()
```

## 通道

通道可以被认为是共享单个tcp连接的轻量级连接。

对于多线程/进程任务，应该为每个单独打开通道，而不是共享一个通道。

### 打开通道

```go
func (c *Connection) Channel() (*Channel, error)

//e.g.
ch, err := conn.Channel()
defer ch.Close()
```

## 队列

RabbitMQ 中的队列是消息的有序集合。消息以 FIFO（先进先出）方式入队和出队（传递给消费者）。

### 声明队列

```go
func (ch *Channel) QueueDeclare(name string, durable, autoDelete, exclusive, noWait bool, args Table) (Queue, error)

// e.g.
q, err := ch.QueueDeclare(
  "hello", // name
  false,   // durable
  false,   // delete when unused
  false,   // exclusive
  false,   // no-wait
  nil,     // arguments
)
```

声明队列是**幂等**的 - 仅当队列尚不存在时才会创建。

RabbitMQ **不允许使用不同的参数重新定义现有队列**，并且会向尝试这样做的任何程序返回错误。

### 临时队列

声明队列时，如果使用空串作为队列名称，返回的示例将使用随机队列名称，如`amq.gen-JzTY20BRgKO-HjmUJj0wLg`。

```go
// e.g.
q, err := ch.QueueDeclare(
  "",    // name
  false, // durable
  false, // delete when unused
  true,  // exclusive
  false, // no-wait
  nil,   // arguments
)
```

### 分发策略

可以使用`Qos()`方法手动控制队列负载。

```go
func (ch *Channel) Qos(prefetchCount, prefetchSize int, global bool) error

// e.g.
err = ch.Qos(
  1,     // prefetch count
  0,     // prefetch size
  false, // global
)
```

- `prefetchCount`: 每个消费者最多能从队列中预先获取并缓存的消息数量。
    当预取计数大于零时，服务器将在接收到确认之前将那么多条消息交付给消费者。
    当消费者以 noAck 方式启动时，服务器会忽略此选项，因为不期望或发送确认。
- `prefetchSize`: 表示允许预取的最大字节数。
    如果设置为 0，则表示没有基于消息大小的限制。
    在大多数情况下，这个值通常被设为 0。
- `global`: 决定了 prefetchCount 是应用于单个消费者还是整个通道上的所有消费者。
    当全局为 true 时，这些 Qos 设置适用于**同一连接**上所有现有和未来的消费者。
    当为 false 时，Channel.Qos 设置将适用于**此通道**上所有现有和未来的消费者。

## 交换机

交换机是发布者发布消息的实体，目的是将流经它们的所有消息路由到一个或多个队列、流 或其他交换器。

生产者并不会直接向队列发送消息，而是将消息发送到交换机，由交换机决定发送消息到何处。

### 声明交换机

```go
func (ch *Channel) ExchangeDeclare(name, kind string, durable, autoDelete, internal, noWait bool, args Table) error

// e.g.
err = ch.ExchangeDeclare(
  "logs",   // name
  "fanout", // type
  true,     // durable
  false,    // auto-deleted
  false,    // internal
  false,    // no-wait
  nil,      // arguments
)
```

### 默认交换机

默认交换机始终存在，无需主动声明。

当未显示指定交换机名称时，将使用默认交换机，消息被路由到由 routing_key 参数指定的名称的队列（如果存在）。

```go
err = ch.PublishWithContext(ctx,
  "",     // exchange
  q.Name, // routing key
  false,  // mandatory
  false,  // immediate
  amqp.Publishing{
    ContentType: "text/plain",
    Body:        []byte(body),
})
```

### 交换机类型

#### fanout

扇出交换机将消息路由到绑定到它的所有队列，并且忽略路由键。

扇出交换机非常适合消息的广播路由。

![fanout exchange](https://rabbitmq.cn/assets/images/exchange-fanout-7155e1fd567292ac471a6b60711c4fc4.png)

#### direct

直连交换机根据消息路由键将消息传递到队列。

直接交换机非常适合消息的单播路由。它们也可以用于多播路由。

![direct exchange](https://rabbitmq.cn/assets/images/exchange-direct-a7628306f367d189dac98aabc4865085.png)

#### topic

主题交换机根据消息路由键与用于将队列绑定到交换机的模式之间的匹配，将消息路由到一个或多个队列。

主题交换机类型通常用于实现各种发布/订阅模式变体。主题交换机通常用于消息的多播路由。

主题交换机的路由键为单词列表，用点分隔。路由键中可以包含任意数量的单词，最多 255 字节的限制。

主题交换机的路由键有两个通配符:

- `*` (星号) 可以替代正好一个单词。
- `#` (井号) 可以替代零个或多个单词。

### 绑定队列

可以使用`QueueBind()`方法将一个交换器绑定到队列。当发布消息的路由键与绑定路由键匹配时，发布到交换器的消息将被路由到该队列。

绑定操作也是幂等的，相同键和参数的重复绑定会被忽略。

```go
func (ch *Channel) QueueBind(name, key, exchange string, noWait bool, args Table) error

// e.g.
err = ch.QueueBind(
  q.Name, // queue name
  "",     // routing key
  "logs", // exchange
  false,
  nil,
)
```

## 发布者

### 发布消息

可以使用`Publish()`系列方法发布消息：

```go
func (ch *Channel) Publish(exchange, key string, mandatory, immediate bool, msg Publishing) error
func (ch *Channel) PublishWithContext(_ context.Context, exchange, key string, mandatory, immediate bool, msg Publishing) error
func (ch *Channel) PublishWithDeferredConfirm(exchange, key string, mandatory, immediate bool, msg Publishing) (*DeferredConfirmation, error)
func (ch *Channel) PublishWithDeferredConfirmWithContext(_ context.Context, exchange, key string, mandatory, immediate bool, msg Publishing) (*DeferredConfirmation, error)

// e.g.
  err = c.ExchangeDeclare("logs", "topic", true, false, false, false, nil)
  if err != nil {
    log.Fatalf("exchange.declare: %v", err)
  }

  msg := amqp.Publishing{
    DeliveryMode: amqp.Persistent,
    Timestamp:    time.Now(),
    ContentType:  "text/plain",
    Body:         []byte("Go Go AMQP!"),
  }

  ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
  defer cancel()

  err = c.PublishWithContext(ctx, "logs", "info", false, false, msg)
  if err != nil {
    log.Fatalf("basic.publish: %v", err)
  }
```

### 远程过程调用 (RPC)

可以在发布时添加reply_to和correlation_id，实现RPC功能，流程如下：

- 当客户端启动时，它会创建一个独占的回调队列。
- 对于 RPC 请求，客户端发送一条消息，其中包含两个属性：reply_to，设置为回调队列，以及 correlation_id，为每个请求设置为唯一值。
- 请求被发送到 rpc_queue 队列。
- RPC 工作进程（即服务器）正在该队列上等待请求。当出现请求时，它会完成工作并将包含结果的消息发送回客户端，使用来自 reply_to 字段的队列。
- 客户端在回调队列上等待数据。当出现消息时，它会检查 correlation_id 属性。如果它与请求中的值匹配，则将响应返回给应用程序。

服务端示例：

```go
//e.g.

q, err := ch.QueueDeclare(
  "rpc_queue", // name
  false,       // durable
  false,       // delete when unused
  false,       // exclusive
  false,       // no-wait
  nil,         // arguments
)

err = ch.Qos(
  1,     // prefetch count
  0,     // prefetch size
  false, // global
)
failOnError(err, "Failed to set QoS")

msgs, err := ch.Consume(
  q.Name, // queue
  "",     // consumer
  false,  // auto-ack
  false,  // exclusive
  false,  // no-local
  false,  // no-wait
  nil,    // args
)

go func() {
  ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
  defer cancel()
  for d := range msgs {
    n, err := strconv.Atoi(string(d.Body))
    failOnError(err, "Failed to convert body to integer")

    log.Printf(" [.] fib(%d)", n)
    response := fib(n)

    err = ch.PublishWithContext(ctx,
      "",        // exchange
      d.ReplyTo, // routing key
      false,     // mandatory
      false,     // immediate
      amqp.Publishing{
        ContentType:   "text/plain",
        CorrelationId: d.CorrelationId,
        Body:          []byte(strconv.Itoa(response)),
      })
    failOnError(err, "Failed to publish a message")

    d.Ack(false)
  }
}()

```

客户端示例：

```go
q, err := ch.QueueDeclare(
  "",    // name
  false, // durable
  false, // delete when unused
  true,  // exclusive
  false, // noWait
  nil,   // arguments
)
failOnError(err, "Failed to declare a queue")

msgs, err := ch.Consume(
  q.Name, // queue
  "",     // consumer
  true,   // auto-ack
  false,  // exclusive
  false,  // no-local
  false,  // no-wait
  nil,    // args
)
failOnError(err, "Failed to register a consumer")

corrId := randomString(32)

ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

err = ch.PublishWithContext(ctx,
  "",          // exchange
  "rpc_queue", // routing key
  false,       // mandatory
  false,       // immediate
  amqp.Publishing{
    ContentType:   "text/plain",
    CorrelationId: corrId,
    ReplyTo:       q.Name,
    Body:          []byte(strconv.Itoa(n)),
  })
failOnError(err, "Failed to publish a message")

for d := range msgs {
  if corrId == d.CorrelationId {
    res, err = strconv.Atoi(string(d.Body))
    failOnError(err, "Failed to convert body to integer")
    break
  }
}
```

## 消费者

### 消费消息

如果使用非扇出/默认交换机，需要先声明交换机并建立绑定，再消费消息。

```go
func (ch *Channel) Consume(queue, consumer string, autoAck, exclusive, noLocal, noWait bool, args Table) (<-chan Delivery, error)
func (ch *Channel) ConsumeWithContext(ctx context.Context, queue, consumer string, autoAck, exclusive, noLocal, noWait bool, args Table) (<-chan Delivery, error)

// e.g.

err = c.ExchangeDeclare("logs", "topic", true, false, false, false, nil)
if err != nil {
  log.Fatalf("exchange.declare: %s", err)
}

type bind struct {
  queue string
  key   string
}

bindings := []bind{
  {"page", "alert"},
  {"email", "info"},
}

for _, b := range bindings {
  _, err = c.QueueDeclare(b.queue, true, false, false, false, nil)
  if err != nil {
    log.Fatalf("queue.declare: %v", err)
  }

  err = c.QueueBind(b.queue, b.key, "logs", false, nil)
  if err != nil {
    log.Fatalf("queue.bind: %v", err)
  }
}

// Set our quality of service.  Since we're sharing 2 consumers on the same
// channel, we want at least 2 messages in flight.
err = c.Qos(2, 0, false)
if err != nil {
  log.Fatalf("basic.qos: %v", err)
}

pages, err := c.Consume("page", "pager", false, false, false, false, nil)
if err != nil {
  log.Fatalf("basic.consume: %v", err)
}

go func() {
  for page := range pages {
    // ... this consumer is responsible for sending pages per log
    if e := page.Ack(false); e != nil {
      log.Printf("ack error: %+v", e)
    }
  }
}()

emails, err := c.Consume("email", "", false, false, false, false, nil)
if err != nil {
  log.Fatalf("basic.consume: %v", err)
}

go func() {
  for email := range emails {
    // ... this consumer is responsible for sending emails per log
    if e := email.Ack(false); e != nil {
      log.Printf("ack error: %+v", e)
    }
  }
}()

// Wait until you're ready to finish, could be a signal handler here.
time.Sleep(10 * time.Second)

// Cancelling a consumer by name will finish the range and gracefully end the
// goroutine
err = c.Cancel("pager", false)
if err != nil {
  log.Fatalf("basic.cancel: %v", err)
}
```

### 消息确认

消费者收到消息后需要发送一个ack确认消息，表示消息成功交付。为被确认的消息将被重新排队消费。

当`Consume()`方法中的`autoAck`参数设置为`true`时，消息将在接收时自动确认；设置为`false`时，需要通过`Delivery.Ack()`手动确认。

## 消息持久化

### 持久化交换机

可以通过将`ExchangeDeclare()`方法中的`durable`参数设置为`true`来持久化交换机。

持久交换机在服务重启后仍然存在。

### 持久化队列

可以通过将`QueueDeclare()`方法中的`durable`参数设置为`true`来持久化队列。

持久队列只能绑定持久交换机，否则持久化不生效。

持久队列在服务重启后仍然存在。

### 持久化消息

可以将`amqp.Publishing`的`DeliveryMode`设置为`amqp.Persistent`来持久化消息。

持久消息需要发送到持久队列，否则持久化不生效。

持久交换机在服务重启后仍然存在。
