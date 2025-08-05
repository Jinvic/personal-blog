---
title: GORM实现Upsert逻辑
date: '2025-08-05T15:08:18+08:00'
tags: 
- Go
- Sql
categories: 
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# GORM实现Upsert逻辑

Upsert，即"存在时更新，不存在时创建"，是一个很常见的用法。Gorm并没有直接提供 Upsert 方法，但有两种方式可以实现类似逻辑。

## FirstOrCreate + Assign

### FirstOrCreate

> FirstOrCreate 用于获取与特定条件匹配的第一条记录，或者如果没有找到匹配的记录，创建一个新的记录。

可以通过`result.RowsAffected`确定是否创建新纪录。

```go
user := User{
    ID:     111,
    Name:   "jinzhu",
    Age:    18
}

// 如果没找到，就创建一个新纪录
result := db.FirstOrCreate(&user, User{Name: "non_existing"})
// SQL: INSERT INTO "users" (name) VALUES ("non_existing");
// user -> User{ID: 112, Name: "non_existing"}
// result.RowsAffected // => 1 (record created)

// 如果用户已经被找到，不会创建新纪录
result = db.Where(User{Name: "jinzhu"}).FirstOrCreate(&user)
// user -> User{ID: 111, Name: "jinzhu", Age: 18}
// result.RowsAffected // => 0 (no record created)
```

### Attrs和Assign

可以使用 `Attrs` 和 `Assign` 进行赋值。其中：

- `Attrs`：存在时忽略，不存在时赋值
- `Assign`：无论是否存在都会赋值

```go
// 如果没找到，根据额外属性创建新的记录
db.Where(User{Name: "non_existing"}).Attrs(User{Age: 20}).FirstOrCreate(&user)
// SQL: SELECT * FROM users WHERE name = 'non_existing';
// SQL: INSERT INTO "users" (name, age) VALUES ("non_existing", 20);
// user -> User{ID: 112, Name: "non_existing", Age: 20}

// 如果user被找到了，`Attrs` 会被忽略
db.Where(User{Name: "jinzhu"}).Attrs(User{Age: 20}).FirstOrCreate(&user)
// SQL: SELECT * FROM users WHERE name = 'jinzhu';
// user -> User{ID: 111, Name: "jinzhu", Age: 18}

// 如果没找到记录，通过 `Assign` 属性 初始化并且保存新的记录
db.Where(User{Name: "non_existing"}).Assign(User{Age: 20}).FirstOrCreate(&user)
// SQL: SELECT * FROM users WHERE name = 'non_existing';
// SQL: INSERT INTO "users" (name, age) VALUES ("non_existing", 20);
// user -> User{ID: 112, Name: "non_existing", Age: 20}

// 通过 `Assign` 属性 更新记录
db.Where(User{Name: "jinzhu"}).Assign(User{Age: 20}).FirstOrCreate(&user)
// SQL: SELECT * FROM users WHERE name = 'jinzhu';
// SQL: UPDATE users SET age=20 WHERE id = 111;
// user -> User{ID: 111, Name: "Jinzhu", Age: 20}
```

通过`FirstOrCreate`和`Assign`组合使用，即可实现“存在时更新，不存在时创建”的Upsert逻辑。

### FirstOrInit

如果需要分开**查询**和**创建**操作，可以使用`FirstOrInit`。区别是未找到时不会直接创建，而是返回一个结构体。同样可以使用`Attrs`和`Assign`赋值。可以在`FirstOrInit`查询后进行某些操作，再手动`Create`创建。

```go
// 如果没找到 User，根据所给条件和额外属性初始化 User
db.Where(User{Name: "non_existing"}).Attrs(User{Age: 20}).FirstOrInit(&user)
// SQL: SELECT * FROM USERS WHERE name = 'non_existing' ORDER BY id LIMIT 1;
// user -> User{Name: "non_existing", Age: 20} if not found

// 如果名为 “Jinzhu” 的 User 被找到，`Attrs` 会被忽略
db.Where(User{Name: "Jinzhu"}).Attrs(User{Age: 20}).FirstOrInit(&user)
// SQL: SELECT * FROM USERS WHERE name = 'Jinzhu' ORDER BY id LIMIT 1;
// user -> User{ID: 111, Name: "Jinzhu", Age: 18} if found

// 根据所给条件和分配的属性初始化，不管记录是否存在
db.Where(User{Name: "non_existing"}).Assign(User{Age: 20}).FirstOrInit(&user)
// user -> User{Name: "non_existing", Age: 20} if not found

// 如果找到了名为“Jinzhu”的用户，使用分配的属性更新结构体
db.Where(User{Name: "Jinzhu"}).Assign(User{Age: 20}).FirstOrInit(&user)
// SQL: SELECT * FROM USERS WHERE name = 'Jinzhu' ORDER BY id LIMIT 1;
// user -> User{ID: 111, Name: "Jinzhu", Age: 20} if found
```

## clause.OnConflict

参考：[使用Gorm进行批量更新--clause子句的妙用](https://juejin.cn/post/7220043684292411451)

如果需要更细粒度的控制，可以使用`clause.OnConflict`的`DoUpdates`或者`UpdateAll`实现。相关定义如下：

```go
type OnConflict struct {
    Columns      []Column
    Where        Where
    TargetWhere  Where
    OnConstraint string
    DoNothing    bool
    DoUpdates    Set
    UpdateAll    bool
}

type Column struct {
    Table string
    Name  string
    Alias string
    Raw   bool
}

type Set []Assignment

func AssignmentColumns(values []string) Set
func Assignments(values map[string]interface{}) Set

type Assignment struct {
    Column Column
    Value  interface{}
}
```

- `Columns`: 定义重复键冲突时需要检查的列。
- `Where`: 定义检查重复键冲突时的条件。
- `OnConstraint`: 定义检查重复键冲突时使用的约束。
- `DoNothing`: 定义当重复键冲突时不执行任何操作。
- `DoUpdates`: 定义当重复键冲突时执行更新操作，需要传入一个`map[string]interface{}`类型的参数，表示需要更新的列及其对应的值。
- `UpdateAll`: 定义当重复键冲突时更新所有列的值，需要传入一个结构体的指针，表示需要更新的记录。

如上，当遇到冲突需要更新的时候我们需要给`Columns`填入需要检查冲突的列，给`DoUpdates`传入要执行的操作即可。

要为`DoUpdates`赋值，可以使用`Assignments`和`AssignmentColumns`方法。其中：

- `Assignments`: 手动传入需要更新的列和值。
- `AssignmentColumns`： 指定需要更新的列，按结构体实例进行更新。

示例如下：

```go
type User struct {
    ID   uint
    Name string
    Age  int
}

// 使用 Assignments 手动指定要更新的字段及其值
func upsertUser(db *gorm.DB, user User) {
    db.Clauses(clause.OnConflict{
        Columns: []clause.Column{{Name: "id"}}, // 冲突列
        DoUpdates: clause.Assignments(map[string]interface{}{
            "name": user.Name, // 更新 name 字段
            "age":  user.Age,  // 更新 age 字段
        }),
    }).Create(&user)
}

// 使用 AssignmentColumns 自动填充要更新的字段
func upsertUserWithAssignmentColumns(db *gorm.DB, user User) {
    db.Clauses(clause.OnConflict{
        Columns: []clause.Column{{Name: "id"}}, // 冲突列
        DoUpdates: clause.AssignmentColumns([]string{"name", "age"}),
    }).Create(&user)
}
```
