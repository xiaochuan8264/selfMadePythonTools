# python小工具
主要是工作和平时兴趣写的一些小python工具，也许可以在之后的工作中复用~

## 1.扫描件更名
**应用场景：** 有时候会有很多单张的文件，原来是从系统导出的PDF文件，但是需要公司盖章之后，另行扫描为扫描件进行复用。数量会比较多，大致为几十个独立文件，然后每个文件都有自己不同的名字，要让扫描后的文件与之前导出的命名一致，一个一个手动改效率非常低

**注意要点：**
1. 新建一个文件夹，这里以“扫描前”指代原始导出的文件，假设文件有20个。每一个都是单页独立文件；
2. 按照时间顺序整理，时间倒序或正序都可。确保在扫描的时候，扫描顺序与文件夹中的排序一致；
3. 再新建一个文件夹，这里命名为“扫描后”，将扫描后的文件存到该文件夹下。可以用Acrobat进行拆分，确保“扫描前”与“扫描后”的文件夹中的文件数量是一致的
4. 预览“扫描后”文件夹中文件的顺序，一般检查首尾两个文件即可。确保与“扫描前”文件夹中的文件是一样的，区别只是在于是有否盖章
5. 运行python小程序：auto-rename-manual_sort.py 按照提示输入粘贴文件夹地址以及选择排序方式即可


## 2.批量给图片添加水印，并自定义添加日期、品牌，动态名称（这里是不同影院）

**应用场景：** 给大批量的图片添加水印，直接运行程序：add_watermark.py 

**注意要点：**
1. 确保已经安装cv2以及PIL模块
2. 两个文件夹中的图片数量必须一致
3. 文本列表中的行数必须与图片数量一致

## 3.批量移动指定文件夹下文件（提取文件字段，移动到对应文件夹）

**应用场景：** 大批量的pdf文件，提取文件名中的关键字，根据关键字，将文件移动到对应关键字文件夹，免去手动去寻找文件夹的低效率工作。

运行程序：movefiles.py 

**注意要点：**
1. 文件名格式是提取“的”到“人民币”中间的关键字，其他关键字提取，需要适当修改规则
2. 目标文件夹下的子文件夹的命名必须与提取的关键字一致
3. 移动的目标文件目前为pdf

## 4.监控指定文件夹，如果出现包含特定字段的文件，则进行进一步操作

**应用场景：** 将文件移动到指定文件夹，有时需要单独建立新的子文件夹以进行文件整理，该程序将自动监控路径下的所有子文件夹，如果出现了特定文件名的文件，就以文件名在当前路径新建文件夹，并将文件移动进去

运行程序：monitor.py 

**注意要点：**
1. 文件名提取规则目前是包含“采购订单”的文件，监控其他文件名，可以自行修改
2. 如果是局域网的文件路径，可能需要手动刷新以查看新建好的文件夹


## 5.读取指定文件夹下pdf，批量生成备注

**应用场景：** 有时需要为许多文件生成相应备注，以方便管理。通过读取pdf，用正则表达式提取pdf中的信息，来生成关键备注；

运行程序：generateNotesFromPdfs.py

**注意要点：**
1. 所有pdf都必须是可编辑的pdf，而不是用打印机扫描后生成的pdf；
2. 提取的pdf信息限定比较死，可复用性较差，主要是个人记录。如果要复用，最多可以复用思路，即用最简单的PyPDF2模块，将pdf读取为文本，用正则匹配关键信息，结合文件名拆分规则，提取文件的关键信息；

## 6.将Excel单个Sheet拆分为多个Sheet

**应用场景：** 根据选定的字段，拆分Excel的表格，例如有一个总表SheetA，其中有个“地区”字段，可以选择按照该字段进行拆分，会自动生成新的excel，其中包含例如：上海、北京、天津、广州命名的新Sheet

运行程序：splitexcel.py

**注意要点：**
1. 首先需要明确要拆分的字段，需要在运行框中输入
2. 文件必须输入绝对路径，不能只是一个文件名

## 7.批量填充合同

**应用场景：** 设置好合同模板，所需字段使用{{字段名}}，然后进行填充，可以批量填充许多合同，避免一个一个字段复制粘贴。程序还待优化

运行程序：contractTemplate.py

**注意要点：**
1. word模板中务必按照此方法设置{{字段名}}
2. 待完善

## 8.将PSD从中文翻译为英文，并批量替换所有文本图层，不改动其他格式
**应用场景：** PSD中有许多的中文反馈，反馈以文字图层形式存在，需要翻译为英文，挨个复制粘贴过于麻烦

运行程序：translatePSDwithGUI.py

**注意要点：**
1. 需要提前配置photoshop，使其可以被唤起
2. 翻译文件前建议复制一个副本出来
3. 运行程序得到Json格式文本输出后，到ChatGPT进行翻译，拿到Json格式输出，并以本地文本文件形式保存
4. 对翻译后的文本进行一定程度的润色（若有需要）
5. 选择翻译后的本地文本文件
6. PSD完成翻译并替换为英文，进行相应排版整理（因为PSD没有自动换行，会存在文字超出边界的情况）
7. 保存并退出





