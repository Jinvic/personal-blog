---
title: GORM速查笔记
date: '2024-08-19T16:10:52+08:00'
tags:
- Go
categories:
- 笔记
draft: false
hiddenFromHomePage: true
hiddenFromSearch: true
---

# GORM笔记

---

[官方中文文档](https://gorm.io/zh_CN/docs/)
基本都在抄文档😓
快速入门的话，看看crud，预加载，钩子，事务，迁移就差不多了。更高级的内容有需要再查文档也行。

【1】：简单，基础
【2】：有一定重要性，了解一下
【3】：非常重要，必须掌握
【4】：太难了看不懂

## 入门

### GORM安装【1】

`go get -u gorm.io/gorm`
`go get -u gorm.io/driver/sqlite`

### 连接数据库【1】

```go
 //Data Source Name 数据源名称
 dsn := "root:root@tcp(127.0.0.1:3306)/test?charset=utf8mb4&parseTime=True&loc=Local&&timeout=10s"
 //链接MySQL数据库
 db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})

 if err != nil {
  panic("failed to connect database: " + err.Error())
 }
```

### 自动迁移【1】

```go
 //自动迁移，根据模型生成或更新数据表
 db.AutoMigrate(&User{})
```

### 声明模型

#### 模型定义【1】

gorm是先写好模型，即表结构体，再通过迁移在数据库中建表。goframe的orm是读取数据库中的表生成模型。两者区别还挺大的。个人感觉gorm的模型写起来麻烦些，需要通过标签设置数据库相关选项。

此外关于字段类型，uint，string等基本类型可以直接使用；指向 `*string` 和 `*time.Time` 类型的指针表示可空字段。而来自 `database/sql` 包的 `sql.NullString` 和 `sql.NullTime` 用于具有更多控制的可空字段。

**约定**：

- 主键：GORM 使用一个名为ID 的字段作为每个模型的默认主键。

- 表名：默认情况下，GORM 将结构体名称转换为 snake_case 并为表名加上复数形式。 例如，一个 User 结构体在数据库中的表名变为 users 。

- 列名：GORM 自动将结构体字段名称转换为 snake_case 作为数据库中的列名。

- 时间戳字段：GORM使用字段 CreatedAt 和 UpdatedAt 来自动跟踪记录的创建和更新时间。

**gorm.Model**：

GORM提供了一个预定义的结构体，名为gorm.Model，其中包含常用字段：

```go
// gorm.Model 的定义
type Model struct {
  ID        uint           `gorm:"primaryKey"`
  CreatedAt time.Time
  UpdatedAt time.Time
  DeletedAt gorm.DeletedAt `gorm:"index"`
}
```

可以直接在自己的结构体中嵌入 gorm.Model ，以便自动包含这些字段。

- `ID` ：每个记录的唯一标识符（主键）。
- `CreatedAt` ：在创建记录时自动设置为当前时间。
- `UpdatedAt` ：每当记录更新时，自动更新为当前时间。
- `DeletedAt` ：用于软删除（将记录标记为已删除，而实际上并未从数据库中删除）。

#### 高级选项【嵌入结构体:1 字段标签：3】

**字段级权限控制**:
可导出的字段在使用 GORM 进行 CRUD 时拥有全部的权限，此外，GORM 允许您用标签控制字段级别的权限。这样您就可以让一个字段的权限是只读、只写、只创建、只更新或者被忽略

```go
type User struct {
  Name string `gorm:"<-:create"` // 允许读和创建
  Name string `gorm:"<-:update"` // 允许读和更新
  Name string `gorm:"<-"`        // 允许读和写（创建和更新）
  Name string `gorm:"<-:false"`  // 允许读，禁止写
  Name string `gorm:"->"`        // 只读（除非有自定义配置，否则禁止写）
  Name string `gorm:"->;<-:create"` // 允许读和写
  Name string `gorm:"->:false;<-:create"` // 仅创建（禁止从 db 读）
  Name string `gorm:"-"`  // 通过 struct 读写会忽略该字段
  Name string `gorm:"-:all"`        // 通过 struct 读写、迁移会忽略该字段
  Name string `gorm:"-:migration"`  // 通过 struct 迁移会忽略该字段
}
```

**创建/更新时间追踪**：

GORM 约定使用 CreatedAt、UpdatedAt 追踪创建/更新时间。如果定义了这种字段，GORM 在创建、更新时会自动填充 当前时间.要使用不同名称的字段，可以配置 `autoCreateTime` 、 `autoUpdateTime` 标签。

如果您想要保存 UNIX（毫/纳）秒时间戳，而不是 time，只需简单地将 time.Time 修改为 int 即可

```go
type User struct {
  CreatedAt time.Time // 在创建时，如果该字段值为零值，则使用当前时间填充
  UpdatedAt int       // 在创建时该字段值为零值或者在更新时，使用当前时间戳秒数填充
  Updated   int64 `gorm:"autoUpdateTime:nano"` // 使用时间戳纳秒数填充更新时间
  Updated   int64 `gorm:"autoUpdateTime:milli"` // 使用时间戳毫秒数填充更新时间
  Created   int64 `gorm:"autoCreateTime"`      // 使用时间戳秒数填充创建时间
}
```

**嵌入结构体**:

对于匿名字段，GORM 会将其字段包含在父结构体中
对于正常的结构体字段，也可以通过标签 embedded 将其嵌入
并且，可以使用标签 embeddedPrefix 来为 db 中的字段名添加前缀

```go
type Blog struct {
  ID      int
  Author  Author `gorm:"embedded;embeddedPrefix:author_"`
  Upvotes int32
}
```

**字段标签**
在声明模型时，标记是可选的，GORM支持以下标记:标记不区分大小写，但首选`camelCase`驼峰命名法。如果使用多个标签，它们之间应该用分号(;)分隔。对解析器有特殊意义的字符可以用反斜杠(\\)转义，允许它们用作参数值。

标签名 | 说明
--- | ---
column | 指定 db 列名
type | 列数据类型，推荐使用兼容性好的通用类型，例如：所有数据库都支持 bool、int、uint、float、string、time、bytes 并且可以和其他标签一起使用，例如：not null、size, autoIncrement… 像 varbinary(8) 这样指定数据库数据类型也是支持的。在使用指定数据库数据类型时，它需要是完整的数据库数据类型，如：MEDIUMINT UNSIGNED not NULL AUTO_INCREMENT
serializer | 指定将数据序列化或反序列化到数据库中的序列化器, 例如: serializer:json/gob/unixtime
size | 定义列数据类型的大小或长度，例如 size: 256
primaryKey | 将列定义为主键
unique | 将列定义为唯一键
default | 定义列的默认值
precision | 指定列的精度
scale | 指定列大小
not null | 指定列为 NOT NULL
autoIncrement | 指定列为自动增长
autoIncrementIncrement | 自动步长，控制连续记录之间的间隔
embedded | 嵌套字段
embeddedPrefix | 嵌入字段的列名前缀
autoCreateTime | 创建时追踪当前时间，对于 int 字段，它会追踪时间戳秒数，您可以使用 nano/milli 来追踪纳秒、毫秒时间戳，例如：autoCreateTime:nano
autoUpdateTime | 创建/更新时追踪当前时间，对于 int 字段，它会追踪时间戳秒数，您可以使用 nano/milli 来追踪纳秒、毫秒时间戳，例如：autoUpdateTime:milli
index | 根据参数创建索引，多个字段使用相同的名称则创建复合索引，查看 索引 获取详情
uniqueIndex | 与 index 相同，但创建的是唯一索引
check | 创建检查约束，例如 check:age > 13，查看 约束 获取详情
<- | 设置字段写入的权限， <-:create 只创建、<-:update 只更新、<-:false 无写入权限、<- 创建和更新权限
-> | 设置字段读的权限，->:false 无读权限
\- | 忽略该字段，- 表示无读写，-:migration 表示无迁移权限，-:all 表示无读写迁移权限
comment | 迁移时为字段添加注释

**关联标签**
GORM 允许通过标签为关联配置外键、约束、many2many 表，详情请参考 [关联部分](#关联)

## CRUD 接口【3】

### 创建

#### 创建记录

```go
 user := User{Name: "Jinzhu", Age: 18, Birthday: time.Now()}
 result := db.Create(&user)
 //分批插入
 users := []User{...}
 db.CreateInBatches(users, 100)
```

`Upsert` 和 `Create With Associations`同样支持批量插入

#### 根据 Map 创建

GORM支持通过 map[string]interface{} 与 []map[string]interface{}来创建记录。

```go
db.Model(&User{}).Create(map[string]interface{}{
  "Name": "jinzhu", "Age": 18,
})

// batch insert from `[]map[string]interface{}{}`
db.Model(&User{}).Create([]map[string]interface{}{
  {"Name": "jinzhu_1", "Age": 18},
  {"Name": "jinzhu_2", "Age": 20},
})
```

注意当使用map来创建时，钩子方法不会执行，关联不会被保存且不会回写主键。

#### 指定字段创建记录

```go
db.Select(字段1,...).Create(&user)
db.Omit(字段1,...).Create(&user)
```

#### 创建&跳过钩子

可以通过实现接口自定义钩子，相当于web的中间件，在数据库操作前后附加操作，详情参阅[Hooks](#钩子2)。

```go
// 创建钩子
func (u *User) BeforeCreate(tx *gorm.DB) (err error) {...}
// 跳过钩子
db.Session(&gorm.Session{SkipHooks: true}).CRUD()
```

#### 使用 SQL 表达式、Context Valuer 创建记录

GORM允许使用SQL表达式来插入数据，有两种方法可以达成该目的，使用`map[string]interface{}`或者 [Customized Data Types](#自定义数据类型4)。

TODO：自定义数据类型相关
这块没看懂，回头再看。

#### Upsert

在 GORM 中，Upsert 通常用于处理以下两种情况：

- `Insert On Duplicate Key Update`：如果记录已经存在，则更新该记录；如果不存在，则插入新记录。这种用法和`save`类似。

```go
db.Clauses(clause.OnConflict{
  DoNothing: false,
  Columns: []clause.Column{{Name: "id"}},
  DoUpdates: clause.AssignmentColumns([]string{"name", "email"}),
}).Create(&user)
```

`Insert Ignore`：如果记录已经存在，则忽略插入操作；如果不存在，则插入新记录。

```go
db.Clauses(clause.OnConflict{
  DoNothing: true,
  Columns: []clause.Column{{Name: "id"}},
}).Create(&user)
```

#### 创建高级选项

- **关联创建**

创建关联数据时，如果关联值非零，这些关联会被`upsert`，并且它们的`Hooks`方法也会被调用。

```go
type CreditCard struct {
  gorm.Model
  Number   string
  UserID   uint
}

type User struct {
  gorm.Model
  Name       string
  CreditCard CreditCard
}

db.Create(&User{
  Name: "jinzhu",
  CreditCard: CreditCard{Number: "411111111111"}
})
// INSERT INTO `users` ...
// INSERT INTO `credit_cards` ...
```

可以通过`Select`, `Omit`方法来跳过关联更新，示例如下：

```go
db.Omit("CreditCard").Create(&user)

// skip all associations
db.Omit(clause.Associations).Create(&user)
```

- **默认值**

可以通过结构体Tag `default`来定义字段的默认值,这些默认值会被当作结构体字段的零值插入到数据库中。

```go
type User struct {
  ID   int64
  Name string `gorm:"default:galeone"`
  Age  int64  `gorm:"default:18"`
}
```

结构体的字段默认值是零值的时候比如 0, '', false，这些字段值将不会被保存到数据库中，可以使用指针类型或者Scanner/Valuer来避免这种情况。

```go
type User struct {
  gorm.Model
  Name string
  Age  *int           `gorm:"default:18"`
  Active sql.NullBool `gorm:"default:true"`
}
```

若要让字段在数据库中拥有默认值则必须使用`default`Tag来为结构体字段设置默认值。如果想要在数据库迁移的时候跳过默认值，可以使用 `default:(-)`，示例如下：

```go
type User struct {
  ID        string `gorm:"default:uuid_generate_v3()"` // db func
  FirstName string
  LastName  string
  Age       uint8
  FullName  string `gorm:"->;type:GENERATED ALWAYS AS (concat(firstname,' ',lastname));default:(-);"`
}
```

### 查询

#### 检索单个对象

GORM 提供了 `First`、`Take`、`Last` 方法，以便从数据库中检索单个对象。当查询数据库时它添加了 `LIMIT 1` 条件，且没有找到记录时，它会返回 `ErrRecordNotFound` 错误。

```go
// 获取第一条记录（主键升序）
db.First(&user)
// SELECT * FROM users ORDER BY id LIMIT 1;

// 获取一条记录，没有指定排序字段
db.Take(&user)
// SELECT * FROM users LIMIT 1;

// 获取最后一条记录（主键降序）
db.Last(&user)
// SELECT * FROM users ORDER BY id DESC LIMIT 1;

// 获取全部记录
db.Find(&users)
// // SELECT * FROM users;
```

`First` and `Last` 方法会按主键排序找到第一条和最后一条记录。只有在目标 struct 是指针或者通过 db.Model() 指定 model 时，该方法才有效。如果相关 model 没有定义主键，那么将按 model 的第一个字段进行排序。

#### 查找失败检查

```go
result := db.First(&user)
result.RowsAffected // 返回找到的记录数
result.Error        // returns error or nil

// 检查 ErrRecordNotFound 错误
errors.Is(result.Error, gorm.ErrRecordNotFound)
```

#### 根据主键查询

```go
db.First(&user,primaryKey)
```

#### 根据条件查询

**String条件**：

```go
db.Where(condition,args,...).CRUD()
```

使用`Where`方法，第一个参数为条件，用`?`占位，后续参数为参数项。示例：

```go
// Get first matched record
db.Where("name = ?", "jinzhu").First(&user)
// SELECT * FROM users WHERE name = 'jinzhu' ORDER BY id LIMIT 1;

// Get all matched records
db.Where("name <> ?", "jinzhu").Find(&users)
// SELECT * FROM users WHERE name <> 'jinzhu';

// IN
db.Where("name IN ?", []string{"jinzhu", "jinzhu 2"}).Find(&users)
// SELECT * FROM users WHERE name IN ('jinzhu','jinzhu 2');

// LIKE
db.Where("name LIKE ?", "%jin%").Find(&users)
// SELECT * FROM users WHERE name LIKE '%jin%';

// AND
db.Where("name = ? AND age >= ?", "jinzhu", "22").Find(&users)
// SELECT * FROM users WHERE name = 'jinzhu' AND age >= 22;

// Time
db.Where("updated_at > ?", lastWeek).Find(&users)
// SELECT * FROM users WHERE updated_at > '2000-01-01 00:00:00';

// BETWEEN
db.Where("created_at BETWEEN ? AND ?", lastWeek, today).Find(&users)
// SELECT * FROM users WHERE created_at BETWEEN '2000-01-01 00:00:00' AND '2000-01-08 00:00:00';
```

如果对象设置了主键，条件查询将不会覆盖主键的值，而是用 And 连接条件。 例如：

```go
var user = User{ID: 10}
db.Where("id = ?", 20).First(&user)
// SELECT * FROM users WHERE id = 10 and id = 20 ORDER BY id ASC LIMIT 1
```

这个查询将会给出`record not found`错误 所以，在想要使用例如 user 这样的变量从数据库中获取新值前，需要将例如 id 这样的主键设置为`nil`。

**Struct & Map 条件**:

直接使用结构体指针或map作为参数，示例如下：

```go
// Struct
db.Where(&User{Name: "jinzhu", Age: 20}).First(&user)
// SELECT * FROM users WHERE name = "jinzhu" AND age = 20 ORDER BY id LIMIT 1;

// Map
db.Where(map[string]interface{}{"name": "jinzhu", "age": 20}).Find(&users)
// SELECT * FROM users WHERE name = "jinzhu" AND age = 20;

// Slice of primary keys
db.Where([]int64{20, 21, 22}).Find(&users)
// SELECT * FROM users WHERE id IN (20, 21, 22);
```

使用`struct`查询时只查询**非零项**，如果需要查询零项可以改用`map`。

```go
db.Where(&User{Name: "jinzhu", Age: 0}).Find(&users)
// SELECT * FROM users WHERE name = "jinzhu";

db.Where(map[string]interface{}{"Name": "jinzhu", "Age": 0}).Find(&users)
// SELECT * FROM users WHERE name = "jinzhu" AND age = 0;
```

使用`struct`查询时可以指定查询字段，这样也可以查询零项。

```go
db.Where(&User{Name: "jinzhu"}, "name", "Age").Find(&users)
// SELECT * FROM users WHERE name = "jinzhu" AND age = 0;

db.Where(&User{Name: "jinzhu"}, "Age").Find(&users)
// SELECT * FROM users WHERE age = 0;
```

**内联条件**和`Where`方法差不多，只是把参数写在CRUD里，`Not`和`Or`的用法也和Where差不多。

**Not**:

`Not`除了查询条件外，还支持not in，not struct，primary key not in等。

```go
db.Not("name = ?", "jinzhu").First(&user)
// SELECT * FROM users WHERE NOT name = "jinzhu" ORDER BY id LIMIT 1;

// Not In
db.Not(map[string]interface{}{"name": []string{"jinzhu", "jinzhu 2"}}).Find(&users)
// SELECT * FROM users WHERE name NOT IN ("jinzhu", "jinzhu 2");

// Struct
db.Not(User{Name: "jinzhu", Age: 18}).First(&user)
// SELECT * FROM users WHERE name <> "jinzhu" AND age <> 18 ORDER BY id LIMIT 1;

// Not In slice of primary keys
db.Not([]int64{1,2,3}).First(&user)
// SELECT * FROM users WHERE id NOT IN (1,2,3) ORDER BY id LIMIT 1;
```

#### 选择特定字段

使用`Select`方法，详见[智能查询字段](#智能选择字段)，示例如下：

```go
db.Select("name", "age").Find(&users)
// SELECT name, age FROM users;

db.Select([]string{"name", "age"}).Find(&users)
// SELECT name, age FROM users;

db.Table("users").Select("COALESCE(age,?)", 42).Rows()
// SELECT COALESCE(age,'42') FROM users;
```

#### 排序

使用`Order`方法，支持多参数，可以拼成一个字符串或者链式连接。

```go
db.Order("age desc, name").Find(&users)
// SELECT * FROM users ORDER BY age desc, name;

// Multiple orders
db.Order("age desc").Order("name").Find(&users)
// SELECT * FROM users ORDER BY age desc, name;

db.Clauses(clause.OrderBy{
  Expression: clause.Expr{SQL: "FIELD(id,?)", Vars: []interface{}{[]int{1, 2, 3}}, WithoutParentheses: true},
}).Find(&User{})
// SELECT * FROM users ORDER BY FIELD(id,1,2,3)
```

#### Limit & Offset

`Limit`表示最大选取几项，`Offset`表示跳过前几项。在链式中使用参数-1取消之前的设定。

```go
db.Limit(3).Find(&users)
// SELECT * FROM users LIMIT 3; 

// Cancel limit condition with -1
db.Limit(10).Find(&users1).Limit(-1).Find(&users2)
// SELECT * FROM users LIMIT 10; (users1)
// SELECT * FROM users; (users2)

db.Offset(3).Find(&users)
// SELECT * FROM users OFFSET 3;

db.Limit(10).Offset(5).Find(&users)
// SELECT * FROM users OFFSET 5 LIMIT 10;

// Cancel offset condition with -1
db.Offset(10).Find(&users1).Offset(-1).Find(&users2)
// SELECT * FROM users OFFSET 10; (users1)
// SELECT * FROM users; (users2)
```

#### Group By & Having

`Group`表示按字段分组，可以使用`Having`对分组结果进一步过滤。

```go
type result struct {
  Date  time.Time
  Total int
}

db.Model(&User{}).Select("name, sum(age) as total").Where("name LIKE ?", "group%").Group("name").First(&result)
// SELECT name, sum(age) as total FROM `users` WHERE name LIKE "group%" GROUP BY `name` LIMIT 1


db.Model(&User{}).Select("name, sum(age) as total").Group("name").Having("name = ?", "group").Find(&result)
// SELECT name, sum(age) as total FROM `users` GROUP BY `name` HAVING name = "group"

rows, err := db.Table("orders").Select("date(created_at) as date, sum(amount) as total").Group("date(created_at)").Rows()
defer rows.Close()
for rows.Next() {
  ...
}

rows, err := db.Table("orders").Select("date(created_at) as date, sum(amount) as total").Group("date(created_at)").Having("sum(amount) > ?", 100).Rows()
defer rows.Close()
for rows.Next() {
  ...
}

type Result struct {
  Date  time.Time
  Total int64
}
db.Table("orders").Select("date(created_at) as date, sum(amount) as total").Group("date(created_at)").Having("sum(amount) > ?", 100).Scan(&results)
```

#### Distinct

`Distinct`表示去重，示例如下：

```go
db.Distinct("name", "age").Order("name, age desc").Find(&results)
/*
SELECT DISTINCT name, age 
FROM users 
ORDER BY name ASC, age DESC;
*/
```

#### Joins

指定连接条件。

```go
type result struct {
  Name  string
  Email string
}

db.Model(&User{}).Select("users.name, emails.email").Joins("left join emails on emails.user_id = users.id").Scan(&result{})
// SELECT users.name, emails.email FROM `users` left join emails on emails.user_id = users.id

rows, err := db.Table("users").Select("users.name, emails.email").Joins("left join emails on emails.user_id = users.id").Rows()
for rows.Next() {
  ...
}

db.Table("users").Select("users.name, emails.email").Joins("left join emails on emails.user_id = users.id").Scan(&results)

// multiple joins with parameter
db.Joins("JOIN emails ON emails.user_id = users.id AND emails.email = ?", "jinzhu@example.org").Joins("JOIN credit_cards ON credit_cards.user_id = users.id").Where("credit_cards.number = ?", "411111111111").Find(&user)

```

- **Joins 预加载**

详见 [预加载](#预加载3) 章节。

虽然这里直接写的Joins，但我还是觉得用Preload更好，虽然我也不知道有什么区别。

```go
db.Joins("Company").Find(&users)
// SELECT `users`.`id`,`users`.`name`,`users`.`age`,`Company`.`id` AS `Company__id`,`Company`.`name` AS `Company__name` FROM `users` LEFT JOIN `companies` AS `Company` ON `users`.`company_id` = `Company`.`id`;

// inner join
db.InnerJoins("Company").Find(&users)
// SELECT `users`.`id`,`users`.`name`,`users`.`age`,`Company`.`id` AS `Company__id`,`Company`.`name` AS `Company__name` FROM `users` INNER JOIN `companies` AS `Company` ON `users`.`company_id` = `Company`.`id`;

// join with conditions
db.Joins("Company", db.Where(&Company{Alive: true})).Find(&users)
// SELECT `users`.`id`,`users`.`name`,`users`.`age`,`Company`.`id` AS `Company__id`,`Company`.`name` AS `Company__name` FROM `users` LEFT JOIN `companies` AS `Company` ON `users`.`company_id` = `Company`.`id` AND `Company`.`alive` = true;
```

- **Joins 一个派生表**

可以把派生表拆出来单独写，之后作为参数放到from里，提高了可读性。

```go
type User struct {
  Id  int
  Age int
}

type Order struct {
  UserId     int
  FinishedAt *time.Time
}

query := db.Table("order").Select("MAX(order.finished_at) as latest").Joins("left join user user on order.user_id = user.id").Where("user.age > ?", 18).Group("order.user_id")
db.Model(&Order{}).Joins("join (?) q on order.finished_at = q.latest", query).Scan(&results)
// SELECT `order`.`user_id`,`order`.`finished_at` FROM `order` join (SELECT MAX(order.finished_at) as latest FROM `order` left join user user on order.user_id = user.id WHERE user.age > 18 GROUP BY `order`.`user_id`) q on order.finished_at = q.latest

```

#### Scan

`Scan`方法把结果转化成结构体，用法类似于`Find`。

```go
type Result struct {
  Name string
  Age  int
}

var result Result
db.Table("users").Select("name", "age").Where("name = ?", "Antonio").Scan(&result)

// Raw SQL
db.Raw("SELECT name, age FROM users WHERE name = ?", "Antonio").Scan(&result)
```

**Find和Scan区别**：

`Find`：

- 专门用于查询 GORM 模型结构体。
- 返回具体的模型实例或模型切片。
- 通常用于处理已定义好的模型结构。
  
`Scan`：

- 适用于查询任意类型的数据。
- 可以将查询结果保存为 `[]map[string]interface{}` 或其他自定义的数据结构。
- 提供更高的灵活性，尤其是在处理非标准数据结构时。

### 高级查询

PS.这一章内容挺多的，但其实只要掌握最基本的查询就够用了。其他都是告诉你支持这样的特性，如果知道并用上会更方便。但个人感觉，首先这么多东西懒得记，记了到时候也会忘。顶多扫一眼留个印象，能用上时想起来就过来看一眼，想不起来就算了。

#### 智能选择字段

在 GORM 中，您可以使用 Select 方法有效地选择特定字段。 这在Model字段较多但只需要其中部分的时候尤其有用，比如编写API响应。

```go
type User struct {
  ID     uint
  Name   string
  Age    int
  Gender string
  // 很多很多字段
}

type APIUser struct {
  ID   uint
  Name string
}

// 在查询时，GORM 会自动选择 `id `, `name` 字段
db.Model(&User{}).Limit(10).Find(&APIUser{})
// SQL: SELECT `id`, `name` FROM `users` LIMIT 10
```

**注意** 在 QueryFields 模式中, 所有的模型字段（model fields）都会被根据他们的名字选择。

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  QueryFields: true,
})

// 当 QueryFields 被设置为 true 时，此行为默认进行
db.Find(&user)
// SQL: SELECT `users`.`name`, `users`.`age`, ... FROM `users`

// 开启 QueryFields 并使用会话模式（Session mode）
db.Session(&gorm.Session{QueryFields: true}).Find(&user)
// SQL: SELECT `users`.`name`, `users`.`age`, ... FROM `users`
```

#### 锁 【2】

一些简单的锁操作，有需要再查。

```go
// 基本的 FOR UPDATE 锁
db.Clauses(clause.Locking{Strength: "UPDATE"}).Find(&users)
// SQL: SELECT * FROM `users` FOR UPDATE
```

上述语句将会在事务（transaction）中锁定选中行（selected rows）。 可以被用于以下场景：当你准备在事务（transaction）中更新（update）一些行（rows）时，并且想要在本事务完成前，阻止（prevent）其他的事务（other transactions）修改你准备更新的选中行。

`Strength` 也可以被设置为 `SHARE` ，这种锁只允许其他事务读取（read）被锁定的内容，而无法修改（update）或者删除（delete）。

```go
db.Clauses(clause.Locking{
  Strength: "SHARE",
  Table: clause.Table{Name: clause.CurrentTable},
}).Find(&users)
// SQL: SELECT * FROM `users` FOR SHARE OF `users`
```

`Table`选项用于指定将要被锁定的表。 这在你想要 join 多个表，并且锁定其一时非常有用。

你也可以提供如 `NOWAIT` 的Options，这将尝试获取一个锁，如果锁不可用，导致了获取失败，函数将会立即返回一个error。 当一个事务等待其他事务释放它们的锁时，此Options（Nowait）可以阻止这种行为

```go
db.Clauses(clause.Locking{
  Strength: "UPDATE",
  Options: "NOWAIT",
}).Find(&users)
// SQL: SELECT * FROM `users` FOR UPDATE NOWAIT
```

Options也可以是SKIP LOCKED，设置后将跳过所有已经被其他事务锁定的行（any rows that are already locked by other transactions.）。 这次高并发情况下非常有用：那时你可能会想要对未经其他事务锁定的行进行操作（process ）。

```go
type User struct {
  ID     uint
  Name   string
  Age    int
  Gender string
  // 很多很多字段
}

type APIUser struct {
  ID   uint
  Name string
}

// 在查询时，GORM 会自动选择 `id `, `name` 字段
db.Model(&User{}).Limit(10).Find(&APIUser{})
// SQL: SELECT `id`, `name` FROM `users` LIMIT 10
```

**QueryFields**模式中默认选择所有字段。

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  QueryFields: true,
})

// 当 QueryFields 被设置为 true 时，此行为默认进行
db.Find(&user)
// SQL: SELECT `users`.`name`, `users`.`age`, ... FROM `users`

// 开启 QueryFields 并使用会话模式（Session mode）
db.Session(&gorm.Session{QueryFields: true}).Find(&user)
// SQL: SELECT `users`.`name`, `users`.`age`, ... FROM `users`
```

#### 子查询

PS.简单来说，就是可以把查询语句的结果当表去查询。

```go
// 在 FROM 子句中使用子查询
db.Table("(?) as u", db.Model(&User{}).Select("name", "age")).Where("age = ?", 18).Find(&User{})
// SQL: SELECT * FROM (SELECT `name`,`age` FROM `users`) as u WHERE `age` = 18

// 在 FROM 子句中结合多个子查询
subQuery1 := db.Model(&User{}).Select("name")
subQuery2 := db.Model(&Pet{}).Select("name")
db.Table("(?) as u, (?) as p", subQuery1, subQuery2).Find(&User{})
// SQL: SELECT * FROM (SELECT `name` FROM `users`) as u, (SELECT `name` FROM `pets`) as p
```

#### Group 条件

```go
// 使用 Group 条件的复杂 SQL 查询
db.Where(
  db.Where("pizza = ?", "pepperoni").Where(db.Where("size = ?", "small").Or("size = ?", "medium")),
).Or(
  db.Where("pizza = ?", "hawaiian").Where("size = ?", "xlarge"),
).Find(&Pizza{})
// SQL: SELECT * FROM `pizzas` WHERE (pizza = "pepperoni" AND (size = "small" OR size = "medium")) OR (pizza = "hawaiian" AND size = "xlarge"）
```

#### 带多个列的In

GROM 支持多列的 IN 子句（the IN clause with multiple columns），允许你在单次查询里基于多个字段值筛选数据。

```go
// 多列 IN
db.Where("(name, age, role) IN ?", [][]interface{}{{"jinzhu", 18, "admin"}, {"jinzhu2", 19, "user"}}).Find(&users)
// SQL: SELECT * FROM users WHERE (name, age, role) IN (("jinzhu", 18, "admin"), ("jinzhu 2", 19, "user"));
```

#### 命名参数详解

GORM 支持命名的参数，提高SQL 查询的可读性和可维护性。 此功能使查询结构更加清晰、更加有条理，尤其是在有多个参数的复杂查询中。 命名参数可以使用 `sql.NamedArg` 或 `map[string]interface{}{}}`，可以根据查询结构灵活提供。

```go
// 使用 sql.NamedArg 命名参数的例子
db.Where("name1 = @name OR name2 = @name", sql.Named("name", "jinzhu")).Find(&user)
// SQL: SELECT * FROM `users` WHERE name1 = "jinzhu" OR name2 = "jinzhu"

// 使用 map 命名参数的例子
db.Where("name1 = @name OR name2 = @name", map[string]interface{}{"name": "jinzhu"}).First(&user)
// SQL: SELECT * FROM `users` WHERE name1 = "jinzhu" OR name2 = "jinzhu" ORDER BY `users`.`id` LIMIT 1
```

更多示例和详细信息详见 [原生SQL和SQL生成器](#原生sql和sql生成器) 。

#### Find 至 map

GORM 提供了灵活的数据查询，允许将结果扫描进（scanned into）`map[string]interface{}` or `[]map[string]interface{}`，这对动态数据结构非常有用。

当使用 Find To Map 时，一定要在你的查询中包含 `Model` 或者 `Table` ，以此来显式地指定表名。

```go
// 扫描第一个结果到 map with Model 中
result := map[string]interface{}{}
db.Model(&User{}).First(&result, "id = ?", 1)
// SQL: SELECT * FROM `users` WHERE id = 1 LIMIT 1

// 扫描多个结果到部分 maps with Table 中
var results []map[string]interface{}
db.Table("users").Find(&results)
// SQL: SELECT * FROM `users`
```

#### FirstOrInit

GORM 的 `FirstOrInit` 方法用于获取与特定条件匹配的第一条记录，如果没有成功获取，就初始化一个新实例。 这个方法与结构和map条件兼容，并且在使用 `Attrs` 和 `Assign` 方法时有着更多的灵活性。

```go
// 如果没找到 name 为 "non_existing" 的 User，就初始化一个新的 User
var user User
db.FirstOrInit(&user, User{Name: "non_existing"})
// user -> User{Name: "non_existing"} if not found

// 检索名为 “jinzhu” 的 User
db.Where(User{Name: "jinzhu"}).FirstOrInit(&user)
// user -> User{ID: 111, Name: "Jinzhu", Age: 18} if found

// 使用 map 来指定搜索条件
db.FirstOrInit(&user, map[string]interface{}{"name": "jinzhu"})
// user -> User{ID: 111, Name: "Jinzhu", Age: 18} if found
```

- **使用 `Attrs` 进行初始化**

当记录未找到，可以使用 `Attrs` 来初始化一个有着额外属性的结构体。 这些属性包含在新结构中，但不在 SQL 查询中使用。

```go
// 如果没找到 User，根据所给条件和额外属性初始化 User
db.Where(User{Name: "non_existing"}).Attrs(User{Age: 20}).FirstOrInit(&user)
// SQL: SELECT * FROM USERS WHERE name = 'non_existing' ORDER BY id LIMIT 1;
// user -> User{Name: "non_existing", Age: 20} if not found

// 如果名为 “Jinzhu” 的 User 被找到，`Attrs` 会被忽略
db.Where(User{Name: "Jinzhu"}).Attrs(User{Age: 20}).FirstOrInit(&user)
// SQL: SELECT * FROM USERS WHERE name = 'Jinzhu' ORDER BY id LIMIT 1;
// user -> User{ID: 111, Name: "Jinzhu", Age: 18} if found
```

- **为属性使用 `Assign`**

`Assign` 方法允许您在结构上设置属性，不管是否找到记录。 这些属性设定在结构上，但不用于生成 SQL 查询，最终数据不会被保存到数据库。

```go
// 根据所给条件和分配的属性初始化，不管记录是否存在
db.Where(User{Name: "non_existing"}).Assign(User{Age: 20}).FirstOrInit(&user)
// user -> User{Name: "non_existing", Age: 20} if not found

// 如果找到了名为“Jinzhu”的用户，使用分配的属性更新结构体
db.Where(User{Name: "Jinzhu"}).Assign(User{Age: 20}).FirstOrInit(&user)
// SQL: SELECT * FROM USERS WHERE name = 'Jinzhu' ORDER BY id LIMIT 1;
// user -> User{ID: 111, Name: "Jinzhu", Age: 20} if found
```

`FirstOrInit`, 以及 `Attrs` 和 `Assign`, 提供了一种强大和灵活的方法来确保记录的存在，并且在一个步骤中以特定的属性初始化或更新。

#### FirstOrCreate

`FirstOrCreate` 用于获取与特定条件匹配的第一条记录，或者如果没有找到匹配的记录，创建一个新的记录。 这个方法在结构和map条件下都是有效的。 `RowsAffected` 属性有助于确定创建或更新记录的数量。

```go
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

- **配合 `Attrs` 使用 FirstOrCreate**

`Attrs` 可以用于指定新记录的附加属性。 这些属性用于创建，但不在初始搜索查询中。

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
```

- **配合 `Assign` 使用 FirstOrCreate**

```go
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

#### 优化器、索引提示【4】

PS.略，Clauses和hints什么的，爱咋咋地。感兴趣自己查文档。高级主题-提示。

#### 迭代

GORM 支持使用 `Rows` 方法对查询结果进行迭代。您可以通过对查询返回的行进行迭代，扫描每行到一个结构体中。 该方法提供了对如何处理每条记录的粒度控制。（granular control）。

```go
`rows`, err := db.Model(&User{}).Where("name = ?", "jinzhu").Rows()
defer rows.Close()

for rows.Next() {
  var user User
  // ScanRows 扫描每一行进结构体
  db.ScanRows(rows, &user)

  // 对每一个 User 进行操作
}
```

#### FindInBatches

`FindInBatches` 允许分批查询和处理记录。 这对于有效地处理大型数据集、减少内存使用和提高性能尤其有用。

```go
// 处理记录，批处理大小为100
result := db.Where("processed = ?", false).FindInBatches(&results, 100, func(tx *gorm.DB, batch int) error {
  for _, result := range results {
    // 对批中的每条记录进行操作
  }

  // 保存对当前批记录的修改
  tx.Save(&results)

  // tx.RowsAffected 提供当前批处理中记录的计数（the count of records in the current batch）
  // 'batch' 变量表示当前批号（the current batch number）

  // 返回 error 将阻止更多的批处理
  return nil
})

// result.Error 包含批处理过程中遇到的任何错误
// result.RowsAffected 提供跨批处理的所有记录的计数（the count of all processed records across batches）

```

#### 查询钩子

类似触发器的函数，但限定触发条件用途较窄。详情看[Hooks](#钩子2)部分。

```go
func (u *User) AfterFind(tx *gorm.DB) (err error) {
  // 在找到 user 后自定义逻辑
  if u.Role == "" {
    u.Role = "user" // 如果没有指定，将设置默认 role
  }
  return
}

// 当用户被查询时，会自动使用AfterFind钩子
```

#### Pluck方法【3】

GORM 中的 `Pluck` 方法用于从数据库中查询**单列**并扫描结果到片段（slice）。 当您需要从模型中检索特定字段时，此方法非常理想。如果需要查询多个列，可以使用 `Select` 配合 `Scan` 或者 `Find` 来代替。

PS.这个方法特别好用，强烈推荐。一般查询结果都是返回行，但这个查询返回列，省的处理行查询结果了，应用场景很广。文档把它放在这么后面实在有点埋没了。

```go
// 检索所有用户的 age
var ages []int64
db.Model(&User{}).Pluck("age", &ages)

// 检索所有用户的 name
var names []string
db.Model(&User{}).Pluck("name", &names)

// 从不同的表中检索 name
db.Table("deleted_users").Pluck("name", &names)

// 使用Distinct和Pluck
db.Model(&User{}).Distinct().Pluck("Name", &names)
// SQL: SELECT DISTINCT `name` FROM `users`

// 多列查询
db.Select("name", "age").Scan(&users)
db.Select("name", "age").Find(&users)
```

#### Scope方法

PS.我一般都是写带几个链式方法的*gorm.DB变量，要用时直接接在后面就行。不过这个方法确实又更好的结构和可维护性，就是有点繁琐。

GORM中的 `Scopes` 是一个强大的特性，它允许将常用的查询条件定义为可重用的方法。 这些作用域可以很容易地在查询中引用，从而使代码更加模块化和可读。

- 定义Scopes

`Scopes` 被定义为被修改后返回一个 gorm.DB 实例的函数。 可以根据应用程序的需要定义各种条件作为范围。

```go
// Scope for filtering records where amount is greater than 1000
func AmountGreaterThan1000(db *gorm.DB) *gorm.DB {
  return db.Where("amount > ?", 1000)
}

// Scope for orders paid with a credit card
func PaidWithCreditCard(db *gorm.DB) *gorm.DB {
  return db.Where("pay_mode_sign = ?", "C")
}

// Scope for orders paid with cash on delivery (COD)
func PaidWithCod(db *gorm.DB) *gorm.DB {
  return db.Where("pay_mode_sign = ?", "COD")
}

// Scope for filtering orders by status
func OrderStatus(status []string) func(db *gorm.DB) *gorm.DB {
  return func(db *gorm.DB) *gorm.DB {
    return db.Where("status IN (?)", status)
  }
}
```

- 在查询中使用Scopes

可以通过 Scopes 方法使用一个或者多个 Scope 来查询。，从而动态地连接多个条件。

```go
// 使用 scopes 来寻找所有的 金额大于1000的信用卡订单
db.Scopes(AmountGreaterThan1000, PaidWithCreditCard).Find(&orders)

// 使用 scopes 来寻找所有的 金额大于1000的货到付款（COD）订单
db.Scopes(AmountGreaterThan1000, PaidWithCod).Find(&orders)

//使用 scopes 来寻找所有的 具有特定状态且金额大于1000的订单
db.Scopes(AmountGreaterThan1000, OrderStatus([]string{"paid", "shipped"})).Find(&orders)
```

`Scopes` 是封装普通查询逻辑的一种干净而有效的方式，增强了代码的可维护性和可读性。 更详细的示例和用法详见文档中的 [Scope](#scope3)的 **范围** 部分。

#### Count

GORM中的 `Count` 方法用于检索匹配给定查询的记录数。 这是了解数据集大小的一个有用的功能，特别是在涉及有条件查询或数据分析的情况下。

- **得到匹配记录的 Count**

可以使用 `Count` 来确定符合您的查询中符合特定标准的记录的数量。

```go
var count int64

// 计数 有着特定名字的 users
db.Model(&User{}).Where("name = ?", "jinzhu").Or("name = ?", "jinzhu 2").Count(&count)
// SQL: SELECT count(1) FROM users WHERE name = 'jinzhu' OR name = 'jinzhu 2'

// 计数 有着单一名字条件（single name condition）的 users
db.Model(&User{}).Where("name = ?", "jinzhu").Count(&count)
// SQL: SELECT count(1) FROM users WHERE name = 'jinzhu'

// 在不同的表中对记录计数
db.Table("deleted_users").Count(&count)
// SQL: SELECT count(1) FROM deleted_users
```

- **配合 Distinct 和 Group 使用 Count**

GORM还允许对不同的值进行计数并对结果进行分组。

```go
// 为不同 name 计数
db.Model(&User{}).Distinct("name").Count(&count)
// SQL: SELECT COUNT(DISTINCT(`name`)) FROM `users`

// 使用自定义选择（custom select）计数不同的值
db.Table("deleted_users").Select("count(distinct(name))").Count(&count)
// SQL: SELECT count(distinct(name)) FROM deleted_users

// 分组记录计数
users := []User{
  {Name: "name1"},
  {Name: "name2"},
  {Name: "name3"},
  {Name: "name3"},
}

db.Model(&User{}).Group("name").Count(&count)
// 按名称分组后计数
// count => 3
```

### 更新

#### 保存所有字段

`Save`会保存所有的字段，即使字段是零值。

```go
db.First(&user)

user.Name = "jinzhu 2"
user.Age = 100
db.Save(&user)
// UPDATE users SET name='jinzhu 2', age=100, birthday='2016-01-01', updated_at = '2013-11-17 21:34:10' WHERE id=111;

```

`Save`是一个组合函数。 如果保存值不包含主键，它将执行 Create，否则它将执行 Update (包含所有字段)。

```go
db.Save(&User{Name: "jinzhu", Age: 100})
// INSERT INTO `users` (`name`,`age`,`birthday`,`update_at`) VALUES ("jinzhu",100,"0000-00-00 00:00:00","0000-00-00 00:00:00")

db.Save(&User{ID: 1, Name: "jinzhu", Age: 100})
// UPDATE `users` SET `name`="jinzhu",`age`=100,`birthday`="0000-00-00 00:00:00",`update_at`="0000-00-00 00:00:00" WHERE `id` = 1
```

**NOTE:** 要将 `Save` 和 `Model` 一同使用, 这是 未定义的行为。

#### 更新单个列

当使用 `Update` 更新单列时，需要有一些条件，否则将会引起`ErrMissingWhereClause` 错误，查看[批量更新](#批量更新)的**阻止全局更新**了解详情。
当使用 `Model` 方法，并且它有主键值时，主键将会被用于构建条件，例如：

```go
// 根据条件更新
db.Model(&User{}).Where("active = ?", true).Update("name", "hello")
// UPDATE users SET name='hello', updated_at='2013-11-17 21:34:10' WHERE active=true;

// User 的 ID 是 `111`
db.Model(&user).Update("name", "hello")
// UPDATE users SET name='hello', updated_at='2013-11-17 21:34:10' WHERE id=111;

// 根据条件和 model 的值进行更新
db.Model(&user).Where("active = ?", true).Update("name", "hello")
// UPDATE users SET name='hello', updated_at='2013-11-17 21:34:10' WHERE id=111 AND active=true;
```

这里只举例了`Update`的使用方法，却没有讲清楚他提到的那个错误怎么引起怎么检测怎么解决，具体看下面[批量更新](#批量更新)的**阻止全局更新**部分。

#### 更新多列

`Updates` 方法支持 `struct` 和 `map[string]interface{}` 参数。当使用 struct 更新时，默认情况下GORM **只更新非零值**的字段。

```go
// 根据 `struct` 更新属性，只会更新非零值的字段
db.Model(&user).Updates(User{Name: "hello", Age: 18, Active: false})
// UPDATE users SET name='hello', age=18, updated_at = '2013-11-17 21:34:10' WHERE id = 111;

// 根据 `map` 更新属性
db.Model(&user).Updates(map[string]interface{}{"name": "hello", "age": 18, "active": false})
// UPDATE users SET name='hello', age=18, active=false, updated_at='2013-11-17 21:34:10' WHERE id=111;

```

#### 更新选定字段

如果想要在更新时选择、忽略某些字段，可以使用 `Select`、`Omit`。

```go
// 选择 Map 的字段
// User 的 ID 是 `111`:
db.Model(&user).Select("name").Updates(map[string]interface{}{"name": "hello", "age": 18, "active": false})
// UPDATE users SET name='hello' WHERE id=111;

db.Model(&user).Omit("name").Updates(map[string]interface{}{"name": "hello", "age": 18, "active": false})
// UPDATE users SET age=18, active=false, updated_at='2013-11-17 21:34:10' WHERE id=111;

// 选择 Struct 的字段（会选中零值的字段）
db.Model(&user).Select("Name", "Age").Updates(User{Name: "new_name", Age: 0})
// UPDATE users SET name='new_name', age=0 WHERE id=111;

// 选择所有字段（选择包括零值字段的所有字段）
db.Model(&user).Select("*").Updates(User{Name: "jinzhu", Role: "admin", Age: 0})

// 选择除 Role 外的所有字段（包括零值字段的所有字段）
db.Model(&user).Select("*").Omit("Role").Updates(User{Name: "jinzhu", Role: "admin", Age: 0})
```

#### 更新Hook

看 [钩子](#hook) 一节吧，这里写了和没写一样。

#### 批量更新

正常的更新就是批量的，查询结果有几条更新几条。

- **阻止全局更新**

如果不带条件进行更新（更新整个表），GORM不会执行并返回`ErrMissingWhereClause`错误。

解决方法有使用条件，使用原生SQL或者开启`AllowGlobalUpdate`模式。

```go
db.Model(&User{}).Update("name", "jinzhu").Error // gorm.ErrMissingWhereClause

db.Model(&User{}).Where("1 = 1").Update("name", "jinzhu")
// UPDATE users SET `name` = "jinzhu" WHERE 1=1

db.Exec("UPDATE users SET name = ?", "jinzhu")
// UPDATE users SET name = "jinzhu"

db.Session(&gorm.Session{AllowGlobalUpdate: true}).Model(&User{}).Update("name", "jinzhu")
// UPDATE users SET `name` = "jinzhu"
```

- **更新的记录数**

可以使用 `result`变量作为CRUD操作的返回值，`result.RowsAffected`即为更新记录数，`result.Error`即为错误。

```go
// Get updated records count with `RowsAffected`
result := db.Model(User{}).Where("role = ?", "admin").Updates(User{Name: "hello", Age: 18})
// UPDATE users SET name='hello', age=18 WHERE role = 'admin';

result.RowsAffected // returns updated records count
result.Error        // returns updating error
```

#### 更新高级选项

- **使用SQL表达式更新**

赋值时可以使用sql表达式。

```go
// product's ID is `3`
db.Model(&product).Update("price", gorm.Expr("price * ? + ?", 2, 100))
// UPDATE "products" SET "price" = price * 2 + 100, "updated_at" = '2013-11-17 21:34:10' WHERE "id" = 3;

db.Model(&product).Updates(map[string]interface{}{"price": gorm.Expr("price * ? + ?", 2, 100)})
// UPDATE "products" SET "price" = price * 2 + 100, "updated_at" = '2013-11-17 21:34:10' WHERE "id" = 3;

db.Model(&product).UpdateColumn("quantity", gorm.Expr("quantity - ?", 1))
// UPDATE "products" SET "quantity" = quantity - 1 WHERE "id" = 3;

db.Model(&product).Where("quantity > 1").UpdateColumn("quantity", gorm.Expr("quantity - ?", 1))
// UPDATE "products" SET "quantity" = quantity - 1 WHERE "id" = 3 AND quantity > 1;
```

TODO:自定数据类型相关

- **根据子查询进行更新**

当然也可以用另一个查询的结果来赋值。

```go
db.Model(&user).Update("company_name", db.Model(&Company{}).Select("name").Where("companies.id = users.company_id"))
// UPDATE "users" SET "company_name" = (SELECT name FROM companies WHERE companies.id = users.company_id);

db.Table("users as u").Where("name = ?", "jinzhu").Update("company_name", db.Table("companies as c").Select("name").Where("c.id = u.company_id"))
// UPDATE users as u SET company_name = (SELECT name FROM campanies as c WHERE c.id = u.company_id) WHERE u.name = "jinzhu" 

db.Table("users as u").Where("name = ?", "jinzhu").Updates(map[string]interface{}{"company_name": db.Table("companies as c").Select("name").Where("c.id = u.company_id")})
```

- **不使用Hook和事件追踪**

如果想跳过钩子方法，和不更新更新时间，可以使用`UpdateColumn`, `UpdateColumns`方法，和`Update`,`Updates`方法用法类似。

- **返回修改行的数据**

只用于支持返回的数据库，使用`Clauses(clause.Returning{})`方法。

```go
// return all columns
var users []User
db.Model(&users).Clauses(clause.Returning{}).Where("role = ?", "admin").Update("salary", gorm.Expr("salary * ?", 2))
// UPDATE `users` SET `salary`=salary * 2,`updated_at`="2021-10-28 17:37:23.19" WHERE role = "admin" RETURNING *
// users => []User{{ID: 1, Name: "jinzhu", Role: "admin", Salary: 100}, {ID: 2, Name: "jinzhu.2", Role: "admin", Salary: 1000}}

// return specified columns
db.Model(&users).Clauses(clause.Returning{Columns: []clause.Column{{Name: "name"}, {Name: "salary"}}}).Where("role = ?", "admin").Update("salary", gorm.Expr("salary * ?", 2))
// UPDATE `users` SET `salary`=salary * 2,`updated_at`="2021-10-28 17:37:23.19" WHERE role = "admin" RETURNING `name`, `salary`
// users => []User{{ID: 0, Name: "jinzhu", Role: "", Salary: 100}, {ID: 0, Name: "jinzhu.2", Role: "", Salary: 1000}}
```

- **检查字段是否有变更**
  
GORM提供`Changed`方法用于**Before Update Hooks**，将返回 字段是否改变。

`Changed`方法只用于`Update`和`Updates`方法，只检查更新值是否等于模型值，如果改变且未被省略则返回true。

```go
func (u *User) BeforeUpdate(tx *gorm.DB) (err error) {
  // if Role changed
    if tx.Statement.Changed("Role") {
    return errors.New("role not allowed to change")
    }

  if tx.Statement.Changed("Name", "Admin") { // if Name or Role changed
    tx.Statement.SetColumn("Age", 18)
  }

  // if any fields changed
    if tx.Statement.Changed() {
        tx.Statement.SetColumn("RefreshedAt", time.Now())
    }
    return nil
}

db.Model(&User{ID: 1, Name: "jinzhu"}).Updates(map[string]interface{"name": "jinzhu2"})
// Changed("Name") => true
db.Model(&User{ID: 1, Name: "jinzhu"}).Updates(map[string]interface{"name": "jinzhu"})
// Changed("Name") => false, `Name` not changed
db.Model(&User{ID: 1, Name: "jinzhu"}).Select("Admin").Updates(map[string]interface{
  "name": "jinzhu2", "admin": false,
})
// Changed("Name") => false, `Name` not selected to update

db.Model(&User{ID: 1, Name: "jinzhu"}).Updates(User{Name: "jinzhu2"})
// Changed("Name") => true
db.Model(&User{ID: 1, Name: "jinzhu"}).Updates(User{Name: "jinzhu"})
// Changed("Name") => false, `Name` not changed
db.Model(&User{ID: 1, Name: "jinzhu"}).Select("Admin").Updates(User{Name: "jinzhu2"})
// Changed("Name") => false, `Name` not selected to update
```

- **在Update时修改值**

要在Before Hooks里更改更新值，应该使用`SetColumn`，除非它是使用`save`的全修改。

```go
func (user *User) BeforeSave(tx *gorm.DB) (err error) {
  if pw, err := bcrypt.GenerateFromPassword(user.Password, 0); err == nil {
    tx.Statement.SetColumn("EncryptedPassword", pw)
  }

  if tx.Statement.Changed("Code") {
    user.Age += 20
    tx.Statement.SetColumn("Age", user.Age)
  }
}

db.Model(&user).Update("Name", "jinzhu")
```

### 删除

删除一条记录时需要指定主键，否则将出发批量删除。

GORM可以通过主键（复合主键）和内联条件删除对象，详情见 [条件](#根据条件查询)的 **内联条件**部分。

```go
// Email 的 ID 是 `10`
db.Delete(&email)
// DELETE from emails where id = 10;

// 带额外条件的删除
db.Where("name = ?", "jinzhu").Delete(&email)
// DELETE from emails where id = 10 AND name = "jinzhu";

db.Delete(&User{}, 10)
// DELETE FROM users WHERE id = 10;

db.Delete(&User{}, "10")
// DELETE FROM users WHERE id = 10;

db.Delete(&users, []int{1,2,3})
// DELETE FROM users WHERE id IN (1,2,3);
```

#### 钩子函数

对于删除操作，GORM 支持 BeforeDelete、AfterDelete Hook，详见 [钩子](#hook)。

#### 批量删除

如果指定的值不包括主属性，将删除所有匹配的记录。可以将一个主键切片传递给Delete 方法，以便更高效的删除数据量大的记录。

```go
db.Where("email LIKE ?", "%jinzhu%").Delete(&Email{})
// DELETE from emails where email LIKE "%jinzhu%";

db.Delete(&Email{}, "email LIKE ?", "%jinzhu%")
// DELETE from emails where email LIKE "%jinzhu%";

db.Where("email LIKE ?", "%jinzhu%").Delete(&Email{})
// DELETE from emails where email LIKE "%jinzhu%";

db.Delete(&Email{}, "email LIKE ?", "%jinzhu%")
// DELETE from emails where email LIKE "%jinzhu%";

```

- **阻止全局删除**

如果不带条件进行删除（删除整个表），GORM不会执行并返回`ErrMissingWhereClause`错误。

解决方法有使用条件，使用原生SQL或者开启`AllowGlobalUpdate`模式。

```go
db.Delete(&User{}).Error // gorm.ErrMissingWhereClause

db.Delete(&[]User{{Name: "jinzhu1"}, {Name: "jinzhu2"}}).Error // gorm.ErrMissingWhereClause

db.Where("1 = 1").Delete(&User{})
// DELETE FROM `users` WHERE 1=1

db.Exec("DELETE FROM users")
// DELETE FROM users

db.Session(&gorm.Session{AllowGlobalUpdate: true}).Delete(&User{})
// DELETE FROM users
```

- **返回删除行的信息**

返回被删除的数据，仅当数据库支持回写功能时才能正常运行，如下例：

```go
// 回写所有的列
var users []User
DB.Clauses(clause.Returning{}).Where("role = ?", "admin").Delete(&users)
// DELETE FROM `users` WHERE role = "admin" RETURNING *
// users => []User{{ID: 1, Name: "jinzhu", Role: "admin", Salary: 100}, {ID: 2, Name: "jinzhu.2", Role: "admin", Salary: 1000}}

// 回写指定的列
DB.Clauses(clause.Returning{Columns: []clause.Column{{Name: "name"}, {Name: "salary"}}}).Where("role = ?", "admin").Delete(&users)
// DELETE FROM `users` WHERE role = "admin" RETURNING `name`, `salary`
// users => []User{{ID: 0, Name: "jinzhu", Role: "", Salary: 100}, {ID: 0, Name: "jinzhu.2", Role: "", Salary: 1000}}
```

#### 软删除

如果模型中包含`gorm.DeletedAt`字段（包含在gorm.Model中），将使用软删除。当调用`Delete`时，GORM并不会从数据库中删除该记录，而是将该记录的`DeleteAt`设置为当前时间，而后的一般查询方法将无法查找到此条记录。

```go
// user's ID is `111`
db.Delete(&user)
// UPDATE users SET deleted_at="2013-10-29 10:23" WHERE id = 111;

// Batch Delete
db.Where("age = ?", 20).Delete(&User{})
// UPDATE users SET deleted_at="2013-10-29 10:23" WHERE age = 20;

// Soft deleted records will be ignored when querying
db.Where("age = 20").Find(&user)
// SELECT * FROM users WHERE age = 20 AND deleted_at IS NULL;
```

如果不想使用gorm.Model，可以在模型中定义一个类型为`gorm.DeletedAt`的字段来开启软删除。

- **查找被软删除的记录**

可以使用`Unscoped`来查询到被软删除的记录。

```go
db.Unscoped().Where("age = 20").Find(&users)
// SELECT * FROM users WHERE age = 20;
```

- **永久删除**

可以使用`Unscoped`来永久删除匹配的记录。

```go
db.Unscoped().Delete(&order)
// DELETE FROM orders WHERE id=10;
```

### 原生SQL和SQL生成器

#### 原生 SQL

`Raw`和`Exec`方法都可用于执行原生SQL语句。两者区别如下：

Raw常用于执行 SELECT 查询，返回查询结果，可以映射到 Go 结构体，通常用于读取数据。

Exec常用于执行非查询操作，也可以用于执行查询操作，但不返回结果。Exec返回一个 sql.Result 对象，可以用来获取受影响的行数等信息。

#### 命名参数简介

GORM 支持 `sql.NamedArg`、`map[string]interface{}{}` 或 `struct` 形式的命名参数。

简单来说，就是有了固定的键值对而不是全用？占位，不需要注意顺序，提高了可读性。

```go
db.Where("name1 = @name OR name2 = @name", sql.Named("name", "jinzhu")).Find(&user)
// SELECT * FROM `users` WHERE name1 = "jinzhu" OR name2 = "jinzhu"

db.Where("name1 = @name OR name2 = @name", map[string]interface{}{"name": "jinzhu2"}).First(&result3)
// SELECT * FROM `users` WHERE name1 = "jinzhu2" OR name2 = "jinzhu2" ORDER BY `users`.`id` LIMIT 1

// 原生 SQL 及命名参数
db.Raw("SELECT * FROM users WHERE name1 = @name OR name2 = @name2 OR name3 = @name",
   sql.Named("name", "jinzhu1"), sql.Named("name2", "jinzhu2")).Find(&user)
// SELECT * FROM users WHERE name1 = "jinzhu1" OR name2 = "jinzhu2" OR name3 = "jinzhu1"

db.Exec("UPDATE users SET name1 = @name, name2 = @name2, name3 = @name",
   sql.Named("name", "jinzhunew"), sql.Named("name2", "jinzhunew2"))
// UPDATE users SET name1 = "jinzhunew", name2 = "jinzhunew2", name3 = "jinzhunew"

db.Raw("SELECT * FROM users WHERE (name1 = @name AND name3 = @name) AND name2 = @name2",
   map[string]interface{}{"name": "jinzhu", "name2": "jinzhu2"}).Find(&user)
// SELECT * FROM users WHERE (name1 = "jinzhu" AND name3 = "jinzhu") AND name2 = "jinzhu2"

type NamedArgument struct {
    Name string
    Name2 string
}

db.Raw("SELECT * FROM users WHERE (name1 = @Name AND name3 = @Name) AND name2 = @Name2",
     NamedArgument{Name: "jinzhu", Name2: "jinzhu2"}).Find(&user)
// SELECT * FROM users WHERE (name1 = "jinzhu" AND name3 = "jinzhu") AND name2 = "jinzhu2"
```

#### DryRun 模式

在不执行的情况下生成 SQL 及其参数，可以用于准备或测试生成的 SQL，详情参见 [会话](#session2)。

```go
stmt := db.Session(&gorm.Session{DryRun: true}).First(&user, 1).Statement
stmt.SQL.String() //=> SELECT * FROM `users` WHERE `id` = $1 ORDER BY `id`
stmt.Vars         //=> []interface{}{1}
```

#### ToSQL

返回生成的 SQL 但不执行。

GORM使用 `database/sql` 的参数占位符来构建 SQL 语句，它会自动转义参数以避免 SQL 注入，但不保证生成 SQL 的安全，建议只用于调试。

```go
sql := db.ToSQL(func(tx *gorm.DB) *gorm.DB {
  return tx.Model(&User{}).Where("id = ?", 100).Limit(10).Order("age desc").Find(&[]User{})
})
sql //=> SELECT * FROM "users" WHERE id = 100 AND "users"."deleted_at" IS NULL ORDER BY age desc LIMIT 10

```

#### Row & Rows

获取 `*sql.Row` 结果

```go
// 使用 GORM API 构建 SQL
row := db.Table("users").Where("name = ?", "jinzhu").Select("name", "age").Row()
row.Scan(&name, &age)

// 使用原生 SQL
row := db.Raw("select name, age, email from users where name = ?", "jinzhu").Row()
row.Scan(&name, &age, &email)
```

获取 `*sql.Rows` 结果

```go
// 使用 GORM API 构建 SQL
rows, err := db.Model(&User{}).Where("name = ?", "jinzhu").Select("name, age, email").Rows()
defer rows.Close()
for rows.Next() {
  rows.Scan(&name, &age, &email)

  // 业务逻辑...
}

// 原生 SQL
rows, err := db.Raw("select name, age, email from users where name = ?", "jinzhu").Rows()
defer rows.Close()
for rows.Next() {
  rows.Scan(&name, &age, &email)

  // 业务逻辑...
}
```

#### 将 sql.Rows 扫描至 model

使用 ScanRows 将一行记录扫描至 struct，例如：

```go
rows, err := db.Model(&User{}).Where("name = ?", "jinzhu").Select("name, age, email").Rows() // (*sql.Rows, error)
defer rows.Close()

var user User
for rows.Next() {
  // ScanRows 将一行扫描至 user
  db.ScanRows(rows, &user)

  // 业务逻辑...
}
```

#### 连接

在一条 tcp DB 连接中运行多条 SQL (不是事务)

```go
db.Connection(func(tx *gorm.DB) error {
  tx.Exec("SET my.role = ?", "admin")

  tx.First(&User{})
})
```

#### 高级

- 子句（Clause）
- 子句构造器
- 子句选项
- StatementModifier

## 关联

### Belongs To

- Belongs To

`belongs to` 会与另一个模型建立了一对一的连接。 这种模型的每一个实例都“属于”另一个模型的一个实例。

```go
// `User` 属于 `Company`，`CompanyID` 是外键
type User struct {
  gorm.Model
  Name      string
  CompanyID int
  Company   Company
}

type Company struct {
  ID   int
  Name string
}
```

- 重写外键

使用`foreignKey`标签可以自定义外键名字。

```go
type User struct {
  gorm.Model
  Name         string
  CompanyRefer int
  Company      Company `gorm:"foreignKey:CompanyRefer"`
  // 使用 CompanyRefer 作为外键
}

type Company struct {
  ID   int
  Name string
}
```

`foreignKey:CompanyID`：指定了外键字段的名称为 CompanyID。
  这告诉 GORM 在 User 表中应该使用 CompanyID 字段作为外键。

- 重写引用

使用`references`标签可以更改引用.

```go
type User struct {
  gorm.Model
  Name      string
  CompanyID string
  Company   Company `gorm:"references:CompanyID"` // 使用 Company.CompanyID 作为引用
}

type Company struct {
  CompanyID   int
  Code        string
  Name        string
}
```

`references:ID`：指定引用字段的名称为 ID。
  这告诉 GORM 在 Company 表中应该使用 ID 字段作为被引用的主键。

- Belongs to 的 CRUD

见 [关联模式](#关联模式) 部分。

- 预加载

GORM 可以通过 `Preload`、`Joins` 预加载 belongs to 关联的记录，查看 [预加载](#预加载3) 获取详情

### Has One

`has one` 与另一个模型建立一对一的关联，但它和一对一关系有些许不同。 这种关联表明一个模型的每个实例都包含或拥有另一个模型的一个实例。

- **重写外键&引用**

同[belongs to](#belongs-to)

- **Has One 的 CURD**

见 [关联模式](#关联模式) 部分。

- **预加载**

查看 [预加载](#预加载3) 获取详情

#### 声明&检索 Has One

- **声明**

```go
// User 有一张 CreditCard，UserID 是外键
type User struct {
  gorm.Model
  CreditCard CreditCard
}

type CreditCard struct {
  gorm.Model
  Number string
  UserID uint
}
```

- **检索**

```go
// 检索用户列表并预加载信用卡
func GetAll(db *gorm.DB) ([]User, error) {
    var users []User
    err := db.Model(&User{}).Preload("CreditCard").Find(&users).Error
    return users, err
}
```

#### 自引用 Has One

```go
type User struct {
  gorm.Model
  Name      string
  ManagerID *uint
  Manager   *User
}
```

### Has Many

has many 与另一个模型建立了一对多的连接。 不同于 has one，拥有者可以有零或多个关联模型。

- **重写外键&引用**

同[belongs to](#belongs-to)

- **Has Many 的 CURD**

见 [关联模式](#关联模式) 部分。

- **预加载**

查看 [预加载](#预加载3) 获取详情

#### 声明&检索 Has Many

- **声明**

```go
// User 有多张 CreditCard，UserID 是外键
type User struct {
  gorm.Model
  CreditCards []CreditCard
}

type CreditCard struct {
  gorm.Model
  Number string
  UserID uint
}
```

- **检索**

```go
// 检索用户列表并预加载信用卡
func GetAll(db *gorm.DB) ([]User, error) {
    var users []User
    err := db.Model(&User{}).Preload("CreditCards").Find(&users).Error
    return users, err
}
```

#### 自引用 Has Many

type User struct {
  gorm.Model
  Name      string
  ManagerID *uint
  Team      []User `gorm:"foreignkey:ManagerID"`
}

### Many To Many

Many to Many 会在两个 model 中添加一张连接表。

```go
// User 拥有并属于多种 language，`user_languages` 是连接表
type User struct {
  gorm.Model
  Languages []Language `gorm:"many2many:user_languages;"`
}

type Language struct {
  gorm.Model
  Name string
}
```

标签 `gorm:"many2many:user_languages;"` 来指定中间表的名称为 user_languages。

- **Has Many 的 CURD**

见 [关联模式](#关联模式) 部分。

- **预加载**

查看 [预加载](#预加载3) 获取详情

- **外键约束**

见[外键约束](#外键约束)

**注意：**某些数据库只允许在唯一索引字段上创建外键，如果您在迁移时会创建外键，则需要指定 `unique index` 标签。

#### 反向引用-Many To Many

- 声明
  
```go
// User 拥有并属于多种 language，`user_languages` 是连接表
type User struct {
  gorm.Model
  Languages []*Language `gorm:"many2many:user_languages;"`
}

type Language struct {
  gorm.Model
  Name string
  Users []*User `gorm:"many2many:user_languages;"`
}
```

- 检索

```go
// 检索 User 列表并预加载 Language
func GetAllUsers(db *gorm.DB) ([]User, error) {
    var users []User
    err := db.Model(&User{}).Preload("Languages").Find(&users).Error
    return users, err
}

// 检索 Language 列表并预加载 User
func GetAllLanguages(db *gorm.DB) ([]Language, error) {
    var languages []Language
    err := db.Model(&Language{}).Preload("Users").Find(&languages).Error
    return languages, err
}
```

#### 自引用 Many2Many

```go
type User struct {
  gorm.Model
    Friends []*User `gorm:"many2many:user_friends"`
}

// 会创建连接表：user_friends
//   foreign key: user_id, reference: users.id
//   foreign key: friend_id, reference: users.id

```

#### 自定义连接表

连接表 可以是一个功能齐全的模型，比如支持 软删除、钩子函数功能，并且可以具有更多字段。您可以通过 SetupJoinTable 设置，例如：

```go
type Person struct {
  ID        int
  Name      string
  Addresses []Address `gorm:"many2many:person_addresses;"`
}

type Address struct {
  ID   uint
  Name string
}

type PersonAddress struct {
  PersonID  int `gorm:"primaryKey"`
  AddressID int `gorm:"primaryKey"`
  CreatedAt time.Time
  DeletedAt gorm.DeletedAt
}

func (PersonAddress) BeforeCreate(db *gorm.DB) error {
  // ...
}

// 修改 Person 的 Addresses 字段的连接表为 PersonAddress
// PersonAddress 必须定义好所需的外键，否则会报错
err := db.SetupJoinTable(&Person{}, "Addresses", &PersonAddress{})
```

#### 复合外键

如果模型使用了 复合主键，GORM 会默认启用复合外键。

也可以覆盖默认的外键、指定多个外键，只需用逗号分隔那些键名。

### Polymorphism

GORM支持Has One和Has Many的多态关联，它将拥有的实体的表名保存到多态类型的字段中，主键值保存到多态字段中。

默认情况下，`polymorphic:<value>`将以`<value>`作为列类型和列id的前缀。
该值将是表名的复数形式。

```go
type Dog struct {
  ID   int
  Name string
  Toys []Toy `gorm:"polymorphic:Owner;"`
}

type Toy struct {
  ID        int
  Name      string
  OwnerID   int
  OwnerType string
}

db.Create(&Dog{Name: "dog1", Toys: []Toy{{Name: "toy1"}, {Name: "toy2"}}})
// INSERT INTO `dogs` (`name`) VALUES ("dog1")
// INSERT INTO `toys` (`name`,`owner_id`,`owner_type`) VALUES ("toy1",1,"dogs"), ("toy2",1,"dogs")
```

可以使用以下GORM标签分别指定多态性属性:

- `polymorphicType`:列的类型。
- `polymorphicId`:列ID。
- `polymorphicValue`:类型值。

```go
type Dog struct {
  ID   int
  Name string
  Toys []Toy `gorm:"polymorphicType:Kind;polymorphicId:OwnerID;polymorphicValue:master"`
}

type Toy struct {
  ID        int
  Name      string
  OwnerID   int
  Kind      string
}

db.Create(&Dog{Name: "dog1", Toys: []Toy{{Name: "toy1"}, {Name: "toy2"}}})
// INSERT INTO `dogs` (`name`) VALUES ("dog1")
// INSERT INTO `toys` (`name`,`owner_id`,`kind`) VALUES ("toy1",1,"master"), ("toy2",1,"master")
```

### 外键约束

可以通过 constraint 标签配置 `OnUpdate`、`OnDelete` 实现外键约束，在使用 GORM 进行迁移时它会被创建，例如：

```go
type User struct {
  gorm.Model
  Name      string
  CompanyID int
  Company   Company `gorm:"constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`
}

type Company struct {
  ID   int
  Name string
}
```

`OnUpdate:CASCADE`：当关联的记录更新时，级联更新外键。
`OnDelete:SET NULL`：当关联的记录被删除时，将外键设置为 NULL。

其他常用设置：
`OnUpdate:NO ACTION`：如果更新被引用的记录会导致违反外键约束，则更新操作将被拒绝。这是mysql的默认行为。
`OnDelete:SET DEFAULT`：当关联的主记录被删除时，所有与之关联的记录的外键字段会被设置为默认值。
`OnDelete:NO ACTION`：这是许多数据库系统的默认行为。如果关联的主记录试图被删除，但仍然有与之关联的记录，那么删除操作将失败。
`OnDelete:RESTRICT`：
与 OnDelete:NO ACTION 类似，如果关联的主记录试图被删除，但仍然有与之关联的记录，那么删除操作将失败。
`OnDelete:DO NOTHING`：
如果关联的主记录试图被删除，但仍然有与之关联的记录，那么删除操作将继续，但是与之关联的记录的外键字段不会被更改。

### 关联模式

#### 自动创建、更新

GORM在创建或更新记录时会自动地保存其关联和引用，主要使用upsert技术来更新现有关联的外键引用。

- 在创建时自动保存关联

当你创建一条新的记录时，GORM会自动保存它的关联数据。 这个过程包括向关联表插入数据以及维护外键引用。

```go
user := User{
  Name:            "jinzhu",
  BillingAddress:  Address{Address1: "Billing Address - Address 1"},
  ShippingAddress: Address{Address1: "Shipping Address - Address 1"},
  Emails:          []Email{
    {Email: "jinzhu@example.com"},
    {Email: "jinzhu-2@example.com"},
  },
  Languages:       []Language{
    {Name: "ZH"},
    {Name: "EN"},
  },
}

// 创建用户及其关联的地址、电子邮件和语言
db.Create(&user)
// BEGIN TRANSACTION;
// INSERT INTO "addresses" (address1) VALUES ("Billing Address - Address 1"), ("Shipping Address - Address 1") ON DUPLICATE KEY DO NOTHING;
// INSERT INTO "users" (name,billing_address_id,shipping_address_id) VALUES ("jinzhu", 1, 2);
// INSERT INTO "emails" (user_id,email) VALUES (111, "jinzhu@example.com"), (111, "jinzhu-2@example.com") ON DUPLICATE KEY DO NOTHING;
// INSERT INTO "languages" ("name") VALUES ('ZH'), ('EN') ON DUPLICATE KEY DO NOTHING;
// INSERT INTO "user_languages" ("user_id","language_id") VALUES (111, 1), (111, 2) ON DUPLICATE KEY DO NOTHING;
// COMMIT;

db.Save(&user)
```

- 通过FullSaveAssociations来更新关联

对于需要全面更新关联数据（不止外键）的情况，就应该使用 FullSaveAssociations 方法。

```go
// 更新用户并完全更新其所有关联
db.Session(&gorm.Session{FullSaveAssociations: true}).Updates(&user)
// SQL：完全更新地址、用户、电子邮件表，包括现有的关联记录
```

使用FullSaveAssociations 方法来确保模型的整体状态，包括其所有关联都反映在了数据库中，从在应用中保持数据的完整性和一致性。

#### 跳过自动创建、更新

GORM提供了在创建或更新操作期间跳过自动保存关联的灵活性。这可以使用Select或Omit方法来实现。

- 使用Select 来指定字段范围

Select方法允许您指定应该保存模型的哪些字段。这意味着只有选定的字段将包含在SQL操作中。

```go
user := User{
  // User and associated data
}

// Only include the 'Name' field when creating the user
db.Select("Name").Create(&user)
// SQL: INSERT INTO "users" (name) VALUES ("jinzhu");
```

- 使用Omit来排除字段或关联

相反，省略允许您在保存模型时排除某些字段或关联。

```go
// Skip creating the 'BillingAddress' when creating the user
db.Omit("BillingAddress").Create(&user)

// Skip all associations when creating the user
db.Omit(clause.Associations).Create(&user)
```

**注意**:对于多对多关联，GORM会在创建连接表引用之前插入关联。若要跳过此设置，请使用省略和关联名称后面跟着。*:

```go
// Skip upserting 'Languages' associations
db.Omit("Languages.*").Create(&user)
```

跳过创建关联及其引用:

```go
// Skip creating 'Languages' associations and their references
db.Omit("Languages").Create(&user)
```

#### Select/Omit 关联字段

在GORM中，当创建或更新记录时，您可以使用Select和Omit方法来明确地包括或排除关联模型的某些字段。
使用Select，您可以指定在保存主模型时应该包含关联模型的哪些字段。这对于有选择地保存关联的某些部分特别有用。
相反，省略允许您从保存中排除关联模型的某些字段。当您想要阻止关联的特定部分被持久化时，这很有用。

```go
user := User{
  Name:            "jinzhu",
  BillingAddress:  Address{Address1: "Billing Address - Address 1", Address2: "addr2"},
  ShippingAddress: Address{Address1: "Shipping Address - Address 1", Address2: "addr2"},
}

// Create user and his BillingAddress, ShippingAddress, including only specified fields of BillingAddress
db.Select("BillingAddress.Address1", "BillingAddress.Address2").Create(&user)
// SQL: Creates user and BillingAddress with only 'Address1' and 'Address2' fields

// Create user and his BillingAddress, ShippingAddress, excluding specific fields of BillingAddress
db.Omit("BillingAddress.Address2", "BillingAddress.CreatedAt").Create(&user)
// SQL: Creates user and BillingAddress, omitting 'Address2' and 'CreatedAt' fields
```

#### 删除关联

GORM允许在删除主记录时使用Select方法删除特定的关联关系(has one, has many, many2many)。此特性对于维护数据库完整性和确保在删除时适当管理相关数据特别有用。

可以使用`Select`指定哪些关联应该与主记录一起删除。

```go
// Delete a user's account when deleting the user
db.Select("Account").Delete(&user)

// Delete a user's Orders and CreditCards associations when deleting the user
db.Select("Orders", "CreditCards").Delete(&user)

// Delete all of a user's has one, has many, and many2many associations
db.Select(clause.Associations).Delete(&user)

// Delete each user's account when deleting multiple users
db.Select("Account").Delete(&users)
```

#### 关联模式相关

GORM中的关联模式提供了各种辅助方法来处理模型之间的关系，提供了一种有效的方法来管理关联数据。

要启动Association Mode，请指定源模型和关系的字段名。源模型必须包含一个主键，并且关系的字段名应该与现有的关联匹配。

```go
var user User
db.Model(&user).Association("Languages")
// Check for errors
error := db.Model(&user).Association("Languages").Error
```

- 查询关联

检索有或没有附加条件的关联记录。

```go
// Simple find
db.Model(&user).Association("Languages").Find(&languages)

// Find with conditions
codes := []string{"zh-CN", "en-US", "ja-JP"}
db.Model(&user).Where("code IN ?", codes).Association("Languages").Find(&languages)
```

- 追加关联

为many to many、has many添加新的关联，或者为has one、belongs to替换当前关联。

```go
// Append new languages
db.Model(&user).Association("Languages").Append([]Language{languageZH, languageEN})

db.Model(&user).Association("Languages").Append(&Language{Name: "DE"})

db.Model(&user).Association("CreditCard").Append(&CreditCard{Number: "411111111111"}
```

- 替换关联

用新关联替换当前关联

```go
// Replace existing languages
db.Model(&user).Association("Languages").Replace([]Language{languageZH, languageEN})

db.Model(&user).Association("Languages").Replace(Language{Name: "DE"}, languageEN)
```

- 删除关联

删除源和参数之间的关系，只删除引用。

```go
// Delete specific languages
db.Model(&user).Association("Languages").Delete([]Language{languageZH, languageEN})

db.Model(&user).Association("Languages").Delete(languageZH, languageEN)
```

- 清空关联

删除源和关联之间的所有引用。

```go
// Clear all languages
db.Model(&user).Association("Languages").Clear()
```

- 关联计数

获取带有或不带有条件的当前关联的计数。

```go
// Count all languages
db.Model(&user).Association("Languages").Count()

// Count with conditions
codes := []string{"zh-CN", "en-US", "ja-JP"}
db.Model(&user).Where("code IN ?", codes).Association("Languages").Count()

```

- 批量数据处理
关联模式允许您处理批处理中多条记录的关系。这包括查找、追加、替换、删除和计数相关数据的操作。

  - **查找关联**:检索记录集合的关联数据。

  ```go
  db.Model(&users).Association("Role").Find(&roles)
  ```

  - **删除关联**:删除多个记录之间的特定关联。

  ```go
  db.Model(&users).Association("Team").Delete(&userA)
  ```

  - **计数关联**:获取一批记录的关联计数。

  ```go
  db.Model(&users).Association("Team").Count()
  ```

  - **追加/替换关联**:管理多个记录的关联。注意需要将参数长度与数据匹配。

  ```go
  var users = []User{user1, user2, user3}

  // Append different teams to different users in a batch
  // Append userA to user1's team, userB to user2's team, and userA, userB, userC to user3's team
  db.Model(&users).Association("Team").Append(&userA, &userB, &[]User{userA, userB, userC})

  // Replace teams for multiple users in a batch
  // Reset user1's team to userA, user2's team to userB, and user3's team to userA, userB, and userC
  db.Model(&users).Association("Team").Replace(&userA, &userB, &[]User{userA, userB, userC})
  ```

#### 删除关联记录

在GORM中，关联模式中的Replace、Delete和Clear方法主要影响外键引用，而不是关联的记录本身。理解和管理这种行为对于数据完整性至关重要。

- **引用更新**:这些方法将关联的外键更新为null，有效地删除源和关联模型之间的链接。
- **无物理记录删除**:实际关联的记录在数据库中保持不变。

**通过Unscoped来变更默认的删除行为**:

对于需要实际删除关联记录的场景，Unscoped方法会改变此行为。

- **软删除**:将关联的记录标记为已删除(设置deleted_at字段)，而不从数据库中删除它们。

  ```go
  db.Model(&user).Association("Languages").Unscoped().Clear()
  ```

- **永久删除**:对数据库中的关联记录进行物理删除。

  ```go
  // db.Unscoped().Model(&user)
  db.Unscoped().Model(&user).Association("Languages").Unscoped().Clear()
  ```

#### 关联标签（Association Tags）

GORM中的关联标签通常用于指定如何处理模型之间的关联。 这些标签定义了一些关系细节，比如外键，引用和约束。 理解这些标签对于有效地建立和管理模型之间的关系而言至关重要。

标签 | 描述
---- | ----
foreignKey | 指定连接表中用作外键的当前模型的列名。
references | 指示连接表的外键映射到的引用表中的列名。
polymorphic | 定义多态类型，通常是模型名称。
polymorphicValue | 如果没有另行指定，则设置多态值，通常为表名。
many2many | 命名多对多关系中使用的连接表。
joinForeignKey | 标识连接表中映射回当前模型表的外键列。
joinReferences | 指向链接到参考模型表的连接表中的外键列。
constraint | 为关联指定关系约束，如OnUpdate, OnDelete。

### 预加载【3】

#### 预加载示例

GORM允许使用 Preload通过多个SQL中来直接加载关系, 例如：

```go
type User struct {
  gorm.Model
  Username string
  Orders   []Order
}

type Order struct {
  gorm.Model
  UserID uint
  Price  float64
}

// 查找 user 时预加载相关 Order
db.Preload("Orders").Find(&users)
// SELECT * FROM users;
// SELECT * FROM orders WHERE user_id IN (1,2,3,4);

db.Preload("Orders").Preload("Profile").Preload("Role").Find(&users)
// SELECT * FROM users;
// SELECT * FROM orders WHERE user_id IN (1,2,3,4); // has many
// SELECT * FROM profiles WHERE user_id IN (1,2,3,4); // has one
// SELECT * FROM roles WHERE id IN (4,5,6); // belongs to
```

#### Joins 预加载

`Preload`在单独的查询中加载关联数据，`Join Preload`将使用左连接加载关联数据。

```go
db.Joins("Company").Joins("Manager").Joins("Account").First(&user, 1)
db.Joins("Company").Joins("Manager").Joins("Account").First(&user, "users.name = ?", "jinzhu")
db.Joins("Company").Joins("Manager").Joins("Account").Find(&users, "users.id IN ?", []int{1,2,3,4,5}
```

带条件的join

```go
db.Joins("Company", DB.Where(&Company{Alive: true})).Find(&users)
// SELECT `users`.`id`,`users`.`name`,`users`.`age`,`Company`.`id` AS `Company__id`,`Company`.`name` AS `Company__name` 
// FROM `users` 
// LEFT JOIN `companies` AS `Company` 
//ON `users`.`company_id` = `Company`.`id` AND `Company`.`alive` = true;
```

join嵌套模型

```go
db.Joins("Manager").Joins("Manager.Company").Find(&users)
// SELECT "users"."id","users"."created_at","users"."updated_at","users"."deleted_at","users"."name","users"."age","users"."birthday","users"."company_id","users"."manager_id","users"."active","Manager"."id" AS "Manager__id","Manager"."created_at" AS "Manager__created_at","Manager"."updated_at" AS "Manager__updated_at","Manager"."deleted_at" AS "Manager__deleted_at","Manager"."name" AS "Manager__name","Manager"."age" AS "Manager__age","Manager"."birthday" AS "Manager__birthday","Manager"."company_id" AS "Manager__company_id","Manager"."manager_id" AS "Manager__manager_id","Manager"."active" AS "Manager__active","Manager__Company"."id" AS "Manager__Company__id","Manager__Company"."name" AS "Manager__Company__name" 
// FROM "users" 
// LEFT JOIN "users" "Manager" 
// ON "users"."manager_id" = "Manager"."id" AND "Manager"."deleted_at" IS NULL 
// LEFT JOIN "companies" "Manager__Company" 
// ON "Manager"."company_id" = "Manager__Company"."id" 
// WHERE "users"."deleted_at" IS NULL
```

`Join Preload`是一对一的关系，例如has one, belong to

#### 预加载全部

`clause.Associations` can work with `Preload` similar like `Select` when creating/updating,
you can use it to `Preload` all associations, for example:

`clause.Associations`可以像select那样在创建/更新时用于`Preload`，可以用它预加载所有的关联。

```go
type User struct {
  gorm.Model
  Name       string
  CompanyID  uint
  Company    Company
  Role       Role
  Orders     []Order
}

db.Preload(clause.Associations).Find(&users)
```

`clause.Associations`不会预加载嵌套关联，但你可以将它与[嵌套预加载](#嵌套预加载)一起使用，例如:

```go
db.Preload("Orders.OrderItems.Product").Preload(clause.Associations).Find(&users)
```

#### 条件预加载

GORM允许预加载与条件关联，它的工作原理类似于[根据条件查询](#根据条件查询)的内联条件。

```go
// Preload Orders with conditions
db.Preload("Orders", "state NOT IN (?)", "cancelled").Find(&users)
// SELECT * FROM users;
// SELECT * FROM orders WHERE user_id IN (1,2,3,4) AND state NOT IN ('cancelled');

db.Where("state = ?", "active").Preload("Orders", "state NOT IN (?)", "cancelled").Find(&users)
// SELECT * FROM users WHERE state = 'active';
// SELECT * FROM orders WHERE user_id IN (1,2) AND state NOT IN ('cancelled');
```

#### 自定义预加载 SQL

可以通过传入`func(db *gorm.DB) *gorm.DB`来自定义预加载SQL，例如:

```go
db.Preload("Orders", func(db *gorm.DB) *gorm.DB {
  return db.Order("orders.amount DESC")
}).Find(&users)
// SELECT * FROM users;
// SELECT * FROM orders WHERE user_id IN (1,2,3,4) order by orders.amount DESC;
```

#### 嵌套预加载

GORM支持嵌套预加载，例如:

```go
db.Preload("Orders.OrderItems.Product").Preload("CreditCard").Find(&users)

// Customize Preload conditions for `Orders`
// And GORM won't preload unmatched order's OrderItems then
db.Preload("Orders", "state = ?", "paid").Preload("Orders.OrderItems").Find(&users)

```

#### 嵌入式预加载

嵌入式预加载用于嵌入式结构体，特别是同一结构体。嵌入式预加载的语法类似于嵌套预加载，它们由点划分。

```go
type Address struct {
    CountryID int
    Country   Country
}

type Org struct {
    PostalAddress   Address `gorm:"embedded;embeddedPrefix:postal_address_"`
    VisitingAddress Address `gorm:"embedded;embeddedPrefix:visiting_address_"`
    Address         struct {
        ID int
        Address
    }
}

// Only preload Org.Address and Org.Address.Country
db.Preload("Address.Country")  // "Address" is has_one, "Country" is belongs_to (nested association)

// Only preload Org.VisitingAddress
db.Preload("PostalAddress.Country") // "PostalAddress.Country" is belongs_to (embedded association)

// Only preload Org.NestedAddress
db.Preload("NestedAddress.Address.Country") // "NestedAddress.Address.Country" is belongs_to (embedded association)

// All preloaded include "Address" but exclude "Address.Country", because it won't preload nested associations.
db.Preload(clause.Associations)
```

在没有歧义的情况下，可以省略嵌入部分。

```go
type Address struct {
    CountryID int
    Country   Country
}

type Org struct {
    Address Address `gorm:"embedded"`
}

db.Preload("Address.Country").Find(&orgs)
db.Preload("Country").Find(&orgs) // omit "Address" because there is no ambiguity
```

## 教程

### 上下文【2】

GORM 的上下文支持由 WithContext 方法启用，是一项强大的功能，可以增强 Go 应用程序中数据库操作的灵活性和控制力。 它允许在不同的操作模式、超时设置以及甚至集成到钩子/回调和中间件中进行上下文管理。

#### 单会话模式

单会话模式适用于执行单个操作。它确保特定操作在上下文范围内执行，从而实现更好的控制和监视。

```go
db.WithContext(ctx).Find(&users)

```

#### 连续会话模式

连续会话模式是执行一系列相关操作的理想模式。它跨这些操作维护上下文，这在事务等场景中特别有用。

```go
tx := db.WithContext(ctx)
tx.First(&user, 1)
tx.Model(&user).Update("role", "admin")
```

#### 上下文超时

给传递给`db.WithContext`的上下文设置超时可以控制长时间运行查询的持续时间。这对于维护性能和避免数据库交互中的资源锁定至关重要。

```go
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()

db.WithContext(ctx).Find(&users)
```

#### Hooks/Callbacks 中的 Context

上下文也可以在GORM的钩子/回调中访问。这样就可以在这些生命周期事件中使用上下文信息。

```go
func (u *User) BeforeCreate(tx *gorm.DB) (err error) {
  ctx := tx.Statement.Context
  // ... use context
  return
}
```

#### 与Chi中间件集成

GORM的上下文支持扩展到web服务器中间件，例如Chi路由器中的那些。这允许为web请求范围内的所有数据库操作设置一个带有超时的上下文。

```go
func SetDBMiddleware(next http.Handler) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    timeoutContext, _ := context.WithTimeout(context.Background(), time.Second)
    ctx := context.WithValue(r.Context(), "DB", db.WithContext(timeoutContext))
    next.ServeHTTP(w, r.WithContext(ctx))
  })
}

// Router setup
r := chi.NewRouter()
r.Use(SetDBMiddleware)

// Route handlers
r.Get("/", func(w http.ResponseWriter, r *http.Request) {
  db, ok := r.Context().Value("DB").(*gorm.DB)
  // ... db operations
})

r.Get("/user", func(w http.ResponseWriter, r *http.Request) {
  db, ok := r.Context().Value("DB").(*gorm.DB)
  // ... db operations
})
```

**注意**：使用WithContext设置上下文是运goroutine安全的。这确保了跨多个goroutine安全地管理数据库操作。要了解更多细节，请参阅GORM中的[Session](#session2)文档。

#### Logger集成

GORM的Logger还接受上下文，它可用于日志跟踪和与现有日志基础设施集成。查阅[Logger](#logger1)获取更多细节。

### 错误处理【2】

#### 基本错误处理

GORM将错误处理集成到其可链式方法语法中。 `*gorm.DB`实例包含一个`Error`字段，当发生错误时会被设置。 通常的做法是在执行数据库操作后，特别是在完成方法（Finisher Methods，见链式操作的[方法类别]）后，检查这个字段。

```go
if err := db.Where("name = ?", "jinzhu").First(&user).Error; err != nil {
  // 处理错误...
}
if result := db.Where("name = ?", "jinzhu").First(&user); result.Error != nil {
  // 处理错误...
}
```

#### ErrRecordNotFound

当使用`First`、`Last`、`Take`等方法未找到记录时，GORM会返回E`rrRecordNotFound`。

```go
err := db.First(&user, 100).Error
if errors.Is(err, gorm.ErrRecordNotFound) {
  // 处理未找到记录的错误...
}
```

#### 处理错误代码

许多数据库返回带有特定代码的错误，这些代码可能表明各种问题，如约束违规、连接问题或语法错误。 在GORM中处理这些错误代码需要解析数据库返回的错误并提取相关代码。

```go
import (
    "github.com/go-sql-driver/mysql"
    "gorm.io/gorm"
)

// ...

result := db.Create(&newRecord)
if result.Error != nil {
    if mysqlErr, ok := result.Error.(*mysql.MySQLError); ok {
        switch mysqlErr.Number {
        case 1062: // MySQL中表示重复条目的代码
            // 处理重复条目
        // 为其他特定错误代码添加案例
        default:
            // 处理其他错误
        }
    } else {
        // 处理非MySQL错误或未知错误
    }
}
```

#### 方言转换错误

当启用TranslateError时，GORM可以返回与所使用的数据库方言相关的特定错误，GORM将数据库特有的错误转换为其自己的通用错误。

```go
db, err := gorm.Open(postgres.Open(postgresDSN), &gorm.Config{TranslateError: true})
```

- `ErrDuplicatedKey`
  当插入操作违反唯一约束时，会发生此错误：

  ```go
  result := db.Create(&newRecord)
  if errors.Is(result.Error, gorm.ErrDuplicatedKey) {
      // 处理重复键错误...
  }
  ```

- `ErrForeignKeyViolated`
当违反外键约束时，会遇到此错误：

  ```go
  result := db.Create(&newRecord)
  if errors.Is(result.Error, gorm.ErrForeignKeyViolated) {
      // 处理外键违规错误...
  }
  ```

通过启用`TranslateError`，GORM提供了一种更统一的错误处理方式，将不同数据库的特定错误转换为常见的GORM错误类型。

#### Errors

要获取GORM可能返回的完整错误列表，请参考GORM文档中的[错误列表](https://github.com/go-gorm/gorm/blob/master/errors.go)。

### 链式操作【1】

GORM的方法链接特性支持流畅的编码风格。例如:

```go
db.Where("name = ?", "jinzhu").Where("age = ?", 18).First(&user)

```

#### 方法类别

- `Chain Methods`

  链式方法用于修改或追加子句到当前语句。一些常见的链式方法包括:
  - `Where`
  - `Select`
  - `Omit`
  - `Joins`
  - `Scopes`
  - `Preload`
  - `Raw` (Note: `Raw` 不能与其他可链方法一起使用来构建SQL)

有关全面的列表，请访问[GORM Chainable API](https://github.com/go-gorm/gorm/blob/master/chainable_api.go)。此外，[SQL 构建器](#原生sql和sql生成器)还提供了关于子句的更多细节。

- `Finisher Methods`
  完成器方法是即时的，执行生成和运行SQL命令的注册回调。这类方法包括:
  - `Create`
  - `First`
  - `Find`
  - `Take`
  - `Save`
  - `Update`
  - `Delete`
  - `Scan`
  - `Row`
  - `Rows`

有关全面的列表，请访问[GORM Finisher API](https://github.com/go-gorm/gorm/blob/master/finisher_api.go)。

- `New Session Methods`

GORM将`Session`、`WithContext`和`Debug`等方法定义为新会话方法，这些方法对于创建可共享和可重用的`*GORM.DB`实例至关重要。有关更多详细信息，请参阅[Session](#session2)。

#### 可重用性和安全性

GORM的一个关键方面是理解`*GORM.DB`实例何时可以安全重用。在`Chain Method`或`Finisher Method`之后，GORM返回一个初始化的`* GORM.DB`实例。此实例对于重用来说是不安全的，因为它可能会保留以前操作的条件，从而可能导致受污染的SQL查询。例如:

- Example of Unsafe Reuse

```go
queryDB := DB.Where("name = ?", "jinzhu")

// First query
queryDB.Where("age > ?", 10).First(&user)
// SQL: SELECT * FROM users WHERE name = "jinzhu" AND age > 10

// Second query with unintended compounded condition
queryDB.Where("age > ?", 20).First(&user2)
// SQL: SELECT * FROM users WHERE name = "jinzhu" AND age > 10 AND age > 20
```

- Example of Safe Reuse

要安全地重用`*gorm.DB`实例，请使用New Session Method:

```go
queryDB := DB.Where("name = ?", "jinzhu").Session(&gorm.Session{})

// First query
queryDB.Where("age > ?", 10).First(&user)
// SQL: SELECT * FROM users WHERE name = "jinzhu" AND age > 10

// Second query, safely isolated
queryDB.Where("age > ?", 20).First(&user2)
// SQL: SELECT * FROM users WHERE name = "jinzhu" AND age > 20
```

在这个场景中，使用`Session(&gorm.Session{})`可以确保每个查询都从一个新的上下文开始，从而防止SQL查询受到先前操作条件的污染。这对于维护数据库交互的完整性和准确性至关重要。

#### Examples for Clarity

没看懂在讲什么，好像和上面差不多，总是用Session就对了。

### Session【2】

#### DryRun

生成 SQL 但不执行。 它可以用于准备或测试生成的 SQL，例如：

```go
// 新建会话模式
stmt := db.Session(&Session{DryRun: true}).First(&user, 1).Statement
stmt.SQL.String() //=> SELECT * FROM `users` WHERE `id` = $1 ORDER BY `id`
stmt.Vars         //=> []interface{}{1}

// 全局 DryRun 模式
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{DryRun: true})

// 不同的数据库生成不同的 SQL
stmt := db.Find(&user, 1).Statement
stmt.SQL.String() //=> SELECT * FROM `users` WHERE `id` = $1 // PostgreSQL
stmt.SQL.String() //=> SELECT * FROM `users` WHERE `id` = ?  // MySQL
stmt.Vars         //=> []interface{}{1}
```

可以使用下面的代码生成最终的 SQL：

```go
// 注意：SQL 并不总是能安全地执行，GORM 仅将其用于日志，它可能导致会 SQL 注入
db.Dialector.Explain(stmt.SQL.String(), stmt.Vars...)
// SELECT * FROM `users` WHERE `id` = 1
```

#### 预编译

没看懂有什么用

#### NewDB

通过 NewDB 选项创建一个不带之前条件的新 DB，例如：

```go
tx := db.Where("name = ?", "jinzhu").Session(&gorm.Session{NewDB: true})

tx.First(&user)
// SELECT * FROM users ORDER BY id LIMIT 1

tx.First(&user, "id = ?", 10)
// SELECT * FROM users WHERE id = 10 ORDER BY id

// 不带 `NewDB` 选项
tx2 := db.Where("name = ?", "jinzhu").Session(&gorm.Session{})
tx2.First(&user)
// SELECT * FROM users WHERE name = "jinzhu" ORDER BY id
```

#### 初始化

创建一个新的数据库会话（DB 对象），这个会话不再支持方法链式调用和 Goroutine 安全性。这样的设计允许对查询行为进行更细粒度的控制，但也意味着需要更小心地管理查询的构建过程。

```go
tx := db.Session(&gorm.Session{Initialized: true})
```

#### 跳过钩子

如果想跳过 `Hooks` 方法，您可以使用 `SkipHooks` 会话模式，例如：

```go
DB.Session(&gorm.Session{SkipHooks: true}).Create(&user)
DB.Session(&gorm.Session{SkipHooks: true}).Create(&users)
DB.Session(&gorm.Session{SkipHooks: true}).CreateInBatches(users, 100)
DB.Session(&gorm.Session{SkipHooks: true}).Find(&user)
DB.Session(&gorm.Session{SkipHooks: true}).Delete(&user)
DB.Session(&gorm.Session{SkipHooks: true}).Model(User{}).Where("age > ?", 18).Updates(&user)
```

#### 禁用嵌套事务

在一个 DB 事务中使用 `Transaction` 方法，GORM 会使用 `SavePoint(savedPointName)`，`RollbackTo(savedPointName)` 为提供嵌套事务支持。 可以通过 `DisableNestedTransaction` 选项关闭它，例如：

```go
db.Session(&gorm.Session{
  DisableNestedTransaction: true,
}).CreateInBatches(&users, 100)
```

#### AllowGlobalUpdate

GORM 默认不允许进行全局更新/删除，该操作会返回 `ErrMissingWhereClause` 错误。 可以通过将一个选项设置为 true 来启用它，例如：

```go
db.Session(&gorm.Session{
  AllowGlobalUpdate: true,
}).Model(&User{}).Update("name", "jinzhu")
// UPDATE users SET `name` = "jinzhu"
```

#### FullSaveAssociations

在创建、更新记录时，GORM 会通过 `Upsert` 自动保存关联及其引用记录。 如果您想要更新关联的数据，您应该使用 `FullSaveAssociations` 模式，例如：

```go
db.Session(&gorm.Session{FullSaveAssociations: true}).Updates(&user)
// ...
// INSERT INTO "addresses" (address1) VALUES ("Billing Address - Address 1"), ("Shipping Address - Address 1") ON DUPLICATE KEY SET address1=VALUES(address1);
// INSERT INTO "users" (name,billing_address_id,shipping_address_id) VALUES ("jinzhu", 1, 2);
// INSERT INTO "emails" (user_id,email) VALUES (111, "jinzhu@example.com"), (111, "jinzhu-2@example.com") ON DUPLICATE KEY SET email=VALUES(email);
// ...
```

#### Context

通过 `Context` 选项，您可以传入 `Context` 来追踪 SQL 操作，例如：

```go
timeoutCtx, _ := context.WithTimeout(context.Background(), time.Second)
tx := db.Session(&Session{Context: timeoutCtx})

tx.First(&user) // 带有 context timeoutCtx 的查询操作
tx.Model(&user).Update("role", "admin") // 带有 context timeoutCtx 的更新操作
```

GORM 也提供了简写形式的方法 `WithContext`，其实现如下：

```go
func (db *DB) WithContext(ctx context.Context) *DB {
  return db.Session(&Session{Context: ctx})
}
```

#### 自定义 Logger

Gorm 允许使用 `Logger` 选项自定义内建 Logger，查看 [Logger](#logger1) 获取更多信息。

```go
newLogger := logger.New(log.New(os.Stdout, "\r\n", log.LstdFlags),
              logger.Config{
                SlowThreshold: time.Second,
                LogLevel:      logger.Silent,
                Colorful:      false,
              })
db.Session(&Session{Logger: newLogger})

db.Session(&Session{Logger: logger.Default.LogMode(logger.Silent)})
```

#### NowFunc

`NowFunc` 允许改变 GORM 获取当前时间的实现，例如：

```go
db.Session(&Session{
  NowFunc: func() time.Time {
    return time.Now().Local()
  },
})
```

#### 调试

`Debug` 只是将会话的 Logger 修改为调试模式的简写形式，其实现如下：

```go
func (db *DB) Debug() (tx *DB) {
  return db.Session(&Session{
    Logger:         db.Logger.LogMode(logger.Info),
  })
}
```

#### 查询字段

声明查询字段,仅返回那些在查询条件中被明确设置为非零值的字段。

```go
db.Session(&gorm.Session{QueryFields: true}).Find(&user)
// SELECT `users`.`name`, `users`.`age`, ... FROM `users` // 有该选项
// SELECT * FROM `users` // 没有该选项
```

#### CreateBatchSize

默认批量大小

```go
users = [5000]User{{Name: "jinzhu", Pets: []Pet{pet1, pet2, pet3}}...}

db.Session(&gorm.Session{CreateBatchSize: 1000}).Create(&users)
// INSERT INTO users xxx (需 5 次)
// INSERT INTO pets xxx (需 15 次)
```

### 钩子【2】

#### 对象生命周期

Hook 是在创建、查询、更新、删除等操作之前、之后调用的函数。

如果已经为模型定义了指定的方法，它会在创建、更新、查询、删除时自动被调用。如果任何回调返回错误，GORM 将停止后续的操作并回滚事务。

钩子方法的函数类型应该是 `func(*gorm.DB) error`

#### Hook

- 创建对象
  
  创建时可用的 hook

  ```text
  // 开始事务
  BeforeSave
  BeforeCreate
  // 关联前的 save
  // 插入记录至 db
  // 关联后的 save
  AfterCreate
  AfterSave
  // 提交或回滚事务
  ```

  代码示例：

  ```go
  func (u *User) BeforeCreate(tx *gorm.DB) (err error) {
  u.UUID = uuid.New()

  if !u.IsValid() {
    err = errors.New("can't save invalid data")
  }
  return
  }

  func (u *User) AfterCreate(tx*gorm.DB) (err error) {
    if u.ID == 1 {
      tx.Model(u).Update("role", "admin")
    }
    return
  }
  ```

  **注意**: 在 GORM 中保存、删除操作会默认运行在事务上， 因此在事务完成之前该事务中所作的更改是不可见的，如果钩子返回了任何错误，则修改将被回滚。
  
- 更新对象
  
  更新时可用的 hook

  ```text
  // 开始事务
  BeforeSave
  BeforeUpdate
  // 关联前的 save
  // 更新 db
  // 关联后的 save
  AfterUpdate
  AfterSave
  // 提交或回滚事务
  ```

  代码示例：

  ```go
  func (u *User) BeforeUpdate(tx *gorm.DB) (err error) {
    if u.readonly() {
      err = errors.New("read only user")
    }
    return
  }

  // 在同一个事务中更新数据
  func (u *User) AfterUpdate(tx *gorm.DB) (err error) {
    if u.Confirmed {
      tx.Model(&Address{}).Where("user_id = ?", u.ID).Update("verfied", true)
    }
    return
  }
  ```

- 删除对象
  
  删除时可用的 hook

  ```text
  // 开始事务
  BeforeDelete
  // 删除 db 中的数据
  AfterDelete
  // 提交或回滚事务
  代码示例：
  ```

  ```go
  // 在同一个事务中更新数据
  func (u *User) AfterDelete(tx *gorm.DB) (err error) {
    if u.Confirmed {
      tx.Model(&Address{}).Where("user_id = ?", u.ID).Update("invalid", false)
    }
    return
  }
  ```

- 查询对象

  ```text
  查询时可用的 hook

  // 从 db 中加载数据
  // Preloading (eager loading)
  AfterFind
  ```

  ```go
  代码示例：

  func (u *User) AfterFind(tx *gorm.DB) (err error) {
    if u.MemberShip == "" {
      u.MemberShip = "user"
    }
    return
  }
  ```

#### 修改当前操作

```go
func (u *User) BeforeCreate(tx *gorm.DB) error {
  // 通过 tx.Statement 修改当前操作，例如：
  tx.Statement.Select("Name", "Age")
  tx.Statement.AddClause(clause.OnConflict{DoNothing: true})

  // tx 是带有 `NewDB` 选项的新会话模式 
  // 基于 tx 的操作会在同一个事务中，但不会带上任何当前的条件
  err := tx.First(&role, "name = ?", user.Role).Error
  // SELECT * FROM roles WHERE name = "admin"
  // ...
  return err
}
```

### 事务【3】

#### 禁用默认事务

为了确保数据一致性，GORM 会在事务里执行写入操作（创建、更新、删除）。如果没有这方面的要求，可以在初始化时禁用它，这将获得大约 30%+ 性能提升。

```go
// 全局禁用
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  SkipDefaultTransaction: true,
})

// 持续会话模式
tx := db.Session(&Session{SkipDefaultTransaction: true})
tx.First(&user, 1)
tx.Find(&users)
tx.Model(&user).Update("Age", 18)
```

#### 事务示例

```go
db.Transaction(func(tx *gorm.DB) error {
  // 在事务中执行一些 db 操作（从这里开始，应该使用 'tx' 而不是 'db'）
  if err := tx.Create(&Animal{Name: "Giraffe"}).Error; err != nil {
    // 返回任何错误都会回滚事务
    return err
  }

  if err := tx.Create(&Animal{Name: "Lion"}).Error; err != nil {
    return err
  }

  // 返回 nil 提交事务
  return nil
})
```

- 嵌套事务

GORM 支持嵌套事务，可以回滚较大事务内执行的一部分操作，例如：

```go
db.Transaction(func(tx *gorm.DB) error {
  tx.Create(&user1)

  tx.Transaction(func(tx2 *gorm.DB) error {
    tx2.Create(&user2)
    return errors.New("rollback user2") // Rollback user2
  })

  tx.Transaction(func(tx3 *gorm.DB) error {
    tx3.Create(&user3)
    return nil
  })

  return nil
})

// Commit user1, user3
```

#### 手动事务

Gorm 支持直接调用事务控制方法（commit、rollback），例如：

```go
// 开始事务
tx := db.Begin()

// 在事务中执行一些 db 操作（从这里开始，您应该使用 'tx' 而不是 'db'）
tx.Create(...)

// ...

// 遇到错误时回滚事务
tx.Rollback()

// 否则，提交事务
tx.Commit()
```

- 一个特殊的示例

```go
func CreateAnimals(db *gorm.DB) error {
  // 再唠叨一下，事务一旦开始，你就应该使用 tx 处理数据
  tx := db.Begin()
  defer func() {
    if r := recover(); r != nil {
      tx.Rollback()
    }
  }()

  if err := tx.Error; err != nil {
    return err
  }

  if err := tx.Create(&Animal{Name: "Giraffe"}).Error; err != nil {
     tx.Rollback()
     return err
  }

  if err := tx.Create(&Animal{Name: "Lion"}).Error; err != nil {
     tx.Rollback()
     return err
  }

  return tx.Commit().Error
}
```

### 迁移【2】

AutoMigrate 会创建表、缺失的外键、约束、列和索引。 如果大小、精度、是否为空可以更改，则AutoMigrate 会改变列的类型。 出于保护数据的目的，它 **不会** 删除未使用的列

#### AutoMigrate

```go
db.AutoMigrate(&User{})

db.AutoMigrate(&User{}, &Product{}, &Order{})

// 创建表时添加后缀
db.Set("gorm:table_options", "ENGINE=InnoDB").AutoMigrate(&User{})
```

AutoMigrate 会自动创建数据库外键约束，可以在初始化时禁用此功能，例如：

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  DisableForeignKeyConstraintWhenMigrating: true,
})
```

#### Migrator 接口

GORM 提供了 Migrator 接口，该接口为每个数据库提供了统一的 API 接口，可用来为的数据库构建独立迁移.

```go
type Migrator interface {
  // AutoMigrate
  AutoMigrate(dst ...interface{}) error

  // Database
  CurrentDatabase() string
  FullDataTypeOf(*schema.Field) clause.Expr

  // Tables
  CreateTable(dst ...interface{}) error
  DropTable(dst ...interface{}) error
  HasTable(dst interface{}) bool
  RenameTable(oldName, newName interface{}) error
  GetTables() (tableList []string, err error)

  // Columns
  AddColumn(dst interface{}, field string) error
  DropColumn(dst interface{}, field string) error
  AlterColumn(dst interface{}, field string) error
  MigrateColumn(dst interface{}, field *schema.Field, columnType ColumnType) error
  HasColumn(dst interface{}, field string) bool
  RenameColumn(dst interface{}, oldName, field string) error
  ColumnTypes(dst interface{}) ([]ColumnType, error)

  // Views
  CreateView(name string, option ViewOption) error
  DropView(name string) error

  // Constraints
  CreateConstraint(dst interface{}, name string) error
  DropConstraint(dst interface{}, name string) error
  HasConstraint(dst interface{}, name string) bool

  // Indexes
  CreateIndex(dst interface{}, name string) error
  DropIndex(dst interface{}, name string) error
  HasIndex(dst interface{}, name string) bool
  RenameIndex(dst interface{}, oldName, newName string) error
}
```

- **当前数据库**
  返回当前使用的数据库名

  ```go
  db.Migrator().CurrentDatabase()
  ```

- 表

  ```go
  // 为 `User` 创建表
  db.Migrator().CreateTable(&User{})

  // 将 "ENGINE=InnoDB" 添加到创建 `User` 的 SQL 里去
  db.Set("gorm:table_options", "ENGINE=InnoDB").Migrator().CreateTable(&User{})

  // 检查 `User` 对应的表是否存在
  db.Migrator().HasTable(&User{})
  db.Migrator().HasTable("users")

  // 如果存在表则删除（删除时会忽略、删除外键约束)
  db.Migrator().DropTable(&User{})
  db.Migrator().DropTable("users")

  // 重命名表
  db.Migrator().RenameTable(&User{}, &UserInfo{})
  db.Migrator().RenameTable("users", "user_infos")
  ```

- 列

  ```go
  type User struct {
   Name string   
  }

  // 添加 name 字段
  db.Migrator().AddColumn(&User{}, "Name")
  // 删除 name 字段
  db.Migrator().DropColumn(&User{}, "Name")
  // 修改 name 字段
  db.Migrator().AlterColumn(&User{}, "Name")
  // 检查 name 字段是否存在
  db.Migrator().HasColumn(&User{}, "Name")

  type User struct {
    Name    string 
    NewName string
  }

  // 字段重命名
  db.Migrator().RenameColumn(&User{}, "Name", "NewName")
  db.Migrator().RenameColumn(&User{}, "name", "new_name")

  // 字段类型
  db.Migrator().ColumnTypes(&User{}) ([]gorm.ColumnType, error)

  type ColumnType interface {
      Name() string
      DatabaseTypeName() string                 // varchar
      ColumnType() (columnType string, ok bool) // varchar(64)
      PrimaryKey() (isPrimaryKey bool, ok bool)
      AutoIncrement() (isAutoIncrement bool, ok bool)
      Length() (length int64, ok bool)
      DecimalSize() (precision int64, scale int64, ok bool)
      Nullable() (nullable bool, ok bool)
      Unique() (unique bool, ok bool)
      ScanType() reflect.Type
      Comment() (value string, ok bool)
      DefaultValue() (value string, ok bool)
  }
  ```

- Views

  通过`ViewOption`创建视图。关于ViewOption:

  - `Query`是一个子查询，这是必需的。
  - 如果`Replace`为true，执行CREATE或Replace，否则执行CREATE。
  - 如果`CheckOption`不为空，则追加到sql，例如`WITH LOCAL CHECK OPTION`。

```go
query := db.Model(&User{}).Where("age > ?", 20)

// Create View
db.Migrator().CreateView("users_pets", gorm.ViewOption{Query: query})
// CREATE VIEW `users_view` AS SELECT * FROM `users` WHERE age > 20

// Create or Replace View
db.Migrator().CreateView("users_pets", gorm.ViewOption{Query: query, Replace: true})
// CREATE OR REPLACE VIEW `users_pets` AS SELECT * FROM `users` WHERE age > 20

// Create View With Check Option
db.Migrator().CreateView("users_pets", gorm.ViewOption{Query: query, CheckOption: "WITH CHECK OPTION"})
// CREATE VIEW `users_pets` AS SELECT * FROM `users` WHERE age > 20 WITH CHECK OPTION

// Drop View
db.Migrator().DropView("users_pets")
// DROP VIEW IF EXISTS "users_pets"
```

- Constraints

```go
type UserIndex struct {
  Name  string `gorm:"check:name_checker,name <> 'jinzhu'"`
}

// Create constraint
db.Migrator().CreateConstraint(&User{}, "name_checker")

// Drop constraint
db.Migrator().DropConstraint(&User{}, "name_checker")

// Check constraint exists
db.Migrator().HasConstraint(&User{}, "name_checker")
```

为关系创建外键：

```go
type User struct {
  gorm.Model
  CreditCards []CreditCard
}

type CreditCard struct {
  gorm.Model
  Number string
  UserID uint
}

// create database foreign key for user & credit_cards
db.Migrator().CreateConstraint(&User{}, "CreditCards")
db.Migrator().CreateConstraint(&User{}, "fk_users_credit_cards")
// ALTER TABLE `credit_cards` ADD CONSTRAINT `fk_users_credit_cards` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)

// check database foreign key for user & credit_cards exists or not
db.Migrator().HasConstraint(&User{}, "CreditCards")
db.Migrator().HasConstraint(&User{}, "fk_users_credit_cards")

// drop database foreign key for user & credit_cards
db.Migrator().DropConstraint(&User{}, "CreditCards")
db.Migrator().DropConstraint(&User{}, "fk_users_credit_cards")
```

- Indexes

```go
type User struct {
  gorm.Model
  Name string `gorm:"size:255;index:idx_name,unique"`
}

// Create index for Name field
db.Migrator().CreateIndex(&User{}, "Name")
db.Migrator().CreateIndex(&User{}, "idx_name")

// Drop index for Name field
db.Migrator().DropIndex(&User{}, "Name")
db.Migrator().DropIndex(&User{}, "idx_name")

// Check Index exists
db.Migrator().HasIndex(&User{}, "Name")
db.Migrator().HasIndex(&User{}, "idx_name")

type User struct {
  gorm.Model
  Name  string `gorm:"size:255;index:idx_name,unique"`
  Name2 string `gorm:"size:255;index:idx_name_2,unique"`
}
// Rename index name
db.Migrator().RenameIndex(&User{}, "Name", "Name2")
db.Migrator().RenameIndex(&User{}, "idx_name", "idx_name_2")
```

#### 约束

GORM在自动迁移或创建表时创建约束，详细信息请参见[约束](#约束1)或[数据库索引](#索引1)。

#### Atlas Integration

[Atlas](https://atlasgo.io/)是一个与GORM正式集成的开源数据库迁移工具。
虽然GORM的`AutoMigrate`特性在大多数情况下都可以工作，但在某些情况下，您可能需要切换到版本化的迁移策略。
一旦发生这种情况，规划迁移脚本并确保它们在运行时符合GORM期望的责任就转移给了开发人员。
Atlas可以使用官方的GORM Provider为开发人员自动规划数据库模式迁移。配置提供程序后，您可以通过运行以下命令自动规划迁移:

`atlas migrate diff --env gorm`

要了解如何将Atlas与GORM一起使用，请查看[官方文档](https://atlasgo.io/guides/orms/gorm)。

#### Other Migration Tools

要将GORM与其他基于go的迁移工具一起使用，GORM提供了一个可能对您有所帮助的通用DB接口。

```go
// returns `*sql.DB`
db.DB()
```

### Logger【1】

#### 日志

Gorm 有一个 默认 logger 实现，默认情况下，它会打印慢 SQL 和错误

Logger 接受的选项不多，您可以在初始化时自定义它，例如：

```go
newLogger := logger.New(
  log.New(os.Stdout, "\r\n", log.LstdFlags), // io writer
  logger.Config{
    SlowThreshold:              time.Second,   // Slow SQL threshold
    LogLevel:                   logger.Silent, // Log level
    IgnoreRecordNotFoundError: true,           // Ignore ErrRecordNotFound error for logger
    ParameterizedQueries:      true,           // Don't include params in the SQL log
    Colorful:                  false,          // Disable color
  },
)

// Globally mode
db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{
  Logger: newLogger,
})

// Continuous session mode
tx := db.Session(&Session{Logger: newLogger})
tx.First(&user)
tx.Model(&user).Update("Age", 18)
```

**日志级别**
GORM 定义了这些日志级别：`Silent`、`Error`、`Warn`、`Info`

```go
db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{
  Logger: logger.Default.LogMode(logger.Silent),
})
```

**Debug**
Debug 单个操作，将当前操作的 log 级别调整为 logger.Info
`db.Debug().Where("name = ?", "jinzhu").First(&User{})`

#### 自定义Logger

参考 GORM 的 默认 logger 来定义您自己的 logger

Logger 需要实现以下接口，它接受 context，所以你可以用它来追踪日志

```GO
type Interface interface {
    LogMode(LogLevel) Interface
    Info(context.Context, string, ...interface{})
    Warn(context.Context, string, ...interface{})
    Error(context.Context, string, ...interface{})
    Trace(ctx context.Context, begin time.Time, fc func() (sql string, rowsAffected int64), err error)
}
```

### 性能【2】

#### 性能-禁用默认事务

对于写操作（创建、更新、删除），为了确保数据的完整性，GORM 会将它们封装在一个事务里。但这会降低性能，可以在初始化时禁用这种方式

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  SkipDefaultTransaction: true,
})
```

#### 缓存预编译语句

执行任何 SQL 时都创建并缓存预编译语句，可以提高后续的调用速度

```go
// 全局模式
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  PrepareStmt: true,
})

// 会话模式
tx := db.Session(&Session{PrepareStmt: true})
tx.First(&user, 1)
tx.Find(&users)
tx.Model(&user).Update("Age", 18)
```

**注意** 也可以参考如何为 MySQL 开启 interpolateparams 以减少 roundtrip <https://github.com/go-sql-driver/mysql#interpolateparams>

**带 PreparedStmt 的 SQL 生成器**:

Prepared Statement 也可以和原生 SQL 一起使用，例如：

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  PrepareStmt: true,
})

db.Raw("select sum(age) from users where role = ?", "admin").Scan(&age)
```

也可以使用 GORM 的 API [DryRun](#dryrun) 模式 编写 SQL 并执行 prepared statement ，查看 [会话模式](#session2) 获取详情

#### 选择字段

默认情况下，GORM 在查询时会选择所有的字段，您可以使用 Select 来指定您想要的字段
`db.Select("Name", "Age").Find(&Users{})`

或者定义一个较小的 API 结构体，使用 [智能选择字段](#智能选择字段)功能

```go
type User struct {
  ID     uint
  Name   string
  Age    int
  Gender string
  // 假设后面还有几百个字段...
}

type APIUser struct {
  ID   uint
  Name string
}

// 查询时会自动选择 `id`、`name` 字段
db.Model(&User{}).Limit(10).Find(&APIUser{})
// SELECT `id`, `name` FROM `users` LIMIT 10
```

#### 迭代、FindInBatches

用迭代或 in batches 查询并处理记录

#### Index Hints

[Index](#索引1) 用于提高数据检索和 SQL 查询性能。 Index Hints 向优化器提供了在查询处理过程中如何选择索引的信息。与 optimizer 相比，它可以更灵活地选择更有效的执行计划

```go
import "gorm.io/hints"

db.Clauses(hints.UseIndex("idx_user_name")).Find(&User{})
// SELECT * FROM `users` USE INDEX (`idx_user_name`)

db.Clauses(hints.ForceIndex("idx_user_name", "idx_user_id").ForJoin()).Find(&User{})
// SELECT * FROM `users` FORCE INDEX FOR JOIN (`idx_user_name`,`idx_user_id`)"

db.Clauses(
    hints.ForceIndex("idx_user_name", "idx_user_id").ForOrderBy(),
    hints.IgnoreIndex("idx_user_name").ForGroupBy(),
).Find(&User{})
// SELECT * FROM `users` FORCE INDEX FOR ORDER BY (`idx_user_name`,`idx_user_id`) IGNORE INDEX FOR GROUP BY (`idx_user_name`)"
```

#### 读写分离

通过读写分离提高数据吞吐量，查看 [Database Resolver](#database-resolver) 获取详情

### 自定义数据类型【4】

#### 实现自定义数据类型

**Scanner / Valuer**
自定义的数据类型必须实现 Scanner 和 Valuer 接口，以便让 GORM 知道如何将该类型接收、保存到数据库

```go
type JSON json.RawMessage

// 实现 sql.Scanner 接口，Scan 将 value 扫描至 Jsonb 反序列化
func (j *JSON) Scan(value interface{}) error {
  bytes, ok := value.([]byte)
  if !ok {
    return errors.New(fmt.Sprint("Failed to unmarshal JSONB value:", value))
  }

  result := json.RawMessage{}
  err := json.Unmarshal(bytes, &result)
  *j = JSON(result)
  return err
}

// 实现 driver.Valuer 接口，Value 返回 json value 序列化
func (j JSON) Value() (driver.Value, error) {
  if len(j) == 0 {
    return nil, nil
  }
  return json.RawMessage(j).MarshalJSON()
}
```

**GormDataTypeInterface**
GORM 会从 type 标签 中读取字段的数据库类型，如果找不到，则会检查该结构体是否实现了 `GormDBDataTypeInterface` 或 `GormDataTypeInterface` 接口，然后使用接口返回值作为数据类型

```go
type GormDataTypeInterface interface {
  GormDataType() string
}

type GormDBDataTypeInterface interface {
  GormDBDataType(*gorm.DB, *schema.Field) string
}
```

GormDataType 的结果用于生成通用数据类型，也可以通过 schema.Field 的 DataType 字段得到。这在 编写插件 或者 hook 时可能会有用.
在迁移时，GormDBDataType 通常会为当前驱动返回恰当的数据类型
如果 struct 没有实现 GormDBDataTypeInterface 或 GormDataTypeInterface 接口，GORM 会根据 struct 第一个字段推测其数据类型

GormValuerInterface
条件表达式

看不懂，整的我有点想吐，生理性难受。

#### 自定义数据类型集合

挂了个网站看示例，略

### Scope【3】

作用域允许你复用通用的逻辑，这种共享逻辑需要定义为类型`func(*gorm.DB) *gorm.DB`。

感觉拿别的函数子查询什么的也能做到相同效果。

#### Scope查询

```go
func AmountGreaterThan1000(db *gorm.DB) *gorm.DB {
  return db.Where("amount > ?", 1000)
}

func PaidWithCreditCard(db *gorm.DB) *gorm.DB {
  return db.Where("pay_mode_sign = ?", "C")
}

func PaidWithCod(db *gorm.DB) *gorm.DB {
  return db.Where("pay_mode_sign = ?", "C")
}

func OrderStatus(status []string) func (db *gorm.DB) *gorm.DB {
  return func (db *gorm.DB) *gorm.DB {
    return db.Where("status IN (?)", status)
  }
}

db.Scopes(AmountGreaterThan1000, PaidWithCreditCard).Find(&orders)
// 查找所有金额大于 1000 的信用卡订单

db.Scopes(AmountGreaterThan1000, PaidWithCod).Find(&orders)
// 查找所有金额大于 1000 的 COD 订单

db.Scopes(AmountGreaterThan1000, OrderStatus([]string{"paid", "shipped"})).Find(&orders)
// 查找所有金额大于1000 的已付款或已发货订单
```

**分页**：

```go
func Paginate(r *http.Request) func(db *gorm.DB) *gorm.DB {
  return func (db *gorm.DB) *gorm.DB {
    q := r.URL.Query()
    page, _ := strconv.Atoi(q.Get("page"))
    if page <= 0 {
      page = 1
    }

    pageSize, _ := strconv.Atoi(q.Get("page_size"))
    switch {
    case pageSize > 100:
      pageSize = 100
    case pageSize <= 0:
      pageSize = 10
    }

    offset := (page - 1) * pageSize
    return db.Offset(offset).Limit(pageSize)
  }
}

db.Scopes(Paginate(r)).Find(&users)
db.Scopes(Paginate(r)).Find(&articles)
```

#### scope动态表

使用 `Scopes` 来动态指定查询的表

```go
func TableOfYear(user *User, year int) func(db *gorm.DB) *gorm.DB {
  return func(db *gorm.DB) *gorm.DB {
        tableName := user.TableName() + strconv.Itoa(year)
        return db.Table(tableName)
  }
}

DB.Scopes(TableOfYear(user, 2019)).Find(&users)
// SELECT * FROM users_2019;

DB.Scopes(TableOfYear(user, 2020)).Find(&users)
// SELECT * FROM users_2020;

// Table form different database
func TableOfOrg(user *User, dbName string) func(db *gorm.DB) *gorm.DB {
  return func(db *gorm.DB) *gorm.DB {
        tableName := dbName + "." + user.TableName()
        return db.Table(tableName)
  }
}

DB.Scopes(TableOfOrg(user, "org1")).Find(&users)
// SELECT * FROM org1.users;

DB.Scopes(TableOfOrg(user, "org2")).Find(&users)
// SELECT * FROM org2.users;
```

#### scope更新

```go
func CurOrganization(r *http.Request) func(db *gorm.DB) *gorm.DB {
  return func (db *gorm.DB) *gorm.DB {
    org := r.Query("org")

    if org != "" {
      var organization Organization
      if db.Session(&Session{}).First(&organization, "name = ?", org).Error == nil {
        return db.Where("org_id = ?", organization.ID)
      }
    }

    db.AddError("invalid organization")
    return db
  }
}

db.Model(&article).Scopes(CurOrganization(r)).Update("Name", "name 1")
// UPDATE articles SET name = "name 1" WHERE org_id = 111
db.Scopes(CurOrganization(r)).Delete(&Article{})
// DELETE FROM articles WHERE org_id = 111
```

### 约定

#### 使用 ID 作为主键

默认情况下，GORM 会使用 `ID` 作为表的主键。你也可以通过标签 `primaryKey` 将其它字段设为主键。[复合主键](#复合主键1)

#### 复数表名

GORM 使用结构体名的 `蛇形命名` 作为表名。对于结构体 User，根据约定，其表名为 users

**TableName**
可以实现 `Tabler` 接口来更改默认表名，例如：

```go
type Tabler interface {
    TableName() string
}

// TableName 会将 User 的表名重写为 `profiles`
func (User) TableName() string {
  return "profiles"
}
```

**注意**： TableName 不支持动态变化，它会被缓存下来以便后续使用。想要使用动态表名，可以使用 `Scopes`，例如：

```go
func UserTable(user User) func (tx *gorm.DB)*gorm.DB {
  return func (tx *gorm.DB)*gorm.DB {
    if user.Admin {
      return tx.Table("admin_users")
    }

    return tx.Table("users")
  }
}

db.Scopes(UserTable(user)).Create(&user)
```

**临时指定表名**
您可以使用 Table 方法临时指定表名，例如：

```go
// 根据 User 的字段创建 `deleted_users` 表
db.Table("deleted_users").AutoMigrate(&User{})

// 从另一张表查询数据
var deletedUsers []User
db.Table("deleted_users").Find(&deletedUsers)
// SELECT * FROM deleted_users;

db.Table("deleted_users").Where("name = ?", "jinzhu").Delete(&User{})
// DELETE FROM deleted_users WHERE name = 'jinzhu';
```

查看 [from 子查询](#子查询) 了解如何在 FROM 子句中使用子查询

**命名策略**
GORM允许用户通过覆盖默认的`NamingStrategy`来更改默认的命名约定，该策略用于构建`TableName`, `ColumnName`, `JoinTableName`, `RelationshipFKName`, `CheckerName`, `IndexName`，查看[GORM Config](#gorm配置2)了解详细信息

#### 列名

根据约定，数据表的列名使用的是 `struct` 字段名的 `蛇形命名`
您可以使用 `column` 标签或 `命名策略` 来覆盖列名

#### 时间戳追踪

对于有 `CreatedAt` 字段的模型，创建记录时，如果该字段值为零值，则将该字段的值设为当前时间
对于有 `UpdatedAt` 字段的模型，更新记录时，将该字段的值设为当前时间。创建记录时，如果该字段值为零值，则将该字段的值设为当前时间
你可以通过将 `autoUpdateTime` 标签置为 `false` 来禁用时间戳

```go
type User struct {
  CreatedAt time.Time `gorm:"autoCreateTime:false"`
  UpdatedAt time.Time `gorm:"autoUpdateTime:false"`
}
```

### 设置

## 高级主题

### Database Resolver

### Sharding

### Serializer【4】

序列化器是一个可扩展的接口，允许自定义如何使用数据库序列化和反序列化数据。

GORM 提供了一些默认的序列化器：json、gob、unixtime，这里有一个如何使用它的快速示例

```go
type User struct {
    Name        []byte                 `gorm:"serializer:json"`
    Roles       Roles                  `gorm:"serializer:json"`
    Contracts   map[string]interface{} `gorm:"serializer:json"`
    JobInfo     Job                    `gorm:"type:bytes;serializer:gob"`
    CreatedTime int64                  `gorm:"serializer:unixtime;type:time"` // 将 int 作为日期时间存储到数据库中
}

type Roles []string

type Job struct {
    Title    string
    Location string
    IsIntern bool
}
```

#### 注册序列化器

一个Serializer需要实现如何对数据进行序列化和反序列化，所以需要实现如下接口

```go
import "gorm.io/gorm/schema"

type SerializerInterface interface {
    Scan(ctx context.Context, field *schema.Field, dst reflect.Value, dbValue interface{}) error
    SerializerValuerInterface
}

type SerializerValuerInterface interface {
    Value(ctx context.Context, field *schema.Field, dst reflect.Value, fieldValue interface{}) (interface{}, error)
}
```

例如，默认 `JSONSerializer` 的实现如下：

```go
// JSONSerializer json序列化器
type JSONSerializer struct {
}

// 实现 Scan 方法
func (JSONSerializer) Scan(ctx context.Context, field *Field, dst reflect.Value, dbValue interface{}) (err error) {
    fieldValue := reflect.New(field.FieldType)

    if dbValue != nil {
        var bytes []byte
        switch v := dbValue.(type) {
        case []byte:
            bytes = v
        case string:
            bytes = []byte(v)
        default:
            return fmt.Errorf("failed to unmarshal JSONB value: %#v", dbValue)
        }

        err = json.Unmarshal(bytes, fieldValue.Interface())
    }

    field.ReflectValueOf(ctx, dst).Set(fieldValue.Elem())
    return
}

// 实现 Value 方法
func (JSONSerializer) Value(ctx context.Context, field *Field, dst reflect.Value, fieldValue interface{}) (interface{}, error) {
    return json.Marshal(fieldValue)
}
```

并使用以下代码注册：
`schema.RegisterSerializer("json", JSONSerializer{})`

注册序列化器后，可以将其与 serializer 标签一起使用，例如：

```go
type User struct {
    Name []byte `gorm:"serializer:json"`
}
```

#### 自定义序列化器类型

你可以通过标签使用已注册的序列化器，你也可以自定义 struct，实现上述的 `SerializerInterface` 接口，随后便可以直接将其作为字段类型使用，例如：

```go
type EncryptedString string

// ctx: contains request-scoped values
// field: the field using the serializer, contains GORM settings, struct tags
// dst: current model value, `user` in the below example
// dbValue: current field's value in database
func (es *EncryptedString) Scan(ctx context.Context, field*schema.Field, dst reflect.Value, dbValue interface{}) (err error) {
    switch value := dbValue.(type) {
    case []byte:
        *es = EncryptedString(bytes.TrimPrefix(value, []byte("hello")))
    case string:
        *es = EncryptedString(strings.TrimPrefix(value, "hello"))
    default:
        return fmt.Errorf("unsupported data %#v", dbValue)
    }
    return nil
}

// ctx: contains request-scoped values
// field: the field using the serializer, contains GORM settings, struct tags
// dst: current model value, `user` in the below example
// fieldValue: current field's value of the dst
func (es EncryptedString) Value(ctx context.Context, field *schema.Field, dst reflect.Value, fieldValue interface{}) (interface{}, error) {
    return "hello" + string(es), nil
}

type User struct {
    gorm.Model
    Password EncryptedString
}

data := User{
    Password: EncryptedString("pass"),
}

DB.Create(&data)
// INSERT INTO `serializer_structs` (`password`) VALUES ("hellopass")

var result User
DB.First(&result, "id = ?", data.ID)
// result => User{
//   Password: EncryptedString("pass"),
// }

DB.Where(User{Password: EncryptedString("pass")}).Take(&result)
// SELECT * FROM `users` WHERE `users`.`password` = "hellopass"
```

### 索引【1】

GORM 允许通过 index、uniqueIndex 标签创建索引，这些索引将在使用 GORM 进行 `AutoMigrate` 或 `Createtable` 时创建

#### 索引标签

GORM 可以接受很多索引设置，例如`class`、`type`、`where`、`comment`、e`xpression`、`sort`、`collate`、`option`

```go
type User struct {
    Name  string `gorm:"index"`
    Name2 string `gorm:"index:idx_name,unique"`
    Name3 string `gorm:"index:,sort:desc,collate:utf8,type:btree,length:10,where:name3 != 'jinzhu'"`
    Name4 string `gorm:"uniqueIndex"`
    Age   int64  `gorm:"index:,class:FULLTEXT,comment:hello \\, world,where:age > 10"`
    Age2  int64  `gorm:"index:,expression:ABS(age)"`
}

// MySQL 选项
type User struct {
    Name string `gorm:"index:,class:FULLTEXT,option:WITH PARSER ngram INVISIBLE"`
}
```

**唯一索引**
`uniqueIndex` 标签的作用与 `index` 类似，它等效于 `index:,unique`

```go
type User struct {
    Name1 string `gorm:"uniqueIndex"`
    Name2 string `gorm:"uniqueIndex:idx_name,sort:desc"`
}
```

#### 复合索引

两个字段使用同一个索引名将创建复合索引

```go
// create composite index `idx_member` with columns `name`, `number`
type User struct {
    Name   string `gorm:"index:idx_member"`
    Number string `gorm:"index:idx_member"`
}
```

**字段优先级**
复合索引列的顺序会影响其性能，可以使用 priority 指定顺序，默认优先级值是 10。如果优先级值相同，则顺序取决于模型结构体字段的顺序

```go
type User struct {
    Name   string `gorm:"index:idx_member"`
    Number string `gorm:"index:idx_member"`
}
// column order: name, number

type User struct {
    Name   string `gorm:"index:idx_member,priority:2"`
    Number string `gorm:"index:idx_member,priority:1"`
}
// column order: number, name

type User struct {
    Name   string `gorm:"index:idx_member,priority:12"`
    Number string `gorm:"index:idx_member"`
}
// column order: number, name
```

**共享复合索引**
MARK 没看懂

#### 多索引

一个字段接受多个 `index`、`uniqueIndex` 标签，这会在一个字段上创建多个索

```go
type UserIndex struct {
    OID          int64  `gorm:"index:idx_id;index:idx_oid,unique"`
    MemberNumber string `gorm:"index:idx_id"`
}
```

### 约束【1】

GORM 允许通过标签创建数据库约束，约束会在通过 GORM 进行 AutoMigrate 或创建数据表时被创建。

#### 检查约束

通过 check 标签创建检查约束

```go
type UserIndex struct {
    Name  string `gorm:"check:name_checker,name <> 'jinzhu'"`
    Name2 string `gorm:"check:name <> 'jinzhu'"`
    Name3 string `gorm:"check:,name <> 'jinzhu'"`
}
```

#### 索引 约束

见[数据库索引](#索引1)

#### 外键 约束

GORM 会为关联创建外键约束，可以在初始化过程中禁用此功能：

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  DisableForeignKeyConstraintWhenMigrating: true,
})
```

GORM 允许通过 `constraint` 标签的 `OnDelete`、`OnUpdate` 选项设置外键约束，例如：

```go
type User struct {
  gorm.Model
  CompanyID  int
  Company    Company    `gorm:"constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`
  CreditCard CreditCard `gorm:"constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`
  //级联更新,级联删除
}

type CreditCard struct {
  gorm.Model
  Number string
  UserID uint
}

type Company struct {
  ID   int
  Name string
}
```

### 复合主键【1】

通过将多个字段设为主键，以创建复合主键，例如：

```go
type Product struct {
  ID           string `gorm:"primaryKey"`
  LanguageCode string `gorm:"primaryKey"`
  Code         string
  Name         string
}
```

**注意**：默认情况下，整型 `PrioritizedPrimaryField` 启用了 `AutoIncrement`，要禁用它，您需要为整型字段关闭 `autoIncrement`：

```go
type Product struct {
  CategoryID uint64 `gorm:"primaryKey;autoIncrement:false"`
  TypeID     uint64 `gorm:"primaryKey;autoIncrement:false"`
}
```

### 安全

GORM 使用 database/sql 的参数占位符来构造 SQL 语句，这可以自动转义参数，避免 SQL 注入数据

**注意** Logger 打印的 SQL 并不像最终执行的 SQL 那样已经转义，复制和运行这些 SQL 时应当注意。

**查询条件**
用户的输入只能作为参数，例如：

```go
userInput := "jinzhu;drop table users;"

// 安全的，会被转义
db.Where("name = ?", userInput).First(&user)

// SQL 注入
db.Where(fmt.Sprintf("name = %v", userInput)).First(&user)
```

**内联条件**.

```go
// 会被转义
db.First(&user, "name = ?", userInput)

// SQL 注入
db.First(&user, fmt.Sprintf("name = %v", userInput))
```

当通过用户输入的整形主键检索记录时，你应该对变量进行类型检查。

```go
userInputID := "1=1;drop table users;"
// safe, return error
id, err := strconv.Atoi(userInputID)
if err != nil {
    return err
}
db.First(&user, id)

// SQL injection
db.First(&user, userInputID)
// SELECT * FROM users WHERE 1=1;drop table users;
```

**SQL 注入方法**
为了支持某些功能，一些输入不会被转义，调用方法时要小心用户输入的参数。

```go
db.Select("name; drop table users;").First(&user)
db.Distinct("name; drop table users;").First(&user)

db.Model(&user).Pluck("name; drop table users;", &names)

db.Group("name; drop table users;").First(&user)

db.Group("name").Having("1 = 1;drop table users;").First(&user)

db.Raw("select name from users; drop table users;").First(&user)

db.Exec("select name from users; drop table users;")

db.Order("name; drop table users;").First(&user)
```

避免 SQL 注入的一般原则是，不信任用户提交的数据。可以进行白名单验证来测试用户的输入是否为已知安全的、已批准、已定义的输入，并且在使用用户的输入时，仅将它们作为参数。

### GORM配置【2】

GORM 提供的配置可以在初始化时使用

```go
type Config struct {
  SkipDefaultTransaction   bool
  NamingStrategy           schema.Namer
  Logger                   logger.Interface
  NowFunc                  func() time.Time
  DryRun                   bool
  PrepareStmt              bool
  DisableNestedTransaction bool
  AllowGlobalUpdate        bool
  DisableAutomaticPing     bool
  DisableForeignKeyConstraintWhenMigrating bool
}
```

#### 跳过默认事务

为了确保数据一致性，GORM 会在事务里执行写入操作（创建、更新、删除）。如果没有这方面的要求，您可以在初始化时禁用它。

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  SkipDefaultTransaction: true,
})
```

#### 命名策略

GORM 允许用户通过覆盖默认的`NamingStrategy`来更改命名约定，这需要实现接口 `Namer`

```go
type Namer interface {
    TableName(table string) string
    SchemaName(table string) string
    ColumnName(table, column string) string
    JoinTableName(table string) string
    RelationshipFKName(Relationship) string
    CheckerName(table, column string) string
    IndexName(table, column string) string
}
```

默认 NamingStrategy 也提供了几个选项，如：

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  NamingStrategy: schema.NamingStrategy{
    TablePrefix: "t_",   // table name prefix, table for `User` would be `t_users`
    SingularTable: true, // use singular table name, table for `User` would be `user` with this option enabled
    NoLowerCase: true, // skip the snake_casing of names
    NameReplacer: strings.NewReplacer("CID", "Cid"), // use name replacer to change struct/field name before convert it to db name
  },
})
```

#### Logger

允许通过覆盖此选项更改 GORM 的默认 logger，参考 [Logger](#logger1) 获取详情

#### owFunc

更改创建时间使用的函数

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  NowFunc: func() time.Time {
    return time.Now().Local()
  },
})
```

#### DryRun配置

生成 SQL 但不执行，可以用于准备或测试生成的 SQL，参考 [会话](#session2) 获取详情

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  DryRun: false,
})
```

#### PrepareStmt

PreparedStmt 在执行任何 SQL 时都会创建一个 prepared statement 并将其缓存，以提高后续的效率，参考 [会话](#session2) 获取详情

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  PrepareStmt: false,
})
```

#### 禁用嵌套事务配置

在一个事务中使用 `Transaction` 方法，GORM 会使用 `SavePoint(savedPointName)`，`RollbackTo(savedPointName)` 为你提供嵌套事务支持，你可以通过 `DisableNestedTransaction` 选项关闭它，查看 [Session](#session2) 获取详情

#### AllowGlobalUpdate配置

启用全局 update/delete，查看 [Session](#session2) 获取详情

#### DisableAutomaticPing

在完成初始化后，GORM 会自动 ping 数据库以检查数据库的可用性，若要禁用该特性，可将其设置为 true

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  DisableAutomaticPing: true,
})
```

#### DisableForeignKeyConstraintWhenMigrating

在 `AutoMigrate` 或 `CreateTable` 时，GORM 会自动创建外键约束，若要禁用该特性，可将其设置为 true，参考 [迁移](#迁移2) 获取详情。

```go
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{
  DisableForeignKeyConstraintWhenMigrating: true,
})
```
