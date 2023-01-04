# 这个用于将指定文件夹下的pdf移动到指定的位置，现目前该位置，我的工作场景中是一些订单pdf
import os, shutil
import numpy as np
import pandas as pd

target = input(r'订单的位置（绝对路径）：')
files = os.listdir(target)

# 识别文件名中指定格式字段，从“的”到“人民币”中间的部分，是需要提取的字段
# 在目标文件夹中，会有对应的名称的文件夹，通过寻找对应关系，将指定文件夹下的pdf移动到各个对应名称的子文件夹
names = []
for file in files:
    de = file.find('的')
    rmb = file.find('人民币')
    name = file[de + 1:rmb]
    names.append([os.path.join(target,file), name])
    
# dst为目标文件夹，我这里因为区分了个人和公司不同主体，因此设置了两个文件夹，可以只设置一个，这里可以优化

dst = r'filepath'
dst_folders = os.listdir(dst)
dst2 = r'filepath'
dst_folders_2 = os.listdir(dst2)
# 给目标文件夹补充绝对路径
dst_final = [[os.path.join(dst, _), _] for _ in dst_folders]
dst_final_2 = [[os.path.join(dst2, _), _] for _ in dst_folders_2]

# 两个文件夹列表合并成一个
dst_final.extend(dst_final_2)

# 转化dateframe格式
match = pd.DataFrame(dst_final)
empty = []
for name in names:
    temp = match[match[1]==name[1]]
    if len(temp) > 0:
        shutil.move(name[0], temp.iloc[0][0])
        print('移动 %s 的订单'% name[1])
    else:
        empty.append(name)
print('移动完成，还有以下文件未能找到匹配位置：')
print(empty)
