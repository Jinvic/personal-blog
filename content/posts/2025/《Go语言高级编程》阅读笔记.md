---
title: 《Go语言高级编程》阅读笔记
date: '2025-07-26T09:33:11+08:00'
tags: 
- Go
categories: 
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 《Go语言高级编程》阅读笔记

一直以来看书学习什么的都是选择的入门书籍，一边复习基础知识一边了解细节，只有最后的几章会比较深入。感觉比起这种查漏补缺式的基础学习，我现在想要进一步提升的话更需要了解一些深入的知识，所以选择了本书。当然，也没要从头到尾完整啃一遍，毕竟很多东西学了暂时用不上没有实践巩固相当于白学。所以只读用得上和感兴趣的章节。

## 1. 语言基础

### 1.1 GO语言创世纪

go语言发展历程的历史介绍。主要介绍Go的并发特性是如何演变的。

### 1.2 Hello, World 的革命

带着代码进一步介绍各语言的演变。最后重点介绍Go语言的演变。

说实话，C和Go以外的语言都看不懂，但也不需要看懂，了解一下就行。

### 1.3 数组、字符串和切片

在Go中，数组、字符串和切片的底层内存结构是一致的，但上层具体实现各不相同，本章则深入底层进行详细讲解。

#### 1.3.1 数组

数组的长度是数组类型的组成部分。所以**不同长度**或不同类型的数据组成的数组都是不同的类型，无法直接赋值。所以Go中很少直接使用数组，而是更为灵活的切片。不过了解数组有助于我们进一步理解切片。

```go
var a [3]int                    // 定义长度为 3 的 int 型数组, 元素全部为 0
var b = [...]int{1, 2, 3}       // 定义长度为 3 的 int 型数组, 元素为 1, 2, 3
var c = [...]int{2: 3, 1: 2}    // 定义长度为 3 的 int 型数组, 元素为 0, 2, 3
var d = [...]int{1, 2, 4: 5, 6} // 定义长度为 6 的 int 型数组, 元素为 1, 2, 0, 0, 5, 6
```

如上是数组可选的定义方式，如下对各种方式进行解释。

1. 指定长度并将每个元素初始化为零值。
2. 定义时初始化全部元素，长度自动计算。
3. 按索引初始化指定元素，为指定元素初始化为零值，长度取决于最大索引。
4. 结合23，按索引从不同位置开始顺序初始化若干个元素。

>Go 语言中数组是**值语义**。一个数组变量即表示整个数组，它并**不是隐式的指向第一个元素的指针**（比如 C 语言的数组），而是一个完整的值。

这里提到可以使用空数组避免占用内存空间，例如`[0]int`。不过更常见的做法还是使用`struct{}{}`。

#### 1.3.2 字符串

一个字符串是一个**不可改变**的字节序列，通常是用来包含人类可读的文本数据。和数组不同的是，字符串的元素不可修改，是一个只读的字节数组。

Go 语言字符串的底层结构在 `reflect.StringHeader` 中定义：

```go
type StringHeader struct {
    Data uintptr
    Len  int
}
```

字符串结构由两个信息组成：第一个是字符串指向的底层字节数组，第二个是字符串的字节的长度。字符串其实是一个结构体，因此字符串的赋值操作也就是 `reflect.StringHeader` 结构体的复制过程，并不会涉及底层字节数组的复制。

Go 语言对字符串和 `[]rune` 类型的相互转换提供了特殊的支持。`rune` 用于表示每个 `Unicode` 码点 只是 `int32` 类型的别名，并不是重新定义的类型。

最后提供了 `string`, `[]byte`, `[]rune` 各种类型的模拟转换方式，想深入底层进一步了解可以看看。

#### 1.3.3 切片(slice)

我们先看看切片的结构定义，`reflect.SliceHeader`：

```go
type SliceHeader struct {
    Data uintptr
    Len  int
    Cap  int
}
```

相比数组，切片多了一个 Cap 成员表示切片指向的内存空间的最大容量（对应元素的个数，而不是字节数）。

和数组的最大不同是，切片的类型和长度信息无关，只要是相同类型元素构成的切片均对应相同的切片类型。

**添加切片元素**：

内置的泛型函数 append 可以在切片的尾部追加 N 个元素。

在容量不足的情况下，append 的操作会导致重新分配内存，可能导致巨大的内存分配和复制数据代价。即使容量足够，依然需要用 append 函数的返回值来更新切片本身，因为新切片的长度已经发生了变化。

除了在切片的尾部追加，我们还可以在切片的开头添加元素，但一般都会导致内存的重新分配，而且会导致已有的元素全部复制 1 次，所以性能会差很多。

可以用 `copy` 和 `append` 组合可以避免创建中间的临时切片：

```go
// 添加到末尾
a = append(a, 0)     // 切片扩展 1 个空间
copy(a[i+1:], a[i:]) // a[i:] 向后移动 1 个位置
a[i] = x             // 设置新添加的元素

// 添加到中间
a = append(a, x...)       // 为 x 切片扩展足够的空间
copy(a[i+len(x):], a[i:]) // a[i:] 向后移动 len(x) 个位置
copy(a[i:], x)            // 复制新添加的切片
```

**删除切片元素**：

删除操作也可以用 `copy` 或者 `append` 避免移动数据指针。如果有C语言基础的话比较容易理解，和C的数组操作类似。

```go
// 从尾部删除
a = []int{1, 2, 3}
a = a[:len(a)-1]   // 删除尾部 1 个元素
a = a[:len(a)-N]   // 删除尾部 N 个元素

// 从头部删除
a = []int{1, 2, 3}
a = a[1:] // 删除开头 1 个元素
a = a[N:] // 删除开头 N 个元素

a = append(a[:0], a[1:]...) // 删除开头 1 个元素
a = append(a[:0], a[N:]...) // 删除开头 N 个元素

a = a[:copy(a, a[1:])] // 删除开头 1 个元素
a = a[:copy(a, a[N:])] // 删除开头 N 个元素

// 从中间删除
a = []int{1, 2, 3, ...}

a = append(a[:i], a[i+1:]...) // 删除中间 1 个元素
a = append(a[:i], a[i+N:]...) // 删除中间 N 个元素

a = a[:i+copy(a[i:], a[i+1:])]  // 删除中间 1 个元素
a = a[:i+copy(a[i:], a[i+N:])]  // 删除中间 N 个元素
```

**切片内存技巧**：

在判断一个切片是否为空时，一般通过 len 获取切片的长度来判断，而不是直接和nil比较。

在原切片上声明0长切片可以直接服用原切片的内存和容量，减少内存分配，提高性能。

```go
// e.g. 根据条件过滤
func Filter(s []byte, fn func(x byte) bool) []byte {
    b := s[:0]
    for _, x := range s {
        if !fn(x) {
            b = append(b, x)
        }
    }
    return b
}
```

**避免切片内存泄漏**：

这里给出了两个例子，一个是切片引用了原始数组导致GC无法回收，解决方法是复制数据到新切片返回：

```go
// 错误：直接返回引用了文件的切片
func FindPhoneNumber(filename string) []byte {
    b, _ := ioutil.ReadFile(filename)
    return regexp.MustCompile("[0-9]+").Find(b)
}

// 正确：复制到新切片
func FindPhoneNumber(filename string) []byte {
    b, _ := ioutil.ReadFile(filename)
    b = regexp.MustCompile("[0-9]+").Find(b)
    return append([]byte{}, b...)
}
```

另一个例子是对于指针切片，删除一个元素后被删除的元素依然被切片引用，其内存不会被GC回收：

```go
// 错误
var a []*int{ ... }
a = a[:len(a)-1]    // 被删除的最后一个元素依然被引用, 可能导致 GC 操作被阻碍

// 正确
var a []*int{ ... }
a[len(a)-1] = nil // GC 回收最后一个元素内存
a = a[:len(a)-1]  // 从切片删除最后一个元素

```

如果切片生命周期很短，不用刻意处理这个问题。GC回收切片时会回收所有元素。

**切片类型强制转换**:

为了安全，当两个切片类型 []T 和 []Y 的底层原始切片类型不同时，Go 语言是无法直接转换类型的。不过也可以通过`unsafe`和`reflect`等包进行更底层的操作，这时的语法就更像C了。

示例略，有需要再看。需要一定的前置知识，而`reflect`和`unsafe`包我都只有简单了解，平时基本用不上。

### 1.4 函数、方法和接口

**init初始化顺序**：

- 不同包：按导入顺序
- 同一包不同文件：顺序不确定
- 同一文件：按出现顺序

[包初始化流程](https://chai2010.cn/advanced-go-programming-book/images/ch1-11-init.ditaa.png)

#### 1.4.1 函数

在 Go 语言中，函数是一类对象，可以保存变量中。函数主要有具名和匿名之分。

Go 语言中的函数可以有多个参数和多个返回值，还支持可变数量的参数，相当于切片类型。

---

当匿名函数捕获了外部外部作用域的局部变量时，我们称其为**闭包**。

闭包对捕获的外部变量并不是传值方式访问，而是以**引用**的方式访问,使得这些变量的生命周期可以超出它们所在的作用域，只要还有引用它们的闭包存在。

闭包的这种引用方式访问外部变量的行为可能会导致一些隐含的问题:

```go
func main() {
    for i := 0; i < 3; i++ {
        defer func(){ println(i) } ()
    }
}
// Output:
// 3
// 3
// 3
```

修复的思路是在每轮迭代中为每个 defer 函数生成独有的变量。可以复制一份或者通过参数传入。

```go
func main() {
    for i := 0; i < 3; i++ {
        i := i // 定义一个循环体内局部变量 i
        defer func(){ println(i) } ()
    }
}

func main() {
    for i := 0; i < 3; i++ {
        // 通过函数传入 i
        // defer 语句会马上对调用参数求值
        defer func(i int){ println(i) } (i)
    }
}
```

---

Go 语言中，以切片为参数调用函数时，有时看起来像是传引用而非传值。虽然切片的底层数组确实是通过隐式指针传递(指针传值，但指向同一份数据)，但切片结构体中还包括len和cap信息是传值的，发生变动时不能反映到原切片。所以一般会通过返回修改后的切片来更新原切片，例如内置函数`append()`。

#### 1.4.2 方法

方法一般是面向对象编程(OOP)的一个特性，在 C++ 语言中方法对应一个类对象的成员函数，是关联到具体对象上的虚表中的。但是 Go 语言的方法却是关联到类型的，这样可以在编译阶段完成方法的静态绑定。

Go 语言中，通过在结构体内置匿名的成员来实现继承。通过嵌入匿名的成员，可以继承其内部成员及匿名成员类型所对应的方法。

```go
type Cache struct {
    m map[string]string
    sync.Mutex
}

func (p *Cache) Lookup(key string) string {
    p.Lock()            // 编译时展开为p.Mutex.Lock()
    defer p.Unlock()    // 同上

    return p.m[key]
}
```

这种方式继承的方法是编译时静态绑定的，并不能实现 C++ 中虚函数的多态特性。所有继承来的方法的接收者参数依然是那个匿名成员本身，而不是当前的变量。如果需要虚函数的多态特性，需要借助 Go 语言接口来实现。

#### 1.4.3 接口

接口这一节讲的比较玄乎，个人理解是只要类型实现了接口定义的方法声明，就算实现了这个接口，不需要显示声明。当然，要真正理解还是需要多加练习。

Go 语言对基础类型的类型一致性要求非常严格，但对于接口类型的转换则非常的灵活。对象和接口之间的转换、接口和接口之间的转换都可能是隐式的转换。

```go
var (
    a io.ReadCloser = (*os.File)(f) // 隐式转换, *os.File 满足 io.ReadCloser 接口
    b io.Reader     = a             // 隐式转换, io.ReadCloser 满足 io.Reader 接口
    c io.Closer     = a             // 隐式转换, io.ReadCloser 满足 io.Closer 接口
    d io.Reader     = c.(io.Reader) // 显式转换, io.Closer 不满足 io.Reader 接口
)
```

有时候对象和接口之间太灵活了，导致我们需要人为地限制这种无意之间的适配。常见的做法是定义一个含特殊方法来区分接口。

```go
type runtime.Error interface {
    error

    // RuntimeError is a no-op function but
    // serves to distinguish types that are run time
    // errors from ordinary errors: a type is a
    // run time error if it has a RuntimeError method.
    RuntimeError()
}

type proto.Message interface {
    Reset()
    String() string
    ProtoMessage()
}
```

不过这种限制也可以被手动实现对应方法或者嵌入匿名的原接口来绕过。

这种通过嵌入匿名接口或嵌入匿名指针对象来实现继承的做法其实是一种纯**虚继承**，我们继承的只是接口指定的规范，真正的实现在运行的时候才被注入。

### 1.5 面向并发的内存模型

#### 1.5.1 Goroutine和系统线程

Goroutine 是 Go 语言特有的并发体，是一种轻量级的线程，由 go 关键字启动。goroutine 和系统线程并不等价，前者开销更小。

系统级线程的栈大小固定（一般默认可能是 2MB），用来保存函数递归调用时参数和局部变量。固定了栈的大小导致了两个问题：

- 对于很多只需要很小的栈空间的线程：
    问题：浪费空间
    解决：降低固定的栈大小，提升空间的利用率
- 对于少数需要巨大栈空间的线程：
    问题：存在栈溢出风险
    解决：增大栈的大小以允许更深的函数递归调用

很明显，两者是无法兼得的。

Goroutine 的栈大小是动态变化的，启动时很小（可能是2KB 或 4KB）当遇到深度递归导致当前栈空间不足时，Goroutine 会根据需要动态地伸缩栈的大小。也因为启动的代价很小，可以轻易启动大量 Goroutine。

关于go的调度器，这里简单提了一下，有机会我再深入了解。

#### 1.5.2 原子操作

所谓的原子操作就是并发编程中“最小的且不可并行化”的操作。数据库四原则ACID中的A就是指的原子性（atomic）。

对粗粒度下的原子操作可以使用`sync.Mutex`的互斥锁保证并发安全。不过`sync.Mutex`常用于整个代码块的复杂逻辑。对于单个数值的原子操作，可以使用性能更高的`sync/atomic`包。

```go
import (
    "sync"
    "sync/atomic"
)

var total uint64

func worker(wg *sync.WaitGroup) {
    defer wg.Done()

    var i uint64
    for i = 0; i <= 100; i++ {
        atomic.AddUint64(&total, i)
    }
}

func main() {
    var wg sync.WaitGroup
    wg.Add(2)

    go worker(&wg)
    go worker(&wg)
    wg.Wait()
}
```

也可以组合原子操作和互斥锁实现高效的单件模式，通过原子检测标志位状态降低互斥锁的使用次数来提高性能。例如标准库的`sync.Once`实现：

```go
type Once struct {
    m    Mutex
    done uint32
}

func (o *Once) Do(f func()) {
    if atomic.LoadUint32(&o.done) == 1 {
        return
    }

    o.m.Lock()
    defer o.m.Unlock()

    if o.done == 0 {
        defer atomic.StoreUint32(&o.done, 1)
        f()
    }
}
```

使用例：

```go
var (
    instance *singleton
    once     sync.Once
)

func Instance() *singleton {
    once.Do(func() {
        instance = &singleton{}
    })
    return instance
}
```

对于复杂对象的原子操作，可以使用`sync/atomic`的`Load`和`Store`方法，其参数和返回值都是`interface{}`。

一个简化的生产者消费者模型使用例：

```go
var config atomic.Value // 保存当前配置信息

// 初始化配置信息
config.Store(loadConfig())

// 启动一个后台线程, 加载更新后的配置信息
go func() {
    for {
        time.Sleep(time.Second)
        config.Store(loadConfig())
    }
}()

// 用于处理请求的工作者线程始终采用最新的配置信息
for i := 0; i < 10; i++ {
    go func() {
        for r := range requests() {
            c := config.Load()
            // ...
        }
    }()
}
```

#### 1.5.3 顺序一致性内存模型

大意就是不同Goroutine之间的执行顺序不确定，有需要时需要使用同步原语明确排序。

#### 1.5.4 初始化顺序

在 [函数](#141-函数) 章节已经介绍过初始化顺序。在 `main.main` 函数执行之前所有代码都运行在同一个 `Goroutine` 中，即运行在程序的主系统线程中。所以所有的 `init` 函数和 `main` 函数都是在主线程完成，它们也是满足顺序一致性模型的。但是 `init` 函数中开启的新 `goroutine` 就并非如此了。

#### 1.5.5 Goroutine的创建

`go` 语句会在当前 Goroutine 对应函数返回前创建新的 Goroutine。但是新创建 Goroutine 对应的 `f()` 的执行事件和 原 Goroutine 返回的事件则是不可排序的，也就是并发的。

#### 1.5.6 基于 Channel 的通信

基本就是一些 Channel 基础用法。

- **对于从无缓冲 Channel 进行的接收，发生在对该 Channel 进行的发送完成之前。**
- **对于 Channel 的第 K 个接收完成操作发生在第 K+C 个发送操作完成之前，其中 C 是 Channel 的缓存大小。**

可以通过控制 Channel 的缓存大小来控制并发执行的 Goroutine 的最大数目。

#### 1.5.7 不靠谱的同步

```go
func main() {
    go println("hello, world")
    time.Sleep(time.Second)
}
```

如上，有时我们会简单通过休眠来保证执行顺序，但这种做法并不严谨。最好使用显式的同步操作。

### 1.6 常见的并发模式

Go 语言的并发编程哲学：

> Do not communicate by sharing memory; instead, share memory by communicating.
> 不要通过共享内存来通信，而应通过通信来共享内存。

#### 1.6.1 并发版本的 Hello world

从`sync.Mutex`到 Channel 缓冲区大小等方面，由浅入深介绍并发条件下如何控制执行顺序，最后引出`sync.WaitGroup`的大致原理和用法。

```go
func main() {
    done := make(chan int, 10) // 带 10 个缓存

    // 开 N 个后台打印线程
    for i := 0; i < cap(done); i++ {
        go func(){
            fmt.Println("你好, 世界")
            done <- 1
        }()
    }

    // 等待 N 个后台线程完成
    for i := 0; i < cap(done); i++ {
        <-done
    }
}
```

如上只是方便理解，实际`sync.WaitGroup`维护的是一个计数器而非通道。不过用法是一致的。

```go
func main() {
    var wg sync.WaitGroup

    // 开 N 个后台打印线程
    for i := 0; i < 10; i++ {
        wg.Add(1)

        go func() {
            fmt.Println("你好, 世界")
            wg.Done()
        }()
    }

    // 等待 N 个后台线程完成
    wg.Wait()
}
```

#### 1.6.2 生产者消费者模型

> 并发编程中最常见的例子就是生产者消费者模式，生产者生产数据放到成果队列中，同时消费者从成果队列中来取这些数据。这样就让生产消费变成了异步的两个过程。

```go
// 生产者: 生成 factor 整数倍的序列
func Producer(factor int, out chan<- int) {
    for i := 0; ; i++ {
        out <- i*factor
    }
}

// 消费者
func Consumer(in <-chan int) {
    for v := range in {
        fmt.Println(v)
    }
}
func main() {
    ch := make(chan int, 64) // 成果队列

    go Producer(3, ch) // 生成 3 的倍数的序列
    go Producer(5, ch) // 生成 5 的倍数的序列
    go Consumer(ch)    // 消费生成的队列

    // Ctrl+C 退出
    sig := make(chan os.Signal, 1)
    signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
    fmt.Printf("quit (%v)\n", <-sig)
}
```

#### 1.6.3 发布订阅模型

> 发布订阅（publish-and-subscribe）模型通常被简写为 pub/sub 模型。在这个模型中，消息生产者成为发布者（publisher），而消息消费者则成为订阅者（subscriber），生产者和消费者是 M:N 的关系。在传统生产者和消费者模型中，是将消息发送到一个队列中，而发布订阅模型则是将消息发布给一个主题。

示例代码怪怪的，订阅者只能订阅一个发布者的一个主题。干脆自己手搓一个示例：[Jinvic/pubsub-example 发布订阅模型示例](https://github.com/Jinvic/pubsub-example)。

#### 1.6.4 控制并发数

介绍虚拟文件系统`vfs`包有一个`gatefs`子包会通过一个带缓存的通道控制访问该虚拟文件系统的访问并发数。不只是这个包，我们在其他功能中需要控制并发数时也可以参考这个实现。

```go
import (
    "golang.org/x/tools/godoc/vfs"
    "golang.org/x/tools/godoc/vfs/gatefs"
)

func main() {
    fs := gatefs.New(vfs.OS("/path"), make(chan bool, 8))
    // ...
}
```

```go
var limit = make(chan int, 3)

func main() {
    for _, w := range work {
        go func() {
            limit <- 1
            w()
            <-limit
        }()
    }
    select{}
}
```

#### 1.6.5 赢者为王

简单来说就是并行运行多个任务，消费最先完成的任务返回的结果（First-Win）。原文示例简化了**资源清理**和**取消机制**，让AI重写补了一下。

```go
package main

import (
    "context"
    "fmt"
    "math/rand"
    "time"
)

// 模拟不同搜索引擎的搜索函数
// 它们接收一个 context.Context，当 context 被取消时，应该停止工作
func searchByBing(ctx context.Context, query string) (string, error) {
    // 模拟随机的网络延迟 (100ms - 1000ms)
    delay := time.Duration(100+rand.Intn(900)) * time.Millisecond
    timer := time.NewTimer(delay)
    defer timer.Stop() // 防止资源泄漏

    select {
    case <-timer.C:
        // 模拟成功返回结果
        return fmt.Sprintf("[Bing] Results for '%s' (took %v)", query, delay), nil
    case <-ctx.Done():
        // context 被取消了，立即返回
        return "", ctx.Err() // 返回错误，通常是 context.Canceled
    }
}

func searchByGoogle(ctx context.Context, query string) (string, error) {
    delay := time.Duration(50+rand.Intn(1500)) * time.Millisecond
    timer := time.NewTimer(delay)
    defer timer.Stop()

    select {
    case <-timer.C:
        return fmt.Sprintf("[Google] Results for '%s' (took %v)", query, delay), nil
    case <-ctx.Done():
        return "", ctx.Err()
    }
}

func searchByBaidu(ctx context.Context, query string) (string, error) {
    delay := time.Duration(200+rand.Intn(2000)) * time.Millisecond
    timer := time.NewTimer(delay)
    defer timer.Stop()

    select {
    case <-timer.C:
        return fmt.Sprintf("[Baidu] Results for '%s' (took %v)", query, delay), nil
    case <-ctx.Done():
        return "", ctx.Err()
    }
}

// 并发搜索：启动多个搜索引擎，返回第一个成功的结果
func parallelSearch(query string) (string, error) {
    // 1. 创建一个可取消的 context
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel() // 当函数返回时，确保取消所有子任务

    // 2. 创建结果通道
    resultCh := make(chan string, 3) // 缓存大小等于并发数

    // 3. 启动多个搜索 Goroutine
    go func() {
        if result, err := searchByBing(ctx, query); err == nil {
            resultCh <- result // 只发送成功结果
        }
    }()
    go func() {
        if result, err := searchByGoogle(ctx, query); err == nil {
            resultCh <- result
        }
    }()
    go func() {
        if result, err := searchByBaidu(ctx, query); err == nil {
            resultCh <- result
        }
    }()

    // 4. 等待第一个成功的结果
    select {
    case result := <-resultCh:
        // 5. 一旦得到第一个结果，立即取消所有其他搜索
        cancel()
        // 6. 返回获胜者的结果
        return result, nil
        // case <-time.After(3 * time.Second):
        //     cancel() // 超时也取消
        //     return "", fmt.Errorf("search timeout")
    }
}

func main() {
    rand.Seed(time.Now().UnixNano()) // 初始化随机数种子

    // 执行并发搜索
    result, err := parallelSearch("golang")
    if err != nil {
        fmt.Printf("Search failed: %v\n", err)
        return
    }

    fmt.Println("Winner:", result)
    // 注意：其他两个搜索 Goroutine 会被 cancel() 触发的 ctx.Done() 中断
}
```

如上，通过`context.WithCancel()`创建了一个可以取消的上下文。当其中一个任务完成时，使用`cancel()`关闭上下文。
同时，各个任务在运行的同时也在监听上下文，当上下文被关闭时中断任务。

#### 1.6.6 素数筛

并发版本的素数筛是一个经典的并发例子，通过它我们可以更深刻地理解 Go 语言的并发特性。实现原理如下：

![素数筛实现原理](https://chai2010.cn/advanced-go-programming-book/images/ch1-13-prime-sieve.png)

个人理解，为了避免混淆，以并发思维去理解并发素数筛算法，需要明确一下几点：

- 每个Goroutine都是独立的，在方法结束后仍在独立运行。
- main函数中的主循环里的ch是在一直更新的，并不是最初的ch。
- 素数直接在主循环中打印输出了，并没有保存状态。

```go
// 返回生成自然数序列的管道: 2, 3, 4, ...
func GenerateNatural() chan int {
    ch := make(chan int)
    go func() {
        for i := 2; ; i++ {
            ch <- i
        }
    }()
    return ch
}
```

GenerateNatural 函数内部启动一个 Goroutine 生产序列，返回对应的管道。

然后是为每个素数构造一个筛子：将输入序列中是素数倍数的数踢出，并返回新的序列，是一个新的管道。

```go
// 管道过滤器: 删除能被素数整除的数
func PrimeFilter(in <-chan int, prime int) chan int {
    out := make(chan int)
    go func() {
        for {
            if i := <-in; i%prime != 0 {
                out <- i
            }
        }
    }()
    return out
}
```

PrimeFilter 函数也是内部启动一个 Goroutine 生产序列，返回过滤后序列对应的管道。

最后在main函数中启动这个并发的素数筛：

```go
func main() {
    ch := GenerateNatural() // 自然数序列: 2, 3, 4, ...
    for i := 0; i < 100; i++ {
        prime := <-ch // 新出现的素数
        fmt.Printf("%v: %v\n", i+1, prime)
        ch = PrimeFilter(ch, prime) // 基于新素数构造的过滤器
    }
}
```

#### 1.6.7 并发的安全退出

正如我在[1.6.5 赢者为王](#165-赢者为王)中提到的，原示例并没有提供安全退出机制，这一节则是介绍如何实现安全退出。循序渐进的介绍了`select`监听多个管道，关闭管道实现消息广播等。其实就是下一节要讲解的`context`包的大致原理。

#### 1.6.8 context 包

> 在 Go1.7 发布时，标准库增加了一个 context 包，用来简化对于处理单个请求的多个 Goroutine 之间与请求域的数据、超时和退出等操作。

如下是改进后的素数筛实现，通过上下文控制那些原本“失控”的Goroutine。

```go
package main

import (
    "context"
    "fmt"
    "sync"
)

// 返回生成自然数序列的管道: 2, 3, 4, ...
func GenerateNatural(ctx context.Context, wg *sync.WaitGroup) chan int {
    ch := make(chan int)
    go func() {
        defer wg.Done()
        defer close(ch)
        for i := 2; ; i++ {
            select {
            case <-ctx.Done():
                return
            case ch <- i:
            }
        }
    }()
    return ch
}

// 管道过滤器: 删除能被素数整除的数
func PrimeFilter(ctx context.Context, in <-chan int, prime int, wg *sync.WaitGroup) chan int {
    out := make(chan int)
    go func() {
        defer wg.Done()
        defer close(out)
        for i := range in {
            if i%prime != 0 {
                select {
                case <-ctx.Done():
                    return
                case out <- i:
                }
            }
        }
    }()
    return out
}

func main() {
    wg := sync.WaitGroup{}
    // 通过 Context 控制后台 Goroutine 状态
    ctx, cancel := context.WithCancel(context.Background())
    wg.Add(1)
    ch := GenerateNatural(ctx, &wg) // 自然数序列: 2, 3, 4, ...
    for i := 0; i < 100; i++ {
        prime := <-ch // 新出现的素数
        fmt.Printf("%v: %v\n", i+1, prime)
        wg.Add(1)
        ch = PrimeFilter(ctx, ch, prime, &wg) // 基于新素数构造的过滤器
    }

    cancel()
    wg.Wait()
}
```

除了上下文的引入，还有两个地方需要注意：

- 通过 `for range` 循环保证了输入管道被关闭时，循环能退出，不会出现死循环；
- 通过 `defer close` 保证了无论是输入管道被关闭，还是 ctx 被取消，只要素数筛退出，都会关闭输出管道。

如上细节处理避免了死锁问题，同时使得实现更为优雅。

### 1.7 错误和异常

Go中的错误类型为一个接口，可以通过 `Error` 方法来获得字符串类型的错误信息。

```go
type error interface {
    Error() string
}
```

> 在 Go 语言中，错误被认为是一种可以预期的结果；而异常则是一种非预期的结果，发生异常可能表示程序中存在 BUG 或发生了其它不可控的问题。Go 语言推荐使用 recover 函数将内部异常转为错误处理，这使得用户可以真正的关心业务相关的错误处理。

#### 1.7.1 错误处理策略

1. 使用defer清理资源

    对于一些需要在退出时进行的操作，如清理资源等，最好使用defer处理，而不是写在函数末尾。

    ```go
    func CopyFile(dstName, srcName string) (written int64, err error) {
        src, err := os.Open(srcName)
        if err != nil {
            return
        }

        dst, err := os.Create(dstName)
        if err != nil {
            return
        }

        written, err = io.Copy(dst, src)
        dst.Close() // 错误：最后清理资源，如果中途报错退出则不会被处理
        src.Close()
        return
    }

    func CopyFile(dstName, srcName string) (written int64, err error) {
        src, err := os.Open(srcName)
        if err != nil {
            return
        }
        defer src.Close() // 正确：使用defer清理资源，确保退出时会被处理

        dst, err := os.Create(dstName)
        if err != nil {
            return
        }
        defer dst.Close()

        return io.Copy(dst, src)
    }
    ```

2. 使用 recover 捕获异常

    > Go 语言库的实现习惯: 即使在包内部使用了 `panic` ，但是在导出函数时会被转化为明确的错误值。

    程序运行时遇到异常时会直接停止。但有时为了系统稳定性不应该停止，就会会通过 `recover` 来防御性地捕获所有处理流程中可能产生的异常，然后将异常转为普通的错误返回。如下是JSON解析器的实现示例：

    ```go
    func ParseJSON(input string) (s *Syntax, err error) {
        defer func() {
            if p := recover(); p != nil {
                err = fmt.Errorf("JSON: internal error: %v", p)
            }
        }()
        // ...parser...
    }   
    ```

#### 1.7.2 获取错误的上下文

介绍作者自己写的`github.com/chai2010/errors`，加入了调用栈信息，支持错误的多级嵌套包装，支持错误码格式。感兴趣可以详细了解。

如果要在生产环境使用，可以考虑`github.com/pkg/errors`包。

实际上，go官方在1.13已经加入了基础的包装特性。随着Go官方错误处理的改进，如上`pkg/errors`之类的三方包基本不再活跃了。

既然如此，就简单了解一下官方errors包的新特性吧。

参考：

- [Working with Errors in Go 1.13](https://go.dev/blog/go1.13-errors)
- [errors package - errors - Go Packages](https://pkg.go.dev/errors)

**Errors before Go 1.13**：

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

**The Unwrap method**：

Go 1.13 引入了一项惯例：一个包含其他错误的对象可以实现一个 `Unwrap` 方法返回底层错误。

如果 e1.Unwrap() 返回 e2 ，我们就说 e1 包装了 e2 ，并且你可以通过 e1 来获取 e2 。

例如对于如上`QueryError`结构体，我们可以实现如下`Unwrap` 方法来实现这一惯例：

```go
func (e *QueryError) Unwrap() error { return e.Err }
```

展开一个错误的结果本身可能也有一个 Unwrap 方法；我们称通过重复展开产生的错误序列为错误链。

**Wrapping errors with %w**:

如前所述，通常使用 fmt.Errorf 函数向错误添加额外信息。在 Go 1.13 中， fmt.Errorf 函数支持一个新的 %w 动词。当这个动词存在时， fmt.Errorf 返回的错误将有一个 Unwrap 方法，该方法返回 %w 的参数， %w 必须是一个错误。在其他所有方面， %w 与 %v 完全相同。

```go
if err != nil {
    // Return an error which unwraps to err.
    return fmt.Errorf("decompress %v: %w", name, err)
}
```

**Examining errors with Is and As**:

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

#### 1.7.3 错误的错误返回

> Go 语言中的错误是一种接口类型。接口信息中包含了原始类型和原始的值。只有当接口的类型和原始的值都为空的时候，接口的值才对应 nil。
> 其实当接口中类型为空的时候，原始值必然也是空的；反之，当接口对应的原始值为空的时候，接口对应的原始类型并不一定为空的。

例如如下内容将返回一个 MyError 类型的空指针而不是nil。

```go
func returnsError() error {
    var p *MyError = nil
    if bad() {
        p = ErrBad
    }
    return p // Will always return a non-nil error.
}
```

正确做法是在没有错误时直接返回nil。

```go
func returnsError() error {
    if bad() {
        return (*MyError)(err)
    }
    return nil
}
```

#### 1.7.4 剖析异常

`panic`支持抛出任意类型的异常（而不仅仅是 `error` 类型的错误）， `recover` 函数调用的返回值和 `panic` 函数的输入参数类型一致，它们的函数签名如下：

```go
func panic(interface{})
func recover() interface{}
```

> 当函数调用 panic 抛出异常，函数将停止执行后续的普通语句，但是之前注册的 defer 函数调用仍然保证会被正常执行，然后再返回到调用者。
>
> 对于当前函数的调用者，因为处理异常状态还没有被捕获，和直接调用 panic 函数的行为类似。
>
> 在异常发生时，如果在 defer 中执行 recover 调用，它可以捕获触发 panic 时的参数，并且恢复到正常的执行流程。

简单来说，就是必须通过defer来调用recover才能正常捕获异常。

```go
func SomeFunc() {
    defer func() {
        if r := recover(); r != nil { 
            ...
        }
    }
}
```

> 必须要和有异常的栈帧只隔一个栈帧，recover 函数才能正常捕获异常。换言之，recover 函数捕获的是祖父一级调用函数栈帧的异常（刚好可以跨越一层 defer 函数）！

即必须在defer调用的函数中调用recover。在defer调用函数中调用recover包装函数或再次defer调用函数(隔两个栈帧)，以及defer直接调用recover(隔零个栈帧)都不行。但是defer调用recover包装函数而不是匿名函数`func(){}`就可以。

```go
// recover包装函数
func MyRecover() interface{} {
    log.Println("trace...")
    return recover()
}

// defer函数内调用包装函数
func Func1() {
    defer func() {
        // 无法捕获异常
        if r := MyRecover(); r != nil {
            fmt.Println(r)
        }
    }()
    panic(1)
}

// defer函数内再调用defer函数
func Func2() {
    defer func() {
        defer func() {
            // 无法捕获异常
            if r := recover(); r != nil {
                fmt.Println(r)
            }
        }()
    }()
    panic(1)
}

// defer直接调用recover
func Func3() {
    // 无法捕获异常
    defer recover()
    panic(1)
}

// defer调用recover包装函数
func main() {
    // 可以正常捕获异常
    defer MyRecover()
    panic(1)
}
```

如果希望将捕获到的异常转为错误，可以针对不同的类型分别处理，实现类型`try-catch`的逻辑：

```go
func main {
    defer func() {
        if r := recover(); r != nil {
            switch x := r.(type) {
            case runtime.Error:
                // 这是运行时错误类型异常
            case error:
                // 普通错误类型异常
            default:
                // 其他类型异常
            }
        }
    }()

    // ...
}
```

不过这样做和 Go 语言简单直接的编程哲学背道而驰了。

## Todo List

- [ ] 4. RPC和Protobuf
- [ ] 5. Go和Web
- [ ] 6. 分布式系统

Last Update: 2025-08-07 15:53:10
