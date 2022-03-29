# flags (v0.1)
一个简易的帮助用户更好的规范化脚本输入输出,工具串接,日志输出等

[english](README_EN.md)

## 特性

* 单脚本 使用方便
* python3 support
* 简单易用
* 主要围绕AI领域的一些训练脚本

## 背景

现如今， python已经成为最流行的胶水语言脚本。AI领域更是如此。

在你的公司，你是否遇到过一些难以启齿、维护的py脚本？

相信你的回答一定是 yes.

Python 提供给我们很多标准库，但是我们没有很好的运用他，所以flags更进一步，帮助用户进一步不需要关注一些冗余配置，让研究员更好的研究算法，产出高效稳定的脚本...

## 开始

* 如何安装

初期暂时只需要复制flags.py[没错就1个文件!] 到你本地脚本目录即可应用，暂时只支持py3

* 未来支持pypi分发，pip直接安装


## 设计

Based on the argparse, we want to standardize scripts Input/Output Parameters format, such as env paramiters format, file location parameters format, logging format, logging level format ,workspace location,

flags主要基于argparse 等标准库。为二次封装的一个简易库，使用时导入即可。

主要为解决我们在ai领域中，常见场景如 数据准备，数据处理，训练，推理，仿真等阶段的各种场景脚本编写，对于不同python程度的研究员开发者，

通过flags库来约束 基本的输入输出，工具调用，日志展示，错误码输出等，将为AI更好地工程化提前铺平道路。

flags让研究员开发者更加专注脚本核心逻辑，以及算法研发，对于周边的这些库规范，只要使用flags相当于大家遵守同一个脚本输入输出规范原则。

当前flags中功能还比较少，欢迎更多AI领域人士参与共建!  欢迎在本github [讨论区](https://github.com/xfyun/flags/discussions/new)发起讨论。




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
README_EN.md
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

### flags错误码装饰器设计&如何使用

定义了exitWithCode装饰器

```python

class GenericException(Exception):
    def __init__(self, message, retcode):
        super().__init__(message, retcode)
        self.message = message
        self.retcode = retcode

# 定义 错误退出错误码装饰器
def exitWithCode(fn):
    def wrapper(self, *args):
        try:
            fn(self, *args)
        except GenericException as e:
            err_info = str(traceback.format_exc())
            print(err_info)
            with open("./ret","w") as r:
                r.write(str(e.retcode)+"\n")
                r.close()

            # 执行错误执行退出码统一-1
            sys.exit(-1)
    return wrapper
```

其中flags定义了一个自定义错误类 GenericException，这段装饰器代码主要用于在用户觉得可能出异常的函数上装饰下，当函数中抛出用户的自定义异常，则该装饰器就会打印堆栈，并且退出程序，并且保存错误码到ret文件

flags库自身就有实际案例使用:

```python
    @exitWithCode
    def add_tool(self, tool: BinTool):
        # 添加tool到全局 tools实例中去
        if tool.name in self.tools:
            logger.info("the tool %s has already been registered" % tool.name)
        else:
            if self.checkTool(tool):
                self.tools[tool.name] = tool
                print("# The tool: {name} located at {location} for {usage} has been registered!!!".format(
                    name=tool.name, location=tool.location, usage=tool.usage))
            else:
                print("## The tool: {name}  has not been registered!!!".format(
                    name=tool.name))
                logger.error("shutdowning!!")
                raise GenericException("shutdowning", StatusCodeEnum.ERROR.value[0])
```

如这一段: 注册tool工具时，如果检查该工具不存在， 则抛出异常信息， exitWithCode自动捕获该异常并退出用户指定的错误码，错误码为整型即可。
实际效果如上节所述。



