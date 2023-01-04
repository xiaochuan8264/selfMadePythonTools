"""
读取指定文件夹下的pdf（可编辑文档，非扫描件），根据pdf内容，及相应自定义规则，为每个文件生成备注，并形成备注列表的excel文件
"""

import camelot, re, os, PyPDF2
from datetime import datetime
import pandas as pd


pdfs_location = input(r'需要提取的pdf地址（文件夹即可）：')

# 根据以下字典的对应规则，对每个文件进行分组，可以自行新增更多类别
cats = {'原画':'2D美术组',
        '模型':'3D美术组', 
        '3渲2':'3D美术组'}

# 正则识别日期，举例格式：2022-12-31
date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
# 正则文件单号，以WBTQ开头，后面紧跟6-9位数字编码
order_pattern = re.compile(r'WBTQ\d{6,9}')

def get_excel(final_res, location):
    df = pd.DataFrame(final_res)
    path = os.path.join(location, '备注列表.xlsx')
    df.to_excel(path)

def get_pdfinfo(file):
    "默认只有一页"
    tables = camelot.read_pdf(file,pages='1', flavor='stream')
    data = tables[0].data
    #for i in data:
        #print(i)
    return data
    
def analyze_data_with_camelot(data, pattern):
    collect = []
    for row in data:
        for cell in row:
            # res = pattern.match(cell) match有可能找不到
            res = pattern.search(cell)
            if res:
                target_res = res.group()
                collect.append(target_res)
    return collect

def analyze_data_with_PyPDF2(file, pattern):
# 用PyPDF读取pdf，并按照正则，找到所有符合的结果
    pdf = open(file, 'rb')
    pdf_document = PyPDF2.PdfFileReader(pdf)
    f_page = pdf_document.getPage(0)
    text = f_page.extractText()
    res = pattern.findall(text)
    res = list(set(res))
    return res
    
    
def middle_note(filename):
    t = 2
    start = 0
    while t:
        start = filename.find('_', start) + 1
        t -= 1
    t = 3
    end = len(filename)
    while t:
        end = filename.rfind('_', 0, end)
        t -= 1
    middle_text = filename[start:end]
    return middle_text
    
def project_name(filename):
    # 根据文件名获取项目组名称，根据文件名进行拆分
    temp = filename.split('_')
    project = temp[1]
    if project == '项目代号1':
        project = '制作组名称1'
    elif project == '项目代号2':
        project = '制作组名称2'
    return project
    
def final_note(date, project, group, middle, order=''):
    date_start = date[0]
    date_end = date[-1]
    y = datetime.strptime(date_end, '%Y-%m-%d')
    month = y.month
    year = y.year
    date_in_dot_start = date_start.replace('-','.')
    date_in_dot_end = date_end.replace('-','.')
    
    if project == '制作组名称1' or project == '制作组名称2':
        note = '%d%02d-%s%s-%s-费用(%s-%s)|WBTQ%s'% (year, month, project, group, middle, date_in_dot_start, date_in_dot_end,order)
    else:
        note = '%d%02d-%s-%s-费用(%s-%s)|WBTQ%s'% (year, month, project, middle, date_in_dot_start, date_in_dot_end,order)
    return note

def get_group(cats, filename):
    # 环节分组
    t = 3
    end = len(filename)
    while t:
        end = filename.rfind('_', 0, end)
        t -= 1
    t = 4
    start = len(filename)
    while t:
        start = filename.rfind('_', 0, start)
        t -= 1
    target = filename[start:end]    
    items = list(cats.keys())
    group = ''
    for item in items:
        if target.find(item) != -1:
            group = cats.get(item)
    return group

def get_pdfs(filepath):
# 访问指定文件夹，获取该文件夹下所有pdf，输出列表包含[pdf的绝对路径, 文件夹下pdf的名称]
    pdfs = os.listdir(filepath)
    container = []
    for pdf in pdfs:
        ab_path = os.path.join(pdfs_location, pdf)
        temp = [ab_path, pdf]
        container.append(temp)
    return container

def sort_order(order_list):
    orders = list(set(order_list))
    text = ''
    for order in orders:
        text += order
        text += ','
    text = text.strip(',')
    text = text.replace('WBTQ','')
    return text
    
pdfs = get_pdfs(pdfs_location)
notes = []
for pdf in pdfs:
    print(pdf[1])
    # data = get_pdfinfo(pdf[0]) 使用camelot读取并返回数据
    # date = analyze_data_with_camelot(data, date_pattern)
    # orders = analyze_data(data, order_pattern)
    date = analyze_data_with_PyPDF2(pdf[0], date_pattern)
    
    orders = analyze_data_with_PyPDF2(pdf[0], order_pattern)
    order = sort_order(orders)
    
    date.sort()
    if len(date)>2:
        date.pop()
    
    project = project_name(pdf[1])
    group = get_group(cats, pdf[1])
    middle = middle_note(pdf[1])
    note = final_note(date, project, group, middle, order)
    notes.append([pdf[1], note])
    print(note)
for note in notes:
    print(note)
    
get_excel(notes, pdfs_location)
