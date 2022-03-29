# flags
A Useful Python lib that can make your scripts more standard and easier to maintain...

[简体中文](README_CN.md)

## Feature

* All in one script, copy anywhere
* python3 support
* Easy to use.

## Background

Now days, python is the most popular script language . In your company , Do you have seen various scripts that have not a standard format?

I think everybody will reply yes.

Python provide us some useful libs such as argparse...

## GetStarted

TODO

## Design （In progress）

Based on the argparse, we want to standardize scripts Input/Output Parameters format, such as env paramiters format, file location parameters format, logging format, logging level format ,workspace location,


### Input/Output Paramters Format 【depreciated 废弃 忽略此处设计】
 
what the difference between the  input/output paramters? Generally , all the paramters is the input parameters, how to distinguish them? 

The easist way is that  the output parameters are always standby the scripts output files location, while input parameters standpy an pure configuration for the scripts/program except the output configuration.

so my design for the input/output is :

```python
flags.in("epoch", int, 0 , "description" ,true)
flags.in("batch_size", int, 6, "description",true)
flags.in("lr", float, 0.01, "description",false)
flags.out("model_path", str, "/workspace/model" ,"model path",true)
```
when run the program:

you can pass parameters by this way:

`python yourprogram.py --in epoch=0,batch_size=10 --out model_path=/workspace`

or you can specify every parameters in another way:

`python yourprogram.py --in epoch=0 --in batch_size=10 --out model_path=/workspace`


### workspace location

workspace is the place where the scripts is running.  default is `os.getcwd()`  ussually means the place that the script's location  or the scrpit's executor's location





