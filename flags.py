#!/usr/bin/env python
# coding:utf-8
"""
@author: nivic ybyang7
@license: Apache Licence
@file: flags.py
@time: 2022/03/28
@contact: ybyang7@iflytek.com
@site:
@software: PyCharm

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
"""

import os
import sys
import argparse
import logging
import logging.handlers
import subprocess
import traceback
from enum import Enum

logger = logging.getLogger('logger')

parsed_args = None

flags_ret_status_location = "/var/run"


def setup_logger():
    # based on https://docs.python.org/3/howto/logging-cookbook.html#multiple-handlers-and-formatters
    # Todo support more logging method here
    global logger
    fmt = logging.Formatter(
        "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s", datefmt="%a, %d %b %Y %H:%M:%S")
    stdout_hd = logging.StreamHandler(sys.stdout)
    stdout_hd.setFormatter(fmt)
    logger.addHandler(stdout_hd)

    stdout_err = logging.StreamHandler(sys.stderr)
    stdout_err.setFormatter(fmt)
    # logger.addHandler(stdout_err)

    logger.setLevel(logging.INFO)


def setLogLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)
    elif level == "WARN":
        logger.setLevel(logging.WARN)
    else:
        logger.setLevel(logging.INFO)


def setup_ret_locate(path=flags_ret_status_location):
    if not os.path.isdir(path):
        os.makedirs(path, True)
    else:
        global flags_ret_status_location
        flags_ret_status_location = path


setup_logger()

setup_ret_locate()


# 定义参数基类

class Args(object):
    """Args 基类"""
    required: bool
    desc: str
    choices: list
    typ: type
    name: str
    default: None

    def __init__(self, *args):
        self.name, self.typ, self.default, self.choices, self.desc, self.required = args
        logger.debug("Args Input: %s" % self.name)


class HPArgs(object):
    """ AI训练中常见 hyper parameters """

    def __init__(self):
        batch_size = 3
        lr = 0.1
        epoch = 20


class Parser(argparse.ArgumentParser):
    # custom parser for give helo when no arguments
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class Flags(object):
    def __init__(self):
        self.args = Parser()
        self.input_args = []
        self.output_args = []
        self.bin_tools = []

    def register(self, input: Args, output: Args):
        if input:
            self.input_args.append(input)
        if output:
            self.output_args.append(output)

    def initflags(self):
        for ia in self.input_args:
            # trick here 如果第三个参数是 bool值 并且，第二个参数不为类型， 为True or False，则True代表 store_true False 代表store_false
            if isinstance(ia.default, bool):
                if isinstance(ia.typ, type):
                    self.args.add_argument("--" + ia.name, type=ia.typ, default=ia.default, required=ia.required,
                                           choices=ia.choices if ia.choices else None, help=ia.desc)
                elif isinstance(ia.typ, bool) and ia.typ == True:
                    action = "store_true"
                    self.args.add_argument("--" + ia.name, action=action, default=ia.default, required=ia.required,
                                           help=ia.desc)
                elif isinstance(ia.typ, bool) and ia.typ == False:
                    action = "store_false"
                    self.args.add_argument("--" + ia.name, action=action, default=ia.default, required=ia.required,
                                           help=ia.desc)
                else:
                    logger.error("no support this second element..")
            else:
                self.args.add_argument("--" + ia.name, type=ia.typ, default=ia.default, required=ia.required,
                                       choices=ia.choices if ia.choices else None, help=ia.desc)
        for oa in self.output_args:
            if isinstance(oa.default, bool):
                if isinstance(oa.typ, type):
                    self.args.add_argument("--" + oa.name, type=oa.typ, default=oa.default, required=oa.required,
                                           choices=oa.choices if oa.choices else None, help=oa.desc)
                elif isinstance(oa.typ, bool) and oa.typ == True:
                    action = "store_true"
                    self.args.add_argument("--" + oa.name, action=action, default=oa.default, required=oa.required,
                                           help=oa.desc)
                elif isinstance(oa.typ, bool) and oa.typ == False:
                    action = "store_false"
                    self.args.add_argument("--" + oa.name, action=action, default=oa.default, required=oa.required,
                                           help=oa.desc)
                else:
                    logger.error("no support this second element..")
            else:
                self.args.add_argument("--" + oa.name, type=oa.typ, default=oa.default, required=oa.required,
                                       choices=oa.choices if oa.choices else None, help=oa.desc)


# 定义 返回工作空间装饰器
def back_origin_workspace(fn):
    def inner(self, *args):
        cwd = os.getcwd()
        path = self.__dict__.get("workspace")
        if path:
            logger.info("entering: %s" % path)
            os.chdir(path)
        ret = fn(self, *args)
        if path:
            logger.info("backing: %s" % cwd)
            os.chdir(cwd)
        return ret

    return inner


#
class StatusCodeEnum(Enum):

    def __str__(self):
        return str(self.value[0])

    def __int__(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]

    @property
    def code(self):
        return self.value[0]


class FlagsErrorCodeEnum(StatusCodeEnum):
    """引用本库状态码枚举类"""
    OK = (0, '成功')
    ERROR = (-1, '错误')
    SERVER_ERR = (500, '服务器异常')


class GenericException(Exception):
    def __init__(self, message, retcode):
        super().__init__(message, retcode)
        self.message = message
        if isinstance(retcode, StatusCodeEnum):
            self.retcode = retcode.value[0]
        else:
            self.retcode = retcode


# 定义logger

def log_helper(fn):
    def wrapper(self, *args):
        logger.info("Start running %s" % fn.__name__)
        ret = fn(self, *args)
        logger.info("End: run  %s" % fn.__name__)
        return ret

    return wrapper


# 定义 错误退出错误码装饰器
def exitWithCode(fn):
    def wrapper(self, *args):
        retfile = os.path.join(flags_ret_status_location, "ret")
        try:
            ret = fn(self, *args)
            return ret
        except GenericException as e:
            err_info = str(traceback.format_exc())
            print(err_info)
            with open(retfile, "w") as r:
                r.write(str(e.retcode) + "\n")
                r.close()

            # 执行错误执行退出码统一-1
            sys.exit(-1)
        except Exception as e:
            # 此异常未用户未预见异常
            err_info = str(traceback.format_exc())
            print(err_info)
            with open(retfile, "w") as r:
                r.write(str(FlagsErrorCodeEnum.ERROR) + "\n")
                r.close()
            # 执行错误执行退出码统一-1
            sys.exit(-1)

    return wrapper


class BinTool(object):
    ## 专门执行二进制工具处理的类
    def __init__(self, name, location, usage, workspace=None, env_path=None, logs_dir=None, ld_library_path=None,
                 env_dict={}):
        # todo 校验 name必须英文
        self.name = name
        self.location = location
        self.usage = usage
        self.workspace = workspace if workspace else os.getcwd()
        self.env_path = env_path
        self.logs_dir = logs_dir
        # todo 校验location 存在性并提示

        # init ld
        if ld_library_path:
            self.initLD(ld_library_path)

        if env_dict:
            for k, v in env_dict.items():
                logger.info("registering env: %s " % k)
            os.putenv(k, v)

        self.workspace = workspace
        pass

    def initLD(self, ldpath):
        os.putenv("LD_LIBRARY_PATH", "$LD_LIBRARY_PATH:%s" % ldpath)
        logger.info("registed LD_LIBRARY_PATH: %s " % ldpath)

    # 单次执行
    @back_origin_workspace
    def execute_once(self, cmd):
        logger.info(os.getcwd())
        if self.workspace != None and os.path.isdir(self.workspace):
            os.chdir(self.workspace)

        logger.info("Executing Shell Cmd: %s" % cmd)
        ret = subprocess.call(cmd, shell=True)
        logger.info("Cmd: %s, return: %s" % (cmd, str(ret)))

        if ret != 0:
            logger.error("cmd: %s execute Error!" % cmd)
        return ret

    # 多进程执行
    def execute_mp(self, *args):
        pass


class Tools(object):
    def __init__(self):
        self.tools = {}
        self.init_python()

    def init_python(self):
        py = BinTool("python", sys.executable, "executing")
        self.add_tool(py)

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
                raise GenericException("shutdowning", FlagsErrorCodeEnum.ERROR)

    def checkTool(self, tool):
        binpath = tool.location
        # 如果tool存在特定的工作空间, 则校验该工作空间和location join的存在必要性
        # todo 这里存疑 当前只能代表必须使用 ./xxx 执行的case
        # 最好都指定绝对路径
        # 然而有些c工具 只能在当前工具下 ./ 执行就比较头疼

        if tool.workspace and os.path.isdir(tool.workspace):
            binpath = os.path.join(tool.workspace, tool.location)
        if not os.path.isfile(binpath):
            logger.error("the tool %s has not been found!" % tool.name)
            return False
        # todo 检验执行权限

        return True

    def get_tool(self, name):
        # name必须英文
        if name not in self.tools:
            logger.info("the tool %s not found  " % name)
            return
        return self.tools.get(name)


flags_instance = Flags()
flags_tools = Tools()


def registerArgs(inputs, outputs):
    for input in inputs:
        flags_instance.register(Args(*input), [])
    for output in outputs:
        flags_instance.register([], Args(*output))
    flags_instance.initflags()


def parse():
    global parsed_args
    parsed_args = flags_instance.args.parse_args()
    return parsed_args


def registerTool(name, location, usage, workspace=None, env_path=None, env_dict={}, ld_library_path=None,
                 logs_dir=None):
    btool = BinTool(name, location, usage, workspace=workspace, env_path=env_path, logs_dir=logs_dir,
                    ld_library_path=ld_library_path, env_dict=env_dict)
    flags_tools.add_tool(btool)


def executeOnceCmd(cmd):
    logger.info(os.getcwd())
    logger.info("Executing Single Cmd: %s" % cmd)
    ret = subprocess.call(cmd, shell=True)
    logger.info("Cmd: %s, return: %s" % (cmd, str(ret)))
    return ret


def executeTool(name, toolArgs):
    tool = flags_tools.get_tool(name)
    if not tool:
        logger.error("No this tool")
        return -1
    cmd = "{tool} {args}".format(tool=tool.location, args=toolArgs)
    return tool.execute_once(cmd)


def getToolLocationDir(name):
    tool = flags_tools.get_tool(name)
    if not tool:
        logger.error("No this tool")
        return ""
    return os.path.dirname(tool.location)


def getWorkspaceDir(name):
    tool = flags_tools.get_tool(name)
    if not tool:
        logger.error("No this tool")
        return ""
    if tool.workspace == None:
        return os.getcwd()
    else:
        if os.path.isdir(tool.workspace):
            return os.path.abspath(tool.workspace)
    return tool.workspace


def executePython(pyscriptCMD):
    tool = flags_tools.get_tool("python")
    if not tool:
        logger.error("No this tool")
        return -1
    cmd = "{tool} {args}".format(tool=tool.location, args=pyscriptCMD)
    return tool.execute_once(cmd)
