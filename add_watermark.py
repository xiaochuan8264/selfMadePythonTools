import cv2, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def imread(path):
    """
    cv2模块默认是无法读取中文路径的文件的，所以使用这个方法来读取中文图片文件
    """
    img = cv2.imdecode(np.fromfile(path,dtype=np.uint8), cv2.IMREAD_COLOR)    #imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def imwrite(path, image):
    """
    cv2.imwrite 无法写入中文路径的文档
    使用此方法来写入中文路径
    """
    cv2.imencode('.png',image)[1].tofile(path)

def adding_watermark(img_in, text, img_out):
    img = imread(img_in)
    h, w = img.shape[:2]
# 判断是否是openCV图片类型
    if (isinstance(img, np.ndarray)):
    # 转化成PIL类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # img = Image.fromarray(img)
    # 这里可以自己调整参数来改变水印位置以及文字大小
    left = int(w/40)
    top = h - int(h/5)
    textSize = int((h/4)/5)

    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype("font/simhei.ttf", textSize, encoding="utf-8")
    # 绘制文本
    # text = '2022-07-15\n完美世界影城（长春新天地店）\n美年达'
    textColor = (255, 255, 255)
    draw.text((left, top), text, textColor, font=fontStyle)
# 转换回OpenCV类型
    img2 = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
# 保存图片
    imwrite(img_out, img2)

first_pic_path = input(r'每页第一张图片所在文件夹:')
second_pic_path = input(r'每页第二张图片所在文件夹:')
cinemas_path = input(r'影院文本文件路径:')
date = input('要添加的日期水印:')
brand = input('要添加的品牌：')


if not os.path.exists('watermark_added'):
    
    os.mkdir('watermark_added')
    # os.mkdir('watermark_added\\picture1')
    # os.mkdir('watermark_added\\picture2')
    
cwd = os.getcwd()
added = os.path.join(cwd, 'watermark_added')
picture1_path = os.path.join(cwd, 'watermark_added\\picture1')
picture2_path = os.path.join(cwd, 'watermark_added\\picture2')

first_pics = os.listdir(first_pic_path)
second_pics = os.listdir(second_pic_path)
with open(cinemas_path, 'r', encoding='utf-8') as f:
    cinemas = f.read()
    cinemas = cinemas.strip()
    cinemas = cinemas.split('\n')

pic_nums = len(first_pics)
suffix = first_pics[0].split('.')[-1]
suffix = '.' + suffix
for i in range(pic_nums):
    text = date + '\n' + cinemas[i] + '\n' + brand
    # 第一张图片参数
    img_in_1 = os.path.join(first_pic_path, first_pics[i])    
    img_out_1 = os.path.join(added, '%d%s'%(i, suffix))
    # img_out_1 = os.path.join(picture1_path, first_pics[i])
    # 第二张图片参数
    img_in_2 = os.path.join(second_pic_path, second_pics[i])
    img_out_2 = os.path.join(added, '%d-%d%s'%(i, i, suffix))
    
    # img_out_2 = os.path.join(picture2_path, second_pics[i])
    # 添加水印
    adding_watermark(img_in_1, text,img_out_1)
    adding_watermark(img_in_2, text,img_out_2)
    

