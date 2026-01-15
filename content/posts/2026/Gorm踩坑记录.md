---
title: Gorm踩坑记录
date: '2026-01-15T09:28:54+08:00'
tags: 
- Go
categories: 
- 问题
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# Gorm踩坑记录

Gorm是一个很好用的orm框架，也是go目前使用最广的orm框架之一。它有很多隐式转换帮我们屏蔽了一些数据库细节，让我们能专注于业务逻辑的开发。但有时也可能“好心办坏事”，导致一些问题。于是我就打算记录一下使用Gorm过程中踩过的那些坑，避免以后再犯。

## gorm实例复用导致sql污染

详见[官方文档](https://gorm.io/zh_CN/docs/method_chaining.html#%E5%8F%AF%E5%A4%8D%E7%94%A8%E6%80%A7%E4%B8%8E%E5%AE%89%E5%85%A8%E6%80%A7)。

简单来说，通过`链式方法`或`结束方法`获取到的`*gorm.DB`实例是**不能安全重用**的。它可能携带先前操作的条件，从而可能导致 SQL 查询受到污染。

```go
queryDB := DB.Where("name = ?", "jinzhu")

// First query
queryDB.Where("age > ?", 10).First(&user)
// SQL: SELECT * FROM users WHERE name = "jinzhu" AND age > 10

// Second query with unintended compounded condition
queryDB.Where("age > ?", 20).First(&user2)
// SQL: SELECT * FROM users WHERE name = "jinzhu" AND age > 10 AND age > 20
```

可以看到，在第二次使用`queryDB`时，生成的sql中仍带有第一次使用的sql。

最简单的处理方式就是使用`Session(gorm.Session{})`创建一个新会话。此外也有一些其他的方式。

```go
db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
// 'db' is a newly initialized *gorm.DB, safe to reuse.

tx := db.Where("name = ?", "jinzhu").Session(&gorm.Session{})
tx := db.Where("name = ?", "jinzhu").WithContext(context.Background())
tx := db.Where("name = ?", "jinzhu").Debug()
// `Session`, `WithContext`, `Debug` methods return a `*gorm.DB` instance marked as safe for reuse. They base a newly initialized `*gorm.Statement` on the current conditions.

// Good case
tx.Where("age = ?", 18).Find(&users)
// SELECT * FROM users WHERE name = 'jinzhu' AND age = 18

// Good case
tx.Where("age = ?", 28).Find(&users)
// SELECT * FROM users WHERE name = 'jinzhu' AND age = 28;
```

其实这种情况还挺常见的，例如查询列表时复用同一个实例去分别`Count`和`Find`。虽然不是很懂为什么会出现这个问题，但以后遇到类似情况也还是注意一下比较好。

## 软删除字段相关

使用`gorm.DeletedAt`类型，或者直接嵌入`gorm.Model`字段，都将直接开启软删除特性。这将导致在使用`Delete`删除时，不会实际删除数据，而是更新软删除字段为当前时间。同时，查询时也会自动添加`deleted_at IS NULL`的sql去过滤已删除数据。

这虽然方便了我们进行操作，但有时这些自动行为是会被绕过的。例如使用`Table`而非`Model`时：

```go
// 查询 - 自动添加 deleted_at IS NULL
global.DB.Model(&User{}).Find(&users)
// 生成: SELECT * FROM users WHERE deleted_at IS NULL

// 删除 - 自动执行软删除（update deleted_at）
global.DB.Model(&User{}).Where("id = ?", 1).Delete(&User{})
// 生成: UPDATE users SET deleted_at = NOW() WHERE id = 1 AND deleted_at IS NULL
```

```go
// 查询 - 需要手动添加 deleted_at IS NULL
global.DB.Table("users").Find(&users)
// 生成: SELECT * FROM users  // 没有软删除条件！

// 删除 - 执行的是硬删除！
global.DB.Table("users").Where("id = ?", 1).Delete(&User{})
// 生成: DELETE FROM users WHERE id = 1  // 直接删除！
```

所以我们日常使用gorm时最好尽量使用`Model`而少使用`Table`。即使有需要用到Table也可以先Model再Teble，例如：

```go
// 场景1：连表时简化表名
query := global.DB.Model(&Course{}).Table("course AS c")
query = query.Joins("LEFT JOIN lesson AS l ON c.id = l.course_id")

// 场景2：分表时获取动态表名
query := global.DB.Model(&Course{}).Table(getCourseTableName(uid))

// 分表函数
func getCourseTableName(uid int64) string {
    return fmt.Sprintf("course_%d", uid%10) // 分10张表
}
```

另一种方法就是显式处理软删除字段，而不是依赖Gorm的自动处理，从而避免踩坑。

## 布尔类型自动转换

mysql中没有专门的布尔数据类型。当使用BOOL/BOOLEAN类型建表时，实际将会转换为TINYINT(1)。
所以如果在模型中定义了一个bool类型字段，再使用`AutoMigrate()`建表，这个字段也会是TINYINT(1)类型。
如果用where+字符串的方式查询，将直接生成sql，结果用true/false去查询tinyint类型。

```go
type Course struct {
    gorm.Model `json:"-"`
    IsTest bool `json:"is_test"`
}

query.Where("is_test = ?", false)  // 异常，WHERE is_test = false
```

由于bool->tinyint的处理是隐式的，所以不注意时很容易出现这个错误。可以直接在查询时将true/false改为1/0来解决。不过还是建议在模型中修改类型并显式声明一下，避免出错。

```go
type Course struct {
    gorm.Model `json:"-"`
    IsTest int8 `json:"is_test" gorm:"default:0;not null;type:tinyint(1)"` // 是否为测试 0-否 1-是
}

query.Where("is_test = ?", 0)  // 正常，WHERE is_test = 0
```

除了mysql，SQLite也没有专门的bool类型，会转换为INTEGER。而PostgreSQL倒是有BOOLEAN类型，不会有这个问题。
