---
title: go-redis速查笔记
date: '2024-08-22T16:15:35+08:00'
tags:
- 笔记
- Go
- Redis
draft: true
hiddenFromHomePage: true
hiddenFromSearch: true
---

# go-redis笔记

基本都在抄API😓

## 快速入门

```go
package main

import (
    "context"
    "fmt"
    "github.com/redis/go-redis/v9"
)

var ctx = context.Background()

func main() {
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379", // Redis 服务器地址
        Password: "",               // 没有密码则留空
        DB:       0,                // 使用默认数据库
    })

    // 测试连接
    pong, err := rdb.Ping(ctx).Result()
    if err != nil {
        fmt.Println("无法连接到 Redis:", err)
        return
    }
    fmt.Println("连接成功:", pong)
}
```

## 基础数据结构

### 字符串（string）

基本的数据存储单元，可以存储字符串、整数或者浮点数。

#### 设置键值对：Set

```go
func (c redis.cmdable) Set(ctx context.Context, key string, value interface{}, expiration time.Duration) *redis.StatusCmd
```

使用示例：`rdb.Set(ctx, key,value,0)`

#### 获取键值对：Get

```go
func (c redis.cmdable) Get(ctx context.Context, key string) *redis.StringCmd
```

使用示例：`rdb.Get(ctx, key)`

#### 删除键值对：Del

支持批量删除。

```go
func (c redis.cmdable) Del(ctx context.Context, keys ...string) *redis.IntCmd
```

使用示例：`rdb.Del(ctx, key)`

#### 递增和递减：Incr/Decr

只能操作整数值。

```go
func (c redis.cmdable) Incr(ctx context.Context, key string) *redis.IntCmd
func (c redis.cmdable) Decr(ctx context.Context, key string) *redis.IntCmd
```

使用示例：`rdb.Incr(ctx, key)` `rdb.Decr(ctx, key)`

#### 批量操作：MSet/MGet

```go
func (c redis.cmdable) MSet(ctx context.Context, values ...interface{}) *redis.StatusCmd
func (c redis.cmdable) MGet(ctx context.Context, keys ...string) *redis.SliceCmd
```

使用示例：

```go
rdb.MSet(ctx, key1, value1, key2, value2...)
rdb.MSet(ctx, []string{key1, value1, key2, value2...})
rdb.MSet(ctx, map[string]interface{}{key1: value1, key2: value2...})
rdb.MSet(struct)

rdb.MGet(ctx, key1, key2...)
```

#### 获取并设置：GetSet

设置指定 key 的值，并返回 key 的旧值。

```go
func (c redis.cmdable) GetSet(ctx context.Context, key string, value interface{}) *redis.StringCmd
```

使用示例：`rdb.GetSet(ctx, key, value)`

#### 追加值：Append

为指定的 key 追加值。

如果 key 已经存在并且是一个字符串， APPEND 命令将 value 追加到 key 原来的值的末尾。

如果 key 不存在， APPEND 就简单地将给定 key 设为 value。

```go
func (c redis.cmdable) Append(ctx context.Context, key string, value string) *redis.IntCmd
```

使用示例：`rdb.Append(ctx, key, value)`

#### 获取字符串长度：StrLen

```go
func (c redis.cmdable) StrLen(ctx context.Context, key string) *redis.IntCmd
```

使用示例：`rdb.StrLen(ctx, key)`

#### 设置字符串指定位置的值：SetRange

```go
func (c redis.cmdable) SetRange(ctx context.Context, key string, offset int64, value string) *redis.IntCmd
```

使用示例：`rdb.SetRange(ctx, key, offset, value)`

#### 获取字符串的部分值：GetRange

```go
func (c redis.cmdable) GetRange(ctx context.Context, key string, start int64, end int64) *redis.StringCmd
```

使用示例：`rdb.GetRange(ctx, key, start, end)`

#### 获取并删除：GetDel

```go
func (c redis.cmdable) GetDel(ctx context.Context, key string) *redis.StringCmd
```

使用示例：`rdb.GetDel(ctx, key)`

#### 获取最小公共子串：LCS

```go
type LCSQuery struct {
    Key1         string
    Key2         string
    Len          bool
    Idx          bool
    MinMatchLen  int
    WithMatchLen bool
}

func (c redis.cmdable) LCS(ctx context.Context, q *redis.LCSQuery) *redis.LCSCmd
```

使用示例：

```go
lcsQuery := redis.LCSQuery{
    Key1: "string1",
    Key2: "string2",
}

rdb.LCS(ctx, lcsQuery)
```

#### 递增浮点数值：IncrByFloat

```go
func (c redis.cmdable) IncrByFloat(ctx context.Context, key string, value float64) *redis.FloatCmd
```

使用示例：`rdb.IncrByFloat(ctx, key, value)`

#### 设置带过期时间的值：SetEx

```go
func (c redis.cmdable) SetEx(ctx context.Context, key string, value interface{}, expiration time.Duration) *redis.StatusCmd
```

使用示例：`rdb.SetEx(ctx, key, valve, 10*time.Second)`

#### 设置不存在的值：SetNX

仅当键不存在时设置值。

```go
func (c redis.cmdable) SetNX(ctx context.Context, key string, value interface{}, expiration time.Duration) *redis.BoolCmd
```

使用示例：`rdb.SetNX(ctx, key, valve, 0)`

#### 设置存在的值：SetXX

仅当键存在时设置值。

```go
func (c redis.cmdable) SetXX(ctx context.Context, key string, value interface{}, expiration time.Duration) *redis.BoolCmd
```

使用示例：`rdb.SetXX(ctx, key, valve, 0)`

#### 批量设置不存在的值：MSetNX

```go
func (c redis.cmdable) MSetNX(ctx context.Context, values ...interface{}) *redis.BoolCmd
```

使用示例：

```go
rdb.MSetNX(ctx, key1, value1, key2, value2...)
rdb.MSetNX(ctx, []string{key1, value1, key2, value2...})
rdb.MSetNX(ctx, map[string]interface{}{key1: value1, key2: value2...})
rdb.MSetNX(struct)
```

#### 设置带参数的值：SetArgs

```go
type SetArgs struct {
    // Mode can be `NX` or `XX` or empty.
    Mode string

    // Zero `TTL` or `Expiration` means that the key has no expiration time.
    TTL      time.Duration
    ExpireAt time.Time

    // When Get is true, the command returns the old value stored at key, or nil when key did not exist.
    Get bool

    // KeepTTL is a Redis KEEPTTL option to keep existing TTL, it requires your redis-server version >= 6.0,
    // otherwise you will receive an error: (error) ERR syntax error.
    KeepTTL bool
}

func (c redis.cmdable) SetArgs(ctx context.Context, key string, value interface{}, a redis.SetArgs) *redis.StatusCmd
```

使用示例：

```go
setArgs := redis.SetArgs{
    Mode: "NX", // 仅当键不存在时设置
    TTL:  10 * time.Second,
}

err := rdb.SetArgs(ctx, "paramKey", "paramValue", setArgs).Err()
```
  
### 哈希（hash）

Redis 的 `Hash` 数据类型类似于传统编程语言中的哈希表或字典。它存储的是键值对集合，特别适合存储对象数据，例如用户信息或配置项。通过 Hash 数据类型，我们可以高效地进行字段的读取、写入、删除操作。

#### HSet 设置指定字段的值

```go
func (c redis.cmdable) HSet(ctx context.Context, key string, values ...interface{}) *redis.IntCmd
```

使用示例：

```go
rdb.HSet(ctx, key, field1, value1, field2, value2...)
rdb.HSet(ctx, key, []string{field1, value1, field2, value2...})
rdb.HSet(ctx, key, map[string]interface{}{key1: value1, field2: value2...})
type hash struct{ Field1 type `redis:field1`; Field2 type `redis:field2`... }
rdb.HSet(ctx, key, hash{value1, value2...}) 
```

#### HMSet 批量设置指定字段的值

在 Redis 4.0 及更高版本中已被标记为弃用。

#### HGet 获取指定字段的值

```go
func (c redis.cmdable) HGet(ctx context.Context, key string, field string) *redis.StringCmd
```

使用示例：`rdb.HGet(ctx, key, field)`

#### HMGet 批量获取指定字段的值

```go
func (c redis.cmdable) HMGet(ctx context.Context, key string, fields ...string) *redis.SliceCmd
```

使用示例：`rdb.HGet(ctx, key, "field1", "field2"...)`

#### HSetNX设置指定字段的值（仅当字段不存在时）

```go
func (c redis.cmdable) SetNX(ctx context.Context, key string, value interface{}, expiration time.Duration) *redis.BoolCmd
```

使用示例：`rdb.HGet(ctx, key, field, value)`

#### HLen 获取字段数量

```go
func (c redis.cmdable) HLen(ctx context.Context, key string) *redis.IntCmd
```

使用示例：`rdb.HLen(ctx, key)`

#### HExists 检查字段是否存在

```go
func (c redis.cmdable) HExists(ctx context.Context, key string, field string) *redis.BoolCmd
```

使用示例：`rdb.HExists(ctx, key, field)`

#### HDel 删除字段

```go
func (c redis.cmdable) HDel(ctx context.Context, key string, fields ...string) *redis.IntCmd
```

使用示例：`rdb.HDel(ctx, key, field1, field2...)`

#### HKeys 获取所有字段

```go
func (c redis.cmdable) HKeys(ctx context.Context, key string) *redis.StringSliceCmd
```

使用示例：`rdb.HKeys(ctx, key)`

#### HVals 获取所有值

```go
func (c redis.cmdable) HVals(ctx context.Context, key string) *redis.StringSliceCmd
```

使用示例：`rdb.HVals(ctx, key)`

#### HGetAll 获取所有字段和值

```go
func (c redis.cmdable) HGetAll(ctx context.Context, key string) *redis.MapStringStringCmd
```

使用示例：`rdb.HGetAll(ctx, key)`

#### HIncrBy 指定字段的整数值增量

```go
func (c redis.cmdable) HIncrBy(ctx context.Context, key string, field string, incr int64) *redis.IntCmd
```

使用示例：`rdb.HIncrBy(ctx, key, field, incr)`

#### HIncrByFloat 指定字段的浮点数值增量

```go
func (c redis.cmdable) HIncrByFloat(ctx context.Context, key string, field string, incr float64) *redis.FloatCmd
```

使用示例：`rdb.HIncrByFloat(ctx, key, field, incr)`

#### HScan 增量迭代字段

它非常适合处理大哈希表，因为它可以在不阻塞服务器的情况下逐步遍历表中的所有元素。

```go
func (c redis.cmdable) HScan(ctx context.Context, key string, cursor uint64, match string, count int64) *redis.ScanCmd
```

使用示例：`rdb.HScan(ctx, key, cursor, match，count)`

- **cursor**：扫描的游标，初始值为 0。
- **match**：匹配模式，这里使用 * 匹配以任意字段。
- **count**：每次扫描提示返回的元素数量。

注意，这里的`count`参数为提示值（hint）。当集合足够小时，SCAN命令会返回集合中的所有元素，直接忽略COUNT属性。

#### HScanNoValues 增量迭代字段（不包括值）

```go
func (c redis.cmdable) HScanNoValues(ctx context.Context, key string, cursor uint64, match string, count int64) *redis.ScanCmd
```

使用示例：`rdb.HScanNoValues(ctx, key, cursor, match，count)`

#### HRandField 随机获取一个或多个字段

```go
func (c redis.cmdable) HRandField(ctx context.Context, key string, count int) *redis.StringSliceCmd
```

使用示例：`rdb.HRandField(ctx, key, count)`

#### HRandFieldWithValues 随机获取一个或多个字段及其值

```go
func (c redis.cmdable) HRandFieldWithValues(ctx context.Context, key string, count int) *redis.KeyValueSliceCmd
```

使用示例：`rdb.HRandFieldWithValues(ctx, key, count)`

#### Hash 过期时间相关

- HExpire 设置指定字段的过期时间（以秒为单位）
- HExpireWithArgs 设置指定字段的过期时间（以秒为单位）并附加过期选项
- HPExpire 设置指定字段的过期时间（以毫秒为单位）
- HPExpireWithArgs 设置指定字段的过期时间（以毫秒为单位）并附加过期选项
- HExpireAt 设置指定字段的过期时间点
- HExpireAtWithArgs 设置指定字段的过期时间点并附加过期选项
- HPExpireAt 设置指定字段的过期时间点（以毫秒为单位）
- HPExpireAtWithArgs 设置指定字段的过期时间点（以毫秒为单位）并附加过期选项
- HExpireTime 获取指定字段的过期时间
- HPExpireTime 获取指定字段的过期时间（以毫秒为单位）
- HPersist 移除指定字段的过期时间，使其永久有效
- HTTL 获取指定字段的剩余生存时间（以秒为单位）
- HPTTL 获取指定字段的剩余生存时间（以毫秒为单位）

### 列表（list）

Redis 的 `List` 数据结构是一种简单的链表数据结构，可以在头部和尾部进行高效的插入和删除操作。它的元素是有序的，可以重复，支持对元素进行任意位置的操作。Redis List 的常见使用场景包括消息队列、任务队列、实时数据流等。

#### LLen：获取列表长度

```go
func (c redis.cmdable) LLen(ctx context.Context, key string) *redis.IntCmd
```

使用示例：`rdb.LLen(ctx, key)`

#### LIndex：获取指定位置的元素

```go
func (c redis.cmdable) LIndex(ctx context.Context, key string, index int64) *redis.StringCmd
```

使用示例：`rdb.LIndex(ctx, key, index)`

#### LPos：查找指定值的位置

```go
func (c redis.cmdable) LPos(ctx context.Context, key string, value string, a redis.LPosArgs) *redis.IntCmd
```

- `args`：查询参数（如开始位置、结束位置等）

使用示例：`rdb.LPos(ctx, key, value, reids.Args{})`

#### LPosCount：查找指定值的位置（限制返回数量）

```go
func (c redis.cmdable) LPosCount(ctx context.Context, key string, value string, count int64, a redis.LPosArgs) *redis.IntSliceCmd
```

使用示例：`rdb.LPos(ctx, list, value, count, reids.Args{})`

#### LInsert：在列表中插入元素

```go
func (c redis.cmdable) LInsert(ctx context.Context, key string, op string, pivot interface{}, value interface{}) *redis.IntCmd
```

- `op`：插入操作（“before” 或 “after”）
- `pivot`：参考元素
- `value`：待插入的元素

使用示例：`rdb.LInsert(ctx, list, "after", pivot, value)`

#### LInsertBefore：在指定元素前插入新元素

```go
func (c redis.cmdable) LInsertBefore(ctx context.Context, key string, pivot interface{}, value interface{}) *redis.IntCmd
```

使用示例：`rdb.LInsertBefore(ctx, list, pivot, value)`

#### LInsertAfter：在指定元素后插入新元素

```go
func (c redis.cmdable) LInsertAfter(ctx context.Context, key string, pivot interface{}, value interface{}) *redis.IntCmd
```

使用示例：`rdb.LInsertAfter(ctx, list, pivot, value)`

#### LPush：将一个或多个元素插入到列表的头部

```go
func (c redis.cmdable) LPush(ctx context.Context, key string, values ...interface{}) *redis.IntCmd
```

使用示例：`rdb.LPush(ctx, list, value1, value2...)`

#### LPop：从列表的头部弹出一个元素

```go
func (c redis.cmdable) LPop(ctx context.Context, key string) *redis.StringCmd
```

使用示例：`rdb.LPop(ctx, list)`

#### LMPop：从一个或多个列表中弹出多个元素

Redis 6.0+ 支持

```go
func (c redis.cmdable) LMPop(ctx context.Context, direction string, count int64, keys ...string) *redis.KeyValuesCmd
```

- `direction`：弹出方向（“left” 或 “right”）
- `count`：弹出数量

使用示例：`rdb.LMPop(ctx, "left", 2, list1, list2...)`

#### RPush：将一个或多个元素插入到列表的尾部

```go
func (c redis.cmdable) RPush(ctx context.Context, key string, values ...interface{}) *redis.IntCmd
```

使用示例：`rdb.RPush(ctx, key, value1, value2...)`

#### RPop：从列表的尾部弹出一个元素

```go
func (c redis.cmdable) RPop(ctx context.Context, key string) *redis.StringCmd
```

使用示例：`rdb.RPush(ctx, list)`

#### RPopLPush：从源列表中弹出一个元素并推送到目标列表的头部

```go
func (c redis.cmdable) RPopLPush(ctx context.Context, source string, destination string) *redis.StringCmd
```

使用示例：`rdb.RPopLPush(ctx, list_src,list_dest)`

#### LPopCount：从列表的头部弹出指定数量的元素

```go
func (c redis.cmdable) LPopCount(ctx context.Context, key string, count int) *redis.StringSliceCmd
```

使用示例：`rdb.LPopCount(ctx, list, cnt)`

#### RPopCount：从列表的尾部弹出指定数量的元素

```go
func (c redis.cmdable) RPopCount(ctx context.Context, key string, count int) *redis.StringSliceCmd
```

使用示例：`rdb.RPopCount(ctx, list, cnt)`

#### LPushX：将一个或多个元素插入到列表的头部，仅在列表存在时生效

```go
func (c redis.cmdable) LPushX(ctx context.Context, key string, values ...interface{}) *redis.IntCmd
```

使用示例：`rdb.LPushX(ctx, list, values1, values2...)`

#### RPushX：将一个或多个元素插入到列表的尾部，仅在列表存在时生效

```go
func (c redis.cmdable) RPushX(ctx context.Context, key string, values ...interface{}) *redis.IntCmd
```

使用示例：`rdb.RPushX(ctx, list, values1, values2...)`

#### LRange：获取列表中指定范围的元素

包含结束索引位置上的值

```go
func (c redis.cmdable) LRange(ctx context.Context, key string, start int64, stop int64) *redis.StringSliceCmd
```

- `start`：起始索引
- `stop`：结束索引

使用示例：`rdb.LRange(ctx, list, start, stop...)`

#### LRem：从列表中移除指定数量的某个元素

```go
func (c redis.cmdable) LRem(ctx context.Context, key string, count int64, value interface{}) *redis.IntCmd
```

使用示例：`rdb.LRem(ctx, list, count, value)`

#### LSet：设置列表中指定位置的元素

```go
func (c redis.cmdable) LSet(ctx context.Context, key string, index int64, value interface{}) *redis.StatusCmd
```

使用示例：`rdb.LRem(ctx, list, index, value)`

#### LTrim：对列表进行修剪，保留指定范围内的元素

包含结束索引位置上的值

```go
func (c redis.cmdable) LTrim(ctx context.Context, key string, start int64, stop int64) *redis.StatusCmd
```

- `start`：起始索引
- `stop`：结束索引

使用示例：`rdb.LTrim(ctx, list, start, stop)`

#### LMove：从一个列表移动元素到另一个列表，并指定源和目标位置

```go
func (c redis.cmdable) LMove(ctx context.Context, source string, destination string, srcpos string, destpos string) *redis.StringCmd
```

- `source`：源列表的键
- `destination`：目标列表的键
- `srcpos`：源列表的位置（“left” 或 “right”）
- `destpos`：目标列表的位置（“left” 或 “right”）

使用示例：`rdb.LMove(ctx, list_src, list_dest, "right", "left")`

#### 阻塞特性方法

这些命令会在没有满足条件的数据可用时阻塞客户端，直到满足条件的数据出现或达到超时限制。这里的 B 代表 "Blocking"（阻塞）。

**阻塞时间**：阻塞命令的第二个参数是阻塞时间，单位是秒。如果设置为 0，则表示无限期阻塞，直到有数据可用或键被删除。

- `BLPop`：阻塞地从一个或多个列表中弹出元素，直到有元素可用或超时。
- `BRPop`：阻塞地从一 个或多个列表中弹出元素，直到有元素可用或超时。
- `BRPopLPush`：从源列表中弹出一个元素并推送到目标列表的头部，支持阻塞操作。
- `BLMPop`：从一个或多个列表中弹出多个元素并返回，支持从头部或尾部弹出，Redis 6.0+ 支持。
- `BLMove`：从源列表的指定方向弹出一个元素并推送到目标列表的指定方向，支持阻塞操作。

### 集合（set）

Redis 的 `Set` 是一个无序的字符串集合。集合中的元素是唯一的，这意味着集合中不能有重复的数据。Sets 提供了一些强大而有用的操作，如求交集、并集和差集等。

#### SAdd 添加元素 / SCard 获取元素数量

```go
func (c redis.cmdable) SAdd(ctx context.Context, key string, members ...interface{}) *redis.IntCmd
func (c redis.cmdable) SCard(ctx context.Context, key string) *redis.IntCmd
```

使用示例：
`rdb.SAdd(ctx, set, member1,member2...)`
`rdb.SCard(ctx,set)`

#### SMembers 获取集合中的所有成员

```go
func (c redis.cmdable) SMembers(ctx context.Context, key string) *redis.StringSliceCmd
```

使用示例：`rdb.SMembers(ctx,set)`

#### SUnion 计算并集 / SInter 计算交集

```go
func (c redis.cmdable) SUnion(ctx context.Context, keys ...string) *redis.StringSliceCmd
func (c redis.cmdable) SInter(ctx context.Context, keys ...string) *redis.StringSliceCmd
```

使用示例：
`db.SUnion(ctx, set1, set2...)`
`db.SInter(ctx, set1, set2...)`

#### SDiff 计算集合的差集

即set1中存在但set2中不存在的元素。

```go
func (c redis.cmdable) SDiff(ctx context.Context, keys ...string) *redis.StringSliceCmd
```

使用示例：`db.SDiff(ctx, set1, set2...)`

#### SIsMember 和 SMIsMember 检查一个或多个元素是否是集合的成员

```go
func (c redis.cmdable) SIsMember(ctx context.Context, key string, member interface{}) *redis.BoolCmd
func (c redis.cmdable) SMIsMember(ctx context.Context, key string, members ...interface{}) *redis.BoolSliceCmd
```

使用示例：
`db.SIsMember(ctx, set, mem)`
`db.SMIsMember(ctx, set, mem1, mem2...)`

#### SMove 将一个元素从一个集合移动到另一个集合

```go
func (c redis.cmdable) SMove(ctx context.Context, source string, destination string, member interface{}) *redis.BoolCmd
```

使用示例：`db.SMove(ctx, set_src, set_dest, mem)`

#### SPop/SPopN 从集合中随机移除一个或多个元素

**注意**：**随机**移除

```go
func (c redis.cmdable) SPop(ctx context.Context, key string) *redis.StringCmd
func (c redis.cmdable) SPopN(ctx context.Context, key string, count int64) *redis.StringSliceCmd
```

使用示例：
`db.SPop(ctx, set)`
`db.SPopN(ctx, set， cnt)`

#### SRandMember/SRandMemberN 从集合中随机获取一个或多个元素，但不移除它们

```go
func (c redis.cmdable) SRandMember(ctx context.Context, key string) *redis.StringCmd
func (c redis.cmdable) SRandMemberN(ctx context.Context, key string, count int64) *redis.StringSliceCmd
```

使用示例：
`db.SRandMember(ctx, set)`
`db.SRandMemberN(ctx, set， cnt)`

#### SRem 从集合中移除一个或多个元素

```go
func (c redis.cmdable) SRem(ctx context.Context, key string, members ...interface{}) *redis.IntCmd
```

使用示例：`db.SRem(ctx, set, mem1, mem2...)`

#### SScan 增量迭代集合中的元素

在处理 Redis Set 集合数据类型时，有时候需要增量迭代集合中的元素以避免一次性获取所有元素带来的性能问题。增量迭代是一种高效的遍历数据集合的方法，特别适用于数据量较大的集合。与一次性获取所有数据不同，增量迭代可以分批次获取数据，降低内存和网络资源的消耗。

```go
func (c redis.cmdable) SScan(ctx context.Context, key string, cursor uint64, match string, count int64) *redis.ScanCmd
```

使用示例：`db.SScan(ctx, set, cursor,match, cnt)`

#### SUnionStore / SInterStore 将多个集合的并集或交集存储到一个新的集合中

```go
func (c redis.cmdable) SUnionStore(ctx context.Context, destination string, keys ...string) *redis.IntCmd
func (c redis.cmdable) SInterStore(ctx context.Context, destination string, keys ...string) *redis.IntCmd
```

使用示例：
`db.SUnionStore(ctx, set_dest, set1,set2...)`
`db.SInterStore(ctx, set_dest, set1,set2...)`

### 有序集合（zset）

`Redis` 有序集合（SortedSet）是一种集合类型，其中的每个元素都关联一个分数，元素按分数从小到大排序。有序集合非常适合用于排行榜、带权重的数据存储、优先级队列等场景。

```go
// Z represents sorted set member.
type Z struct {
    Score  float64
    Member interface{}
}
```

#### ZAdd：添加一个或多个成员

```go
func (c redis.cmdable) ZAdd(ctx context.Context, key string, members ...redis.Z) *redis.IntCmd
```

使用示例：`rdb.ZAdd(ctx, zset, mem1, mem2...)`

#### ZAddLT/ZAddGT：添加成员，根据分数更新

ZAddLT:如果新成员的分数小于现有成员的分数，则更新。
ZAddGT:如果新成员的分数大于现有成员的分数，则更新。

```go
func (c redis.cmdable) ZAddLT(ctx context.Context, key string, members ...redis.Z) *redis.IntCmd
func (c redis.cmdable) ZAddGT(ctx context.Context, key string, members ...redis.Z) *redis.IntCmd
```

使用示例：
`rdb.ZAddLT(ctx, zset, mem1, mem2...)`
`rdb.ZAddGT(ctx, zset, mem1, mem2...)`

#### ZAddNX/ZAddXX：添加成员，仅当成员不存在/存在时才执行

```go
func (c redis.cmdable) ZAddNX(ctx context.Context, key string, members ...redis.Z) *redis.IntCmd
func (c redis.cmdable) ZAddXX(ctx context.Context, key string, members ...redis.Z) *redis.IntCmd
```

使用示例：
`rdb.ZAddNX(ctx, zset, mem1, mem2...)`
`rdb.ZAddXX(ctx, zset, mem1, mem2...)`

#### ZAddArgs/ZAddArgsIncr：添加成员，并使用参数配置（若已存在则分数增加。）

```go
// ZAddArgs WARN: The GT, LT and NX options are mutually exclusive.
type ZAddArgs struct {
    NX      bool
    XX      bool
    LT      bool
    GT      bool
    Ch      bool
    Members []Z
}

func (c redis.cmdable) ZAddArgs(ctx context.Context, key string, args redis.ZAddArgs) *redis.IntCmd
func (c redis.cmdable) ZAddArgsIncr(ctx context.Context, key string, args redis.ZAddArgs) *redis.FloatCmd
```

使用示例：
`rdb.ZAddArgs(ctx, zset, args)`
`rdb.ZAddArgsIncr(ctx, zset, args)`

#### ZIncrBy：成员分数增加指定的增量

```go
func (c redis.cmdable) ZIncrBy(ctx context.Context, key string, increment float64, member string) *redis.FloatCmd
```

使用示例：`rdb.ZIncrBy(ctx, zset, incr, mem)`

#### ZScore/ZMScore：获取（多个）成员的分数

```go
func (c redis.cmdable) ZScore(ctx context.Context, key string, member string) *redis.FloatCmd
func (c redis.cmdable) ZMScore(ctx context.Context, key string, members ...string) *redis.FloatSliceCmd
```

使用示例：
`rdb.ZScore(ctx, zset, mem)`
`rdb.ZMScore(ctx, zset, mem1, mem2...)`

#### ZCard：获取成员数量

```go
func (c redis.cmdable) ZCard(ctx context.Context, key string) *redis.IntCmd
```

使用示例：`rdb.ZCard(ctx, zset)`

#### ZCount/ZLexCount：获取指定分数范围/指定字典区间内的成员数量

```go
func (c redis.cmdable) ZCount(ctx context.Context, key string, min string, max string) *redis.IntCmd
func (c redis.cmdable) ZLexCount(ctx context.Context, key string, min string, max string) *redis.IntCmd
```

使用示例：
`rdb.ZCount(ctx, zset, min, max)`
`rdb.ZLexCount(ctx, zset, min, max)`

#### ZInter/ZInterWithScores：计算多个有序集合的交集，并返回（带分数）结果

```go
// ZStore is used as an arg to ZInter/ZInterStore and ZUnion/ZUnionStore.
type ZStore struct {
    Keys    []string
    Weights []float64
    // Can be SUM, MIN or MAX.
    Aggregate string
}

func (c redis.cmdable) ZInter(ctx context.Context, store *redis.ZStore) *redis.StringSliceCmd
func (c redis.cmdable) ZInterWithScores(ctx context.Context, store *redis.ZStore) *redis.ZSliceCmd
```

使用示例：

```go
store := &redis.ZStore{
        Keys: []string{"zset1", "zset2"},
    }
rdb.ZInter(ctx, store)
rdb.ZInterWithScores(ctx, store)
```

#### ZInterCard：计算交集数量

```go
func (c redis.cmdable) ZInterCard(ctx context.Context, limit int64, keys ...string) *redis.IntCmd
```

`limit`：交集计算的最大数量。

使用示例：`rdb.ZInterCard(ctx, limit, zset1, zset2...)`

#### ZInterStore：计算交集并将存储结果

```go
func (c redis.cmdable) ZInterStore(ctx context.Context, destination string, store *redis.ZStore) *redis.IntCmd
```

使用示例：`rdb.ZInterStore(ctx, zset_dest, store)`

#### ZMPop：批量弹出最小或最大的多个成员

```go
func (c redis.cmdable) ZMPop(ctx context.Context, order string, count int64, keys ...string) *redis.ZSliceWithKeyCmd
```

`order`：弹出成员的顺序，"MIN" 表示最小，"MAX" 表示最大。

使用示例：`rdb.ZMPop(ctx, order, count, zset1, zset2...)`

#### BZMPop：批量弹出最大或最小分数的成员【阻塞】

```go
func (c redis.cmdable) BZMPop(ctx context.Context, timeout time.Duration, order string, count int64, keys ...string) *redis.ZSliceWithKeyCmd
```

`timeout`：超时时间，阻塞等待的时间。

#### BZPopMax/BZPopMin：批量弹出最大/最小分数的成员【阻塞】

```go
func (c redis.cmdable) BZPopMax(ctx context.Context, timeout time.Duration, keys ...string) *redis.ZWithKeyCmd
func (c redis.cmdable) BZPopMin(ctx context.Context, timeout time.Duration, keys ...string) *redis.ZWithKeyCmd
```

#### ZPopMax/ZPopMin：弹出最大/最小分数的成员

```go
func (c redis.cmdable) ZPopMax(ctx context.Context, key string, count ...int64) *redis.ZSliceCmd
func (c redis.cmdable) ZPopMin(ctx context.Context, key string, count ...int64) *redis.ZSliceCmd
```

`count`：要弹出的成员数量（可选）。

使用示例：
`rdb.ZPopMax(ctx, zset, count)`
`rdb.ZPopMin(ctx, zset, count)`

#### ZRange/ZRangeWithScores：获取指定区间内的成员（及其分数）

```go
func (c redis.cmdable) ZRange(ctx context.Context, key string, start int64, stop int64) *redis.StringSliceCmd
func (c redis.cmdable) ZRangeWithScores(ctx context.Context, key string, start int64, stop int64) *redis.ZSliceCmd
```

`start`：开始索引。
`stop`：结束索引。

使用示例：
`rdb.ZRange(ctx, zset, start, stop)`
`rdb.ZRangeWithScores(ctx, zset, start, stop)`

#### ZRangeByScore/ZRangeByLex/ZRangeByScoreWithScores：获取指定分数范围/指定字典区间内的成员(及其分数)

```go
type ZRangeBy struct {
    Min, Max      string
    Offset, Count int64
}

func (c redis.cmdable) ZRangeByScore(ctx context.Context, key string, opt *redis.ZRangeBy) *redis.StringSliceCmd
func (c redis.cmdable) ZRangeByLex(ctx context.Context, key string, opt *redis.ZRangeBy) *redis.StringSliceCmd
func (c redis.cmdable) ZRangeByScoreWithScores(ctx context.Context, key string, opt *redis.ZRangeBy) *redis.ZSliceCmd
```

`min`：最小分数/最小字典值。
`max`：最大分数/最大字典值。

使用示例：
`rdb.ZRangeByScore(ctx, zset, min, max)`
`rdb.ZRangeByLex(ctx, zset, min, max)`
`rdb.ZRangeWithScores(ctx, zset, min, max)`

#### ZRangeArgs/ZRangeArgsWithScores：根据给定的参数获取有成员(及其分数)

```go
type ZRangeArgs struct {
    Key string

    // You can read the documentation for more information: https://redis.io/commands/zrange
    Start interface{}
    Stop  interface{}

    // The ByScore and ByLex options are mutually exclusive.
    ByScore bool
    ByLex   bool

    Rev bool

    // limit offset count.
    Offset int64
    Count  int64
}

func (c redis.cmdable) ZRangeArgs(ctx context.Context, z redis.ZRangeArgs) *redis.StringSliceCmd
func (c redis.cmdable) ZRangeArgsWithScores(ctx context.Context, z redis.ZRangeArgs) *redis.ZSliceCmd
```

使用示例：

```go
// 使用 ZRangeArgs 获取有序集合中的成员及其分数
args := redis.ZRangeArgs{
    Key:     "zset",
    Start:   0,
    Stop:    -1,
    ByScore: true,
}
rdb.ZRangeArgs(ctx, args)
rdb.ZRangeArgsWithScores(ctx, args)
```

#### ZRangeStore：将指定范围内的成员存储到另一个集合中

```go
func (c redis.cmdable) ZRangeStore(ctx context.Context, dst string, z redis.ZRangeArgs) *redis.IntCmd
```

使用示例：

```go
// 使用 ZRangeStore 将有序集合中的成员存储到另一个集合中
args := redis.ZRangeArgs{
    Key:     "zset",
    Start:   0,
    Stop:    -1,
    ByScore: true,
}
result := rdb.ZRangeStore(ctx, "zset_dest", args)
```

#### ZRevRange/ZRevRangeWithScores：获取指定范围内的成员(及其分数)，按分数从高到低排序

```go
func (c redis.cmdable) ZRevRange(ctx context.Context, key string, start int64, stop int64) *redis.StringSliceCmd
func (c redis.cmdable) ZRevRangeWithScores(ctx context.Context, key string, start int64, stop int64) *redis.ZSliceCmd
```

使用示例：
`rdb.ZRevRange(ctx, zset, start, stop)`
`rdb.ZRevRangeWithScores(ctx, zset, start, stop)`

#### ZRevRangeByScore/ZRevRangeByLex/ZRevRangeByScoreWithScores：获取指定分数范围/指定字典范围内的成员(及其分数)，按分数从高到低排序

```go
type ZRangeBy struct {
    Min, Max      string
    Offset, Count int64
}
func (c redis.cmdable) ZRevRangeByScore(ctx context.Context, key string, opt *redis.ZRangeBy) *redis.StringSliceCmd
func (c redis.cmdable) ZRevRangeByLex(ctx context.Context, key string, opt *redis.ZRangeBy) *redis.StringSliceCmd
func (c redis.cmdable) ZRevRangeByScoreWithScores(ctx context.Context, key string, opt *redis.ZRangeBy) *redis.ZSliceCmd
```

使用示例：

```go
// 获取有序集合中指定分数范围内的成员，按分数从高到低排序
opt := &redis.ZRangeBy{
    Min: "-inf",
    Max: "+inf",
}
rdb.ZRevRangeByScore(ctx, zset, opt)
rdb.ZRevRangeByScoreWithScores(ctx, zset, opt)
// 获取有序集合中指定字典范围内的成员，按字典顺序从高到低排序
opt2 := &redis.ZRangeBy{
    Min: "[a",
    Max: "[c",
}
rdb.ZRevRangeByLex(ctx, zset, opt)
```

#### ZRank/ZRankWithScore：获取指定成员的排名(及其分数)

```go
func (c redis.cmdable) ZRank(ctx context.Context, key string, member string) *redis.IntCmd
func (c redis.cmdable) ZRankWithScore(ctx context.Context, key string, member string) *redis.RankWithScoreCmd
```

使用示例：
`rdb.ZRank(ctx, zset, mem)`
`rdb.ZRankWithScore(ctx, zset, mem)`

#### ZRevRank/ZRevRankWithScore：获取指定成员的逆序排名（及其分数）

```go
func (c redis.cmdable) ZRevRank(ctx context.Context, key string, member string) *redis.IntCmd
func (c redis.cmdable) ZRevRankWithScore(ctx context.Context, key string, member string) *redis.RankWithScoreCmd
```

使用示例：
`rdb.ZRevRank(ctx, zset, mem)`
`rdb.ZRevRankWithScore(ctx, zset, mem)`

#### ZRem/ZRemRangeByRank/ZRemRangeByScore/ZRemRangeByLex：移除（指定排名范围/指定分数范围/指定字典范围 内的）一个或多个成员

```go
func (c redis.cmdable) ZRem(ctx context.Context, key string, members ...interface{}) *redis.IntCmd
func (c redis.cmdable) ZRemRangeByRank(ctx context.Context, key string, start int64, stop int64) *redis.IntCmd
func (c redis.cmdable) ZRemRangeByScore(ctx context.Context, key string, min string, max string) *redis.IntCmd
func (c redis.cmdable) ZRemRangeByLex(ctx context.Context, key string, min string, max string) *redis.IntCmd
```

使用示例：
`rdb.ZRem(ctx, zset, mem1, mem2...)`
`rdb.ZRemRangeByRank(ctx, zset, start, stop)`
`rdb.ZRemRangeByScore(ctx, zset, min, max)`
`rdb.ZRemRangeByLex(ctx, zset, min, max)`

#### ZRandMember/ZRandMemberWithScores：随机获取有序集合中的一个或多个成员（及其分数）

```go
func (c redis.cmdable) ZRandMember(ctx context.Context, key string, count int) *redis.StringSliceCmd
func (c redis.cmdable) ZRandMemberWithScores(ctx context.Context, key string, count int) *redis.ZSliceCmd
```

使用示例：
`rdb.ZRandMember(ctx, zset, cnt)`
`rdb.ZRandMemberWithScores(ctx, zset, cnt)`

#### ZUnion/ZUnionWithScores：计算多个有序集合的并集（及其分数）

```go
// ZStore is used as an arg to ZInter/ZInterStore and ZUnion/ZUnionStore.
type ZStore struct {
    Keys    []string
    Weights []float64
    // Can be SUM, MIN or MAX.
    Aggregate string
}
func (c redis.cmdable) ZUnion(ctx context.Context, store redis.ZStore) *redis.StringSliceCmd
func (c redis.cmdable) ZUnionWithScores(ctx context.Context, store redis.ZStore) *redis.ZSliceCmd
```

使用示例：

```go
// 计算多个有序集合的并集
store := redis.ZStore{
    Keys:    []string{"zset1", "zset2"},
    Weights: []float64{1, 1},
}
result := rdb.ZUnion(ctx, store)
result := rdb.ZUnionWithScores(ctx, store)
```

#### ZUnionStore：将多个有序集合的并集存储到一个新的有序集合中

```go
// ZStore is used as an arg to ZInter/ZInterStore and ZUnion/ZUnionStore.
type ZStore struct {
    Keys    []string
    Weights []float64
    // Can be SUM, MIN or MAX.
    Aggregate string
}
func (c redis.cmdable) ZUnionStore(ctx context.Context, dest string, store *redis.ZStore) *redis.IntCmd
```

使用示例：

```go
// 将多个有序集合的并集存储到一个新的有序集合中
store := &redis.ZStore{
    Keys:    []string{"zset1", "zset2"},
    Weights: []float64{1, 1},
}
result := rdb.ZUnionStore(ctx, "zunion", store)
```

#### ZDiff/ZDiffWithScores：计算多个有序集合的差集（及其分数）

```go
func (c redis.cmdable) ZDiff(ctx context.Context, keys ...string) *redis.StringSliceCmd
func (c redis.cmdable) ZDiffWithScores(ctx context.Context, keys ...string) *redis.ZSliceCmd
```

使用示例：
`rdb.ZDiff(ctx, zset1, zset2...)`
`rdb.ZDiffWithScores(ctx, zset1, zset2...)`

#### ZDiffStore：将多个有序集合的差集存储到一个新的有序集合中

```go
func (c redis.cmdable) ZDiffStore(ctx context.Context, destination string, keys ...string) *redis.IntCmd
```

使用示例：
`rdb.ZDiffStore(ctx, zset_dest, zset1, zset2...)`

#### ZScan：迭代有序集合中的成员

```go
func (c redis.cmdable) ZScan(ctx context.Context, key string, cursor uint64, match string, count int64) *redis.ScanCmd
```

cursor：迭代游标。
match：匹配模式。

使用示例：
`rdb.ZScan(ctx, zset, cursor, "*", 10)`

## 高级数据结构

### 位图（Bitmaps）

Redis 的 bitmap 是一种位数组，通常用于高效地处理大量二进制数据。

#### GetBit - 获取位图中指定偏移量的值

```go
func (c redis.cmdable) GetBit(ctx context.Context, key string, offset int64) *redis.IntCmd
```

使用示例：
`rdb.GetBit(ctx, bitmap, offset)`

#### SetBit - 设置位图中指定偏移量的值

```go
func (c redis.cmdable) SetBit(ctx context.Context, key string, offset int64, value int) *redis.IntCmd
```

使用示例：
`rdb.GetBit(ctx, bitmap, offset, value)`

#### BitCount - 计算位图中值为 1 的位数

```go
type BitCount struct {
    Start, End int64
    Unit       string // BYTE(default) | BIT
}
func (c redis.cmdable) BitCount(ctx context.Context, key string, bitCount *redis.BitCount) *redis.IntCmd
```

使用示例：

```go
// 计算位图中值为 1 的位数，指定范围为 0 到 7
bitCount := &redis.BitCount{
    Start: 0,
    End:   7,
}
rdb.BitCount(ctx, bitmap, bitCount)
```

#### BitOpAnd - 对一个或多个位图执行 AND操作，并将结果存储在目标位图中

```go
func (c redis.cmdable) BitOpAnd(ctx context.Context, destKey string, keys ...string) *redis.IntCmd
```

使用示例：
`rdb.BitOpAnd(ctx, bitmap_dest, bitmap1, bitmap2...)`

#### BitOpOr - 对一个或多个位图执行 OR 操作，并将结果存储在目标位图中

```go
func (c redis.cmdable) BitOpOr(ctx context.Context, destKey string, keys ...string) *redis.IntCmd
```

使用示例：
`rdb.BitOpOr(ctx, bitmap_dest, bitmap1, bitmap2...)`

#### BitOpXor - 对一个或多个位图执行 XOR 操作，并将结果存储在目标位图中

```go
func (c redis.cmdable) BitOpXor(ctx context.Context, destKey string, keys ...string) *redis.IntCmd
```

使用示例：
`rdb.BitOpOr(ctx, bitmap_dest, bitmap1, bitmap2...)`

#### BitOpNot - 对位图执行取反(NOT)操作，并将结果存储在目标位图中

```go
func (c redis.cmdable) BitOpNot(ctx context.Context, destKey string, key string) *redis.IntCmd
```

使用示例：
`rdb.BitOpOr(ctx, bitmap_dest, bitmap1   )`

#### BitPos - 查找位图中第一个设置为指定值的位的位置

```go
func (c redis.cmdable) BitPos(ctx context.Context, key string, bit int64, pos ...int64) *redis.IntCmd
```

使用示例：
`rdb.BitPos(ctx, bitmap, pos1, pos2...)`

#### BitPosSpan - 查找指定范围内第一个设置为指定值的位的位置

```go
func (c redis.cmdable) BitPosSpan(ctx context.Context, key string, bit int8, start int64, end int64, span string) *redis.IntCmd
```

`span`：字符串，表示跨度（byte | bit，redis 7.0.0）。

使用示例：
`rdb.BitPosSpan(ctx, bitmap, start, end, span)`

#### BitField - 执行多个位域操作

```go
func (c redis.cmdable) BitField(ctx context.Context, key string, values ...interface{}) *redis.IntSliceCmd
```

`values`：接口，可变参数，表示多个位域操作。

使用示例：

```go
BitField("set", "i1", "offset1", "value1","cmd2", "type2", "offset2", "value2")
BitField([]string{"cmd1", "type1", "offset1", "value1","cmd2", "type2", "offset2", "value2"})
BitField([]interface{}{"cmd1", "type1", "offset1", "value1","cmd2", "type2", "offset2", "value2"})
```

### 超日志（HyperLogLogs）

HyperLogLog 是一种概率数据结构，用于估算基数（即去重后元素的数量）。它在提供极小空间消耗的同时，能够在一定误差范围内高效地计算基数。相较于传统的计数数据结构，HyperLogLog 能在处理海量数据时保持极低的内存消耗。

#### 基数估算

基数就是指一个集合中不同值的数目，比如 a, b, c, d 的基数就是 4，a, b, c, d, a 的基数还是 4。虽然 a 出现两次，只会被计算一次。

基数估算指的是对一个集合中唯一元素数量的估算。传统的计算方法往往需要记录每个元素，从而消耗大量内存。而 HyperLogLog 则通过概率算法提供了一种高效的估算方法，使其能够在有限的内存中处理海量数据。

#### PFAdd - 将指定元素添加到 HyperLogLog

```go
func (c redis.cmdable) PFAdd(ctx context.Context, key string, els ...interface{}) *redis.IntCmd
```

使用示例：
`rdb.PFAdd(ctx, key, els1, els2...)`

返回结果：返回一个 `*IntCmd`，结果为 1 表示 HyperLogLog 被修改，0 表示没有修改。

#### PFCount - 返回给定 HyperLogLog 的基数估算值

```go
func (c redis.cmdable) PFCount(ctx context.Context, keys ...string) *redis.IntCmd
```

使用示例：
`rdb.PFCount(ctx, key)`

#### PFMerge - 将多个 HyperLogLog 合并为一个

```go
func (c redis.cmdable) PFMerge(ctx context.Context, dest string, keys ...string) *redis.StatusCmd
```

使用示例：
`rdb.PFCount(ctx, key_dest, key1, key2...)`

### 地理空间（Geospatial）

Redis 的 GEO 地理空间数据结构允许我们存储、查询和操作地理空间信息。通过 GEO 命令，我们可以实现类似于地理信息系统（GIS）的一些功能，比如添加地理位置、计算距离、查询附近的点等。

#### GeoAdd - 添加地理空间位置

```go
type GeoLocation struct {
    Name                      string
    Longitude, Latitude, Dist float64
    GeoHash                   int64
}

func (c redis.cmdable) GeoAdd(ctx context.Context, key string, geoLocation ...*redis.GeoLocation) *redis.IntCmd
```

使用示例：
`rdb.GeoAdd(ctx, geo, loc1, loc2...)`

#### GeoPos - 获取地理空间位置

```go
func (c redis.cmdable) GeoPos(ctx context.Context, key string, members ...string) *redis.GeoPosCmd
```

使用示例：
`rdb.GeoAdd(ctx, geo, mem1, mem2...)`

#### GeoRadius - 根据经纬度查询附近的地理位置

```go
type GeoRadiusQuery struct {
    Radius float64
    // Can be m, km, ft, or mi. Default is km.
    Unit        string
    WithCoord   bool
    WithDist    bool
    WithGeoHash bool
    Count       int
    // Can be ASC or DESC. Default is no sort order.
    Sort      string
    Store     string
    StoreDist string

    // WithCoord+WithDist+WithGeoHash
    withLen int
}

func (c redis.cmdable) GeoRadius(ctx context.Context, key string, longitude float64, latitude float64, query *redis.GeoRadiusQuery) *redis.GeoLocationCmd
```

`longitude`：查询中心点的经度。
`latitude`：查询中心点的纬度。
`query`：查询参数，类型为`*GeoRadiusQuery`，包含半径、单位等。

使用示例：

```go
query := &redis.GeoRadiusQuery{
        Radius:      1,
        Unit:        "km", // Can be m, km, ft, or mi. Default is km.
        WithCoord:   true,
        WithDist:    true,
        WithGeoHash: true,
        Count:       10,
        Sort:        "asc", // Can be ASC or DESC. Default is no sort order.
    }
rdb.GeoRadius(ctx, geo, longitude, latitude, query)
```

#### GeoRadiusStore - 根据经纬度查询附近的地理位置并存储结果

```go
func (c redis.cmdable) GeoRadiusStore(ctx context.Context, key string, longitude float64, latitude float64, query *redis.GeoRadiusQuery) *redis.IntCmd
```

使用示例：

```go
query := &redis.GeoRadiusQuery{
    Radius: 1, // 1公里半径
    Unit:   "km",
    Store:  "china:beijing:nearby", // 存储结果的key
}

result, err := rdb.GeoRadiusStore(ctx, "china:beijing", 116.4039, 39.915, query).Result()
```

#### GeoRadiusByMember - 根据已有成员的位置查询附近的地理位置

```go
func (c redis.cmdable) GeoRadiusByMember(ctx context.Context, key string, member string, query *redis.GeoRadiusQuery) *redis.GeoLocationCmd
```

使用示例：

```go
query := &redis.GeoRadiusQuery{
    Radius:      1,
    Unit:        "km",
    WithCoord:   true,
    WithDist:    true,
    WithGeoHash: true,
    Sort:        "asc",
}

rdb.GeoRadiusByMember(ctx, "china:beijing", "PalaceMuseum", query)
```

#### GeoRadiusByMemberStore - 根据已有成员的位置查询附近的地理位置并存储结果

```go
func (c redis.cmdable) GeoRadiusByMemberStore(ctx context.Context, key string, member string, query *redis.GeoRadiusQuery) *redis.IntCmd
```

使用示例：

```go
query := &redis.GeoRadiusQuery{
    Radius: 1, // 1公里半径
    Unit:   "km",
    Store:  "china:beijing:nearby", // 存储结果的key
}

rdb.GeoRadiusByMemberStore(ctx, "china:beijing", "PalaceMuseum", query)
```

#### GeoSearch - 根据不同条件搜索地理位置

```go
type GeoSearchQuery struct {
    Member string

    // Latitude and Longitude when using FromLonLat option.
    Longitude float64
    Latitude  float64

    // Distance and unit when using ByRadius option.
    // Can use m, km, ft, or mi. Default is km.
    Radius     float64
    RadiusUnit string

    // Height, width and unit when using ByBox option.
    // Can be m, km, ft, or mi. Default is km.
    BoxWidth  float64
    BoxHeight float64
    BoxUnit   string

    // Can be ASC or DESC. Default is no sort order.
    Sort     string
    Count    int
    CountAny bool
}

func (c redis.cmdable) GeoSearch(ctx context.Context, key string, q *redis.GeoSearchQuery) *redis.StringSliceCmd
```

使用示例：

```go
query = &redis.GeoSearchQuery{
  Member:     "",
  Longitude:  116.4039,
  Latitude:   39.915,
  Radius:     1,
  RadiusUnit: "km",
  BoxWidth:   0.0,
  BoxHeight:  0.0,
  BoxUnit:    "",
  Sort:       "asc",
  Count:      0,  // 指定查询结果返回的最大数量。
  CountAny:   false,  // CountAny为false或未设置，则只会返回精确匹配的结果，数量等于Count指定的数量。当CountAny设置为true时，Redis将尽可能返回接近Count指定数量的结果，允许结果集包含不精确的匹配。
 }
rdb.GeoSearch(ctx, "china:beijing", query).Result()
```

#### GeoSearchLocation - 根据不同条件搜索地理位置并返回详细信息

```go
type GeoSearchLocationQuery struct {
    GeoSearchQuery

    WithCoord bool
    WithDist  bool
    WithHash  bool
}
// Embedded fields:
Member     string  // through GeoSearchQuery 
Longitude  float64 // through GeoSearchQuery 
Latitude   float64 // through GeoSearchQuery 
Radius     float64 // through GeoSearchQuery 
RadiusUnit string  // through GeoSearchQuery 
BoxWidth   float64 // through GeoSearchQuery 
BoxHeight  float64 // through GeoSearchQuery 
BoxUnit    string  // through GeoSearchQuery 
Sort       string  // through GeoSearchQuery 
Count      int     // through GeoSearchQuery 
CountAny   bool    // through GeoSearchQuery 

func (c redis.cmdable) GeoSearchLocation(ctx context.Context, key string, q *redis.GeoSearchLocationQuery) *redis.GeoSearchLocationCmd
```

使用示例：

```go
query = &redis.GeoSearchLocationQuery{
    GeoSearchQuery: redis.GeoSearchQuery{
        Member:     "",
        Longitude:  116.4039,
        Latitude:   39.915,
        Radius:     1, // 1公里半径
        RadiusUnit: "km",
        BoxWidth:   0.0,
        BoxHeight:  0.0,
        BoxUnit:    "",
        Sort:       "asc",
        Count:      0,
        CountAny:   false,
    },
    WithCoord: true,
    WithDist:  true,
    WithHash:  true,
}
rdb.GeoSearchLocation(ctx, "china:beijing", query)
```

#### GeoSearchStore - 根据不同条件搜索地理位置并存储结果

```go
func (c redis.cmdable) GeoSearchStore(ctx context.Context, key string, store string, q *redis.GeoSearchStoreQuery) *redis.IntCmd
```

使用示例：
`rdb.GeoSearchStore(ctx, geo, geo_store, query)`

#### GeoDist - 计算两个地理位置之间的距离

```go
func (c redis.cmdable) GeoDist(ctx context.Context, key string, member1 string, member2 string, unit string) *redis.FloatCmd
```

`unit`：距离单位，如m（米）、km（公里）、mi（英里）、ft（英尺）。
使用示例：
`rdb.GeoDist(ctx, geo, mem1, mem2, unit)`

#### GeoHash - 获取地理位置的哈希表示

```go
func (c redis.cmdable) GeoHash(ctx context.Context, key string, members ...string) *redis.StringSliceCmd
```

使用方法：
`rdb.GeoDist(ctx, geo, mem1, mem2...)`

### 流（Streams）

Redis Stream 主要用于消息队列（MQ，Message Queue）,提供了消息的持久化和主备复制功能，可以让任何客户端访问任何时刻的数据，并且能记住每一个客户端的访问位置，还能保证消息不丢失。

#### redis.XAddArgs

```go
type XAddArgs struct {
    Stream     string
    NoMkStream bool
    MaxLen     int64 // MAXLEN N
    MinID      string
    // Approx causes MaxLen and MinID to use "~" matcher (instead of "=").
    Approx bool
    Limit  int64
    ID     string
    Values interface{}
}
```

- `Stream`      插入的stream键值
- `NoMkStream`  如果设置了 NoMkStream 为 true，并且目标 Stream 不存在，则 XADD 命令将返回一个错误，而不是创建一个新的 Stream
- `MaxLen`      最大长度
- `MinID`       读取时指定最小的条目 ID
- `Approx`      当 MaxLen 设置时，此标志指示是否使用近似裁剪策略。
- `Limit`       限制从 Stream 中读取的条目数量
- `ID`          指定条目的 ID。如果为空，则由 Redis 自动生成。

XAddArgs 接受如下格式的值:

```go
XAddArgs.Values = []interface{}{"key1", "value1", "key2", "value2"}
XAddArgs.Values = []string("key1", "value1", "key2", "value2")
XAddArgs.Values = map[string]interface{}{"key1": "value1", "key2": "value2"}
```

注意，map不会保留键值对的顺序。MaxLen/MaxLenApprox和MinID冲突，只能使用其中一个。

#### redis.XReadArgs

```go
type XReadArgs struct {
    Streams []string // list of streams and ids, e.g. stream1 stream2 id1 id2
    Count   int64
    Block   time.Duration
    ID      string
}
```

- `Streams` stream和id的列表 e.g. stream1 stream2 id1 id2
- `Count`   读取数量
- `Block`   阻塞时间
- `ID`      从哪个 ID 开始读取条目。如果设置了 Streams 映射，则 ID 字段将被忽略。

#### redis.XReadGroupArgs

```go
type XReadGroupArgs struct {
    Group    string
    Consumer string
    Streams  []string // list of streams and ids, e.g. stream1 stream2 id1 id2
    Count    int64
    Block    time.Duration
    NoAck    bool
}
```

- `Group` 指定
- `Consumer` 指定消费者
- `Streams` 用于指定从哪些 Stream 读取条目以及从哪个最小 ID 开始读取。
- `Count` 返回的条目数量。
- `Block` 指定阻塞时间。
- `NoAck` 禁用自动确认。

#### XAdd - 添加消息到末尾

```go
func (c redis.cmdable) XAdd(ctx context.Context, a *redis.XAddArgs) *redis.StringCmd
```

使用示例：

```go
xAddArgs := &redis.XAddArgs{
    Stream: "stream",
    MaxLen: 1000,
    Approx: true,
    ID:     "",
    Values: []interface{}{"key1", "valve1", "key2", "value2"},
}
rdb.XAdd(ctx, xAddArgs)
```

#### XTrimMaxLen/XTrimMaxLenApprox 基于长度裁剪

```go
func (c redis.cmdable) XTrimMaxLen(ctx context.Context, key string, maxLen int64) *redis.IntCmd
func (c redis.cmdable) XTrimMaxLenApprox(ctx context.Context, key string, maxLen int64, limit int64) *redis.IntCmd
```

使用示例：
`cdb.XTrimMaxLen(ctx, stream, maxLen)`
`cdb.XTrimMaxLenApprox(ctx, stream, maxLen, limit)`

#### XTrimMinID/XTrimMinIDApprox 基于ID裁剪

```go
func (c redis.cmdable) XTrimMinID(ctx context.Context, key string, minID string) *redis.IntCmd
func (c redis.cmdable) XTrimMinIDApprox(ctx context.Context, key string, minID string, limit int64) *redis.IntCmd
```

使用示例：
`cdb.XTrimMinID(ctx, stream, minID)`
`cdb.XTrimMinIDApprox(ctx, stream, minID, limit)`

#### XDel 删除消息

```go
func (c redis.cmdable) XDel(ctx context.Context, stream string, ids ...string) *redis.IntCmd
```

使用示例：
`cdb.XDel(ctx, stream, id1, id2...)`

#### XLen 获取流包含的元素数量，即消息长度

```go
func (c redis.cmdable) XLen(ctx context.Context, stream string) *redis.IntCmd
```

使用示例：
`cdb.XLen(ctx, stream)`

#### XRange/XRevRange 获取消息列表，会自动过滤已经删除的消息

```go
func (c redis.cmdable) XRange(ctx context.Context, stream string, start string, stop string) *redis.XMessageSliceCmd
func (c redis.cmdable) XRevRange(ctx context.Context, stream string, start string, stop string) *redis.XMessageSliceCmd
```

`start` ：开始值， - 表示最小值
`end` ：结束值， + 表示最大值

使用示例：
`rdb.XRange(ctx, stream, "0-0", "+")`
`rdb.XRevRange(ctx, stream, "+", "-")`

#### XRead/XReadGroup/XReadStreams 获取消息列表

```go
func (c redis.cmdable) XRead(ctx context.Context, a *redis.XReadArgs) *redis.XStreamSliceCmd
func (c redis.cmdable) XReadGroup(ctx context.Context, a *redis.XReadGroupArgs) *redis.XStreamSliceCmd
func (c redis.cmdable) XReadStreams(ctx context.Context, streams ...string) *redis.XStreamSliceCmd
```

#### XGroupCreate/XGroupCreateConsumer/XGroupCreateMkStream 创建消费者（组）

```go
func (c redis.cmdable) XGroupCreate(ctx context.Context, stream string, group string, start string) *redis.StatusCmd
func (c redis.cmdable) XGroupCreateConsumer(ctx context.Context, stream string, group string, consumer string) *redis.IntCmd
func (c redis.cmdable) XGroupCreateMkStream(ctx context.Context, stream string, group string, start string) *redis.StatusCmd
```

`XGroupCreateMkStream`：如果 Stream 不存在，则会自动创建一个新的 Stream。

#### XAck 将消息标记为"已处理"

```go
func (c redis.cmdable) XAck(ctx context.Context, stream string, group string, ids ...string) *redis.IntCmd
```

#### XGroupSetID 为消费者组设置新的最后递送消息ID

```go
func (c redis.cmdable) XGroupSetID(ctx context.Context, stream string, group string, start string) *redis.StatusCmd
```

#### XGroupDelConsumer 删除消费者

```go
func (c redis.cmdable) XGroupDelConsumer(ctx context.Context, stream string, group string, consumer string) *redis.IntCmd
```

#### XGroupDestroy 删除消费者组

```go
func (c redis.cmdable) XGroupDestroy(ctx context.Context, stream string, group string) *redis.IntCmd
```

#### XPending/XPendingExt 示待处理消息的相关信息

#### XClaim/XClaimJustID/ 转移消息的归属权

#### XAutoClaim/XAutoJustID/ 转移消息的归属权

#### XInfoStream/XInfoGroups/XInfoConsumers 打印信息

## 其他

### 键（key）

#### Del 删除键

```go
func (c redis.cmdable) Del(ctx context.Context, keys ...string) *redis.IntCmd
```

使用示例：`rdb.LRem(ctx,key)`

返回值：被删除 key 的数量。

#### Dump 序列化键

- 序列化：把对象转化为可传输的字节序列过程称为序列化。
- 反序列化：把字节序列还原为对象的过程称为反序列化。

序列化最终的目的是为了对象可以跨平台存储，和进行网络传输。而我们进行跨平台存储和网络传输的方式就是IO，而我们的IO支持的数据格式就是字节数组。

```go
func (c redis.cmdable) Dump(ctx context.Context, key string) *redis.StringCmd
```

使用示例：`rdb.Dump(ctx,key)`

返回值：如果 key 不存在，那么返回 nil 。 否则，返回序列化之后的值。

#### Exists 检查键是否存在

```go
func (c redis.cmdable) Exists(ctx context.Context, keys ...string) *redis.IntCmd
```

使用示例：`rdb.Exists(ctx,key)`

返回值：若 key 存在返回 1 ，否则返回 0 。

#### Expire 设置过期时间

```go
func (c redis.cmdable) Expire(ctx context.Context, key string, expiration time.Duration) *redis.BoolCmd
```

使用示例：`rdb.Expire(ctx,key 5*Time.Second)`

返回值：设置成功返回 1 。 当 key 不存在或者不能为 key 设置过期时间时返回 0 。

#### ExpireAt 设置过期时间（时间戳）

```go
func (c redis.cmdable) ExpireAt(ctx context.Context, key string, tm time.Time) *redis.BoolCmd
```

使用示例：`rdb.ExpireAt(ctx,key，time.Now().Add(10*time.Second))`

返回值：设置成功返回 1 。 当 key 不存在或者不能为 key 设置过期时间时返回 0 。

#### Keys 查找符合模式的key

```go
func (c redis.cmdable) Keys(ctx context.Context, pattern string) *redis.StringSliceCmd
```

`pattern`表示匹配模式，语法见下。

使用示例：`rdb.Keys(ctx, "user:*")`

返回值：符合给定模式的 key 列表。

#### Move 移动数据至另一数据库

```go
func (c redis.cmdable) Move(ctx context.Context, key string, db int) *redis.BoolCmd
```

使用示例：`rdb.Move(ctx, key, num_db)`

返回值：移动成功返回 1 ，失败则返回 0 。

#### Persist 移除过期时间

```go
func (c redis.cmdable) Persist(ctx context.Context, key string) *redis.BoolCmd
```

使用示例：`rdb.Persist(ctx, key)`

返回值：移动成功返回 1 ，失败则返回 0 。

#### TTL 返回剩余生存时间

`PTTL`：以毫秒为单位返回 key 的剩余过期时间。

```go
func (c redis.cmdable) TTL(ctx context.Context, key string) *redis.DurationCmd
func (c redis.cmdable) PTTL(ctx context.Context, key string) *redis.DurationCmd
```

使用示例：`rdb.TTL(ctx, key)`

返回值：当 key 不存在时，返回 -2 。 当 key 存在但没有设置剩余生存时间时，返回 -1 。 否则，以秒为单位，返回 key 的剩余生存时间。

#### RandomKey 随机返回一个key

```go
func (c redis.cmdable) RandomKey(ctx context.Context) *redis.StringCmd
```

使用示例：`rdb.RandomKey(ctx)`

返回值：当数据库不为空时，返回一个 key 。 当数据库为空时，返回 nil 。

#### Rename 修改键的名称

```go
func (c redis.cmdable) Rename(ctx context.Context, key string, newkey string) *redis.StatusCmd
```

使用示例：`rdb.Rename(ctx, key, newkey)`

返回值：成功返回OK，失败返回错误。

#### RenameNX 修改键的名称（仅当新键不存在时）

```go
func (c redis.cmdable) RenameNX(ctx context.Context, key string, newkey string) *redis.BoolCmd
```

使用示例：`rdb.RenameNX(ctx, key, newkey)`

返回值：成功返回1，新键已存在返回0。

#### Scan 迭代数据库中的键

```go
func (c redis.cmdable) Scan(ctx context.Context, cursor uint64, match string, count int64) *redis.ScanCmd
```

使用示例：`rdb.Scan(ctx, cursor, match, count)`

返回值：数组列表。

#### Type 返回key所储存的值的类型

```go
func (c redis.cmdable) Type(ctx context.Context, key string) *redis.StatusCmd
```

使用示例：`rdb.Type(ctx, key)`

返回值：数组列表。

#### 匹配模式

- `*`：匹配零个或多个任意字符。
- `?`：匹配单个任意字符。
- `[set]`：匹配括号内的任何一个字符。
- `[!set]`：匹配不在括号内的任何一个字符。

### 发布/订阅（Pub/Sub）

- `Subscribe` - 订阅一个或多个频道，返回一个 PubSub 对象。
- `PSubscribe` - 订阅一个或多个模式匹配的频道。
- `Unsubscribe` - 取消订阅一个或多个频道。
- `PUnsubscribe` - 取消订阅一个或多个模式匹配的频道。
- `Publish` - 向一个频道发布消息。
- `ReceiveMessage` - 接收订阅频道的消息。
- `Close` - 关闭 PubSub 对象，取消所有订阅。
- `PubSubChannels` - 查询活跃的频道。
- `PubSubNumSub` - 查询指定频道有多少个订阅者。
- `ReceiveTimeout` - 在指定时间内接收消息，超时则返回错误。
- `Receive` - 接收消息或返回其他类型的信息，如 Subscription、Message、Pong 等。
- `Channel` - 返回一个 Go channel，用于并发接收消息。
- `ChannelWithSubscriptions` - 返回一个 Go channel，消息类型包括*Subscription和*Message，用于检测重新连接。

#### 接收发布示例

```go
 ctx := context.Background()
 rdb := redis.NewClient(&redis.Options{
  Addr: "localhost:6379", // Redis 服务器地址
 })
 // 启动订阅者
 go subscriber(ctx, rdb)
 // 启动发布者
 go publisher(ctx, rdb)

// subscriber 订阅频道并接收消息
func subscriber(ctx context.Context, rdb *redis.Client) {
 pubsub := rdb.Subscribe(ctx, "mychannel")
 defer pubsub.Close()
 ch := pubsub.Channel()
 for msg := range ch {
  fmt.Printf("Received message from channel %s: %s\n", msg.Channel, msg.Payload)
 }
}

// publisher 发布消息到频道
func publisher(ctx context.Context, rdb *redis.Client) {
 messages := []string{"Hello", "World", "Redis", "PubSub", "Example"}
 for _, msg := range messages {
  fmt.Printf("Publishing message: %s\n", msg)
  err := rdb.Publish(ctx, "mychannel", msg).Err()
  time.Sleep(1 * time.Second) // 等待1秒钟再发布下一个消息
 }
 fmt.Println("All messages published.")
}
```

#### 不同接收方法区别

- `Receive`：用于接收所有类型的消息（`*redis.Message`、`*redis.Subscription`、`*redis.Pong`）。
- `ReceiveMessage`：用于接收 `*redis.Message` 类型的消息，专注于 PubSub 消息。
- `ReceiveTimeout`：类似于 Receive，但支持超时控制，适用于需要等待消息但希望避免长时间阻塞的场景。
- `Channel`：提供了异步和并发接收消息的机制，适合需要处理消息流的场景。

**Receive**
功能：`Receive` 是一个通用的方法，用于接收任何类型的消息。它可以返回 `*redis.Message`（消息类型）、`*redis.Subscription`（订阅类型）或 `*redis.Pong`（Pong 类型）。
适用场景：当你需要处理多种类型的 PubSub 消息时使用，特别是当你需要从 PubSub 订阅中接收连接检测响应（`*redis.Pong`）时。

**ReceiveMessage**
功能：`ReceiveMessage` 方法专门用于接收 `*redis.Message` 类型的消息。如果接收到其他类型的消息（如 `*redis.Subscription` 或 `*redis.Pong`），它将返回错误。
适用场景：当你只关心 PubSub 消息，而不需要处理其他类型的消息时使用。

**ReceiveTimeout**
功能：`ReceiveTimeout` 方法类似于 Receive，但它支持超时控制。如果在指定的时间内未收到任何消息，将返回 `context.DeadlineExceeded` 错误。它可以接收 `*redis.Message`、`*redis.Subscription` 和 `*redis.Pong` 类型的消息。
适用场景：当你希望在指定时间内等待消息时使用，适用于高延迟或网络不稳定的环境，能够防止因长时间等待而阻塞程序。

**Channel**
功能：通过 `Channel` 方法，你可以获取一个 Go channel 用于并发接收 PubSub 消息。该 channel 会持续接收 `*redis.Message` 和 `*redis.Subscription` 类型的消息。
适用场景：当你需要并发处理消息，或者希望以异步方式处理消息流时使用。使用 channel 还可以让你更方便地处理消息，并在处理过程中实现更好的消息同步。
示例：

### 管道和事务

### Redis集群

### Redis哨兵

### Redis分片

### AOF 日志

AOF 默认不开启，需要修改`redis.conf`

```conf
appendonly      yes                 // 表示是否开启AOF持久化，默认关闭
appendfilename  "appendonly.aof"    // AOF持久化文件名称
```

顺序：**先执行命令，再写入日志**

好处：

- 避免额外的检查开销
- 不会阻塞当前写操作命令的执行

风险：

- 丢失的风险
- 可能会给「下一个」命令带来阻塞风险。

#### 三种写回策略

- `Always`      操作命令执行完后，同步写回硬盘
- `Everysec`    先写入内核缓冲区，每隔一秒写回硬盘
- `No`          不由redis控制，由操作系统决定

业务场景选择：

- 如果要高性能，就选择 No 策略；
- 如果要高可靠，就选择 Always 策略；
- 如果允许数据丢失一点，但又想性能高，就选择 Everysec 策略。

#### AOF重写机制

### RDB 快照

RDB快照记录某一时刻的内存数据。

有`save`和`bgsave`两种命令，区别在后者创建子进程来生成RDB文件 **避免阻塞** 。

Redis 的快照是**全量快照**，也就是说每次执行快照，都是把内存中的「所有数据」都记录到磁盘中。所以不能频繁执行影响性能。

#### 写时复制技术

（Copy-On-Write, COW）

（Copy-On-Write, COW）

执行 `bgsave` 命令的时候，会通过 `fork()` 创建子进程，此时子进程和父进程是共享同一片内存数据的，因为创建子进程的时候，会复制父进程的页表，但是页表指向的物理内存还是一个。只有在发生修改内存数据的情况时，物理内存才会被复制一份。
