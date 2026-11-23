---
title: CEL-Go笔记
date: '2026-11-19T16:51:59+08:00'
tags: 
- Go
categories: 
- 笔记
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# CEL-Go笔记

> 文档站转载，不保证内容为最新。[源站点](https://doc.jinvic.top/gopkg/thirdparty/google/cel-go/)

`https://github.com/google/cel-go`

参考：

- [CEL | Common Expression Language](https://cel.dev/?hl=zh-cn)
- [CEL-Go Codelab](https://codelabs.developers.google.com/codelabs/cel-go?hl=zh-cn#0)
- [cel.dev/cel-go/cel - Go Packages](https://pkg.go.dev/cel.dev/cel-go/cel)

## Hello World

```go
func exercise1() {
    fmt.Println("=== Exercise 1: Hello World ===")
    env, err := cel.NewEnv()
    if err != nil {
        fmt.Println("Error creating environment:", err)
        return
    }

    expr := `"Hello, World!"`
    ast, iss := env.Compile(expr)
    if iss.Err() != nil {
        fmt.Println("Error compiling expression:", iss.Err())
        return
    }

    if !reflect.DeepEqual(ast.OutputType(), cel.StringType) {
        fmt.Println("Error: Expression does not return a string")
        return
    }

    prg, err := env.Program(ast)
    if err != nil {
        fmt.Println("Error creating program:", err)
        return
    }

    out, _, err := prg.Eval(cel.NoVars())
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }

    fmt.Println("Result value:", out.Value())
    fmt.Println("Result type:", out.Type())
    fmt.Println()
}
```

`cel.NewEnv()`: 创建环境`cel.Env`，可以传入`cel.EnvOption`类型的选项。

`env.Compile()`: 将cel表达式字符串编译为`cel.Ast`抽象语法树（Abstract Syntax Tree）。注意第二个返回值是`*cel.Issues`问题集合，用`iss.Err()`取出错误；为nil表示无问题。

Compile得到的`cel.Ast`已带类型信息，`ast.OutputType()`能拿到表达式推断出的输出类型，可以使用`reflect.DeepEqual`判断是否符合要求。

`env.Program()`: 将ast转换为可以求值的程序实例。可以类比理解为一个函数变量。

`prg.Eval()`: 向程序中传参去进行求值，签名为`func (p *Program) Eval(input any) (ref.Val, *EvalDetails, error)`。可以看到处理错误有着两个返回值，其中EvalDetails求值详情主要是给调试和可观测性用，普通业务可忽略，只需要关注返回值`ref.Val`就行。可以使用`out.Value()`将其转为Go原生类型，或`out.Type()`拿到其CEL类型。

## 声明变量

注册变量和类型就是在`cel.NewEnv()`通过传入不同的`option`完成的。

```go
import (
    rpcpb "google.golang.org/genproto/googleapis/rpc/context/attribute_context"
    structpb "google.golang.org/protobuf/types/known/structpb"
    tpb "google.golang.org/protobuf/types/known/timestamppb"
)

func exercise2() {
    fmt.Println("=== Exercise 2: Variables ===")
    env, err := cel.NewEnv(
        cel.Types(&rpcpb.AttributeContext_Request{}),
        cel.Variable("request", cel.ObjectType("google.rpc.context.AttributeContext.Request")),
    )
    if err != nil {
        fmt.Println("Error creating environment:", err)
        return
    }
    expr := `request.auth.claims.group == "admin"`
    ast, iss := env.Compile(expr)
    if iss.Err() != nil {
        fmt.Println("Error compiling expression:", iss.Err())
        return
    }
    prg, err := env.Program(ast)
    if err != nil {
        fmt.Println("Error creating program:", err)
        return
    }

    claims := map[string]string{"group": "admin"}
    claimFields := make(map[string]*structpb.Value)
    for k, v := range claims {
        claimFields[k] = structpb.NewStringValue(v)
    }
    req := &rpcpb.AttributeContext_Request{
        Auth: &rpcpb.AttributeContext_Auth{
            Principal: "user:me@acme.co",
            Claims:    &structpb.Struct{Fields: claimFields},
        },
        Time: &tpb.Timestamp{Seconds: time.Now().Unix()},
    }
    vars := map[string]any{"request": req}
    out, _, err := prg.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }
    fmt.Println("Result value:", out.Value())
    fmt.Println("Result type:", out.Type())
    fmt.Println()
}
```

### 声明一个变量

`func Variable(name string, t *Type) EnvOption`

```go
cel.Variable("request", cel.ObjectType("google.rpc.context.AttributeContext.Request"))
cel.Variable("age", cel.IntType)
cel.Variable("name", cel.StringType)
cel.Variable("tags", cel.ListType(cel.StringType))
```

这个option声明环境中有一个叫name的变量，类型为t。

### 注册自定义类型

`func cel.Types(addTypes ...any) cel.EnvOption`

```go
cel.Types(&rpcpb.AttributeContext_Request{}, &MyStruct{})
```

这个option把Go/protobuf类型注册进类型系统，这样 cel.ObjectType("...") 引用的类型名才能被解析。

### 变量类型

CEL提供了如下类型构造器，可以作为`cel.Variable`的第二个类型参数。这些类型也可以嵌套。

| 构造器                    | 含义                    | 示例                                       |
| ------------------------- | ----------------------- | ------------------------------------------ |
| `cel.BoolType`            | bool                    |                                            |
| `cel.IntType`             | int64                   |                                            |
| `cel.UintType`            | uint64                  |                                            |
| `cel.DoubleType`          | float64                 |                                            |
| `cel.StringType`          | string                  |                                            |
| `cel.BytesType`           | []byte                  |                                            |
| `cel.TimestampType`       | 时间                    |                                            |
| `cel.DurationType`        | 时长                    |                                            |
| `cel.DynType`             | 动态（任意类型）        | 放弃类型检查                               |
| `cel.NullType`            | null                    |                                            |
| `cel.ListType(elem)`      | 列表                    | `cel.ListType(cel.StringType)`             |
| `cel.MapType(key, value)` | 映射                    | `cel.MapType(cel.StringType, cel.IntType)` |
| `cel.ObjectType(name)`    | 已注册的对象/proto 类型 | `cel.ObjectType("main.Request")`           |
| `cel.TypeParamType("T")`  | 类型参数（泛型函数用）  |                                            |
| `cel.OptionalType(t)`     | optional 包装           | `cel.OptionalType(cel.StringType)`         |

### 声明变量示例

#### 原生类型变量

```go
env, _ := cel.NewEnv(
    cel.Variable("name", cel.StringType),
    cel.Variable("age", cel.IntType),
)
// 表达式: name == "bob" && age > 18
// Eval: map[string]any{"name": "bob", "age": int64(20)}
```

#### 嵌套 map（动态结构）

```go
env, _ := cel.NewEnv(
    cel.Variable("request", cel.MapType(cel.StringType, cel.DynType)),
)
// 表达式: request.auth.claims.group == "admin"
// Eval: map[string]any{"request": map[string]any{...}}
```

DynType 让 CEL 不深究嵌套结构，字段逐层在 map 里查。灵活但类型检查弱。

#### 强类型对象（protobuf 或 struct）

```go
// protobuf
env, _ := cel.NewEnv(
    cel.Types(&rpcpb.AttributeContext_Request{}),          // 注册类型
    cel.Variable("request",                                // 声明变量
        cel.ObjectType("google.rpc.context.AttributeContext.Request")),
)

// 或 Go struct（带 cel 标签）
type Request struct {
    Auth Auth `cel:"auth"`
}
env, _ := cel.NewEnv(
    ext.NativeTypes(ext.ParseStructTags(true),
        // reflect.TypeFor[Request](), // go 1.22+
        reflect.TypeOf(&Request{}),
    ),
    cel.Variable("request", cel.ObjectType("main.Request")),
)
```

`cel.ObjectType`传入的类型名要和注册的名字一致：

- proto 用完整 message 名，如 google.rpc.context.AttributeContext.Request。
- Go struct 用 包路径.类型名，如 main.Request（可以用 reflect.TypeOf 确认）。

强类型对象有类型检查，编译期就能确认字段`request.xxx`是否存在。

## 逻辑与/或

```go
func exercise3() {
    fmt.Println("=== Exercise 3: Logical AND/OR ===")
    env, _ := cel.NewEnv(
        cel.Types(&rpcpb.AttributeContext_Request{}),
        cel.Variable("request",
            cel.ObjectType("google.rpc.context.AttributeContext.Request"),
        ),
    )

    conditionGroup := `request.auth.claims.group == 'admin'`
    conditionUser := `request.auth.principal == 'user:me@acme.co'`

    // 或运算符测试
    exprOr := conditionGroup + " || " + conditionUser
    astOr, iss := env.Compile(exprOr)
    if iss.Err() != nil {
        fmt.Println("Error compiling expression:", iss.Err())
        return
    }
    prgOr, err := env.Program(astOr)
    if err != nil {
        fmt.Println("Error creating program:", err)
        return
    }

    // 与运算符测试
    exprAnd := conditionGroup + " && " + conditionUser
    astAnd, iss := env.Compile(exprAnd)
    if iss.Err() != nil {
        fmt.Println("Error compiling expression:", iss.Err())
        return
    }
    prgAnd, err := env.Program(astAnd)
    if err != nil {
        fmt.Println("Error creating program:", err)
        return
    }

    // request.auth.claims.group 不存在
    emptyClaims := map[string]string{}
    userMe := "user:me@acme.co"
    userOther := "user:other@acme.co"
    claimFields := make(map[string]*structpb.Value)
    for k, v := range emptyClaims {
        claimFields[k] = structpb.NewStringValue(v)
    }

    reqMe := &rpcpb.AttributeContext_Request{
        Auth: &rpcpb.AttributeContext_Auth{
            Principal: userMe,
            Claims:    &structpb.Struct{Fields: claimFields},
        },
        Time: &tpb.Timestamp{Seconds: time.Now().Unix()},
    }

    reqOther := &rpcpb.AttributeContext_Request{
        Auth: &rpcpb.AttributeContext_Auth{
            Principal: userOther,
        },
        Time: &tpb.Timestamp{Seconds: time.Now().Unix()},
    }

    // 或运算符conditionUser条件满足，短路退出，不会报错
    vars := map[string]any{"request": reqMe}
    out, _, err := prgOr.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }
    fmt.Println("Result1 value:", out.Value())
    fmt.Println("Result1 type:", out.Type())
    fmt.Println()

    // 或运算符conditionUser条件不满足，继续执行conditionGroup，会报错
    vars = map[string]any{"request": reqOther}
    out, _, err = prgOr.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        // return
    }
    fmt.Println("Result2 value:", out.Value())
    fmt.Println("Result2 type:", out.Type())
    fmt.Println()

    // 与运算符conditionUser条件不满足，短路退出，不会报错
    vars = map[string]any{"request": reqOther}
    out, _, err = prgAnd.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }
    fmt.Println("Result3 value:", out.Value())
    fmt.Println("Result3 type:", out.Type())
    fmt.Println()

    // 与运算符conditionUser条件满足，继续执行conditionGroup，会报错
    vars = map[string]any{"request": reqMe}
    out, _, err = prgAnd.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        // return
    }
    fmt.Println("Result4 value:", out.Value())
    fmt.Println("Result4 type:", out.Type())
    fmt.Println()
}
```

直接使用`||`和`&&`逻辑运算符拼接表达式即可。需要注意的是，CEL的逻辑运算符是可交换的，而不是常见的按顺序执行，条件分支的任一侧都可以使其短路退出。

## 自定义函数

```go
func exercise4() {
    fmt.Println("=== Exercise 4: Customization ===")

    mapContainsKeyValue := func(args ...ref.Val) ref.Val {
        if len(args) != 3 {
            return types.NewErr("contains: expected 3 args, got %d", len(args))
        }

        m, ok := args[0].(traits.Mapper)
        if !ok {
            return types.NewErr("contains: receiver is not a map")
        }
        key := args[1]
        value := args[2]
        v, found := m.Find(key)
        if !found {
            if v != nil && (types.IsError(v) || types.IsUnknown(v)) {
                // key 类型不支持时可能给 err
                return v
            }
            return types.False
        }
        return v.Equal(value)
    }

    TypeKey := cel.TypeParamType("Key")
    TypeValue := cel.TypeParamType("Value")
    TypeMap := cel.MapType(TypeKey, TypeValue)

    env, err := cel.NewEnv(
        cel.Types(&rpcpb.AttributeContext_Request{}),
        cel.Variable("request",
            cel.ObjectType("google.rpc.context.AttributeContext.Request"),
        ),
        cel.Function(
            "contains",
            cel.MemberOverload(
                "map_contains_key_value",
                []*cel.Type{TypeMap, TypeKey, TypeValue},
                cel.BoolType,
                cel.FunctionBinding(mapContainsKeyValue),
            ),
        ),
    )
    if err != nil {
        fmt.Println("Error creating environment:", err)
        return
    }

    expr := `request.auth.claims.contains("group", "admin")`
    ast, iss := env.Compile(expr)
    if iss.Err() != nil {
        fmt.Println("Error compiling expression:", iss.Err())
        return
    }
    prg, err := env.Program(ast)
    if err != nil {
        fmt.Println("Error creating program:", err)
        return
    }

    claims := map[string]string{"group": "admin"}
    claimFields := make(map[string]*structpb.Value)
    for k, v := range claims {
        claimFields[k] = structpb.NewStringValue(v)
    }
    req := &rpcpb.AttributeContext_Request{
        Auth: &rpcpb.AttributeContext_Auth{
            Principal: "user:me@acme.co",
            Claims:    &structpb.Struct{Fields: claimFields},
        },
        Time: &tpb.Timestamp{Seconds: time.Now().Unix()},
    }
    wrongClaims := map[string]string{"group": "admin123"}
    wrongClaimFields := make(map[string]*structpb.Value)
    for k, v := range wrongClaims {
        wrongClaimFields[k] = structpb.NewStringValue(v)
    }
    wrongReq := &rpcpb.AttributeContext_Request{
        Auth: &rpcpb.AttributeContext_Auth{
            Principal: "user:me@acme.co",
            Claims:    &structpb.Struct{Fields: wrongClaimFields},
        },
        Time: &tpb.Timestamp{Seconds: time.Now().Unix()},
    }
    emptyReq := &rpcpb.AttributeContext_Request{
        Auth: &rpcpb.AttributeContext_Auth{
            Principal: "user:me@acme.co",
            Claims:    &structpb.Struct{Fields: make(map[string]*structpb.Value)},
        },
    }

    // 正常情况
    vars := map[string]any{"request": req}
    out, _, err := prg.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }
    fmt.Println("Result1 value:", out.Value())
    fmt.Println("Result1 type:", out.Type())
    fmt.Println()

    // key存在，value不匹配
    vars = map[string]any{"request": wrongReq}
    out, _, err = prg.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }
    fmt.Println("Result2 value:", out.Value())
    fmt.Println("Result2 type:", out.Type())
    fmt.Println()

    // key不存在
    vars = map[string]any{"request": emptyReq}
    out, _, err = prg.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }
    fmt.Println("Result3 value:", out.Value())
    fmt.Println("Result3 type:", out.Type())
    fmt.Println()
}
```

### 声明自定义函数

`func Function(name string, opts ...FunctionOpt) EnvOption`

这个option声明环境中有一个名为name的自定义函数。`FunctionOpt`类型的opts参数可以通过`MemberOverload`和`Overload`两个重载方法创建。前者重载成员函数，后者重载全局函数。同一个`cel.Function`可以挂多个`FunctionOpt`（即同一函数名的多个重载），由CEL按参数类型选择。

### 成员函数与全局函数

`func MemberOverload(overloadID string, args []*Type, resultType *Type, opts ...OverloadOpt) FunctionOpt`
`func Overload(overloadID string, args []*Type, resultType *Type, opts ...OverloadOpt) FunctionOpt`

可以看到，两者的声明是一样的。但其调用形式和第一个参数的含义不同。假设args有三个参数a、b、c，对于全局函数，直接通过f(a, b, c)的形式调用，其参数列表直接传入函数f；而对于成员函数，需要通过a.f(b,c)的形式调用，其第一个参数作为函数的接收者，后续参数才传入函数。

`overloadID string`: 全局唯一的重载id，命名习惯建议*函数名_参数类型简写*。和go不同，cel是支持函数重载的，将根据参数列表和选择合适的重载。
`args []*Type`: 参数列表，上文已介绍过。
`resultType *Type`: 返回类型。可以看到只有一个类型而不是类型数组，cel的函数都只支持单返回值。错误也不会额外返回一个error，而是作为一个特殊值在`ref.Val`里传播，最终在`prg.Eval`的第三个返回值error里暴露给Go调用方。
`opts ...OverloadOpt`: 将声明的函数重载绑定到具体的实现上。详见下文。

### 函数重载绑定实现

```go
type UnaryOp func(ref.Val) ref.Val
type BinaryOp func(ref.Val, ref.Val) ref.Val
type FunctionOp func(...ref.Val) ref.Val
```

`func UnaryBinding(binding functions.UnaryOp) OverloadOpt`
`func BinaryBinding(binding functions.BinaryOp) OverloadOpt`
`func FunctionBinding(binding functions.FunctionOp) OverloadOpt`

三者语义等价，只是参数数量不同。可以只使用最通用的`FunctionBinding`；或者当只有1/2个参数时使用前两者，可读性更强且避免手写args\[0\]、args\[1\]这样的拆包。

### 自定义函数实现

这里以`FunctionOp`为例。

需要注意的是，在写cel的自定义函数时不能再使用Go的原生类型作为参数或返回值，函数边界必须用`ref.Val`进行桥接。由此我们可以得到一个通用流程：

1. 拆包：ref.Val —> 具体接口/原生类型
2. 计算
3. 装箱：原生结果 -> ref.Val

```go
m, ok := args[0].(traits.Mapper)
if !ok {
    return types.NewErr("contains: receiver is not a map")
}
```

可以看到，这里我们是将传入的map断言为了`traits.Mapper`接口，而不是具体实现。cel为了跨语言一致性提供了一套按能力划分的抽象接口，屏蔽底层实现。详见`cel.dev/cel-go/common/types/traits`。`ref.Val`+`types`+`traits`是CEL自建的值体系。代价是边界处要装箱/拆包，但这是策略表达式引擎的必要设计。

```go
    TypeKey := cel.TypeParamType("Key")
    TypeValue := cel.TypeParamType("Value")
    TypeMap := cel.MapType(TypeKey, TypeValue)

    env, err := cel.NewEnv(
        cel.Types(&rpcpb.AttributeContext_Request{}),
        cel.Variable("request",
            cel.ObjectType("google.rpc.context.AttributeContext.Request"),
        ),
        cel.Function(
            "contains",
            cel.MemberOverload(
                "map_contains_key_value",
                // []*cel.Type{cel.MapType(cel.StringType, cel.StringType), cel.StringType, cel.StringType},
                []*cel.Type{TypeMap, TypeKey, TypeValue},
                cel.BoolType,
                cel.FunctionBinding(mapContainsKeyValue),
            ),
        ),
    )
```

可以看到，这里传入的参数列表不是直接使用cel的StringType等具体类型，而是通过`TypeParamType`定义了一个类型参数（type parameter），作用相当于Go泛型里的T。它在函数签名里引入泛型约束，让一个重载能适配多种具体类型，而不是把类型写死成StringType或DynType。同名类型参数出现多次会强制"这几处类型一致"。例如示例的`map<Key,Value>, Key, Value`会要求第一个参数的key和第二个参数类型一致，第一个参数的value和第三个参数类型一致。

## 构建结构化数据

```go
func exercise5() {
    fmt.Println("=== Exercise 5: Building Structural Data ===")

    env, err := cel.NewEnv(
        cel.Variable("now", cel.TimestampType),
    )
    if err != nil {
        fmt.Println("Error creating environment:", err)
        return
    }

    expr := `
        {'sub': 'serviceAccount:delegate@acme.co',
        'aud': 'my-project',
        'iss': 'auth.acme.com:12350',
        'iat': now,
        'nbf': now,
        'exp': now + duration('300s'),
        'extra_claims': {
            'group': 'admin'
        }}`
    ast, iss := env.Compile(expr)
    if iss.Err() != nil {
        fmt.Println("Error compiling expression:", iss.Err())
        return
    }
    prg, err := env.Program(ast)
    if err != nil {
        fmt.Println("Error creating program:", err)
        return
    }

    vars := map[string]any{"now": time.Now()}
    out, _, err := prg.Eval(vars)
    if err != nil {
        fmt.Println("Error evaluating program:", err)
        return
    }
    fmt.Println("Result value:", out.Value())
    fmt.Println("Result type:", out.Type())
    fmt.Println()

    // map[string]any
    v, err := out.ConvertToNative(reflect.TypeFor[map[string]any]())
    if err != nil {
        fmt.Println("Error converting to native:", err)
    }
    fmt.Println("Result value map[string]any:", v)
    fmt.Println("Result value type:", reflect.TypeOf(v))
    fmt.Println()

    // struct
    type JWT struct {
        Sub         string            `json:"sub"`
        Aud         string            `json:"aud"`
        Iss         string            `json:"iss"`
        Iat         time.Time         `json:"iat"`
        Nbf         time.Time         `json:"nbf"`
        Exp         time.Time         `json:"exp"`
        ExtraClaims map[string]string `json:"extra_claims"`
    }
    v, err = out.ConvertToNative(reflect.TypeFor[*JWT]())
    if err != nil {
        fmt.Println("Error converting to native:", err)
    }
    fmt.Println("Result value struct:", v)
    fmt.Println("Result value type:", reflect.TypeOf(v))
    fmt.Println()
}
```

除了常见的布尔值输出，CEL 还可以生成`map(string, dyn)`之类的结构化输出。可以通过`ref.Val.ConvertToNative()`转换为宿主语言的结构化数据。

## 宏

宏是Parse阶段的语法改写。当解析器遇到特定调用形式时，会把表达式改写成另一段表达式，而不是在运行时调用一个函数。它的语法`x.exists(e, p)`和函数调用`f(a, b)`一致，但语义不同。

宏工作在AST层，能看、能改表达式结构；函数工作在值层，只拿到求值结果。因此"绑定变量、惰性求值、存在性检查、错误吸收"这四类需求只能靠宏实现。

### 1. `has(e.f)` —— 存在性检查

```cel
has(user.address)       // message 字段是否存在
has(m.key_name)         // map 的 key 是否存在
```

- map：检查 key 是否存在（`f` 必须是标识符）。
- proto2：repeated/map 字段检查非空；singular/oneof 字段检查是否 set。
- proto3：repeated/map 检查非空；oneof/message 字段检查是否 set；其他 singular 字段检查是否为非默认值。

### 2. `e.all(x, p)` —— 全称谓词

```cel
[1, 2, 3].all(x, x > 0)          // true
{'a': 1, 'b': 2}.all(k, k != 'b') // false
```

- 对 list 遍历**元素**，对 map 遍历**key**。
- `x` 是绑定变量，在 `p` 中可用。
- 用 `&&` 组合，任一为 false 则整体 false，**忽略其他谓词的错误**（错误吸收）。

### 3. `e.exists(x, p)` —— 存在谓词

```cel
[1, 2, 3].exists(i, i % 2 != 0)  // true
[].exists(i, i > 0)              // false
```

- 与 `all` 对称，用 `||` 组合，任一为 true 则整体 true，**忽略其他错误**（错误吸收）。
- 对 list 遍历元素，对 map 遍历 key。

### 4. `e.exists_one(x, p)` —— 恰好一个

```cel
[1, 2, 2].exists_one(i, i < 2)   // true
[1, 2, 3, 4].exists_one(n, n % 2 == 0) // false
```

- 恰好一个元素/key 满足谓词才返回 true；0 个或多个都返回 false。
- **不吸收错误**：任一谓词出错，整个宏报错（因为必须看全部结果才能判断"恰好一个"）。

### 5. `e.map(x, t)` —— 变换

```cel
[1, 2, 3].map(x, x * 2)              // [2, 4, 6]
{'one': 1, 'two': 2}.map(k, k)       // ['one', 'two']
```

- 对 list 遍历元素、对 map 遍历 key，对每个求值 `t`，结果组成**新 list**。
- **任何元素求值错误 → 整个宏报错**。

### 6. `e.map(x, p, t)` —— 带过滤的变换

```cel
[1, 2, 3, 4].map(n, n % 2 == 0, n * 2)  // [4, 8]
```

- 先按谓词 `p` 过滤，再对通过的元素应用 `t`。
- 等价于 filter + map 的组合。

### 7. `e.filter(x, p)` —— 过滤

```cel
[1, 2, 3].filter(x, x > 1)           // [2, 3]
{'one': 1, 'two': 2}.filter(k, k == 'one') // ['one']
```

- 对 list 返回满足谓词的**元素子列表**；对 map 返回满足谓词的 **key 列表**。
- 无匹配返回**空 list**（不是 null/错误）。
- **任何元素求值错误 → 整个宏报错**。
