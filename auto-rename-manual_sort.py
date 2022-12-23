import os

source = input(r'源文件地址-将根据此文件夹内文件进行命名：')
target = input(r'目标文件夹：')

sfiles = os.listdir(source)
sfiles_dir = [[sfiles[i], source+"\\"+sfiles[i], os.path.getmtime(source+"\\"+sfiles[i])] for i in range(len(sfiles))]
tfiles = os.listdir(target)
tfiles_dir = [[tfiles[i], target+"\\"+tfiles[i], os.path.getmtime(target+"\\"+tfiles[i])] for i in range(len(tfiles))]

def order(temp):
    return temp[2]

choice_s = int(input('源文件夹（命名依据）排序方式，日期升序1，日期倒序2 ：'))
choice_t = int(input('目标文件夹（扫描后文件）排序方式，日期升序1，日期倒序2 ：'))

if choice_s == 1:
    reverse_s = False
else:
    reverse_s = True
    
if choice_t == 1:
    reverse_t = False
else:
    reverse_t = True

sfiles_dir.sort(key=order, reverse=reverse_s)
tfiles_dir.sort(key=order, reverse=reverse_t)

os.chdir(target)
for i in range(len(sfiles)):
    os.rename(tfiles_dir[i][0],sfiles_dir[i][0])
    
print('重命名完成...')