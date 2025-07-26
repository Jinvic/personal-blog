set shell := ["powershell.exe", "-c"]

year:="2025"

build:
    hugo

test:
    hugo server --disableFastRender

test2:
    hugo server --disableFastRender -D

# 创建新文章
# e.g. just new example
new postname:
    hugo new content/posts/{{year}}/{{postname}}.md