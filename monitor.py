# 监测文件夹是否出现包含特定文件名的文件，出现了就对其进行进一步操作
# 1. 以文件名新建在文件所在路径，新建一个同名文件夹
# 2. 将该文件移动到同名文件夹下
import os, difflib, time, shutil

# 我这里设置监视两个文件夹，可以改为只有一个
dst = r"filepath"
dst2 = r"filepath"

def find_orders(dst):
    suppliers = os.listdir(dst)   
    suppliers = [os.path.join(dst, _) for _ in suppliers]

    for supplier in suppliers:
        files =[os.path.join(supplier,_) for _ in os.listdir(supplier) if os.path.isfile(os.path.join(supplier,_))]
        # 这里指定的特殊文件名，为包含“采购订单”几个字的文件，如果出现了该文件，则会进行进一步操作
        orders = [_ for _ in files if _.find('采购订单') != -1]
        if len(orders):
            for order in orders:
                folder = order.replace('.pdf','')
                os.mkdir(folder)
                print(folder)
                shutil.move(order, folder)
   
    
def runing_time():
  # 用于统计程序运行的时间
    t = time.perf_counter()
    print('运行开始')
    find_orders(dst)
    print('运行结束')
    print(f'用时：{time.perf_counter() - t:.8f}s')
    
while True:
    find_orders(dst)
    find_orders(dst2)
    time.sleep(0.5)
