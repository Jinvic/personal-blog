---
title: go上下文库-context-笔记
date: '2025-07-07T11:48:51+08:00'
tags:
- Go
categories:
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# context

**参考**：

- [并发 | Golang 中文学习文档](https://golang.halfiisland.com/essential/senior/110.concurrency.html#context)
- [详解context包，看这一篇就够了 - Golang梦工厂 - 博客园](https://www.cnblogs.com/asong2020/articles/13662174.html)

上下文（context）是在go中是非常常见的概念之一，平时做api开发时也经常见到。但一直这么迷迷糊糊地用也不是办法，还是尝试了解一下。

上下文这个概念与并发有关。在go中，控制并发有channel，waitgroup，context，以及传统的锁控制等。其中channel用户协程间通信，waitgroup用于控制协程数量，而context的主要应用场景则为子孙协程层层嵌套。

阅读相关内容时，总有一种割裂感，好像讲的和我用的不太一样，实际上是因为go原生的context只是一个接口，而web框架通常对其做了封装实现（如gin.context）。使用成品库时常常有种知其然而不知所以然的感觉，所以还是了解一下原生的代码实现。

## Context

首先是Context本身的接口定义：

```go
type Context interface {

   Deadline() (deadline time.Time, ok bool)

   Done() <-chan struct{}

   Err() error

   Value(key any) any
}
```

- `Deadline()` 有两个返回值，前者为取消时间，后者为是否设置deadline。
- `Done()` 用于指示上下文是否取消。
- `Err()` 返回上下文关闭的原因，未关闭时返回nil。
- `Value()` 返回对应的键值，key不存在或不支持该方法时返回nil。

## emptyCtx

emptyCtx 就是空的上下文，可以通过 `context.Background()` 和 `context.TODO()` 来进行创建。

在创建上下文后，可以通过with系列方法创建子上下文。

```go
func WithCancel(parent Context) (ctx Context, cancel CancelFunc)
func WithDeadline(parent Context, deadline time.Time) (Context, CancelFunc)
func WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc)
func WithValue(parent Context, key, val interface{}) Context
```

如下是相关的源码实现：

```go
var (
  background = new(emptyCtx)
  todo       = new(emptyCtx)
)

func Background() Context {
  return background
}

func TODO() Context {
  return todo
}
```

`context.Background()` 和 `context.TODO()` 方法返回的值是一样的，只是在使用和语义上稍有不同。

- `context.Background()` 是上下文的默认值，所有其他的上下文都应该从它衍生（Derived）出来。
- `context.TODO()` 应该只在不确定应该使用哪种上下文时使用。

```go
type emptyCtx int

func (*emptyCtx) Deadline() (deadline time.Time, ok bool) {
   return
}

func (*emptyCtx) Done() <-chan struct{} {
   return nil
}

func (*emptyCtx) Err() error {
   return nil
}

func (*emptyCtx) Value(key any) any {
   return nil
}
```

`emptyCtx` 的底层类型使用int而非空结构体，是因为 `emptyCtx` 的实例必须要有不同的内存地址。

`emptyCtx` 没法被取消，没有 deadline，也不能取值，实现的方法都是返回零值。

## valueCtx

```go
type valueCtx struct {
   Context
   key, val any
}

func (c *valueCtx) Value(key any) any {
   if c.key == key {
      return c.val
   }
   return value(c.Context, key)
}
```

`valueCtx`类型只是添加了一个键值对，以及实现了`Value()`方法。并且对`Value()`方法的实现也很简单，当前找不到就去父上下文找。

以我个人常用的`gin.Context`来说，传值时基本不会用上这个Value方法，而是内部实现一个`map[any]any`，通过`Set()/Get()`方法操作，避免了不断衍生子上下文的层层嵌套。Value方法则主要用于兼容请求传来的`http.Request.Context()`。

## cancelCtx

`cancelCtx`实现了`canceler`接口，如下：

```go
type canceler interface {
    // removeFromParent 表示是否从父上下文中删除自身
    // err 表示取消的原因
  cancel(removeFromParent bool, err error)
    // Done 返回一个管道，用于通知取消的原因
  Done() <-chan struct{}
}
```

当调用`WithCancel()`创建`cancelCtx`时，首先通过`propagateCancel()`方法尝试将自身添加进父级的children中实现级联取消，然后闭包`cancel`方法作为返回值供外界调用。

```go
// A cancelCtx can be canceled. When canceled, it also cancels any children
// that implement canceler.
type cancelCtx struct {
    Context

    mu       sync.Mutex            // protects following fields
    done     atomic.Value          // of chan struct{}, created lazily, closed by first cancel call
    children map[canceler]struct{} // set to nil by the first cancel call
    err      error                 // set to non-nil by the first cancel call
    cause    error                 // set to non-nil by the first cancel call
}

func withCancel(parent Context) *cancelCtx {
    if parent == nil {
        panic("cannot create context from nil parent")
    }
    c := &cancelCtx{}
    // 尝试将自身添加进父级的children中
    c.propagateCancel(parent, c)
    return c
}

type CancelFunc func()

func WithCancel(parent Context) (ctx Context, cancel CancelFunc) {
    c := withCancel(parent)
    return c, func() { c.cancel(true, Canceled, nil) }
}
```

如下是`propagateCancel()`方法的具体实现，逻辑大致如下：

- 如果`parent.Done() == nil`，即父上下文不会取消时，直接返回。
- 如果父上下文已经取消时，取消子上下文并返回。
- 将子上下文加入父上下文的children列表；
- 新建协程监听父子上下文的取消信号：
  - 如果父上下文取消，取消子上下文；
  - 如果子上下文取消，退出协程。

```go
// propagateCancel arranges for child to be canceled when parent is.
// It sets the parent context of cancelCtx.
func (c *cancelCtx) propagateCancel(parent Context, child canceler) {
    c.Context = parent

    done := parent.Done()
    if done == nil {
        return // parent is never canceled
    }

    select {
    case <-done:
        // parent is already canceled
        child.cancel(false, parent.Err(), Cause(parent))
        return
    default:
    }

    if p, ok := parentCancelCtx(parent); ok {
        // parent is a *cancelCtx, or derives from one.
        p.mu.Lock()
        if p.err != nil {
            // parent has already been canceled
            child.cancel(false, p.err, p.cause)
        } else {
            if p.children == nil {
                p.children = make(map[canceler]struct{})
            }
            p.children[child] = struct{}{}
        }
        p.mu.Unlock()
        return
    }

    if a, ok := parent.(afterFuncer); ok {
        // parent implements an AfterFunc method.
        c.mu.Lock()
        stop := a.AfterFunc(func() {
            child.cancel(false, parent.Err(), Cause(parent))
        })
        c.Context = stopCtx{
            Context: parent,
            stop:    stop,
        }
        c.mu.Unlock()
        return
    }

    goroutines.Add(1)
    go func() {
        select {
        case <-parent.Done():
            child.cancel(false, parent.Err(), Cause(parent))
        case <-child.Done():
        }
    }()
}

```

最后是`cancelCtx`实现的`cancel()`方法，遍历子上下文逐个取消，然后将自己从父上下文的children中删除。

```go
// cancel closes c.done, cancels each of c's children, and, if
// removeFromParent is true, removes c from its parent's children.
// cancel sets c.cause to cause if this is the first time c is canceled.
func (c *cancelCtx) cancel(removeFromParent bool, err, cause error) {
    if err == nil {
        panic("context: internal error: missing cancel error")
    }
    if cause == nil {
        cause = err
    }
    c.mu.Lock()
    if c.err != nil {
        c.mu.Unlock()
        return // already canceled
    }
    c.err = err
    c.cause = cause
    d, _ := c.done.Load().(chan struct{})
    if d == nil {
        c.done.Store(closedchan)
    } else {
        close(d)
    }
    for child := range c.children {
        // NOTE: acquiring the child's lock while holding parent's lock.
        child.cancel(false, err, cause)
    }
    c.children = nil
    c.mu.Unlock()

    if removeFromParent {
        removeChild(c.Context, c)
    }
}
```

## timerCtx

`timerCtx` 是 `cancelCtx` 的封装，增加了超时机制，可以通过`WithDeadline()`和`WithTimeout()`创建。前者指定具体时间，何时超时；后者指定时间间隔，过多久超时。此外，后者也是前者的封装。

```go
// A timerCtx carries a timer and a deadline. It embeds a cancelCtx to
// implement Done and Err. It implements cancel by stopping its timer then
// delegating to cancelCtx.cancel.
type timerCtx struct {
    cancelCtx
    timer *time.Timer // Under cancelCtx.mu.

    deadline time.Time
}

func WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc) {
    return WithDeadline(parent, time.Now().Add(timeout))
}
```

让我们将重点放到`WithDeadline()`上，逻辑大致如下：

- 如果子上下文的到期时间晚于父上下文的到期时间，将直接继承父上下文。
- 如果已经到期，直接取消子上下文并返回。
- 通过`time.AfterFunc()`设置定时器，到期时取消子上下文。

```go
func WithDeadline(parent Context, d time.Time) (Context, CancelFunc) {
    return WithDeadlineCause(parent, d, nil)
}

func WithDeadlineCause(parent Context, d time.Time, cause error) (Context, CancelFunc) {
    if parent == nil {
        panic("cannot create context from nil parent")
    }
    if cur, ok := parent.Deadline(); ok && cur.Before(d) {
        // The current deadline is already sooner than the new one.
        return WithCancel(parent)
    }
    c := &timerCtx{
        deadline: d,
    }
    c.cancelCtx.propagateCancel(parent, c)
    dur := time.Until(d)
    if dur <= 0 {
        c.cancel(true, DeadlineExceeded, cause) // deadline has already passed
        return c, func() { c.cancel(false, Canceled, nil) }
    }
    c.mu.Lock()
    defer c.mu.Unlock()
    if c.err == nil {
        c.timer = time.AfterFunc(dur, func() {
            c.cancel(true, DeadlineExceeded, cause)
        })
    }
    return c, func() { c.cancel(true, Canceled, nil) }
}
```
