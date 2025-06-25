---
title: go依赖注入库 samber/do 笔记
date: '2025-06-24T11:05:03+08:00'
tags:
- 笔记
- Go
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# do

@[TOC]

[samber/do](https://github.com/samber/do)

文档：[⚙️ do: Typesafe dependency injection for Go | do](https://do.samber.dev/)
参考：[源码分析——Go语言依赖注入库 samber/do - 飞鸟记](https://blog.aflybird.cn/2023/08/read-open-source-go-dependency-injection-library-samber-do)

do是一个依赖注入库。相比于用过的wire，do更加轻量且无需代码生成。

>**注意：** v2正在开发中，新版本可能有较大改动。

## 依赖注入定义

>狭义DI定义
>>对象的使用方式不应该依赖于对象的创建方式。
>
>所以我们要实现的，就是：
>
> - 提供一个「第三方」
> - 对象创建者，把特定类型的对象创建出来并注册到第三方
> - 对象使用者，从第三方获取对象

我的理解是，使用对象时不需要去关注对象如何创建，不需要自己创建对象，而是直接使用一个现成的对象。
如何将对象交给使用者，就是所谓的“注入”。
最简单的理解就是一个map，需要什么对象时查询map从里面拿。

## 快速使用

```go
func main() {
    // create DI container and inject package services
    injector := do.New()

    do.Provide(injector, NewCar)
    do.Provide(injector, NewEngine)
    do.ProvideValue(&Config{
        Port: 4242,
    })

    // invoking car will instantiate Car services and its Engine dependency
    car, err := do.Invoke[*Car](i)
    if err != nil {
        log.Fatal(err.Error())
    }

    car.Start()  // that's all folk 🤗

    // handle ctrl-c and shutdown services
    i.ShutdownOnSignals(syscall.SIGTERM, os.Interrupt)
}
```

1. 使用`do.New()`创建一个依赖注入容器（即一个`map[string]any`）
2. 使用`do.Provide()`注册服务（提供对象创建方式）
3. 使用`do.Invoke[Type](injector)`调用服务（获取对应类型的对象）
4. 使用对象

## 匿名服务与命名服务

do框架在进行服务注册时，都有提供`Provide`和`ProvideNamed`两种方法。

```go
func Provide[T any](i do.Injector, provider do.Provider[T])
func ProvideNamed[T any](i do.Injector, name string, provider do.Provider[T])
```

前者为匿名服务，由框架处理命名。后者为命名服务，用户自己提供命名作为`map[string]any`的key键。

顺便一提，匿名服务中框架生成服务名的方式就是直接打印变量类型：

```go
func generateServiceName[T any]() string {
    var t T

    // struct
    name := fmt.Sprintf("%T", t)
    if name != "<nil>" {
        return name
    }

    // interface
    return fmt.Sprintf("%T", new(T))
}
```

## 急加载和懒加载

**急加载(Eager Loading)** 是在注册服务时直接传入变量。
**懒加载（Lazy Loading）** 是传入创建变量的方式，等用到时再创建。

```go
// 急加载
func ProvideValue[T any](i do.Injector, value T)
func ProvideNamedValue[T any](i do.Injector, name string, value T)
// 懒加载
func Provide[T any](i do.Injector, provider do.Provider[T])
func ProvideNamed[T any](i do.Injector, name string, provider do.Provider[T])
```

要更深入理解两者的区别，我们需要了解服务的定义和两种服务注册方式的实现。如下是部分源码（已简化）:

```go
type Service[T any] interface {
    getName() string
    getInstance(*Injector) (T, error)
}
```

服务本身是一个接口，`getName`方法获取服务名，`getInstance`方法获取服务实例。无论是急加载还是懒加载，以及其他的瞬时加载和包加载等，只要实现了这个接口就行。

### 急加载

```go
type ServiceEager[T any] struct {
    name     string
    instance T
}

func newServiceEager[T any](name string, instance T) Service[T] {
    return &ServiceEager[T]{
        name:     name,
        instance: instance,
    }
}

//nolint:unused
func (s *ServiceEager[T]) getName() string {
    return s.name
}

//nolint:unused
func (s *ServiceEager[T]) getInstance(i *Injector) (T, error) {
    return s.instance, nil
}
```

急加载直接传入创建好的实例，调用时返回就行。

### 懒加载

```go
type Provider[T any] func(*Injector) (T, error)

type ServiceLazy[T any] struct {
    mu       sync.RWMutex
    name     string
    instance T

    // lazy loading
    built    bool
    provider Provider[T]
}

func newServiceLazy[T any](name string, provider Provider[T]) Service[T] {
    return &ServiceLazy[T]{
        name: name,

        built:    false,
        provider: provider,
    }
}

//nolint:unused
func (s *ServiceLazy[T]) getName() string {
    return s.name
}

//nolint:unused
func (s *ServiceLazy[T]) getInstance(i *Injector) (T, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    if !s.built {
        err := s.build(i)
        if err != nil {
            return empty[T](), err
        }
    }

    return s.instance, nil
}

//nolint:unused
func (s *ServiceLazy[T]) build(i *Injector) (err error) {
    instance, err := s.provider(i)
    if err != nil {
        return err
    }

    s.instance = instance
    s.built = true

    return nil
}
```

`Provider[T any]`类型为创建实例的方式。从懒加载服务中获取实例时先通过`built`标记判断实例是否已创建。
如果已创建，直接返回实例。如果未创建，使用传入的`provider`创建实例。创建过程通过并发变量`mu`保证并发安全。

## 服务调用

```go
do.Invoke[T any](do.Injector) (T, error)
do.InvokeNamed[T any](do.Injector, string) (T, error)
do.MustInvoke[T any](do.Injector) T
do.MustInvokeNamed[T any](do.Injector, string) T
```

使用`do.Invoke`调用匿名服务，`do.InvokeNamed`调用命名服务。
而`Must`版本是正常版本的封装，单返回值可以直接用于表达式中，报错时不返回错误而是直接panic。

## 其他

其他用法和特性因为没用过理解不深，为了避免抄文档就干脆不写了。
以后用上了再查文档记笔记吧。
