set shell := ["powershell.exe", "-c"]

year:="2026"

build:
    hugo

serve:
    hugo server --disableFastRender

served:
    hugo server --disableFastRender -D

# 创建新文章
# e.g. just new example
new postname:
    hugo new content/posts/{{year}}/{{postname}}.md