# flags
一个简易的帮助你更好的规范化脚本输入输出,工具串接等

[english](README.md)

## 特性

* 单脚本 使用方便
* python3 support
* 简单易用
* 主要围绕AI领域的一些训练脚本

## Background

Now days, python is the most popular script language . In your company , Do you have seen various scripts that have not a standard format?

I think everybody will reply yes.

Python provide us some useful libs such as argparse...

## GetStarted

TODO

## 设计

Based on the argparse, we want to standardize scripts Input/Output Parameters format, such as env paramiters format, file location parameters format, logging format, logging level format ,workspace location,


### 通过flags 快速度定义Input/Output Paramters 
 
定义格式为主要是2个数组 ，每个数组的1个元素为一个6元素元组
分别对应: (name, type, default, choices, desc, required)
其中 choices为可选值， desc为描述该参数意义， required代表该参数是否可选


```python
import flags

IN = [
    ("step", str, "compose", ["compose", "transform"], "", True),
    ("source_path", str, "", [], "", True),
    ("male", int, 0, [], "男性", True),
    ("female", int, 0, [], "女性", True),
]
OUT = [
    ("dest_path", str, "", [], "", True),
]

flags.registerArgs(IN, OUT)
flags.parse()

```
运行该脚本:

```bash
error: the following arguments are required: --step, --source_path, --male, --female, --dest_path
usage: demo_args.py [-h] --step {compose,transform} --source_path SOURCE_PATH
                    --male MALE --female FEMALE --dest_path DEST_PATH

optional arguments:
  -h, --help            show this help message and exit
  --step {compose,transform}
  --source_path SOURCE_PATH
  --male MALE           男性
  --female FEMALE       女性
  --dest_path DEST_PATH
```

### 通过flags注册二进制程序，规范二进制调用逻辑
```python
import flags

flags.registerTool(name="ls", usage='listfiles ', logs_dir=None, location="/bin/ls")

flags.executeTool("ls",".")

```
程序输出:

```bash
# The tool: ls located at /bin/ls for listfiles  has been registered!!!
Tue, 29 Mar 2022 14:31:04 flags.py[line:45] INFO ('/Users/yangyanbo/projects/iflytek/code/flags',)
Tue, 29 Mar 2022 14:31:04 flags.py[line:45] INFO ('Executing Shell Cmd: /bin/ls .',)
LICENSE
README.md
README_CN.md
__pycache__
demo_args.py
demo_tools.py
flags.py
ret
test.py
Tue, 29 Mar 2022 14:31:04 flags.py[line:45] INFO ('Cmd: /bin/ls ., return: 0',)
```


### 通过flags错误码装饰器，统一退出错误码，并打印堆栈信息

***注意由于程序进程退出状态码取值有限，为了使用用户定义的错误码，程序退出时，将错误码记录在当前目录ret文件中***

模拟一个错误，/bin/lss 程序不存在，程序应该报错并退出

```python
import flags

# 模拟错误 /bin/lsss 不存在
flags.registerTool(name="ls", usage='listfiles ', logs_dir=None, location="/bin/lsss")

flags.executeTool("ls",".")
```

程序输出:

```bash
Tue, 29 Mar 2022 14:33:50 flags.py[line:53] ERROR ('the tool ls has not been found!',)
## The tool: ls  has not been registered!!!
Tue, 29 Mar 2022 14:33:50 flags.py[line:53] ERROR ('shutdowning!!',)
Traceback (most recent call last):
  File "/Users/yangyanbo/projects/iflytek/code/flags/flags.py", line 162, in wrapper
    fn(self, *args)
  File "/Users/yangyanbo/projects/iflytek/code/flags/flags.py", line 224, in add_tool
    raise GenericException("shutdowning", StatusCodeEnum.ERROR.value[0])
flags.GenericException: ('shutdowning', 10001)
```
返回码:

```bash
$ cat ret 
10001
```





