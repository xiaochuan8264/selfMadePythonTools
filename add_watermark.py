import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QFileDialog, QMessageBox
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QIntValidator

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

def adding_watermark(img_in, text, img_out, left_adjust=0, top_adjust=0, text_size_adjust=0):
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
    left += left_adjust
    top += top_adjust
    textSize += text_size_adjust

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
    return left, top, textSize

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.firstPicPath = ''
        self.secondPicPath = ''
        self.cinemaFilePath = ''
        self.watermarkInfoLabel = None
        self.left = 0
        self.top = 0
        self.textSize = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 添加用于显示水印信息的标签
        self.watermarkInfoLabel = QLabel('水印信息：左边距=0, 顶边距=0, 字体大小=0')
        layout.addWidget(self.watermarkInfoLabel)

        # 选择第一张图片文件夹及其显示标签
        self.firstPicBtn = QPushButton('选择第一张图片文件夹')
        self.firstPicBtn.clicked.connect(self.chooseFirstPicFolder)
        self.firstPicLabel = QLabel('未选择')
        layout.addWidget(self.firstPicBtn)
        layout.addWidget(self.firstPicLabel)

        # 选择第二张图片文件夹及其显示标签
        self.secondPicBtn = QPushButton('选择第二张图片文件夹')
        self.secondPicBtn.clicked.connect(self.chooseSecondPicFolder)
        self.secondPicLabel = QLabel('未选择')
        layout.addWidget(self.secondPicBtn)
        layout.addWidget(self.secondPicLabel)

        # 选择影院文件及其显示标签
        self.cinemaFileBtn = QPushButton('选择影院文件')
        self.cinemaFileBtn.clicked.connect(self.chooseCinemaFile)
        self.cinemaFileLabel = QLabel('未选择')
        layout.addWidget(self.cinemaFileBtn)
        layout.addWidget(self.cinemaFileLabel)

        # 输入框
        self.dateLineEdit = QLineEdit(self)
        self.dateLineEdit.setPlaceholderText("输入日期")
        layout.addWidget(self.dateLineEdit)

        self.brandLineEdit = QLineEdit(self)
        self.brandLineEdit.setPlaceholderText("输入品牌")
        layout.addWidget(self.brandLineEdit)
        
        self.leftAdjustEdit = QLineEdit(self)
        self.leftAdjustEdit.setPlaceholderText("左边距微调")
        self.leftAdjustEdit.setValidator(QIntValidator())  # 只允许输入数字
        layout.addWidget(self.leftAdjustEdit)

        self.topAdjustEdit = QLineEdit(self)
        self.topAdjustEdit.setPlaceholderText("顶边距微调")
        self.topAdjustEdit.setValidator(QIntValidator())
        layout.addWidget(self.topAdjustEdit)

        self.textSizeAdjustEdit = QLineEdit(self)
        self.textSizeAdjustEdit.setPlaceholderText("字体大小微调")
        self.textSizeAdjustEdit.setValidator(QIntValidator())
        layout.addWidget(self.textSizeAdjustEdit)

        # 开始处理按钮
        self.startBtn = QPushButton('开始处理')
        self.startBtn.clicked.connect(self.startProcessing)
        layout.addWidget(self.startBtn)

        self.setLayout(layout)
        self.setWindowTitle('图片水印处理')
        self.setGeometry(300, 300, 350, 200)

    def chooseFirstPicFolder(self):
        self.firstPicPath = QFileDialog.getExistingDirectory(self, "选择第一张图片文件夹")
        self.firstPicLabel.setText(f'已选择: {self.firstPicPath}')

    def chooseSecondPicFolder(self):
        self.secondPicPath = QFileDialog.getExistingDirectory(self, "选择第二张图片文件夹")
        self.secondPicLabel.setText(f'已选择: {self.secondPicPath}')

    def chooseCinemaFile(self):
        self.cinemaFilePath, _ = QFileDialog.getOpenFileName(self, "选择影院文件", "", "Text files (*.txt)")
        self.cinemaFileLabel.setText(f'已选择: {self.cinemaFilePath}')

    def startProcessing(self):
        self.leftAdjust = int(self.leftAdjustEdit.text() or 0)
        self.topAdjust = int(self.topAdjustEdit.text() or 0)
        self.textSizeAdjust = int(self.textSizeAdjustEdit.text() or 0)
        # 开始处理图片
        date = self.dateLineEdit.text()
        brand = self.brandLineEdit.text()
        #print(1)
        if not all([self.firstPicPath, self.secondPicPath, self.cinemaFilePath, date, brand]):
            QMessageBox.warning(self, "警告", "请确保所有字段都填写完整！")
            return

        try:
            # 调用处理图片的函数
            # 注意：您需要根据需要调整此处的代码
            #print(2)
            added, textinfo = process_images(self.firstPicPath, self.secondPicPath, self.cinemaFilePath, date, brand,self.leftAdjust, self.topAdjust, self.textSizeAdjust)
            #print(4)
            self.watermarkInfoLabel.setText(f'水印信息：左边距={textinfo[0]}, 顶边距={textinfo[1]}, 字体大小={textinfo[2]}')
            QMessageBox.information(self, "完成", "图片处理完成。查看路径：%s"%added)
        except Exception as e:
            QMessageBox.critical(self, "错误", "请确保影院文本保存为了utf-8的编码格式：%s"%str(e))

# ... 其他必要的函数定义 ...

def process_images(first_pic_path, second_pic_path, cinemas_path, date, brand, left_adjust=0, top_adjust=0, text_size_adjust=0):
    # 您原来的处理图片的代码逻辑
    # ...
    if not os.path.exists('watermark_added'):    
        os.mkdir('watermark_added')
    # os.mkdir('watermark_added\\picture1')
    # os.mkdir('watermark_added\\picture2')
    #print(3)
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
        #print(cinemas[:10])

    pic_nums = len(first_pics)
    suffix = first_pics[0].split('.')[-1]
    suffix = '.' + suffix
    textinfo = ''
    for i in range(pic_nums):
        text = date + '\n' + cinemas[i] + '\n' + brand
        #print(text)
        # 第一张图片参数
        img_in_1 = os.path.join(first_pic_path, first_pics[i])    
        img_out_1 = os.path.join(added, '%d%s'%(i, suffix))
        # img_out_1 = os.path.join(picture1_path, first_pics[i])
        # 第二张图片参数
        img_in_2 = os.path.join(second_pic_path, second_pics[i])
        img_out_2 = os.path.join(added, '%d-%d%s'%(i, i, suffix))
    
        # img_out_2 = os.path.join(picture2_path, second_pics[i])
        # 添加水印
        textinfo = adding_watermark(img_in_1, text,img_out_1, left_adjust, top_adjust, text_size_adjust)
        textinfo = adding_watermark(img_in_2, text,img_out_2, left_adjust, top_adjust, text_size_adjust)
    return added, textinfo


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
