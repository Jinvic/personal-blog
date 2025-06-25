---
title: 基于python爬虫的arcptt计算器【备份留档】
date: '2023-06-05T23:24:24+08:00'
tags:
- Python
- 存档
categories:
- 开发
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

---

# 备份留档

**注意：** 以下内容为早期边学边做的记录，已过时，仅作备份留档用。
项目最新进度可以查看 **[GUI项目地址](https://github.com/Jinvic/arc_pttcul/tree/main/GUI_PySide6)**

---

# 前言

arcaea在一次更新后删减了api的返回数据，所以各种查分bot都用不了，查分被做成了付费功能。。，约14RMB一个月。玩家直接倒退回excel时代手算ptt。虽然excel写好函数后也还算方便了，没必要写个计算器套壳。但我想学习了解一下**python爬虫**和**Qtpy**这些，就从这个点入手了。做自己感兴趣的题材学起来也没那么枯燥。
**[CLI项目地址（不再维护）](https://github.com/Jinvic/arc_pttcul)**
**[GUI项目地址](https://github.com/Jinvic/arc_pttcul/tree/main/GUI_PySide6)**

---

# 爬取网页

因为没打算深入学习，只想快点搞个成品出来，所以各项原理只是简单过了遍，没有深入学习，像是查字典一样去找自己需要的部分。

参考书籍为：**Python3网络爬虫开发实战 第二版**
<br>
先是用的`urllib.request.urlopen`，返回一个response，print时没什么问题，存文件就会报错：`UnicodeEncodeError`，python的编码问题不是很懂，先略过。
<br>
往后翻了翻，使用`requests.get`，这次报错`requests.exceptions.SSLError`。查一下，加个`verify=False`来避免ssl认证。再跑，报错`requests.exceptions.ProxyError`，再查，代理的问题。因为我随时上谷歌和github page，代理是一直挂着的。关了代理，verify=False也删掉，再跑，终于好了：

```Python
import requests

# 获取网页
url = 'https://wiki.arcaea.cn/%E5%AE%9A%E6%95%B0%E8%AF%A6%E8%A1%A8'  # 定数详表页面
response = requests.get(url)
with open('website.html', mode='wb') as html_file:
    html_file.write(response.text)
```

emm其实爬虫的部分可以到此为止了，接下来就是数据的提取和处理。不过这样未免过于虎头蛇尾，再往后看看有什么用得上的。

---

# 解析提取数据

书上提供了XPath，Beautiful Soup、pyquery等几种库，看得我眼花缭乱。最后选择了pyquery库，它用的选择器和CSS是一样的。之前做移动终端编程也了解过一点jquery。想到这个我就有满满的槽要吐，这个有空再聊。
<br>
想从之前保存的网页中读，又报错了：`UnicodeDecodeError`。还是字符问题，有空再把python的字符整明白。这里url比较简单，不需要加什么参数，就不用request库直接用pyquery访问了：

```Python
from pyquery import PyQuery as pq

target_url = 'https://wiki.arcaea.cn/%E5%AE%9A%E6%95%B0%E8%AF%A6%E8%A1%A8'  # 定数详表页面
doc = pq(url=target_url)
chart_constant_table = doc('tbody')  # 定数表
print(chart_constant_table('th').text())
for item in chart_constant_table('tr').items():
    print(item('td').text())
```

定数表拿到了，接下来的问题就是用什么样的数据结构存这张表。

---

# 定数表存储

比较让人恼火的一点是，这些曲目似乎并没有一个统一的编号。arcaea中文维基只是简单粗暴的用曲名作为表示符。这样增删改查感觉都不怎么方便。我也懒得折腾就这样吧。
<br>
使用csv库来存储定数表，又报错了：`UnicodeEncodeError`。看看存了一半的csv，原来是Löschen中的ö是德文字符，默认gbk字符集写入没有这个字符。之前的报错应该也都是这个原因。加个`encoding='utf-8'`，问题解决。

```Python
from pyquery import PyQuery as pq
import csv

target_url = 'https://wiki.arcaea.cn/%E5%AE%9A%E6%95%B0%E8%AF%A6%E8%A1%A8'  # 定数详表页面
doc = pq(url=target_url)
chart_constant_table = doc('tbody')  # 定数表
# print(list(chart_constant_table('th').text().split(' ')))

with open('chart_constant_table.csv', 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for item in chart_constant_table('tr').items():
        print(item.text().split('\n'))
        writer.writerow(item.text().split('\n'))
```

---

# 定数表查询

正常写个遍历查询。考虑了一下要不要用pandas库，因为csv表很小就三百来行，也不需要什么高级的数据分析处理就算了。
本来是`{head[i]}:{row[i]}`这样输出，感觉看起来不是很方便就改成类似表格的格式输出了。求取曲名列最大长度后用`ljust`对齐。

```Python
import csv

def CCT_search(st):
    # 读取csv并查询
    with open('chart_constant_table.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        head = next(reader)
        res = []
        for row in reader:
            if(row[0].upper().find(st.upper()) != -1):
                res.append(row)

        # 寻找曲名的最大宽度
        max_width = max([len(str(row[0])) for row in res])
        max_widths = [5, max_width, 5, 5, 5, 5]  # 编号和定数列宽度固定
        # print(max_widths)

        if(len(res) == 0):
            print('未查找到结果，请重新查找')
        else:

            # 输出表头
            head = ['编号']+head
            formatted_row = ''
            for i in range(len(head)):
                if(i < 2):  # 前两列为中文，宽度短一点不然对不齐
                    formatted_row += str(head[i]).ljust(max_widths[i])
                else:
                    formatted_row += str(head[i]).ljust(max_widths[i] + 2)
            print(formatted_row)

            # 输出定数表
            idx = 0
            for row in res:
                # print(f'', end=' ')
                row = [idx]+row
                formatted_row = ''
                for i in range(len(row)):
                    # print(f'{head[i]}:{row[i]}', end=' ')
                    formatted_row += str(row[i]).ljust(max_widths[i] + 2)
                print(formatted_row)
                idx += 1

        return res
```

这只是查曲名用的，大小写不敏感。给查询结果编号输出，用户通过编号选择对应曲目。以查询`red`为例，输出如下：

```text
编号   曲目                            PST    PRS    FTR    BYD    
0      Redolent Shape                  4.5    7.5    10.2
1      Hybris (The one who shattered)  4.5    7.5    9.8
2      Red and Blue                    4.0    7.5    9.4    10.0
3      Redraw the Colorless World      4.0    6.5    9.2
```

---

# 玩家成绩存储和更新

我打算另建一张用户数据表来存储玩家玩了哪些曲目，以及对应的成绩和潜力值。
最开始用户数据表是空的。玩家每次玩了新歌，录入成绩时需要从定数表中拿曲名和定数出来，再结合成绩计算潜力值存入用户数据表，表头为`曲名 难度 定数 成绩 潜力值`。之后推了更高的分，就直接在用户数据表里面更新。添加成绩代码如下：

```Python
import csv
from CCT_search import CCT_search
from ptt_culculation import ptt_cul


# 从定数表添加新行
def UDT_add():
    print('请输入关键词以查找曲目')
    st = input()

    res = CCT_search(st)
    if(len(res) == 0):
        return

    input_check = False
    while input_check == False:
        print("选择添加的曲目，输入编号")
        idx = int(input())
        if(idx >= len(res) or idx < 0):
            print("编号不合法")
        else:
            input_check = True

    input_check = False
    while input_check == False:
        print("选择难度[pst|prs|ftr|byd]")
        difficults = ['PST', 'PRS', 'FTR', 'BYD']
        difficult = input()
        dif_id = -1
        for i in range(4):
            if(difficults[i].upper() == difficult.upper()):
                dif_id = i
                break
        if(dif_id == -1):
            print('难度输入错误')
        else:
            input_check = True

    print("输入成绩")
    score = int(input())

    # 曲名 难度 定数 成绩 潜力值
    new_row = [res[idx][0],
               difficults[dif_id],
               res[idx][dif_id+1],
               score,
               ptt_cul(float(res[idx][dif_id+1]), score)]
    print(new_row)

    # 写入用户数据表
    with open('user_data_table.csv', 'a', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(new_row)

     UDT_sort()
```

更新成绩代码如下，查找部分和之前`CCT_search()`差不多，感觉一直打表和查找代码重复度太高了，有空再优化吧。

```Python
def UDT_update():
    print('请输入关键词以查找曲目')
    st = input()

    # 在用户数据表搜索
    with open('user_data_table.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
        res = []
        dic = {}  # 存查找结果到原表行数的映射
        row_no = 0  # 原表行数
        idx = 0  # 结果编号
        for row in rows:
            if(row[0].upper().find(st.upper()) != -1):
                res.append([idx]+row)
                dic[idx] = row_no
                idx += 1
            row_no += 1
        if(len(res) == 0):
            print('未查找到结果，请重新查找')
            return

    # 寻找曲名的最大宽度
    max_width = max([len(str(row[1])) for row in res])
    max_widths = [5, max_width, 5, 5, 10, 10]
    head = ['编号', '曲名', '难度', '定数', '成绩', '潜力值']
    head_widths = [3, max_width, 3, 3, 8, 7]

    # 输出表头
    formatted_row = ''
    for i in range(len(head)):
        formatted_row += str(head[i]).ljust(head_widths[i] + 2)
    print(formatted_row)

    # 输出用户数据表
    for row in res:
        formatted_row = ''
        for i in range(len(row)):
            formatted_row += str(row[i]).ljust(max_widths[i] + 2)
        print(formatted_row)

    input_check = False
    while input_check == False:
        print("选择修改的曲目，输入编号")
        idx = int(input())
        if(idx >= len(res) or idx < 0):
            print("编号不合法")
        else:
            input_check = True

    print('输入更新后的成绩')
    score = int(input())
    rows[dic[idx]][3] = score
    rows[dic[idx]][4] = ptt_cul(
        float(rows[dic[idx]][2]), rows[dic[idx]][3])

    with open('user_data_table.csv', 'w', encoding='utf-8', newline='') as new_csvfile:
        writer = csv.writer(new_csvfile)
        writer.writerows(rows)

    UDT_sort()
```

写个排序函数,每次更改用户数据表后排序。

```Python
def UDT_sort():
    with open('user_data_table.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]

    sorted_rows = sorted(rows, key=lambda x: float(x[4]), reverse=True)

    with open('user_data_table.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sorted_rows)
```

---

# b30和r10计算

每次计算b30前使用`UDT_sort()`排序。如果成绩大于30项，只取前30项。
单曲ptt和r10都有公式算。
一起的代码如下：

```Python
import csv


def ptt_cul(cc, score):
    if(score > 10000000):
        return cc+2
    elif(score >= 9800000):
        return cc+1+(score-9800000)/200000
    else:
        return max(cc+(score-9500000)/300000, 0)


def b30_cul():

    with open('user_data_table.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        cnt = 0
        sum = 0
        for row in reader:
            sum += float(row[4])
            cnt += 1
            if(cnt == 30):
                break
        return sum/30


def r10_cul(b30, ptt):
    return (ptt*40-b30*30)/10
```

---

# 命令行界面和打包

做个简单的命令行界面看能不能用。

```Python
from spider import CCT_update
from user_data_edit import UDT_add, UDT_list, UDT_update
from ptt_culculation import b30_cul, r10_cul


def main():
    print('选择你要进行的操作：')
    print('1. 更新定数表')
    print('2. 列出用户成绩')
    print('3. 添加新成绩')
    print('4. 更新现有成绩')
    print('5. 计算b30')
    print('6. 计算r10')

    input_check = False
    while input_check == False:
        idx = int(input())
        if(idx > 6 or idx <= 0):
            print("编号不合法")
        else:
            input_check = True

    if(idx == 1):
        CCT_update()
    elif(idx == 2):
        UDT_list()
    elif(idx == 3):
        UDT_add()
    elif(idx == 4):
        UDT_update()
    elif(idx == 5):
        print(b30_cul())
    else:
        print('输入你现在的ptt')
        ptt = input()
        print(r10_cul(b30_cul(), float(ptt)))


if __name__ == '__main__':
    while(True):
        print()
        main()

```

安装`PyInstaller`，使用`Pyinstaller -F main.py`命令进行单文件打包。
初次使用需要先生成两个表格。启动程序，先使用`1. 更新定数表`命令生成定数表。再使用`3. 添加新成绩`命令生成用户数据表。也可以自己导入用户数据，方法见上。

---

# Qtpy图形化界面

~~诶，还没做呢。CLI能用懒得做GUI了，有生之年系列。~~
开始做了。懒得贴代码了，去github看吧。这里记一下进度。
**[项目地址](https://github.com/Jinvic/arc_pttcul/tree/main/GUI_PySide6)**
<br>
23-06-12 0:17
GUI使用`Pyside6`开发，先搭一个架子。

- 整合了CCT查询和UDT查询。表格显示使用`TableView`空间，不再手动格式化。
- 给UDT加了个表头，使CCT和UDT的搜索通用。

<br>
23-06-13 3:16

- 把各个文件整合为单文件。
- 添加了爬取定数表失败的异常处理。
- 使用`QInputDialog`进行参数输入。控件自带的输入限制省去了手写异常处理的工作量。
- **完成了GUI的开发。**

（居然两天就做完了，还以为会拖很久）
