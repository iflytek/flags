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
import subprocess
import traceback
from enum import Enum

logger = None
parsed_args = None


class Logger(object):
    log_level = "INFO"

    @staticmethod
    def info(*args):
        return logging.info(args)

    @staticmethod
    def debug(*args):
        return logging.debug(args)

    @staticmethod
    def error(*args):
        return logging.error(args)


def get_logger():
    # Todo support more logging method here
    global logger

    if logger == None:
        logger = Logger
        logging.basicConfig(level=logger.log_level,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            stream=sys.stdout)
        Logger.debug("logger inited...")


get_logger()


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
        logger.debug("Args Input: ", self.name)


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
            self.args.add_argument("--" + ia.name, type=ia.typ, default=ia.default, required=ia.required,
                                   choices=ia.choices if ia.choices else None, help=ia.desc)
        for oa in self.output_args:
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
        fn(self, *args)
        if path:
            logger.info("backing: %s" % cwd)
            os.chdir(cwd)

    return inner


#
class StatusCodeEnum(Enum):
    """状态码枚举类"""
    OK = (0, '成功')
    ERROR = (10001, '错误')
    SERVER_ERR = (500, '服务器异常')


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


class BinTool(object):
    ## 专门执行二进制工具处理的类
    def __init__(self, name, location, usage, workspace=None, env_path=None, logs_dir=None):
        # todo 校验 name必须英文
        self.name = name
        self.location = location
        self.usage = usage
        self.workspace = workspace if workspace else os.getcwd()
        self.env_path = env_path
        self.logs_dir = logs_dir
        # todo 校验location 存在性并提示

        self.workspace = workspace
        pass

    # 单次执行
    @back_origin_workspace
    def execute_once(self, cmd):
        logger.info(os.getcwd())
        logger.info("Executing Shell Cmd: %s" % cmd)
        ret = subprocess.call(cmd, shell=True)
        logger.info("Cmd: %s, return: %s" % (cmd, str(ret)))

        if ret != 0:
            logger.error("cmd: %s execute Error!" % cmd)

    # 多进程执行
    def execute_mp(self, *args):
        pass


class Tools(object):
    def __init__(self):
        self.tools = {}

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

    def checkTool(self, tool):
        if not os.path.isfile(tool.location):
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


def registerTool(name, location, usage, workspace=None, env_path=None, logs_dir=None):
    btool = BinTool(name, location, usage, workspace=workspace, env_path=env_path, logs_dir=logs_dir)
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
        return
    cmd = "{tool} {args}".format(tool=tool.location, args=toolArgs)
    tool.execute_once(cmd)
