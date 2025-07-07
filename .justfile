set shell := ["powershell.exe", "-c"]

build:
    hugo

test:
    hugo server --disableFastRender

test2:
    hugo server --disableFastRender -D