---
title: 《Java核心技术》阅读笔记
date: '2026-06-05T13:35:56+08:00'
tags: 
- Java
categories: 
- 笔记
draft: true
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 《Java核心技术》阅读笔记

[Java核心技术·卷I（原书第12版）](https://book.douban.com/subject/35920145/)

本来不喜欢Java学的go，但要维护java项目不得不再捡起来。没想到还是逃不过。

## 第1章 Java程序设计概述

主要是一些背景知识介绍。

### 1.2 Java白皮书的关键术语

1. 简单性
2. 面向对象
3. 分布式
4. 健壮性
5. 安全性
6. 体系结构中立
7. 可移植性
8. 解释性
9. 高性能
10. 多线程
11. 动态性

很多内容看起来都是自吹自擂，不过放在96年那个时候还是相当厉害的。

## 第2章 Java编程环境

还是建议在网上自己找教程，书上的方法往往都很落后。

我目前配置的环境是使用`vfox`进行java的版本管理，ide继续使用`VSCode`和`Cursor`，安装`Extension Pack for Java`和`Spring Boot Extension Pack`扩展包。

### 2.4 Jshell

`Jshell`可以不用写完整的类和main方法，以及编译运行这一整套流程，直接写 Java 代码并立即看到结果。

在单独学习语法时或许会很方便，可以试试。

## 第3章 Java的基本程序设计结构

这一章都是一些基础语法，有其他语言基础快速过一遍就行。主要了解一些Java的特性的专属用法。不过我还是习惯性地记得详细了些。

### 3.1 一个简单的Java程序

```java
public class FirstSample
{
   public static void main(String[] args)
   {
      System.out.println("We will not use 'Hello, World!'");
   }
}
```

经典helloworld，注意所有Java语句都以分号结束。

源代码的文件名必须与公共类的类名相同，并用java作为扩展名。因此，存储这个代
码时，文件名必须为`FirstSample.java`。注意大小写保持一致。

```bash
# 编译
PS D:\Workspace\Java\corejava12\v1ch03\FirstSample> javac .\FirstSample.java

# 运行
PS D:\Workspace\Java\corejava12\v1ch03\FirstSample> java FirstSample
We will not use 'Hello, World!'

# 或者直接运行
PS D:\Workspace\Java\corejava12\v1ch03\FirstSample> java .\FirstSample.java 
We will not use 'Hello, World!'
```

Java的通用语法为`object.method(parameters)`，所以这里我们就是调用`System.out`对象的`println`方法，接受一个字符串参数并进行打印。

### 3.2 注释

很常见的方法。`//`单行注释，`/* */`跨行注释。

### 3.3 数据类型

#### 3.3.1 整形

| 类型  | 存储需求 | 取值范围                                   |
| ----- | -------- | ------------------------------------------ |
| int   | 4字节    | -2147483648 ~ 2147483647                   |
| short | 2字节    | -32768 ~ 32767                             |
| long  | 8字节    | -9223372036854775808 ~ 9223372036854775807 |
| byte  | 1字节    | -128～127                                  |

和C/C++不同，在Java中，整型的范围与运行Java代码的机器无关，这解决了可移植性的问题。

长整型数值有一个后缀L或1(如400000000L)。十六进制数值有一个前缀x或θX(如0xCAFE)。八进制有一个前缀θ(例如，010对应十进制中的8)。显然，八进制表示法比较容易混淆，所以很少有程序员使用八进制常数。

加上前缀θb或θB还可以写二进制数。例如，0b1001就是9。另外，可以为数字字面量加下画线，如用1_000_000(或0b1111_0100_0010_0100_0000)表示100万。这些下画线只是为了让人更易读。Java编译器会去除这些下画线。

#### 3.3.2 浮点类型

| 类型   | 存储需求 | 取值范围                                       |
| ------ | -------- | ---------------------------------------------- |
| float  | 4字节    | 大约 ±3.40282347×10^38(6～7位有效数字)         |
| double | 8字节    | 大约 ±1.79769313486231570×10^308(15位有效数字) |

float类型的数值有一个后缀F或f(例如，3.14F)。没有后缀F的浮点数值(如3.14)总
是默认为double类型。可选地，也可以在 double数值后面添加后缀D或d(例如，3.14D)。

#### 3.3.3 char类型

char类型原本用于表示单个字符。不过，现在一些Unicode字符则需要两个char值。

char类型的字面量值要用单引号括起来。例如：'A'是编码值为65的字符常量。而双引号的"A"是包含一个字符的字符串。

char类型的值可以表示为十六进制值，其范围从\u0000~\uFFFF。除了\u，还有其他一些可用的转义序列。

![特殊字符的转义序列](/post-images/《Java核心技术》阅读笔记/v1ch03_01.png)

#### 3.3.4 Unicode和char类型

总结：强烈建议不要在程序中使用char类型，除非确实需要处理UTF-16代码单元。最好将字符串作为抽象数据类型来处理。

#### 3.3.5 boolean类型

boolean(布尔)类型有两个值：false和true，用来判定逻辑条件。整型值和布尔值之间不能进行相互转换。在C++中，值甚至指针可以代替布尔值，而Java中不行。

### 3.4 变量与常量

#### 3.4.1 声明变量

在Java中，每个变量都有一个类型(type)。声明一个变量时，先指定变量的类型，然后是变量名。

```java
double salary;
int vacationDays;
long earthPopulation;
boolean done;
```

可以在一行中声明多个变量。不过，不提倡使用这种风格。分别声明每一个变量可以提高程序的可读性。

```java
int i, j; // both are integers
```

#### 3.4.2 初始化变量

声明一个变量之后，必须用赋值语句显式地初始化变量。使用未初始化的变量编译器将会报错。

```java
// 先声明再初始化
int vacationDays;
vacationDays = 12;

// 声明的同时初始化
int vacationDays = 12;
```

从Java 10开始，对于局部变量，如果可以从变量的初始值推断出它的类型，就不再需要声明类型。只需要使用关键字`var`。

```java
var vacationDays = 12; // vacationDays is an int
var greeting ="Hello"; // greeting is a String
```

#### 3.4.3 常量

在Java中，可以用关键字`final`指示常量，表示这个变量只能被赋值一次。一旦赋值，就不能再更改了。习惯上，常量名使用全大写。

```java
final double CM_PER_INCH= 2.54;
```

顺便一提，`const`是Java保留的关键字，但目前并没有使用。在Java中，必须使用`final`声明常量。

#### 3.4.4 枚举类型

有时候，一个变量只包含有限的一组值。针对这种情况，可以自定义枚举类型(enumerated type)。枚举类型包括有限个命名值。

```java
enum Size{ SMALL, MEDTUM, LARGE, EXTRA_LARGE };

Size s = Size.MEDTUM;
```

枚举类型的变量只能存储这个类型声明中所列的某个值，或者特殊值null，标识没有设置任何值。

### 3.5 运算符

#### 3.5.1 算数运算符

在Java中，使用通常的算术运算符+、一、*、/分别表示加、减、乘、除运算。

当参与/运算的两个操作数都是整数时，/表示整数除法；否则，这表示浮点除法。

整数的求余操作(有时称为取模(modulus))用%表示。

需要注意，整数被0除将产生一个异常，而浮点数被0除将会得到一个无穷大或NaN结果。

#### 3.5.2 数学函数与常量

Math类中包含你可能会用到的各种数学函数。具体函数列表可以查阅定义或文档。

Math类提供了一些方法使整数运算更安全。如果一个计算溢出，数学运算符只
是悄悄地返回错误的结果而不做任何提醒，例如1000000000*3的计算
结果将是-1294967296，因为最大的int值也只是刚刚超过20亿。`Math.multiplyExact(100000000,3)`就会生成一个异常。可以捕获这个异常或者让程
序终止，而不是允许它给出一个错误的结果然后悄无声息地继续运行。

#### 3.5.3 数值类型之间的转换

![数值类型之间的合法转换](/post-images/《Java核心技术》阅读笔记/v1ch03_02.png)

实线箭头表示无信息丢失的转换；虚线箭头表示可能有精度损失的转换。

当用一个二元运算符连接两个不同类型的值时（例如n+f，n是整数，f是浮点数）,先要将两个操作数转换为同一种类型，然后再进行计算。转换的优先级是`double > float > long > int`，优先转换为两者中优先级更大的类型。

#### 3.5.4 强制类型转换

强制类型转换的语法格式是在圆括号中指定想要转换的目标类型，后面紧跟待转换的变量名。

```java
double x = 9.997;
int nx = (int)x; // nx = 9
```

如果想舍入（round）一个浮点数来得到最接近的整数（大多数情况下，这种操作更有
用）,可以使用`Math.round`方法。

```java
double x = 9.997;
int nx = (int) Math.round(x); // nx = 10
```

#### 3.5.5 赋值

可以在赋值中使用二元运算符，为此有一种很方便的简写形式。例如`x += 4`等价于`x = x + 4`。

#### 3.5.6 自增与自减运算符

在Java中，借鉴了C和C++中的做法，也提供了自增、自减运算符：`n++`将变量n的当前值加1，`n--`则将n的值减1。

还有一种“前缀”形式：`++n`和`--n`。前缀形式会先完成加减再使用；而后缀形式会使用变量原来的值，然后再加减。

#### 3.5.7 关系和boolean运算符

java有着丰富的关系运算符，如`=`(相等)、`!=`(不相等)、`<`(小于)、`>`(大于)、`<=`(小于等于)和`>=`(大于等于)。

Java沿用了C++的做法，使用`&&`表示逻辑“与”运算符，使用`||`表示逻辑“或”运
算符，感叹号`!`标识逻辑非运算符。

&&和||运算符是按照“短路”方式来求值的：如果第一个操作数已经能够确定表达式的值，第二个操作数就不必计算了。一个常用的示例如下，可以确保除数不为0：

```java
x !=0 && 1 / x > x + y // no division by 0
```

#### 3.5.8 条件运算符

Java提供了条件运算符`?:`，可以根据一个布尔表达式选择一个值。

```txt
condition ? expression1 : expression2
```

如果条件为true，表达式就计算为第一个表达式的值，否则为第二个表达式的值。例如`x<y?x:y`会返回两者中较小的一个。

#### 3.5.9 switch表达式

需要在两个以上的值中做出选择时，可以使用switch 表达式：

```java
String seasonName = switch (seasonCode) {
    case 0 -> "Spring";
    case 1 -> "Summer";
    case 2 -> "Fall";
    case 3 -> "Winter";
    default -> "???";
};
```

可以为各个case提供多个标签，用逗号分隔：

```java
int numLetters = switch(seasonName) {
    case "Spring", "Summer", "Winter" -> 6;
    case "Fall" -> 4;
    default -> -1;
};
```

switch表达式中使用枚举常量时，不需要为各个标签提供枚举名，这可以从switch值推导得出。

```java
enum Size { SMALL, MEDTUM, LARGE, EXTRA_LARGE };
Size itemSize =...;
String label = switch(itemSize)
{
    case SMALL -> "S";// no need to use Size.SMALL
    case MEDIUM -> "M";
    case LARGE -> "L";
    case EXTRA_LARGE -> "XL";
}
```

#### 3.5.10 位运算符

位运算符包括：`&`(and) `|`(or) `^`(xor) `~`(not)。以及`>>`和`<<`运算符可以将位模式左移或右移。最后，`>>>`运算符会用0填充高位，这与`>>`不同，`>>`会用符号位填充高位。不存在`<<<`运算符。

位运算个人用的很少不是很了解，甚至都想不出什么合适的例子。

#### 3.5.11 括号与运算符级别

没什么好记的，直接查表

![运算符优先级](/post-images/《Java核心技术》阅读笔记/v1ch03_03.png)

![运算符优先级续](/post-images/《Java核心技术》阅读笔记/v1ch03_04.png)

### 3.6 字符串

Java字符串就是Unicode字符序列。Java没有内置的字符串类型，而是标准Java类库中提供了一个预定义类`String`。每个用双引号括起来的字符串都是String类的一个实例：

```java
String e = ""; // an empty string
String greeting = "Hello";
```

#### 3.6.1 子串

String类的`substring`方法可以从一个较大的字符串提取出一个子串。

```java
String greeting = "Hello";
String s = greeting.substring(0, 3); // Hel
```

#### 3.6.2 拼接

与绝大多数程序设计语言一样，Java语言允许使用+号连接(拼接)两个字符串。

```java
String expletive = "Expletive";
String PG13 = "deleted";
String message = expletive + PG13 // Expletivedeleted
```

当将一个字符串与一个非字符串的值进行拼接时，后者会转换成字符。这个特性通常用在输出语句中。

```java
int age = 13
String rating = "PG" + age; // PG13
```

如果需要把多个字符串放在一起，用一个界定符分隔，可以使用静态`join`方法：

```java
String all = String.join(" / ", "S", "M", "L", "XL");
// S / M / L / XL
```

在Java 11中，还提供了一个`repeat`方法：

```java
String repeated = "Java".repeat(3); // JavaJavaJava
```

#### 3.6.3 字符串不可变

String类没有提供任何方法来修改字符串中的某个字符。可以提取想要保留的子串，再与希望替换的字符拼接：

```java
String greeting = "Hello";
greeting = greeting.substring(0, 3) + "p!" // Help!
```

可以将Java的Sting类比为C的char*指针，或者C++的string类，而不是char[]字符数组。

#### 3.6.4 检测字符串是否相等

可以用`equals`或`equalsIgnoreCase`检测两个字符串是否相等。不能像C++那样使用`==`检测，因为C++的string类重载了`==`运算符而Java没有，所以Java中仍是比较指针地址。

```java
String greeting = "Hello";
"Hello".equals(greeting) // true

// 忽略大小写
"Hello".equalsIgnoreCase("hello") // true

// 错误
greeting == "Hello"
```

#### 3.6.5 空串与Null串

空串""是长度为0的字符串。可以用`str.length()==0`或`str.equals("")`检测。

null标识空对象。因为String是一个对象，所以其值可以为空。不能在空对象上调用方法。所以一般用如下形式判空：

```java
if (str != null && str.length() != 0) { /* do something*/ }
```

#### 3.6.6 码点与代码单元

Java字符串是一个char值序列。char数据类型是采用UTF-16编码表示Unicode码点的一个**代码单元**。常用的Unicode字符可以用一个代码单元表示，而辅助字符需要一对代码单元表示。

所以直接使用char有时不能正确处理两个代码单元的字符，这时就要引入**码点**的概念。它是Unicode标准中分配给每个字符的唯一数字编号，也是真正和字符有着一对一的关系。因此我们在进行字符串操作是常常要使用码点概念替换字符概念。例如遍历字符串：

```java
String s = "A中𝕆";
int codePointCount = s.codePointCount(0, s.length());
for (int i = 0; i < codePointCount; i++) {
    int codePoint = s.codePointAt(s.offsetByCodePoints(0, i));
    System.out.println(Character.toChars(codePoint));
}
```

#### 3.6.7 String API

String常用方法，这里就不抄书了。

#### 3.6.8 阅读联机API文档

[Java SE](https://docs.oracle.com/en/java/javase/25/docs/api/index.html)
[Java EE](https://docs.oracle.com/javaee/7/api/toc.htm)
[Spring](https://spring.io/projects/spring-boot)

#### 3.6.9 构建字符串

使用字符串拼接的方式构建字符串时，每次拼接都会创建一个新的String对象，既耗时又浪费空间。使用StringBuilder类可以避免这个问题。

```java
StringBuilder builder = new StringBuilder();

char ch = 'a';
String str = "bc";

builder.append(ch);
builder.append(str);

String res = builder.toString()
```

然后使一些Strbuilder的常用方法，还是不抄书。

#### 3.6.10 文本块

文本块（text block）可以提供跨多行的字符串字面量。文本块以"""开头，后面是一个换行符，并以另一个"""结尾。

```java
String greeting = """
Hello
World
"""
```

如上文本块比文本块比相应的字符串字面量`"Hello\nworld\n"`更易于读写。

有一个转义序列只能在文本块中使用。行尾的\会把这一行与下一行连接起来。

```java
"""
Hello,my name is Hal. \
Please enter your name:""";

// 等价于

"Hello,my name is Hal. Please enter your name:"
```

文本块会对行结束符进行标准化，删除末尾的空白符，并把Windows的行结束符(\r\n)改为简单的换行符(\n)。

对于前导空白符，将去除文本块中所有行的公共缩进。

### 3.7 输入与输出

#### 3.7.1 读取输入

如前所述，打印输出到标准输出流（控制台窗口）只需要使用`System.out.println()`。而读取标准输入了会麻烦一些，需要构建一个`java.util.Scanner`对象，再使用其各种方法读取输入。

```java
Scanner in = new Scanner(System.in);

// get first input
System.out.print("What is your name? ");
String name = in.nextLine();

// get second input
System.out.print("How old are you? ");
int age = in.nextInt();

// display output on console
System.out.println("Hello, " + name + ". Next year, you'll be " + (age + 1));
```

#### 3.7.2 格式化输出

和C一样的printf方法，即`System.out.printf`。

![用于printf的转换字符](/post-images/《Java核心技术》阅读笔记/v1ch03_5.png)

![用于printf的标志](/post-images/《Java核心技术》阅读笔记/v1ch03_6.png)

可以使用静态的String.format 方法创建一个格式化的字符串，而不打印输出：

```java
String name = "Jack";
int age = 12;
String message = String.format("Hello, %s. Next year, you'll be %d",name, age + 1);

// 或者
String message = "Hello, %s. Next year, you'll be %d".formatted(name, age + 1);
```

#### 3.7.3 文件输入与输出

文件输入也是构建一个Scanner对象，只不过入参有变化，从标准输入`System.in`改成文件：

```java
Scanner in = new Scanner(Path.of("myfile.txt"), StandardCharsets.UTF_8);
```

如果文件名中包含反斜线符号，记住要在每个反斜线之前再加一个额外的反斜线转义：
`"c:\\mydirectory\\myfile.txt"`。

文件输出则是构造一个`PrintWriter`对象：

```java
PrintWriter out = new PrintWriter("myfile.txt", StandardCharsets.UTF_8);
```

### 3.8 控制流程

#### 3.8.1 块作用域

块（即复合语句）由若干条Java语句组成，并用一对大括号括起来。块确定了变量的作用域。一个块可以嵌套在另一个块中。

需要注意的是，不能在嵌套的两个块中声明同名的变量。其他语言如Go中内部块的声明会覆盖外部块，而java中会直接编译报错：

```java
public static void main(String[] args)
{
    int n;
    ...
    {
        int k;
        int n; //  ERROR--can't redeclare n in inner block
    }
}
```

#### 3.8.2 条件语句

```txt
if (condition) statement
if (condition) statement1 else statement2
```

这里的条件必须用小括号括起来。lse部分总是可选的。

#### 3.8.3 while循环

```txt
while (condition) statement
do statement while (condition);
```

#### 3.8.4 确定性循环

for循环语句是支持迭代的一种通用结构，它由一个计数器或类似的变量控制迭代次数，每次迭代后这个变量将会更新。

```java
for(int i=1; i<=10; i++)
{
    System.out.println(i);
}
```

for语句的第1部分通常是对计数器初始化；第2部分给出每次新一轮循环执行前要检测的循环条件；第3部分指定如何更新计数器。

#### 3.8.5 多重选择：switch语句

case标签可以是：

- 类型为char、byte、short或int的常量表达式
- 枚举常量
- 字符串字面量
- 多个字符串，用逗号分隔

```java
// 非直通式
switch(choice)
{
    case 1 ->
        // do something
    case 2 ->
        // do something
    case 3 ->
        // do something
    case 4 ->
        // do something
    default ->
    System.out.println("Bad input");
}
```

```java
// 直通式
switch(choice)
{
    case 1 :
        // do something
        break
    case 2 :
        // do something
        break
    case 3 :
        // do something
        break
    case 4 :
        // do something
        break
    default :
    System.out.println("Bad input");
}
```

如上，switch语句分为直通和非直通两种。其中直通式如果没有`break`语句的话，会继续执行后面的代码块。

此外，switch还可以作为表达式使用，此时可以使用`yield`关键字，终止执行并返回一个值。

```java
// 非直通式
int numLetters = switch (seasonName) {
    case "Spring" -> {
        System.out.println("spring time!");
        yield 6;
    }
    case "Summer", "Winter" -> 6;
    case "Fall" -> 4;
    default -> -1;
}
```

```java
// 直通式
int numLetters = switch (seasonName) {
    case "Spring":
        System.out.println("spring time!");
    case "Summer", "Winter":
        yield 6;
    case "Fall":
        yield 4;
    default:
        yield -1;
}
```

#### 3.8.6 中断控制流程的语句

goto在java中虽然是一个保留字，但并没有投入使用。

在java中可以使用带标签的break做到类似的效果，即跳出多重嵌套的循环。此时标签必须放在要跳出的最外层循环前，带一个冒号。如下是一个示例：

```java
Scanner in = new Scanner(System.in);
int n;
read_data:
while (...) { // this loop statement is tagged with the label
    for (...) {
        System.out.print("Enter a number >=0: ");
        n = in.nextInt();
        if (n < 0) { // should never happen - can't go on
            break read_data; // break out of read_data loop
        }
    }
}
// this statement is executed immediately after the labeled break
if (n < 0) {
    // deal with bad situation
} else {
    // carry out normal processing
}
```

还有一个`continue`语句，和其他语言基本一致。

### 3.9 大数

`java.math`包的`BigInteger`和`BigDecimal`类可以处理包含任意长度数字序列的数值。

使用静态的`valueOf`方法可以将一个普通的数转换为大数。对于更长的数，可以使用一个带字符串参数的构造器。

```java
BigInteger a = BigInteger.valueOf(100);

BigInteger rellyBig = new BigInteger("1234567980132456789012345678901234567890");
```

大数之间的运算不能直接使用算数运算符，而是类中的add和multiply等方法。

```java
BigInteger c = a.add(b); // c = a + b
BigInteger d = c.multiply(b.add(BigInteger.value0f(2))); // d = c * ( b + 2 )
```

### 3.10 数组

#### 3.10.1 声明数组

```java
// 声明并创建
int[] a = new int[100]; // or var a = new int[100];

// 声明并初始化值
int[] smallPrimes = { 2, 3, 5, 7, 11, 13 };

// 使用匿名数组重新赋值
smallPrimes = new int[]{ 17, 19, 23, 29, 31, 37 };
```

和C不同，数组长度不要求是常量。`new int[n]`会创建一个长度为n的数组。

#### 3.10.2 访问数组元素

数组元素从0开始编号。最后一个合法的索引为数组长度减1。

创建一个数字数组时，所有元素都初始化为0。boolean数组的元素会初始化为false。对象数组的元素则初始化为一个特殊值null。需要注意的是，字符串String在java中是对象而不是基本数据类型，所以其零值也是null而不是空串""。

要想获得数组中的元素个数，可以使用array,Length。

#### 3.10.3 for each 循环

```java
for (variable : collection) statement
```

这种循环结构可以用来依次处理数组（或者任何其他元素集合）中的每个元素，而不必考虑指定索引值。

#### 3.10.4 数组拷贝

和C类似，直接赋值的话，两个变量将引用同一个数组：

```java
int[] luckyNumbers = smallPrimes;
luckyNumbers[5] = 12; // now smallPrimes[5] is also 12
```

![拷贝一个数组变量](/post-images/《Java核心技术》阅读笔记/v1ch03_07.png)

要进行值拷贝，需要使用`Arrays`类的`copyOf`方法：

```java
int[] copiedLuckyNumbers = Arrays.copyof(luckyNumbers, luckyNumbers.Length);
```

第2个参数是新数组的长度。这个方法通常用来增加数组的大小：

```java
luckyNumbers = Arrays.copyof(luckyNumbers, 2 * luckyNumbers.Length);
```

#### 3.10.5 命令行参数

每一个Java程序都有一个带String arg[]参数的main方法。这个参数表明main方法将接收一个字符串数组，也就是命令行上指定的参数。

```java
public class Message {
    public static void main(String[] args) {
        if (args.length == 0 || args[0].equals("-h"))
            System.out.print("Hello,");
        else if (args[0].equals("-g"))
            System.out.print("Goodbye,");
        // print the other command-line arguments
        for (int i = 1; i < args.length; i++)
            System.out.print(" " + args[i]);
        System.out.println("!");
    }
}

// java .\Message.java -g cruel world
// Goodbye, cruel world!
```

#### 3.10.6 数组排序

`java.util.Arrays`

要想对数值型数组进行排序，可以使用Arrays类中的sort方法：

```java
int[] a = new int[10000];
// do something
Arrays.sort(a)
```

#### 3.10.7 多维数组

```java
// 仅声明
double[][] balances;

// 声明并初始化
balances = new double[NYEARS][NRATES];

// 声明并初始化值
int[][] magicSquare =
{
    {16,3,2,13},
    {5,10,11,8},
    {9,6,7,12},
    {4,15,14,1}
};
```

#### 3.10.8 不规则数组

大意就是，对于多维数组，其元素是Arrays类，但不指定其长度，所以同一层级的Arrays可以拥有不同的长度。

## 第4章 对象与类

### 4.1 面向对象程序设计概述

本节主要介绍**面向对象程序设计(Object-Oriented Programming, OOP)**。

#### 4.1.1 类

**类（class）**指定了如何构造对象。由一个类**构造（construct）**对象的过程称为创建这个类的一个**实例（instance）**。

**封装（encapsulation，有时称为信息隐藏）**是处理对象的一个重要概念。从形式上看，封装就是将数据和行为组合在一个包中，并对对象的使用者隐藏具体的实现细节。对象中的数据称为**实例字段（instance field）**，操作数据的过程称为**方法（method）**。作为一个类的实例，一个特定对象有一组特定的实例字段值。这些值的集合就是这个对象的当前**状态（state）**。只要在对象上调用一个方法，它的状态就有可能发生改变。

可以通过扩展其他类来构建新类。扩展一个已有的类时，这个新类具有被扩展的那个类的全部属性和方法。你只需要在新类中提供适用于这个新类的新方法和实例字段。通过扩展一个类来得到另外一个类的概念称为**继承（inheritance）**。

#### 4.1.2 对象

对象的三个主要特性：

- 对象的**行为（behavior）**——可以对这个对象做哪些操作，或者可以对这个对象应用哪些方法?
- 对象的**状态（state）**——调用那些方法时，对象会如何响应?
- 对象的**标识（identity）**——如何区分可能有相同行为和状态的不同对象?

#### 4.1.3 识别类

识别类的一个简单经验是在分析问题的过程中寻找名词，而方法对应动词。

#### 4.1.4 类之间的关系

- **依赖（ependence，“uses-a”）**
    如果一个类的方法要使用或操作另一个类的对象，我们就说前一个类依赖于后一个类。
    应当尽可能减少相互依赖的类，即尽可能减少类之间的耦合（coupling）。
- **聚合（aggregation，“has-a”）**
    包含关系意味着类A的对象包含类B的对象。
- **继承（inheritance，“is-a”）**
  表示一个更特殊的类与一个更一般的类之间的关系。

### 4.2 使用预定义类

#### 4.2.1 对象与对象变量

要想使用对象，首先必须构造对象，并指定其初始状态。然后对对象应用方法。

在Java程序设计语言中，要使用**构造器（constructor，或称构造函数）**构造新实例。构造器是一种特殊的方法，其作用是构造并初始化对象。

要认识到重要的一点：对象变量并不实际包含一个对象，它只是引用一个对象。在Java中，任何对象变量的值都是一个引用，指向存储在另外一个地方的某个对象。new操作符的返回值也是一个引用。可以显式地将对象变量设置为null，指示这个对象变量目前没有引用任何对象。

简单地说，Java中的对象变量类似于C++中的对象指针。

```java
Date rightNow; // java
```

```C++
Date* rightnow // C++
```

#### 4.2.2 Java类库中的LocalDate类

介绍通过静态工厂方法（factory method）构造LocalDate类对象。

```java
LocalDate now = LocalDate.now() // 当前日期

LocalDate newYearEve = LocalDate.of(1999, 12, 31) // 指定日期 

// 获取年月日
int year = newYearsEve.getYear(); // 1999
int month = newYearsEve.getMonthValue(); // 12
int day = newYearsEve.getDayOfMonth(); //31

// 日期计算
LocalDate aThousandDaysLater = newYearsEve.plusDays(1000);
year = aThousandDaysLater.getYear();// 2002
month = aThousandDaysLater.getMonthValue(); //09
day = aThousandDaysLater.getDayOfMonth(); // 26
```

#### 4.2.3 更改器方法与访问器方法

LocaLDate.plusDays将生成一个新的LocalDate对象，原来的对象没有**更改（mutate）**。

调用后对象的状态会改变的方法称为个**更改器方法（mutator method）**。

只访问对象而不修改对象的方法称为**访问器方法（accessor method）**。

一个打印日历的实践练习，主要使用的各种getter方法：

```java
import java.time.LocalDate;

public class Main {
    public static void main(String[] args) {

        String[] header = new String[] { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };
        for (int i = 0; i < header.length; i++) {
            System.out.printf("%s\t", header[i]);
        }
        System.out.println();

        LocalDate now = LocalDate.now();
        int month = now.getMonthValue();
        int today = now.getDayOfMonth();

        LocalDate date = now.minusDays(today - 1);
        int weekday = date.getDayOfWeek().getValue();
        for (int i = 1; i < weekday; i++) {
            System.out.printf("\t");
        }

        while (date.getMonthValue() == month) {
            weekday = date.getDayOfWeek().getValue();
            int day = date.getDayOfMonth();
            String format = (day == today) ? "%d*\t" : "%d\t";
            System.out.printf(format, day);
            if (weekday == 7)
                System.out.println();

            date = date.plusDays(1);
        }
    }
}

/*
> java .\Main.java # 2026-06-11
Mon     Tue     Wed     Thu     Fri     Sat     Sun
1       2       3       4       5       6       7
8       9       10      11*     12      13      14
15      16      17      18      19      20      21
22      23      24      25      26      27      28
29      30
*/
```

### 4.3 自定义类

#### 4.3.1 Employee类

在Java中，最简单的类定义形式为：

```txt
class ClassName
{
    field1
    field2
    ...
    constructor1
    constructor2
    ...
    method1
    method2
    ...
}
```

```java
// EmployeeTest.java
import java.time.*;

/**
 * This program tests the Employee class.
 * @version 1.13 2018-04-10
 * @author Cay Horstmann
 */
public class EmployeeTest
{
   public static void main(String[] args)
   {
      // fill the staff array with three Employee objects
      Employee[] staff = new Employee[3];

      staff[0] = new Employee("Carl Cracker", 75000, 1987, 12, 15);
      staff[1] = new Employee("Harry Hacker", 50000, 1989, 10, 1);
      staff[2] = new Employee("Tony Tester", 40000, 1990, 3, 15);

      // raise everyone's salary by 5%
      for (Employee e : staff)
         e.raiseSalary(5);

      // print out information about all Employee objects
      for (Employee e : staff)
         System.out.println("name=" + e.getName() + ",salary=" + e.getSalary() + ",hireDay=" 
            + e.getHireDay());
   }
}

class Employee
{
   private String name;
   private double salary;
   private LocalDate hireDay;

   public Employee(String n, double s, int year, int month, int day)
   {
      name = n;
      salary = s;
      hireDay = LocalDate.of(year, month, day);
   }

   public String getName()
   {
      return name;
   }

   public double getSalary()
   {
      return salary;
   }

   public LocalDate getHireDay()
   {
      return hireDay;
   }

   public void raiseSalary(double byPercent)
   {
      double raise = salary * byPercent / 100;
      salary += raise;
   }
}
```

在这个示例程序中包含两个类：Employee类和带有public访问修饰符的EmployeeTest
类。EmployeeTest类包含main方法。

源文件名是EmployeeTest.java,这是因为文件名必须与public类的名字匹配。一个源文件中只能有一个公共类，但可以有任意数目的非公共类。

接下来，编译这段源代码的时候，编译器将在目录中创建两个类文件：EmployeeTest.class和Employee.class。

#### 4.3.2 使用多个源文件

建议各个类放在一个单独的源文件中。例如，将Employee类存放在文件Employee.java中，而将EmployeeTest类存放在文件EmployeeTest.java中。

编译时可以使用通配符，一次性编译多个文件：

```bash
# 匹配Employee开头的java源文件
javac Employee*.java

# 或者之间编译所有java源文件
javac *.java
```

此外，直接`javac EmployeeTest.java`其实也可以同时编译Employee.java，因为EmployeeTest.java中使用了Employee类。可以理解为java编译器内置了类似make的功能。

#### 4.3.3 刨析Employee类

```java
class Employee
{
   private String name;
   private double salary;
   private LocalDate hireDay;

   public Employee(String n, double s, int year, int month, int day)
   public String getName()
   public double getSalary()
   public LocalDate getHireDay()
   public void raiseSalary(double byPercent)
}
```

Employee类用`public`标识所有方法，标识任何类的任何方法都可以调用；用`private`标识所有实例字段，标识任何其他类的方法都不能读写这些字段。

#### 4.3.4 从构造器开始

```java
   public Employee(String n, double s, int year, int month, int day)
   {
      name = n;
      salary = s;
      hireDay = LocalDate.of(year, month, day);
   }
```

- 构造器与类同名。
- 每个类可以有一个以上的构造器。
- 构造器可以有0个、1个或多个参数。
- 构造器没有返回值。
- 构造器总是结合new操作符一起调用。

#### 4.3.5 用var声明局部变量

在Java 10中，如果可以从变量的初始值推导出它们的类型，那么可以用`var`关键字声明
局部变量，而无须指定类型。以避免重复写类型名。

注意var关键字只能用于方法中的局部变量。参数和字段的类型必须声明。

```java
// 显示声明
Employee harry = new Employee("Harry Hacker",50000,1989,10,1);
// 自动推断
var harry = new Employee("Harry Hacker",50000,1989,10,1);
```

#### 4.3.6 使用null引用

对象变量包含一个对象的引用，或者包含一个特殊值`null`，后者表示没有引用任何对象。如果对null值应用一个方法，会产生一个`NullPointerException`异常。

```java
LocalDate rightNow = null;
String s = rightNow.toString(); // NullPointerException
```

例如Employee的构造器中，name可能为null，就需要手动进行检查：

```java
// 简单语法
if(n == null) name = "unknown"; else name = n;
// 使用Object类赋默认值
name = Objects.requireNonNullElse(n, "unknown");
// 使用Objectl类校验
name = Objects.requireNonNull(n, "The name cannot be null");
/*
|  异常错误 java.lang.NullPointerException：The name cannot be null
|        at Objects.requireNonNull (Objects.java:246)
|        at (#6:1)
*/
```

#### 4.3.7 隐式参数与显式参数

方法会操作对象并访问它们的实例字段。例如raiseSalary方法：

```java
public void raiseSalary(double byPercent)
{
    double raise = salary * byPercent / 100;
    salary += raise;
}

// numbere007.raiseSalary(5);
```

该方法有两个参数。第一个参数是出现在方法名前的Employee类型的对象，称为**隐式（implicit）参数**；第二个参数是位于方法名后面括号中的数值，这是一个**显式（explicit）参数**。

可以看到，显式参数显式地列在方法声明中，例如 double byPercent。隐式参数则没有出现在方法声明中。

也可以使用关键字this指示隐式参数。这样可以将实例字段与局部变量明显地区分开来。

```java
public void raiseSalary(double byPercent)
{
    double raise = this.salary * byPercent / 100;
    this.salary += raise;
}
```

#### 4.3.8 封装的优点

```java
   public String getName()
   {
      return name;
   }

   public double getSalary()
   {
      return salary;
   }

   public LocalDate getHireDay()
   {
      return hireDay;
   }
```

这些都是典型的访问器方法。由于它们只返回实例字段的值，因此又称为**字段访问器（field accessor）**。

建议通过访问器/修改器使用实例字段，而不是直接对外暴露字段。

- 首先可以保护实例字段不被预期以外的行为更改，例如name为只读字段，salary只能使用raiseSalary修改，出了问题也方便调试。
- 另一方面可以改变内部实现而不影响外部代码，例如姓名改成firstName和lastName后只需要修改访问器getName的实现为firstName+LastName。
- 最后可以在更改器中封装错误检查等常用逻辑。例如在setSalary方法可以检查工资是否小于0。

需要注意的是，不要编写返回可变对象引用的访问器方法。

```java
class Employee
{
   private LocalDate hireDay;

   public Date getHireDay()
   {
      return (Date) hireDay;
   }
}
```

LocalDate类没有更改器方法，但Date类有一个更改器方法setTime。如上，如果将hireDay返回为Date类型，外部就可以通过获取到的引用修改内部变量，破坏封装性。

```java
Employee harry = new Employee("Harry Hacker",50000,1989,10,1);
Date d= harry.getHireDay();
double tenYearsInMilliseconds = 10*365.25*24*60*60*1000;
d.setTime(d,getTime()-(long) tenYearsInMilliseconds);
// let's give Harry ten years of added seniority
```

如果需要返回一个可变对象的引用，首先应该对它进行**克隆(clone)**。

```java
class Employee
{
   private LocalDate hireDay;

   public Date getHireDay()
   {
      return (Date) hireDay.clone();
   }
}
```

#### 4.3.9 基于类的访问权限

方法可以访问**调用这个方法的对象**的私有数据。一个类的方法可以访问**这个类的所有对象**的私有数据。如下是一个示例：

```java
class Employee {
    public boolean equals(Employee other)
    {
        return name.equals(other.name);
    }
}

// if(harry.equals(boss)) ...
```

equals是Employee类的方法，而boss虽然不是调用方法的对象，但也是Employee类的对象，所以可以被quials方法访问。

#### 4.3.10 私有方法

在Java中，要实现一个私有方法，只需将关键字`public`改为`private`即可。

#### 4.3.11 final实例字段

可以将实例字段定义为final。这样的字段**必须**在构造对象时初始化。也就是说，必须确保在每一个构造器执行之后，这个字段的值已经设置，并且以后不能再修改这个字段。

final修饰符对于类型为基本类型或者**不可变类**的字段尤其有用。对于可变类，使用final修饰符可能会造成混乱。final关键字只是表示存储在变量中的对象引用不会再指示另一个不同的对象。但这个对象本身可以更改的。

### 4.4 静态字段与静态方法

#### 4.4.1 静态字段

如果将一个字段定义为static，那么这个字段并不出现在每个类的对象中。每个静态字段只有一个副本。可以认为静态字段属于类，而不属于单个对象。

一个使用示例，全局唯一的自增id：

```java

class Employee
{
    private static int nextTd = 1;
    private int id;

    public Employee() {
        id = nextId;
        nextId++;
    }
}
```

#### 4.4.2 静态常量

相比于静态变量，更常用的是静态常量。

```java
public class Math
{
    public static final double PI = 3.14159265358979323846;
}
```

#### 4.4.3 静态方法

静态方法是不操作对象的方法，即没有隐式参数。例如`Math.pow(x,a)`计算x<sup>a</sup>，不依赖具体的Math对象。

Employee类的静态方法不能访问非静态的id实例字段，因为它并不操作对象。但是，静态方法可以访问静态字段。

```java

class Employee
{
    private static int nextTd = 1;
    private int id;

    public static int advanceId(){
        int r= nextId;// obtain next available id
        nextId++;
        return r;
    }
}

// int n= Employee.advanceId();
```

下面两种情况可以使用静态方法：

- 方法不需要访问对象状态，因为它需要的所有参数都通过显式参数提供（例如Math.pow）。
- 方法只需要访问类的静态字段（例如Employee.advanceId）。

#### 4.4.4 工厂方法

静态方法的一种常见用途是使用静态**工厂方法（factory method）**构造对象。

```java
NumberFormat currencyFormatter = NumberFormat.getCurrencyInstance();
NumberFormat percentFormatter = NumberFormat.getPercentInstance();
double x = 0.1;
System.out.println(currencyFormatter.format(x)); // prints $0.10
System.out.println(percentFormatter.format(x)); // prints 10%
```

不使用构造器是因为无法为构造器命名且构造的类型固定，而我们需要两种不同的实例。

#### 4.4.5 main方法

main方法也是一个静态方法。每一个类都可以有一个main方法。这是为类增加演示代码的一个技巧。直接`java 类名`就可以运行这个main方法。如果该类是更大应用的一部分，那么在运行应用时类的main方法不会执行。

```java
/**
 * This program demonstrates static methods.
 * @version 1.03 2021-09-03
 * @author Cay Horstmann
 */
public class StaticTest
{
   public static void main(String[] args)
   {
      // fill the staff array with three Employee objects
      var staff = new Employee[3];

      staff[0] = new Employee("Tom", 40000);
      staff[1] = new Employee("Dick", 60000);
      staff[2] = new Employee("Harry", 65000);

      // print out information about all Employee objects
      for (Employee e : staff)
      {
         System.out.println("name=" + e.getName() + ",id=" + e.getId() + ",salary="
            + e.getSalary());
      }

      int n = Employee.advanceId(); // calls static method
      System.out.println("Next issued id=" + n);
   }
}

class Employee
{
   private static int nextId = 1;

   private String name;
   private double salary;
   private int id;

   public Employee(String n, double s)
   {
      name = n;
      salary = s;
      id = advanceId();
   }

   public String getName()
   {
      return name;
   }

   public double getSalary()
   {
      return salary;
   }

   public int getId()
   {
      return id;
   }

   public static int advanceId()
   {
      int r = nextId; // obtain next available id
      nextId++;
      return r;
   }

   public static void main(String[] args) // unit test
   {
      var e = new Employee("Harry", 50000);
      System.out.println(e.getName() + " " + e.getSalary());
   }
}

/*
> java Employee        
Harry 50000.0

> java StaticTest  
name=Tom,id=1,salary=40000.0
name=Dick,id=2,salary=60000.0
name=Harry,id=3,salary=65000.0
Next issued id=4
*/
```

### 4.5 方法参数

**按值调用（call by value）**表示方法接收的是调用者提供的值。而**按引用调用（call by reference）**表示方法接收的是调用者提供的变量**位置（location）**。所以，方法可以修改按引用传递的变量的值，而不能修改按值传递的变量的值。

Java程序设计语言总是采用按值调用。也就是说，方法会得到所有参数值的一个副本。
对于基本数据类型的参数，内部变量的变更不会影响外部变量。而对于对象参数，虽然传递的是这个对象的引用的副本，但因为两个引用都指向一个对象，所以外部变量的状态也可以被改变。

对于对象参数，容易将其误解为按引用调用，实际上还是按值调用，是复制了引用的值。如下是一个示例：

```java
class Employee {
    private String name;

    public Employee(String n) {
        name = n;
    }

    public String getName() {
        return name;
    }

    // doesn't work
    public static void swap(Employee x,Employee y) {
        Employee temp = x;
        x = y;
        y = temp;
    }
}

var a = new Employee("Alice");
var b= new Employee("Bob");
Employee.swap(a, b);
// does a now refer to Bob, b to Alice?

System.out.println("a: " + a.getName()); // a: Alice
System.out.println("b: " + b.getName()); // b: Bob
```

如上swap方法只交换了方法内副本引用指向的变量，而外部的引用还是指向原本的变量。说明**对象引用（object reference）**也是按值传递的。

总结：

- 方法不能修改基本数据类型的参数（即数值型或布尔型）。
- 方法可以改变对象参数的状态。
- 方法不能让一个对象参数引用一个新对象。

完整测试代码：

```java
/**
 * This program demonstrates parameter passing in Java.
 * @version 1.01 2018-04-10
 * @author Cay Horstmann
 */
public class ParamTest
{
   public static void main(String[] args)
   {
      /*
       * Test 1: Methods can't modify numeric parameters
       */
      System.out.println("Testing tripleValue:");
      double percent = 10;
      System.out.println("Before: percent=" + percent);
      tripleValue(percent);
      System.out.println("After: percent=" + percent);

      /*
       * Test 2: Methods can change the state of object parameters
       */
      System.out.println("\nTesting tripleSalary:");
      var harry = new Employee("Harry", 50000);
      System.out.println("Before: salary=" + harry.getSalary());
      tripleSalary(harry);
      System.out.println("After: salary=" + harry.getSalary());

      /*
       * Test 3: Methods can't attach new objects to object parameters
       */
      System.out.println("\nTesting swap:");
      var a = new Employee("Alice", 70000);
      var b = new Employee("Bob", 60000);
      System.out.println("Before: a=" + a.getName());
      System.out.println("Before: b=" + b.getName());
      swap(a, b);
      System.out.println("After: a=" + a.getName());
      System.out.println("After: b=" + b.getName());
   }

   public static void tripleValue(double x) // doesn't work
   {
      x = 3 * x;
      System.out.println("End of method: x=" + x);
   }

   public static void tripleSalary(Employee x) // works
   {
      x.raiseSalary(200);
      System.out.println("End of method: salary=" + x.getSalary());
   }

   public static void swap(Employee x, Employee y)
   {
      Employee temp = x;
      x = y;
      y = temp;
      System.out.println("End of method: x=" + x.getName());
      System.out.println("End of method: y=" + y.getName());
   }
}

class Employee // simplified Employee class
{
   private String name;
   private double salary;

   public Employee(String n, double s)
   {
      name = n;
      salary = s;
   }

   public String getName()
   {
      return name;
   }

   public double getSalary()
   {
      return salary;
   }

   public void raiseSalary(double byPercent)
   {
      double raise = salary * byPercent / 100;
      salary += raise;
   }
}

/*
Testing tripleValue:
Before: percent=10.0
End of method: x=30.0
After: percent=10.0

Testing tripleSalary:
Before: salary=50000.0
End of method: salary=150000.0
After: salary=150000.0

Testing swap:
Before: a=Alice
Before: b=Bob
End of method: x=Bob
End of method: y=Alice
After: a=Alice
After: b=Bob
*/
```

### 4.6 对象构造

#### 4.6.1 重载

果多个方法有相同的方法名但有不同的参数，便出现了**重载（overloading）**。

编译器用各个方法首部中的参数类型与特定方法调用中所使用的值类型进行匹配，来选出正确的方法。如果编译器无法匹配参数，就会产生编译时错误。个查找匹配的过程称为**重载解析（overloading resolution）**。

#### 4.6.2 默认字段初始化

如果在构造器中没有显式地为一个字段设置初始值，就会将它自动设置为默认值：数值将设置为θ，布尔值为false，对象引用为null。

这是字段与局部变量的一个重要区别。方法中的局部变量必须明确地初始化。但是在类中，如果没有初始化类中的字段，将会自动初始化为默认值。

#### 4.6.3 无参数的构造器

很多类都包含无参数的构造器，由无参数构造器创建对象时，对象的状态会设置为适当的默认值。

如果写的类没有构造器，就会为你提供一个无参数构造器。这个构造器将所有的实例字段设置为相应的默认值。

如果类中提供了至少一个构造器，但是没有提供无参数构造器，那么构造对象时就必须提供参数，否则就是不合法的。

#### 4.6.4 显式字段初始化

通过重载类的构造器方法，可以采用多种形式设置类实例字段的初始状态。

可以在类定义中直接为任何字段赋值。

```java
class Employee
{
    private String name =""; // 常量初始化
    private static int nextId;
    private int id= advanceId(); // 方法初始化

    private static int advanceId() {
        int r = nextId;
        nextId++;
        return r;

    }

    public String getName() {
        return name;
    }

    public int getID() {
        return id;
    }
}
```

#### 4.6.5 参数名

使用单字母作为参数名很简便但可读性较差。一种方法是使用a前缀，另一种方法是直接*遮蔽*同名的实例字段，然后通过`this.field`的方法访问实例字段。

```java
// 单字母
public Employee(String n, double s)
{
    name = n;
    salary = s;
}

// a前缀
public Employee(String aName, double aSalary)
{
    name = aName;
    salary = aSalary;
}

// 遮蔽实例字段
public Employee(String name, double salary)
{
    this.name = name;
    this.salary = salary;
}
```

#### 4.6.6 调用另一个构造器

如果构造器的第一个语句形如`this(...)`，这个构造器将调用同一个类的另一个构造器。

```java
public Employee(double s)
{
    // calls Employee(String, double)
    this("Employee #" + nextId, s);
    nextId++;
}
```

#### 4.6.7 初始化块

在一个类的声明中，可以包含任意的代码块。构造这个类的对象时，这些块就会执行。这种机制成为称为**初始化块（initialization block）**。类似Golang的init()。

```java
class Employee
{
    private static int nextId;
    private int id;
    private String name;
    private double salary;

    // object initialization block
    {
    id = nextId;
    nextId++;
    }

    public Employee(String n, double s)
    {
    name = n;
    salary = s;
    }

    public Employee()
    {
    name = "";
    salary = 0;
    }
}
```

如果类的静态字段需要很复杂的初始化代码，那么可以使用静态的初始化块。

```java
private static Random generator = new Random();
// static initialization block
static
{
    nextId = generator.nextInt(10000);
}
```

本节小结：

- 重载构造器；
- 用`this(...)`调用另一个构造器；
- 无参数构造器；
- 对象初始化块；
- 静态初始化块；
- 实例字段初始化。

```java
import java.util.*;

/**
 * This program demonstrates object construction.
 * @version 1.02 2018-04-10
 * @author Cay Horstmann
 */
public class ConstructorTest
{
   public static void main(String[] args)
   {
      // fill the staff array with three Employee objects
      var staff = new Employee[3];

      staff[0] = new Employee("Harry", 40000);
      staff[1] = new Employee(60000);
      staff[2] = new Employee();

      // print out information about all Employee objects
      for (Employee e : staff)
         System.out.println("name=" + e.getName() + ",id=" + e.getId() + ",salary="
            + e.getSalary());
   }
}

class Employee
{
   private static int nextId;

   private int id;
   private String name = ""; // instance field initialization
   private double salary;

   private static Random generator = new Random();
   
   // static initialization block
   static
   {
      // set nextId to a random number between 0 and 9999
      nextId = generator.nextInt(10000);
   }

   // object initialization block
   {
      id = nextId;
      nextId++;
   }

   // three overloaded constructors
   public Employee(String n, double s)
   {
      name = n;
      salary = s;
   }

   public Employee(double s)
   {
      // calls the Employee(String, double) constructor
      this("Employee #" + nextId, s);
   }

   // the default constructor
   public Employee()
   {
      // name initialized to ""--see above
      // salary not explicitly set--initialized to 0
      // id initialized in initialization block
   }

   public String getName()
   {
      return name;
   }

   public double getSalary()
   {
      return salary;
   }

   public int getId()
   {
      return id;
   }
}
```

#### 4.6.8 对象析构与finalize方法

C++有显式的析构器方法，但Java有GC所以不支持析构器。

如果一个资源一旦使用完就需要立即关闭，那么应当提供一个close方法来完成必要的清理工作。可以在对象使用完时调用这个close方法。

如果可以等到虚拟机退出，那么可以用方法Runtime.addshutdownHook增加一个“关闭钩”（shutdown hook）。在Java 9中，可以使用Cleaner类注册一个动作，当对象不再可达时（除了清洁器还能访问，其他对象都无法访问这个对象），就会完成这个动作。不过在实际中这些情况很少见。

不要使用finalize方法来完成清理。该方法已经被废弃。

### 4.7 记录

创建一个类需要大量样板代码。对于不需要负担复杂业务逻辑的数据集合来说很麻烦，所以新增了一个“记录”特性。

#### 4.7,1 记录概念

**记录（record）**是一种特殊形式的类，其状态不可变，而且公共可读。一个记录的实例字段称为**组件（component）**。

```java
record Point(double x, double y) {}

// 类比为类等价如下
class Point {
    private final double x;
    private final double y;
    
    Point(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public double x() { return this.x; }
    public double y() { return this.y; }

    public String toString() {...}
    public boolean equals(Object o) {...}
    public int hashCode() {...}
}
```

如上，对于声明的record，将会自动包含实例字段、构造器、公共访问方法（方法名与组件同名，例如 x()、y()，而不是传统的 getX()）、toSring,equals和hashCode方法，不需要手动实现这些样板代码。

当然，也可以像类一样重写已有方法或者添加自定义方法，但注意**不能为记录增加实例字段**。

记录的实例字段自动为final字段。不过，它们可能是可变对象的引用，这样记录实例将是可变的。如果希望记录实例是不可变的，那么字段就不能使用可变的类型。

```java
record PointInTime(double x, double y, Date when) { }

var pt = new PointInTime(0, 0, new Date()); 
// Mon Jun 15 10:34:11 HKT 2026
pt.when().setTime(0); 
// Thu Jan 01 08:00:00 HKT 1970
```

#### 4.7.2 构造器：标准、自定义和简洁

自动定义地设置所有实例字段的构造器称为**标准构造器（canonical constructor）**。

和[4.6.6](#466-调用另一个构造器)一样，还可以定义另外的**自定义构造器（custom constructor）**，再通过`this(...)`，调用主构造器。

```java
record Point(double x, double y) {
    private final double x;
    private final double y;
    
    // 标准构造器，一般由record默认实现
    Point(double x, double y) {
        this.x = x;
        this.y = y;
    }

    // 自定义构造器，通过this()调用主构造器
    Point() { this(0, 0) }
}
```

如果需要完成额外的工作，可以重写标准构造器。此外，record也支持一种**简洁构造器（compact constructor）**，不用指定参数列表和手动赋值。

```java
// 标准构造器
record Range(int from, int to)
{
    public Range(int from, int to)
    {
        if(from <= to)
        {
            this.from = from;
            this.to = to;
        }
        else
        {
            this.from = to;
            this.to = from;
        }
    }
}

// 简洁构造器
record Range(int from, int to)
{
    public Range
    {
        if(from > to)
        {
            int temp = from;
            from = to;
            to= temp;
        }
    }
}
```

简洁形式构造器相当于标准构造器的预处理，它只是在为实例字段this.from和 this.to赋值之前修改参数变量from和to。不能在简洁构造器的主体中读取或修改实例字段，因为此时字段尚未初始化，只能修改参数变量。

### 4.8 包

Java使用**包（package）**将类组织在一个集合中，方便组织代码，和区分不同的代码库。

#### 4.8.1 包名

使用包的主要原因是确保类名的唯一性。常见包名形式是使用因特网域名逆序+项目名+类名，如com.horstmann.corejava.Employee。

#### 4.8.2 类的导入

一个类可以使用所属包（这个类所在的包）中的所有类，以及其他包中的**公共类（public class）**。

有两种方式访问另一个包中的公共类。第一种方式是使用**完全限定名（fully qualified name）**，也就是包名+类名，比较繁琐。更简单且更常用的方式是使用import语句，在使用类时不必写出类的全名。

```java
// 完全限定名
java.time.LocalDate today = java.time.LocalDate.now();

// 使用import语句，导入java.time包
import java.time.*;
// 或者导入包中特定类
// import java.time.LocalDate;
LocalDate today = LocaDate.now();
```

如果要使用不同包的同名类，可以临时回退到完全限定名避免冲突。

```java
var startTime = new java.util.Date();
var today = new java.sql.Date(...);
```

Java中的package和import语句类似于C++中的namespace和using指令。

#### 4.8.3 静态导入

可以使用`static`关键字导入静态方法和静态字段，不必加类名前缀。

```java
// 无静态导入
Math.sqrt(Math.pow(x,2)+ Math.pow(y,2))

// 静态导入
import static java.lang.Math.*;
sqrt(pow(x,2)+ pow(y,2))
```

#### 4.8.4 在包中增加类

要想将类放入包中，就必须将包名放在源文件的开头，即放在定义这个包中各个类的代码之前。

```java
package com.horstmann.corejava;

public class Employee
{
    ...
{
```

如果没有在源文件中放置package语句，那么这个源文件中的类就属于**无名包（unnamed package）。**无名包没有包名。

源文件应该放到与完整包名匹配的子目录中。

#### 4.8.5 包访问

- 标记为public的部分可以由任意类使用；
- 标记为private的部分只能由定义它们的类使用。
- 如果没有指定public或private,这个部分（类、方法或变量）可以由同一个包中的所有方法访问。

#### 4.8.6 类路径

类除了存储在与包名匹配的文件系统的子目录中，也可以存储在JAR（Java归档）文件中。在一个JAR文件中，可以包含多个压缩格式的类文件和子目录，这样既可以节省空间又可以改善性能。

类路径（class path）是所有包含类文件的路径的集合。在UNIX环境中，类路径中的各项之间用冒号（:）分隔，而在Windows环境中，则以分号（;）分隔。不论是UNIX还是Windows,都用句点（.）表示当前目录。

```bash
# unix
/home/user/classdir:.:/home/user/archives/archive.jar

# windows
c:\classdir;.;c:\archives\archive.jar
```

#### 4.8.7 设置类路径

最好使用`-classpath`或`-cp`选项指定类路径:

```bash
# unix
java -classpath /home/user/classdir:.:/home/user/archives/archive.jar MyProg

# windows
java -classpath c:\classdir;.;c:\archives\archive.jar MyProg
```

另一种方法是通过设置CLASSPATH环境变量来指定类路径。具体细节依赖于所使用的shell。

```bash
# bash
export CLASSPATH=/home/user/classdir:.:/home/user/archives/archive.jar

# Windows shell
set CLASSPATH=c:\classdir;.;c:\archives\archive.jar
```

### 4.9 JAR文件

JAR使用了ZIP压缩格式。

更多关于jar命令和JAR文件规范可以查阅官方文档：

- [jar](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jar.html)
- [JAR](https://docs.oracle.com/en/java/javase/25/docs/specs/man/index.html)

#### 4.9.1 创建JAR文件

```bash
jar options file1 file2

# e.g.
jar cvf CalculatorClasses.jar *.class icon.gif
```

jar的选项类似于UNIX tar命令的选项。

![jar程序选项](/post-images/《Java核心技术》阅读笔记/v1ch04_01.png)

#### 4.9.2 清单文件

每个JAR文件包含一个**清单文件（manifest）**，用于描述归档文件的特殊特性。

清单文件被命名为`MANIFEST.MF`,它位于JAR文件的一个特殊的META-INF子目录中。

合法的最小清单文件极其简单：`Manifest-Version: 1.0`。

复杂的清单文件可能包含更多条目。这些清单条目被分组为多个节。第一节被称为**主节（main section）**。它作用于整个JAR文件。随后的条目可以指定命名实体的属性，如单个文件、包或者URL。它们都必须以一个Name条目开始。节与节之间用空行分开。

```txt
Manifest-Version: 1.0
lines describing this archive

Name:Woozle.class
lines describing this file
Name: com/mycompany/mypkg/
lines describing this package
```

### 4.9.3 可执行JAR文件

可以使用jar命令中的`e`选项指定程序的入口点，即通常调用java执行程序时指定的类：

```bash
jar cvfe MyProgram.jar com.mycompany.mypkg.MainAppClass ...
```

或者在清单文件中指定程序的主类，不需要加扩展名.class：

```bash
Main-Class: com.mycompany.mypkg.MainAppClass
```

可以通过`-jar`选项启动JAR文件：

```bash
java -jar MyProgram.jar
```

### 4.9.4 多版本JAR文件

简单来说，多版本JAR文件的目的是让同一个JAR兼容多版本，而不需要对各个版本分别打包，实现用户无感，不需要手动选择对应版本的JAR包。

但这个特性并不常用。首先，大部分应用只跑在一个固定的JDK版本上，不需要在不同JDK版本上运行。其次，对于库维护者更常见的做法也是直接提升最低JDK版本要求，而不是维护多版本。最后，也可以在代码里判断JDK版本，动态选择不同的实现路径。这样就不需要特殊构建流程，简单直观。

```java
public class CssParserFactory {
    public static CssParser create() {
        if (Runtime.version().feature() >= 9) {
            return new Java9CssParser();  // 使用新 API
        } else {
            return new Java8CssParser();  // 使用旧 API
        }
    }
}
```

总的来说，这个特性不需要过多了解。

### 4.9.5 关于命令行选项的说明

简单来说就是屎山，各种用法并不统一，简单看看就行，不用深入了解。

### 4.10 文档注释

`javadoc`工具可以由源文件生成一个HTML文档。简单看看就行，不了解这些规则也看得懂注释。

[官方文档](https://docs.oracle.com/en/java/javase/26/docs/specs/man/javadoc.html)

#### 4.10.1 注释的插入

javadoc主要抽取以下信息：

- 模块；
- 包；
- 公共类与接口；
- 公共的和受保护的字段；
- 公共的和受保护的构造器及方法。

注释以`/**`开始，并以`*/`结束。含**标记**以及之后紧跟着的**自由格式文本（free-form text）**。标记以`@`开始。自由格式文本的第一个句子应该是一个概要陈述，avadoc工具将抽取生成概要页。

自由格式文本支持HTML修饰符。但要键入等宽代码，需要使用`{@code ⋯ }`而不是`<code>⋯</code>`，避免对代码中的`<`字符转义。

#### 4.10.2 类注释

类注释放在import语句之后，class定义之前。示例如下：

```java
/**
* A {@code Card} object represents a playing card, such
* as "Queen of Hearts".A card has a suit (Diamond, Heart,
* Spade or Club) and a value (1= Ace, 2...10, 11 = Jack,
* 12= Queen, 13 = King)
*/
public class Card
{
    ...
}
```

每一行开始的*非必须，但大部分IDE都会自动提供。

#### 4.10.3 方法注释

方法注释放在所描述方法之前。如下是可用标记：

- `@param variable description`
    这个标记将给当前方法的“parameters”（参数）部分添加一个条目。
    一个方法的所有@param标记必须放在一起。
- `@return description`
    这个标记将给当前方法添加“returns”（返回）部分。
- `@throws class description`
    这个标记将添加一个注释，表示这个方法有可能抛出异常。

```java
/**
* Raises the salary of an employee.
* @param byPercent the percentage by which to raise the salary (e.g., 10 means 10%)
* @return the amount of the raise
*/
public double raiseSalary(double byPercent)
{
    double raise = salary * byPercent / 100;
    salary += raise;
    return raise;
}
```

#### 4.10.4 字段注释

只需要对公共字段（通常指的是静态常量）增加文档注释。例如:

```java
/**
* The "Hearts" card suit
*/
public static final int HEARTS = 1;
```

#### 4.10.5 通用注释

标记`@since text`会建立一个“since”（始于）条目。text（文本）可以是对引入这个特性的版本的描述。例如，@since 1.7.1。

类文档注释可以使用如下标记：

- `@author name`
    这个标记将建立一个“author”（作者）条目。可以有多个@author标记，每个@author标记对应一个作者。此标记非必需，git之类版本控制系统能够更好地跟踪作者。
- `@version text`
    这个标记将建立一个“version”（版本）条目。这里的text可以是对当前版本的任何描述。
- `@see reference`
    这个标记将在在“see also”（参见）部分增加一个超链接。它可以用于类中，也可以用于方法中。可选项如下：

  - `package.class#feature label` 即类名#方法名。
  - `<a href="...">label</a>` 即外部链接。
  - text 即任意文本。

#### 4.10.6 包注释

包注释需要在包目录中添加一个单独的文件。有两个选择：

- 提供一个名为package-info.java的Java文件。这个文件必须包含一个初始的Javadoc注释，以`/**`和`*/`界定，后面是一个package语句。它不能包含更多的代码或注释。
2.提供一个名为package.html的HTML文件，抽取标记`<body>...</body>`之间的所有文本。

#### 4.10.7 注释提取

使用`-d`选项指定存放提取出来的注释的目标目录。

```bash
# 一个包
javadoc -d  docDirectory nameOfPackage
# 多个包
javadoc -d  docDirectory nameOfPackage1 nameOfPackage2 ...
# 无名包
javadoc -d  docDirectory *.java
```

- 可以使用`-author`和`-version`选项在文档中包含@author和@version标记。
- 选项`-link`可以用来为标准类添加超链接。
- 如果使用`-linksource`选项，那么每个源文件将会转换为HTML（不对代码着色，但包含行号）,并且每个类和方法名将变为指向源代码的超链接。
- 用户可以提供一个类似overview.html的文件作为概要注释。命令行选项`-overview filename`将抽取标记<body>⋯</body>之间的所有文本。当用户从导航栏中选择“Overview”时，就会显示这些内容。

### 4.11 类设计技巧

1. 一定要保证数据私有
2. 一定要初始化数据
3. 不要在类中使用过多的基本类型
4. 不是所有字段都需要单独的字段访问器和更改器
5. 分解有过多指责的类
6. 类名和方法名要能够体现他们的职责
7. 优先使用不可变的类

## 第5章 继承

### 5.1 类、超类和子类

#### 5.1.1 定义子类

可以使用`extend`关键字标识继承。

```java
public class Manager extends Employee
{
    ...
}
```

关键字extends 指示正在构造的新类派生于一个已存在的类。这个已存在的类称为**超类（superclass）**、**基类（base class）**或**父类（parent class）**；新类称为**子类（subclass/child class）**或**派生类（derived class）**。

通过扩展超类定义子类的时候，只需要指出子类与超类的不同之处。因此，在设计类的时候，应该将最一般的方法放在超类中，而将更特殊的方法放在子类中，这种将通用功能抽取到超类的做法在面向对象程序设计中十分普遍。

#### 5.1.2 覆盖方法

超类中的有些方法对子类不一定适用。这是就需要提供一个新的方法来**覆盖（override）**超类中的这个方法。

```java
public class Manager extends Employee
{
    public double getSalary()
    {
        double baseSalary = super.getSalary();
        return baseSalary + bonus;
    }
}
```

如上，可以使用特殊的关键字`super`指示编译调用超类方法。

子类可以*增加*字段、*增加*方法或*覆盖*超类的方法，但继承不会删除任何字段或方法。

#### 5.1.3 子类构造器

```java
public Manager(String name, double salary, int year,int month, int day)
{
    super(name, salary, year, month, day);
    bonus = 0;
}
```

由于 Manager类的构造器不能访问 Employee类的私有字段，所以必须通过一个构造器来初始化这些私有字段。可以利用特殊的super语法调用这个构造器。使用super调用构造器的语句必须是子类构造器的第一条语句。

如果构造子类对象时没有显式地调用超类的构造器，那么超类必须有一个无参数构造器。这个构造器会在子类构造之前调用。

```java
Manager boss = new Manager("Carl Cracker",80000,1987,12,15);
boss.setBonus(5000);

var staff = new Employee[3];

staff[0] = boss; // 向Employee数组传入Manager对象
staff[1] = new Employee("Harry Hacker",50000,1989,10,1);
staff[2] = new Employee("Tony Tester",40000,1990,3,15);

for(Employee e:staff)
    // 对staff[0]，将调用Manager.getSalary()
    // 对staff[1]，将调用Employee.getSalary()
    System.out.println(e.getName() + "" + e.getSalary()); 

/*
Carl Cracker 85000.0
Harry Hacker 58000.0
Tommy Tester 40000.0
*/
```

如上，一个对象变量（例如，变量e）可以指示多种实际类型，这一点称为**多态（polymorphism）**。在运行时能够自动地选择适当的方法，这称为**动态绑定（dynamic binding）**。

#### 5.1.4 继承层次结构

继承并不仅限于一个层次。由一个公共超类派生出来的所有类的集合称为**继承层次结构（inheritance hierarchy）**，如图所示。在继承层次结构中，从某个特定的类到其祖先的路径称为该类的**继承链（inheritance chain）**。

![继承层次结构](/post-images/《Java核心技术》阅读笔记/v1ch05_01.png)

#### 5.1.5 多态

“is-a”规则可以用来判断是否应该将数据设计为继承关系，它指出子类的每个对象也是超类的对象。另一种表述是**替换原则（substitution principle）**，它指出程序中需要超类对象的任何地方都可以使用子类对象替换。

在Java程序设计语言中，对象变量是**多态（polymorphic）**的。一个超类类型的变量既可以引用一个超类类型的对象，也可以引用超类的任何一个子类的对象。同时，不能将超类的引用赋值给子类。

```java
public class Employee{}
public class Manager extends Employee{}

Emploee e;
e = new Employee(); // OK
e = new Manager(); // OK

Manager m;
m = new Manager(); // OK
e = new Manager();
m = e; // ERROR 虽然e引用的对象为Manager类型，但e本身是Emploee类型，不能直接复制给Manager类型变量

m = new Manager();
e = new Manager();
m.setBonus(5000); // OK
e.setBonus(5000); // ERROR 虽然e引用的对象为Manager类型，但e本身是Emploee类型，没有setBonus方法

```

可能导致一些问题，如下：

```java
Manager[] managers = new Manager[10];

// 子类引用数组可以转换成超类引用数组，而不需要使用强制类型转换。
Employee[] staff = managers; // OK

// staff[0]和managers[0]是相同引用，将报错ArrayException异常。
staff[0]= new Employee("Harry Hacker",...);
```

### 5.1.6 理解方法调用

进行方法调用时，编译器首先会查看对象的声明类型和方法名，列举类及其超类中所有方法名相同且课访问的方法。然后确定方法调用中提供的参数类型，若所有方法中存在与所提供参数类型完全匹配的方法则选择该方法，这个过程称为**重载解析（overloading resolution）**。

这个过程允许类型转换（int->double，Manager->Employee等），情况可能很复杂。如果没有找到参数类型匹配的方法或者类型转换后有多个方法匹配，编译器将报错。

返回类型不是签名的一部分。不过在覆盖一个方法时，需要保证返回类型的兼容性。允许子类将覆盖方法的返回类型改为原返回类型的子类型。此时这两个方法有**协变（covariant）**的返回类型。

```java
public class Employee {
    public Employee getBuddy(){...}
}
public class Manager extends Employee {
    public Manager getBuddy(){...}// OK to change return type
}
```

对于private方法、static方法、final方法或者构造器，编译器可以准确地知道应该调用哪个方法。这称为**静态绑定（static binding）**。与此对应的是，如果要调用的方法依赖于隐式参数的实际类型，那么必须在运行时使用动态绑定。

程序运行并且采用动态绑定调用方法时，虚拟机必须调用与变量所引用对象的实际类型对应的那个方法。若子类有目标方法则调用该方法，否则将在其超类寻找对于方法，以此类推。

每次调用方法都要完成这个搜索，时间开销相当大。因此，虚拟机预先为每个类计算了一个**方法表（method table）**,其中列出了所有方法的签名和要调用的实际方法。这样一来，真正调用方法的时候，虚拟机仅查找这个表就行了。

```java
Employee:
    getName()-> Employee.getName()
    getSalary()->Employee.getSalary()
    getHireDay()-> Employee.getHireDay()
    raiseSalary(double)->Employee.raiseSalary(double)

Manager:
    getName()->Employee.getName()
    getSalary()->Manager.getSalary()
    getHireDay()->Employee.getHireDay()
    raiseSalary(double)->Employee.raiseSalary(double)
    setBonus(double)->Manager.setBonus(double)
```

动态绑定有一个非常重要的特性：无须修改现有的代码就可以对程序进行扩展。假设增加一个新类，当变量引用这个类的对象时，我们不需要对方法调用的代码重新进行编译，而是会自动调用新类的方法。

覆盖一个方法的时候，子类方法不能低于超类方法的可见性。

### 5.1.7 阻止继承：final类方法

如果在类定义中使用了final修饰符，就表明这个类不允许扩展，被称为final类。也可以将类中的某个特定方法声明为final，所有子类都不能覆盖这个方法（final类中的所有方法自动地成为final方法）。

```java
public final class Executive extends Manager {}

public class Employee{
    private String name;

    public final String getName(){
        return name;
    }
}
```

> 字段也可以声明为final。对于final字段来说，构造对象之后就不允许改变了。不过，如果将一个类声明为final,只有其中的方法自动地成为final，而不包括字段。

早期会使用final关键字进行**内联（inline）**优化，但现在的编译器能力够强会自动处理内联，手写final标注几乎无效。所以绝不要因为“性能”而使用 final，而是用于确保它们不会在子类中改变语义。

> 举和记录总是final,它们不允许扩展。

#### 5.1.8 强制类型转换

除了基本数据类型，对象引用也可以进行强制类型转换。

- 只能在继承层次结构内进行强制类型转换。
- 在将超类强制转换成子类之前，应该使用instanceof进行检查。

在进行强制类型转换之前，建议使用`instanceof`操作符先查看是否能够成功地转换。

```java
var staff = new Employee[3];
staff[0] = new Manager("Carl Cracker",80000,1987,12,15);
staff[1] = new EmpLoyee("Harry Hacker",50000,1989,10,1);
staff[2] = new Employee("Tony Tester",40000,1990,3,15);

Manager boss=(Manager)staff[0]; // OK
Manager boss =(Manager) staff[1]; // ERROR ClassCastException

if (staff[i] instanceof Manager)
{
    boss = (Manager) staff[i];
}
```

实际上，通过强制类型转换来转换对象的类型通常并不是一个好主意。如果需要在超类上调用子类方法，就应该考虑是否有必要重新设计超类添加该方法。一般情况下，最好尽量少用强制类型转换和instanceof操作符。

#### 5.1.9 instanceof 模式匹配

```java
// 反复提到子类 Manager 3次
if(staff[i] instanceof Manager)
{
    Manager boss = (Manager) staff[i];
    boss.setBonus(5000);
}

// java16新增，检查通过直接声明并赋值变量
if(staff[i] instanceof Manager boss)
{
    boss.setBonus(5000);
}
```

#### 5.1.10 受保护访问

`protected`修饰的成员（字段或方法）可以被同一个包中的任何类访问，以及不同包中的子类访问。简单来说，就是在默认本包访问的基础上加上对子类开放访问权限。

1. 仅本类可以访问——private。
2. 可由外部访问——public。
3. 本包和所有子类可以访问——protected。
4. 本包中可以访问——默认，不需要修饰符。

不建议使用受保护字段，它将破坏封装，导致脆弱基类问题。永远把字段设为 private。 如果子类真的需要，提供 protected 的 getter/setter 方法。

建议使用受保护方法。它标志着“内部扩展点”。只允许受信的子类调用，外部类不允许随便调用。

### 5.2 Object：所有类的超类

Object类是Java所有类的始祖，每个类都扩展了Object，但并不需要显式声明。

#### 5.2.1 Object类型的变量

可以使用Object类型的变量引用任何类型的对象，作为一个泛型容器。具体操作时还是要进行相应的强制类型转换。

在Java中，只有**基本类型（primitive type）**不是对象，例如，数值、字符和布尔类型的值都不是对象。

所有的数组类型（不管是对象数组还是基本类型的数组）都扩展了Object类的类类型。

#### 5.2.2 equals方法

Object类中的equals方法用于检测一个对象是否等于另外一个对象。而Object类中实现的equals方法 只检测两个对象是否为同一个对象（引用相等）。要比较“值”是否相等（逻辑相等），需要子类自行重写 equals 方法。

#### 5.2.3 相等测试与继承

~~叽里呱啦说啥呢~~

Java语言规范要求equals方法具有下述性质。

1.自反性：对于任何非null引用x，x.equals(x)应该返回 true。
2.对称性：对于任何引用x和y。当且仅当y.equals(x)返回 true时，x.equals(y)返回 true。
3.传递性：对于任何引用x、y和z，如果x.equals(y)返回 true, y.equals(z)返回 true，则x.equals(z)也应该返回 true。
4.一致性：如果x和y引用的对象没有发生变化，则反复调用x.equals(y)应该返回同样的结果。
5.对于任意非null引用x，x.equals(null)应该返回 false。

- 如果子类可能有自己的相等性概念，则对称性需求强制使用getClass检测。
- 如果由超类决定相等性概念，那么可以使用instanceof检测，这样不同子类的对象也可能相等。

```java
@Override
public boolean equals(Object otherObject) { // 注意：参数必须是 Object，不能是 Employee！
    // 1. 自己跟自己比（性能优化）
    if (this == otherObject) return true;
    
    // 2. 防 null
    if (otherObject == null) return false;
    
    // 3. 关键抉择：类检测（此处以“严格模式”为例）
    if (getClass() != otherObject.getClass()) return false;
    
    // 4. 强制转换
    Employee other = (Employee) otherObject;
    
    // 5. 比较字段（使用 Objects.equals 防 null）
    return Objects.equals(name, other.name)
        && salary == other.salary
        && Objects.equals(hireDay, other.hireDay);
}
```

总结：日常开发中，99% 的普通 JavaBean（数据类）建议使用 getClass 严格模式；只有当明确所有子类都没有额外关键字段时，才考虑 instanceof。

#### 5.2.4 hashCode方法

**散列码（hash code）**是由对象导出的一个整型值。hashCode方法定义在Object类中，默认由对象的内容地址得出。

> 如果 x.equals(y) 返回 true，那么 x.hashCode() 必须等于 y.hashCode()。

所以，如果我们重写了equals方法，则必须同步重写hashCode方法。可以以调用Objects.hash并提供所有值作为参数。这个方法会对各个参数调用0bjects.hashCode,并组合这些散列值。

```java
public int hashcCode()
{
    return Objects.hash(name, salary, hireDay);
}
```

#### 5.2.5 toString方法

Object类有一个`toString`方法，默认为`类名@内存地址`，没有业务信息。所以我们基本都需要重写toString方法打印具体字段值，方便日志打印和调试。

```java
@Override
public String toString() {
    return getClass().getName() + "[name=" + name 
        + ",salary=" + salary 
        + ",hireDay=" + hireDay + "]";
}
```

对于数组和多维数组，则可以使用静态方法`Arrays.toString`和`Arrays.deepToString`。

```java
int[] luckyNumbers ={2,3,5,7,11,13};
String s= "" + luckyNumbers; // [I@1a46e30 前缀[I表示这是一个整型数组
s = Arrays.toString(luckyNumbers); // [2,3,5,7,11,13]
```

### 5.3 泛型数组列表

ArrayList类与数组类似，但在添加或删除元素时，它能够自动地调整容量，而不需要为此额外编写代码。

ArrayList是一个有**类型参数（type parameter）**的**泛型类（generic class）**。为了指定数组列表保存的元素对象的类型，需要用一对尖括号将类名括起来追加到ArrayList 后面，例如`ArrayList<Employee>`。

#### 5.3.1 声明数组列表

```java
// 标准写法
ArrayList<Employee> staff = new ArrayList<Employee>();

// 可以省略右边类型参数
ArrayList<Employees> staff = new ArrayList<>();

// Java10+，可以使用var简化
var staff= new ArrayList<Employee>();
```

使用`add`方法添加元素，`size`获取大小。

使用`ensureCapacity`方法设置容量，或者初始化时直接构造器传参。超出容量时会自动扩容，创建更大容量的数组并拷贝元素。所以已知大小的情况下预设容量可以减小开销。

确认数组大小不再改变后，可以使用`trimToSize`方法回收多余的存储空间。

```java
staff.add(new Employee("Harry Hacker",...));
staff.add(new Employee("Tony Tester",...));

staff.size();

staff.ensureCapacity(100);

ArrayList<Employee staff = new ArrayList<>(100);

staff.trimToSize(2);
```

> C++的vector模板重载了[]操作符以便于访问元素。由于Java没有操作符重载，
所以必须调用显式的方法。
> 对于赋值操作a=b，C++的vector是按值复制。Java的ArrayList则是让两个变量引用同一个数组列表。

#### 5.3.2 访问数组列表元素

ArrayList不能使用ArrayList\[i\]，只能通过get/set方法访问和修改元素。

```java
staff.set(i,harry);
Employee e = staff.get(i);
```

一种可行的方法是使用ArrayList添加元素，然后使用`toArray`方法转换成常规数组进行操作。

```java
var list = new ArrayList<X>();
while(...)
{ 
    X=...;
    list.add(x);
}

var a = new X[list.size()];
list.toArray(a);
```

可以在数组中间添加和删除元素，但会移动操作位置之后的所有元素，所以在数组过大时不推荐使用。

```java
int n = staff.size()/2;
staff.add(n, e);

Employee e = staff.remove(n);
```

可以使用`for each`循环遍历数组列表的内容：

```java
for(Employee e : staff)
    do something with e

// 等价于
for(int i=0; i< staff.size(); i++)
{
    Employee e = staff.get(i);
    do something with e
}
```

#### 5.3.3 类型化与原始数组列表的兼容性

介绍与无泛型的ArrayList（即Object类型）如何兼容，写新代码不用考虑。

### 5.4 对象包装器与自动装箱

所有的基本类型都有一个与之对应的类。通常，这些类称为包装器(wrapper)。

包装器类是不可变的，即一旦构造了包装器，就不允许更改包装在其中的值。同时，包装器类还是final,因此不能派生它们的子类。

数组的类型参数不允许是基本类型，这时就可以用到包装器类。

> 由于每个值分别包装在一个对象中，所以`ArrayList<Integer>`的效率远远低于`int[]`数组。因此，只有当程序员操作的方便性比执行效率更重要的时候，才会考虑对较小的集合使用这种构造。

可以直接向`ArrayList<Integer>`中添加int类型元素，int值会被自动转换为Integer类，这种转换称为**自动装箱（autoboxing）**。反过来，将一个Integer对象赋给一个int值时，将会**自动拆箱（unboxed）**。

```java
var list = new ArrayList<Integer>();

list.add(3);
// 等价于
list.add(Integer.valueof(3));

int n =list.get(i);
// 等价于
int n =list.get(i).intValue();
```

- 自动装箱和自动拆箱甚至也适用于算术表达式。但对于`==`，由于包装器是类，所以比较时将比较内存地址。
- 包装器类可能为null，自动拆箱就可能抛`NullPointerException`异常。
- 一个表达式中混用Interger和Double类型时，Interger将拆箱转换为double再装箱为Double。

```java
Integer a = 1000;
Integer b= 1000;
if(a==b)... // 可能为false

Integer n= null;
System。out.println(2*n); // throws NullPointerException

Integer n=1;
Double x= 2.0;
System.out.println(true?n:x); // prints 1.0
```

### 5.5 参数个数可变的方法

参数个数可变的方法有时也被称为**变参（varargs）方法**。 省略号`...`表明这个方法可以接收任意数量的对象

```java
public static double max(double... values){
    double largest = Double.NEGATIVE_INFINITY;
    for (double v:values) if (v> largest) largest = v;
    return largest;
}
```

### 5.6 抽象类

如果用`abstract`关键字声明方法，则这个方法只需声明不需要具体实现，这样的方法被称为**抽象方法**。包含抽象方法的类也必须用`abstract`声明为**抽象类**。除了抽象方法之外，抽象类还可以包含字段和具体方法。即使不含抽象方法，也可以将类声明抽象类。

抽象方法相当于子类中实现的具体方法的占位符。扩展一个抽象类时，可以有两种选择。一种是在子类中保留抽象类中的部分或所有抽象方法仍未定义，这样就必须将子类也标记为抽象类；另一种做法是定义全部方法，这样一来，子类就不再是抽象的。

抽象类不能实例化。可以创建一个抽象类的**对象变量（object variable）**,但是这样一个变量只能引用非抽象子类的对象。

```java
public abstract class Person
{
   public abstract String getDescription();
   private String name;

   public Person(String name) { this.name = name; }
   public String getName() { return name; }
}

var people = new Person[2];

// fill the people array with Student and Employee objects
people[0] = new Employee("Harry Hacker", 50000, 1989, 10, 1);
people[1] = new Student("Maria Morris", "computer science");

// print out names and descriptions of all Person objects
for (Person p : people)
    System.out.println(p.getName() + ", " + p.getDescription());

```

由于不可能构造抽象类Person的对象，所以变量p永远不会引用Person对象，而总是引用一个具体子类（如 Employee或Student）的对象。这些对象中都定义了getDescription方法。

如果省略Person超类中的抽象方法，而仅在Employee和Student子类中定义getDescription方法，就不能在变量p上调用getDescription方法了。编译器只允许调用在类中声明的方法。

### 5.7 枚举类

枚举类在定义时就创建好了对应的实例，不能构造新的对象，所以可以直接用`==`比较。

可以为枚举类添加构造器、方法和字段。枚举的构造器总是私有的，可以省略`private`修饰符。

所有的枚举类都是抽象类`Enum`的子类。其中`toString`方法可以返回枚举常量名。逆方法是`valueOf`。

每个枚举类型都有一个静态的`values`方法，它将返回一个包含全部枚举值的数组。

`ordinal`方法返回一个枚举常量在enum声明中的位置，位置从0开始计数。例

```java

public enum Size { SMALL, MEDIUM, LARGE, EXTRA_LARGE }

public enum Size{
    SMALL("S"),MEDIUM("M"),LARGE("L"),EXTRA_LARGE("XL");
    
    // automatically private
    Size(String abbreviation) { this.abbreviation = abbreviation; }
    public String getAbbreviation() { return abbreviation; }
    
    private String abbreviation;
}

String str = Size.SMALL.toString(); // "SMALL"
Size s= Enum.valueOf(Size.class,"SMALL"); // Size.SMALL
Size[] values = Size.values(); // [SMALL, MEDIUM, LARGE, EXTRA_LARGE]
int index = Size.MEDIUM.ordinal() // 1
```

### 5.8 密封类

可以通过`sealed`关键字将类声明为**密封类（sealed class）**。密封类可以控制哪些类可以继承它。

```java
public abstract sealed class JSONValue
    permits JSONArray,JSONNumber,JSONString,JSONBoolean,JSONObject,JSONNull
{
    ...
}
```

一个密封类允许的子类必须是可访问的。它们不能是嵌套在另一个类中的私有类，也不能是位于另一个包中的包可见的类。

密封类可以不加`permits`子句。这样一来，它的所有直接子类都必须在同一个文件中声明。

使用密封类的一个重要原因是编译时检查。

```java
public String type()
return switch(this)
{
    case JSONArray j->"array";
    case JSONNumber j->"number";
    case JSONString j->"string";
    case JSONBoolean j->"boolean";
    case JSONObject j->"object";
    case JSONNull j->"null";
    // No default needed here
    };
}
```

密封类的子类必须指定它是sealed、final，还是允许继续派生子类。对于最后一种情况，必须声明为non-sealed。

### 5.9 反射

**反射库（reflection library）**提供了一个丰富且精巧的工具集，可以用来编写动态操纵Java代码的程序。能够分析类能力的程序称为**可反射（reflective）**。可以用于：

- 在运行时分析类的能力。
- 在运行时检查对象，例如，编写一个适用于所有类的toString方法。
- 实现泛型数组操作代码。
- 利用Method 对象，这个对象很像C++中的函数指针。

TODO：暂略。

### 5.10 继承的设计技巧

1. 将公共操作和字段放在超类中。
2. 不要使用受保护的字段。
3. 使用继承实现“1s-a”关系。
4. 除非所有继承的方法都有意义，否则不要使用继承。
5. 覆盖方法时，不要改变预期的行为。
6. 使用多态，而不要使用类型信息。
7. 不要滥用反射。

## 第6章 接口、lambda表达式和内部类

学lambda表达式和方法引用，感觉Java就是被“一切皆对象”的教条困住了，函数始终只能作为二等公民，导致每次只能写一大堆样板代码去把需要的函数逻辑包装到类里面。又嫌弃这么写太麻烦，就生造一堆概念和语法糖去简化编程范式同时匹配旧有的对象逻辑。写法看上去现代多了但底层编译器还是那一套，和个`#define`差不多。

### 6.1 接口

#### 6.1.1 接口的概念

**接口（interface）**用来描述类应该做什么,而不指定它们具体应该如何做。一个类可以**实现（implement）**一个或多个接口。

```java
public interface Comparable<T>
{
    int compareTo(T other); // parameter has type T
}
```

任何实现Comparable接口的类都需要包含一个compareTo方法，接受一个Object参数，并返回一个整数。否
则，这个类也应当是抽象的，不能构造这个类的对象。调用x.compareTo(y)的时候，当x小于y时，返回一个负数；当x等于y时，返回0；否则返回一个正数。

为了让类实现一个接口，需要完成下面两个步骤：

1.将类声明为实现给定的接口。
2.对接口中的所有方法提供定义。

要声明一个类实现某个接口，需要使用关键字`implements`。

```java
public class Employee implements Comparable<Employee>
{
   private String name;
   private double salary;

   /**
    * Compares employees by salary
    * @param other another Employee object
    * @return a negative value if this employee has a lower salary than
    * otherObject, 0 if the salaries are the same, a positive value otherwise
    */
   public int compareTo(Employee other)
   {
      return Double.compare(salary, other.salary);
   }
}
```

#### 6.1.2 接口的属性

接口不是类。具体来说，不能使用new操作符实例化。但可以声明接口变量，引用实现了这个接口的类对象。

```java
x = new Comparable(...); // ERROR

Comparable x; // 0K

x = new Employee(...);// 0K provided Employee implements Comparable
```

和类的继承一样，接口也可以继承接口。接口不能包含实例字段，但可以包含常量。

```java
public interface Moveable
{
    void move(double x, double y);
}

public interface Powered extends Moveable
{
    double milesPerGallon();
    double SPEED_LINIT = 95; // a public static final constant
}
```

尽管每个类只能有一个超类，但可以实现多个接口。可以使用逗号将想要实现的各个接口分隔开。

```java
class Employee implements Cloneable, Comparable
```

接口可以是密封的（sealed）。与密封类一样，直接子类型（可以是类或接口）必须在permits子句中声明，或者要放在同一个源文件中。

#### 6.1.3 接口与抽象类

每个类只能扩展一个类，但每个类可以实现任意多个接口。Java刻意舍弃了*多重继承的复杂性*，才必须提供接口这种机制，让类在单继承的限制下，依然能拥有多种能力。

- 抽象类：适合定义“是什么”（is-a），并提供一些可以被子类复用的代码。
- 接口：适合定义“能做什么”（can-do），提供纯粹的行为契约。

Java 8 允许接口有 default 方法和 static 方法（接口也可以提供实现了）。这让接口在某些场景下像“轻量级的抽象类”。但接口依然不能有实例字段，所以它永远无法完全取代抽象类。

#### 6.1.4 静态和私有方法

在Java 8中，允许在接口中增加静态方法。这似乎有违于将接口作为抽象规范的初衷。通常的做法都是将静态方法放在伴随类中。如标准库中的Collection/Collections或Path/Paths。在Java 11中，Path接口提供了等价的方法，Paths类就不再是必要的了。

```java
public interface Path
{
    public static Path of(URI uri){...}
    public static Path of(String first, String⋯ more){...}
}
```

在Java 9中，接口中的方法可以是private方法。private方法可以是静态方法或实例方法。由于私有方法只能在接口本身的方法中使用，所以它们的用途很有限，只是作为接口中其他方法的辅助方法。

#### 6.1.5 默认方法

可以为任何接口方法提供一个*默认*实现，必须用`default`修饰符标记该方法。

```java
public interface Comparable<T>
{
    default int compareTo(T other){ return 0;}
    // by default, all elements are the same
}
```

比较常见的用法就是直接抛错该方法未实现。此外，默认方法也可以调用其他方法。这样就可以把公共逻辑提到上层，不需要在子类中重复实现。

```java
public interface Iterators{
    boolean hasNext();
    E next();
    default void remove(){ throw new UnsupportedoperationException("remove");}
    // 如果是只读迭代器，不需要实现remove方法。
}

public interface Collection
{
    int size();// an abstract method
    default boolean isEmpty(){ return size()==0;}
    // 不需要重复实现isEmpty方法。
}
```

默认方法的一个重要用法是**接口演化（interface evolution）**。当接口新增方法时实现为默认方法，避免未实现该方法的旧代码编译失败，保证**源代码兼容（source compatible）**。

#### 6.1.6 解决默认方法冲突

1. 超类优先。如果一个类的继承超类和实现接口有着相同方法，则会使用超类方法而忽略接口默认方法。
2. 接口冲突。如果一个类实现的多个接口有相同的方法，且其中至少一个为默认方法，则必须显式重写该方法来解决二义性避免冲突。

```java
interface Person
{
    default String getName() { return "";};
}

interface Named
{
    default String getName(){ return getClass().getName()+"_"+hashCode();}
    // String getName(); 
    // Person.getName是默认方法而Named.getName不是默认方法时，实现类也必须重写。
}

class Student implements Person, Named
{
    public String getName(){ return Person.super.getName();}
}
```

#### 6.1.7 接口与回调

**回调（callback）**是一种常见的程序设计模式。在这种模式中，可以指定某个特定事件发生时应该采取的动作。

```java
public interface ActionListener
{
    void actionPerformed(ActionEvent event);
}

class TimePrinter implements ActionListener
{
    public void actionPerformed(ActionEvent event)
    {
        System.out.println("At the tone, the time is"
            + Instant.ofEpochMilli(event.getWhen()));
        Toolkit.getDefaultToolkit().beep();
    }
}

var listener = new TimePrinter();
var timer = new Timer(1000, listener);
timer.start();
```

#### 6.1.8 Comparator接口

Arrays.sort可以排序对象数组，前提是对象类实现了Comparable接口，即实现了compareTo方法。

当是不方便直接修改compareTo方法时，可以传入一个**比较器（comparator）**作为参数，自定义比较方法。

```java
public interface Comparator<T>
{
    int compare(T first, T second);
}

class LengthComparator implements Comparator<String>
{
    public int compare(String first, String second)
    {
        return first.length() - second.length();
    }
}

var comp = new LengthComparator();
if(comp.compare(words[i],words[j])>0) ...

String[] friends ={"Peter","Paul","Mary" };
Arrays.sort(friends, new LengthComparator());
```

#### 6.1.9 对象克隆

```java
var original = new Employee("John Public",50000);
Employee copy = original;
Copy.raiseSalary(10); // oops-also changed original

mployee copy = original.clone();
copy.raiseSalary(10); // 0K--original unchanged
```

`clone`方法是Object的一个protected方法，将逐个字段进行拷贝。而对象字段的值为引用，对其拷贝会得到相同子对象的另一个引用。即默认的克隆操作是**浅拷贝**，并没有克隆对象中引用的其他对象。

果原对象和浅克隆对象共享的子对象是不可变的，那么这种共享就是安全的。即该子对象属于不可变类，或者器生命周期中不会被变更或引用。但通常子对象都是可变的，必须重新定义clone方法实现**深拷贝（deep copy）**，克隆所有子对象。

```java
public class Employee implements Cloneable
{
   private String name;
   private double salary;
   private Date hireDay;

   public Employee clone() throws CloneNotSupportedException
   {
      // call Object.clone()
      Employee cloned = (Employee) super.clone();

      // clone mutable fields
      cloned.hireDay = (Date) hireDay.clone();

      return cloned;
   }
}
```

所有数组类型都有一个公共的 clone方法，而不是受保护的。可以用这个方法建立一个新数组，包含原数组所有元素的副本。

```java
int[] luckyNumbers ={2,3,5,7,11,13};
int[] cloned = luckyNumbers.clone();
cloned[5] = 12; // doesn't change luckyNumbers[5]
```

### 6.2 lambda表达式

#### 6.2.1 为什么引入lambda表达式

lambda表达式是一个可传递的代码块，可以在以后执行一次或多次。Java是一种面向对象语言，所以必须构造一个对象，这个对象的类要有一个方法包含所需的代码。导致我们只需要某段逻辑时常常需要专门定义一个类去承接代码块。

```java
class Worker implements ActionListener
{
    public void actionPerformed(ActionEvent event)
    {
        // do some work
    }
}

class LengthComparator implements Comparator<String>
{
    public int compare(String first, String second)
    {
        return first.length()·second.Length(); 
    }
?
Arrays.sort(strings, new LengthComparator());
```

#### 6.2.2 lambda表达式的语法

lambda表达式就是一个代码块，以及必须传入代码的所有变量的规范。

- lambda表达式包括参数，箭头（->）以及一个表达式。
- 如果代码要完成的计算无法放在一个表达式中，就可以像写方法一样，把这些代码放在{}中，并包含显式的 return语句。
- 即使lambda表达式没有参数，仍然要提供空括号，就像无参数方法一样。
- 如果可以推导出一个lambda表达式的参数类型，则可以忽略其类型。
- 如果方法只有一个参数，而且这个参数的类型可以推导得出，那么甚至还可以省略小括号。
- 无须指定lambda表达式的返回类型。lambda表达式的返回类型总是会由上下文推导得出。
- 可以使用var指示一个推导的类型。这不常见。发明这个语法是为了关联注解。

```java
var planets = new String[] { "Mercury", "Venus", "Earth", "Mars", 
    "Jupiter", "Saturn", "Uranus", "Neptune" };
System.out.println(Arrays.toString(planets));
System.out.println("Sorted by length:");
Arrays.sort(planets, (first, second) -> first.length() - second.length());
System.out.println(Arrays.toString(planets));
    
var timer = new Timer(1000, event ->
    System.out.println("The time is " + new Date()));
timer.start();   
```

#### 6.2.3 函数式接口

对于只有一个抽象方法的接口，需要这种接口的对象时，就可以提供一个lambda表达式。这种接口称为**函数式接口（functional interface）**。

lambda表达式可以转换为接口。Java API在java.util.function包中定义了很多非常通用的函数式接口。其中一个接口`BiFunction<T,U,R>`描述了参数类型为T和U而且返回类型为R的函数。可以将对应参数的lambda表达式保存在这个类型的变量中。

```java
BiFunction<String,String,Integer> comp =
    (first, second) -> first.Length() - second.length();
```

不过Arrays.sort方法不接收接收一个BiFunction，所以不能直接用于排序。类似Comparator的接口往往有一个特定的用途，而不只是提供一个有指定参数和返回类型的方法。想要用lambda表达式做某些处理时，还是建议建立一个特定的函数式接口。

java.util.function包中有一个尤其有用的接口`Predicate`，这个接口专门用来传递lambda表达式。例如ArrayList类的removeIf方法：

```java
public interface Predicate<T>
{
    boolean test(T t);
    // additional default and static methods
}

list.removeIf(e -> e == null);
```

另一个有用的函数式接口是`Supplier<T>`，供应者（supplier）没有参数，调用时会生成一个T类型的值，用于实现**懒加载（lazy evaluation）**。

```java
public interface Supplier<T>
{
    T get();
}

// 无懒加载，必定创建新对象
LocaLDate hireDay = Objects.requireNonNullElse(day, LocalDate.of(1970,1,1));
// 有懒加载，仅当day为null是才走另一分支创建新对象
LocalDate hireDay = Objects.requireNonNulLElseGet(day, () -> LocalDate.of(1970,1,1));
```

#### 6.2.4 方法引用

有时lambda表达式涉及一个方法，期望直接传递该方法：

```java
var timer = new Timer(1000, event -> System.out.println(event));
var timer = new Timer(1000,System.out::println);
```

System.out::println是一个**方法引用（method reference）**，指示编译器生成一个函数式接口的实例，覆盖这个接口的抽象方法来调用给定的方法。

似于lambda表达式，方法引用也不是一个对象。不过，为一个类型为函数式接口的变量赋值时会生成一个对象。

方法引用要用`::`分隔方法名与对象或类名。

1. `object::instanceMethod`: 等价于lambda表达式。即`System.out::print`等价于`x->System.out::print(x)`。
2. `Class::instanceMethod`: 第一个参数会成为方法的隐式参数。即`String::compareToIgnoreCase`等价于`(x,y)->x.compareToIgnoreCase(y)`。
3. `Class::staticMethod`: 所有参数都传递到静态方法。即`Math::pow`等价于`(x,y)->Math.pow(x,y)`。

也可以使用在方法引用中使用this或super参数。

```java
this::instanceMethod
super::instanceMethod
```

#### 6.2.5 构造器引用

构造器引用与方法引用很类似，只不过方法名为new。使用哪个构造器取决于上下文传递的参数列表。

```java
ArrayList<String> names =...;
Stream<Person> stream = names.stream().map(Person::new); // Person(String)
List<Person> people = stream.toList();
```

可以用数组类型建立构造器引用，此时它的参数为数组长度。例如`int[]:new`等价于`x -> new int[x]`。

Java有一个限制：无法构造泛型类型T的数组。即`new T[n]`将创建为`new Object[n]`。通过stream.ToArray传入构造器引用就可以创建特定类型的数组。

```java
Person[] people = stream.toArray(Person[]::new);
```

#### 6.2.6 变量作用域

```java
public static void repeatMessage(String text, int delay)
{
    ActionListener listener = event ->
        {
            System.out.println(text);
            Toolkit.getDefaultToolkit().beep();
        };
    new Timer(delay, listener).start();
}

repeatMessage("Hello",1000);// prints Hello every 1,000 milliseconds
```

对于如上实例，lambda表达式包含一个外部变量delay，这样的变量被称为**自由变量**。

lambda表达式有3个部分：

1. 一个代码块；
2. 参数；
3. *自由变量*的值，这是指非参数而且不在代码中定义的变量。

关于代码块连同自由变量值有一个术语：**闭包（closure）**。在Java中，lambda表达式就是闭包。

Java的lambda表达式中捕获的变量必须是**事实最终变量（effectively final）**。事实最终变量是指，这个变量初始化之后就不会再为它赋新值。

```java
public static void countDown(int start, int delay)
{
    ActionListener listener = event ->
    {
        start--; // ERROR:Can't mutate captured variable
        System.out.println(start);
    };
    new Timer(delay,listener).start();
}

public static void repeat(String text, int count)
    for(int i=1;i<=count;i++)
    {
        ActionListener listener = event ->
        {
            System.out.println(i+":"+text);
            // ERROR:Cannot refer to changing i
        };
        new Timer(1000, listener).start();
    }
}
```

lambda表达式的与其所在的代码块有着**相同的作用域**。即声明与局部变量同名的参数或局部变量都不合法。

```java
Path first = Path.of("/usr/bin");
Comparator<String> comp =
(first, second)-> first.Length()-second.Length();
// ERROR:Variable first already defined
```

在一个lambda表达式中使用this关键字时，是指创建这个lambda表达式的方法的this参数。即创建lambda表达式的外围类对象。lambda表达式本身并不是一个匿名对象类没有this参数。

#### 6.2.7 处理lambda表达式

使用lambda表达式的重点是**延迟执行（deferred execution）**。例如如下场景：

- 在一个单独的线程中运行代码；
- 多次运行代码；
- 在算法的适当位置运行代码（例如，排序中的比较操作）;
- 发生某种情况时运行代码（如，点击了一个按钮，数据已经到达，等等）;
- 只在必要时才运行代码。

以重复运行代码为例：

```java
// no argument
public static void repeat(int n, Runnable action)
{
    for(int i=0;i<n; i++) action.run();
}

repeat(10,() -> System.out.println("Hello,World!"));

// int argument
public static void repeat(int n, IntConsumer action)
{
    for(int i=0; i<n; i++) action.accept(i);
}

repeat(10, i -> System.out.println("Countdown:"+(9-i)));
```

如上使用了Runnable和IntConsumer等函数式接口。更多常用的函数式接口如下表：

![表6-2 常用函数式接口](/post-images/《Java核心技术》阅读笔记/v1ch06_01.png)
![表6-2 常用函数式接口续](/post-images/《Java核心技术》阅读笔记/v1ch06_02.png)
![表6-3 基本类型的函数式接口](/post-images/《Java核心技术》阅读笔记/v1ch06_03.png)
![表6-2 常用函数式接口续](/post-images/《Java核心技术》阅读笔记/v1ch06_04.png)

在定义函数式接口时，可以使用`@functionalInterface`注解进行标记。这不是必须的，但可以让编译器帮你检查，同时更具有可读性。类似`@override`注解。

#### 6.2.8 再谈Comparator

Comparator接口包含很多方便的静态方法来创建比较器。这些方法可以用于lambda表达式或方法引用。

静态comparing方法接受一个“键提取器”函数，它将类型T映射为一个可比较的类型（如String）。对要比较的对象应用这个函数，然后对返回的键完成比较。

```java
Arrays.sort(people, Comparator.comparing(Person::getName));
```

可以把比较器与thenComparing方法串起来，来处理比较结果相同的情况。实现多级比较。

```java
Arrays.sort(people,
    Comparator.comparing(Person::getLastName)
    .thenComparing(Person::getFirstName));
```

以为comparing和 thenComparing方法提取的键指定一个比较器。

```java
Arrays.sort(people, Comparator.comparing(Person::getName,
    (s, t) -> Integer.compare(s.Length(),t.length())));
```

另外，comparing和 thenComparing方法都有变体形式，可以避免int、Long或double值的装箱。

```java
Arrays.sort(people, Comparator.comparingInt(p->p.getName().Length()));
```

如果键函数可能返回null,可能就要用到nullsFirst和nullsLast适配器。这些静态方法会修改现有的比较器，从而在遇到null值时不会抛出异常，而是将这个值标记为小于或大于正常值。

nullsFirst方法需要一个比较器，在这里就是比较两个字符串的比较器。natural0rder方法可以为任何实现了Comparable的类建立一个比较器。

静态reverseOrder方法会提供自然顺序的逆序。要让比较器逆序比较，可以使用reversed实例方法。例如 naturalOrder().reversed()等同于 reverseOrder()。

```java
Arrays.sort(people, Comparator.comparing(Person::getMiddleName,
    Comparator.nullsFirst(Comparator.naturalOrder())));
```

### 6.3 内部类

**内部类（inner class）**是定义在另一个类中的类。

- 内部类可以对同一个包中的其他类隐藏。
- 内部类方法可以访问定义这些方法的作用域中的数据，包括原本私有的数据。

相比c++的嵌套类，Java的内部类的对象会有一个隐式引用，指向实例化这个对象的外部类对象，不需要显式指针。

#### 6.3.1 使用内部类访问对象状态

一个内部类方法可以访问自身的实例字段，也可以访问创建它的外部类对象的实例字段。为此，内部类的对象总有一个隐式引用，指向创建它的外部类对象。

```java
public class TalkingClock
{
    private int interval;
    private boolean beep;
    public TalkingClock(int interval, boolean beep){...}
    public void start(){...}

    public class TimePrinter implements ActionListener
    {
        public void actionPerformed(ActionEvent event)
        {
            System.out.println("At the tone, the time is "
                + Instant.ofEpochMilli(event.getwhen()));
            if(beep)Toolkit.getDefaultToolkit().beep();
        }
    }
}
```

这个引用在内部类的定义中是不可见的。不过，为了说明这个概念，我们将外部类对象的引用称为outer。于是如上的`if(beep)`等价于`if(outer.beep)`。

外部类的引用在构造器中设置。编译器会修改所有的内部类构造器，添加一个对应外部类引用的参数。例如：

```java
public TimePrinter(TaLkingCLock clock) // automatically generated code
    outer = clock;
}
```

#### 6.3.2 内部类的特殊语法规则

上一节的outer正规语法为`OuterClass,this`，表示外部类引用；反过来，可以采用`outerObject.new InnerClass(construction parameters)`更加明确地编写内部类对象的构造器。

```java
public void actionPerformed(ActionEvent event)
{
    ...
    if (TalkingClock.this.beep) Toolkit.getDefaultToolkit().beep();
}

public void start()
{
    ActionListener listener = this.new TimePrinter();
    var timer = new Timer(interval, listener);
    timer.start();
}
```

外部类的作用域之外，可以通过`OuterClass.InnerClass`引用内部类。

#### 6.3.3 内部类是否有用、必要和安全

内部类将转换为常规的类文件，用$(美元符号)分隔外部类名与内部类名。例如`TalkingClock$TimePrinter.class`。

可以使用`javap`反编译查看内部类定义，需要用单引号包裹类名避免$被当作变量。

```java
// javap -p 'innerClass.TalkingClock$TimePrinter'
public class innerClass.TalkingClock$TimePrinter implements java.awt.event.ActionListener {
  final innerClass.TalkingClock this$0;
  public innerClass.TalkingClock$TimePrinter(innerClass.TalkingClock);
  public void actionPerformed(java.awt.event.ActionEvent);
}
```

可以看到编译器生成了一个额外的实例字段`this$0`对应外部类的引用。构造器也有一个外部类参数。

#### 6.3.4 局部内部类

在TalkingClock类中TimePrinter内部类只在start方法中创建这个类型的对象时使用了一次。类似这种情况可以在方法中*局部地*定义这个类。

```java
public void start()
{
    class TimePrinter implements ActionListener
    {
        public void actionPerformed(ActionEvent event)
        {
            System,out.println("At the tone, the time is"
                + Instant.ofEpochMilli(event.getWhen()));
            if (beep) Toolkit.getDefaultToolkit().beep();
        }
    }
    var listener = new TimePrinter();
    var timer = new Timer(interval, listener);
    timer.start();
}
```

声明局部类时不能有访问说明符（即public或private）。局部类的作用域总是限定在声明这个局部类的块中。

#### 6.3.5 由外部方法访问变量

局部类不仅能够访问外部类的字段，还可以访问局部变量。些局部变量必须是*事实最终*变量（effectively final）。

当局部内部类访问局部变量而非外部类字段时。局部变量生命周期结束后仍能正常访问该变量。通过反编译可以发现访问的并不是原变量而是在局部内部类内部创建的一份副本。这就是闭包的**变量捕获（Variable Capture）**机制。

```java
public void start(int interval, boolean beep) // 方法参数而不是外部类字段
{
    class TimePrinter implements ActionListener
    {
        public void actionPerformed(ActionEvent event)
        {
            System,out.println("At the tone, the time is"
                + Instant.ofEpochMilli(event.getWhen()));
            if (beep) Toolkit.getDefaultToolkit().beep();
        }
    }
    var listener = new TimePrinter();
    var timer = new Timer(interval, listener);
    timer.start();
}
```

```java
public class innerClass.TalkingClock$TimePrinter implements java.awt.event.ActionListener {
  final innerClass.TalkingClock this$0;
  final boolean val$beep;
  public innerClass.TalkingClock$TimePrinter(innerClass.TalkingClock);
  public void actionPerformed(java.awt.event.ActionEvent);
}
```

反编译可以看到，beep变量的值会拷贝存储在内部类的val$beep字段中。

#### 6.3.6 匿名内部类

```java
public void start(int interval, boolean beep)
{
    var listener = new ActionListener()
    {
        public void actionPerformed(ActionEvent event)
        {
            System.out.println("At the tone, the time is"
            + Instant.ofEpochMilli(event.getWhen()));
            if(beep) Toolkit.getDefaultToolkit().beep();
        }
    };
    var timer = new Timer(interval, listener);
    timer.start();
}
```

如上，当只需要这个类的一个对象时，可以不指定名字直接声明，这样的类被称为**匿名内部类（onymous inner class）**。

```java
new SuperType(construction parameters)
{
    // inner class methods and data
}
```

在这里，SuperType可以是接口，内部类要实现这个接口。SuperType也可以是一个类，内部类要扩展这个类。

由于构造器的名字必须与类名相同，而匿名内部类没有类名，所以匿名内部类不能有构造器。构造参数将传递给超类（superclass）构造器。匿名类不能有构造器，但可以提供一个对象初始化块。

```java
var queen = new Person("Mary");
// a Person object
var count = new Person("Dracula"){...};
// an object of an inner class extending Person

var count = new Person("Dracula")
{
    {initialization} // initialization block
};
```

#### 6.3.7 静态内部类

有时候，使用内部类只是为了把一个类隐藏在另外一个类的内部，并不需要内部类有外部类对象的一个引用。为此，可以将内部类声明为static，这样就不会生成那个引用。

```java
class ArrayAlg
{
   public static class Pair
   {
      private double first;
      private double second;

      public Pair(double f, double s)
      {
         first = f;
         second = s;
      }

      public double getFirst() {return first;}
      public double getSecond() {return second;}
   }

   public static Pair minmax(double[] values)
   {
      double min = Double.POSITIVE_INFINITY;
      double max = Double.NEGATIVE_INFINITY;
      for (double v : values)
      {
         if (min > v) min = v;
         if (max < v) max = v;
      }
      return new Pair(min, max);
   }
}

public class StaticInnerClassTest
{
   public static void main(String[] args)
   {
      var values = new double[20];
      for (int i = 0; i < values.length; i++)
         values[i] = 100 * Math.random();
      ArrayAlg.Pair p = ArrayAlg.minmax(values);
      System.out.println("min = " + p.getFirst());
      System.out.println("max = " + p.getSecond());
   }
}
```

一方面，使用内部类`ArrayAlg.Pair`相比直接定义一个`Pair`类更不容易混淆。另一方面，对于如上示例，由于Pair类在静态方法中使用，所以必须声明为静态类，否则编译器将报错没有可用的ArrayAlg类型隐式对象来初始化内部类对象。

态内部类可以有静态字段和方法。接口中声明的内部类自动是static和public。声明的接口、记录和枚举都自动为static。

### 6.4 服务加载器

TODO 不是很懂，先略过。

### 6.5 代理

TODO 不是很懂，先略过。

## 总结

（未待完续）
