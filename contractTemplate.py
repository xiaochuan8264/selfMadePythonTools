from docxtpl import DocxTemplate
from bs4 import BeautifulSoup as bf

# word模板中，所需字段必须以{{字段内容}}形式展示，否则无法成功替换

file = "模板合同.docx"

doc = DocxTemplate(file)

context = {"year":"2023",
           "month":"12",
           "day":"18",
           "partyb": "乙方姓名",
           "id": "身份证号码或者社会识别码",
           "contact": "联系人",
           "phone": "电话号码",
           "adress": "详细地址",
           "email": "邮箱地址",
           "qq": "QQ号码",
           "bankaccount": "银行账号",
           "bankinfo": "具体开户行信息"}

doc.render(context)

doc.save("filled_document.docx")

# 字段名称
htmlfile = "filelocation"

with open(file,'r',encoding='utf-8') as f:
    soup = bf(f.read(),'lxml')

# 找到指定的fieldname
element = soup.find(attrs={"data-fieldname": "lxr"})
def has_data_fieldname(tag):
    return tag.has_attr('data-fieldname')
           
nodes_with_data_fieldname = soup.find_all(has_data_fieldname)

data-fieldnames={"gysmc" : "供应商名称",
                 "frsfzh": "身份证号",
                 "dz": "联系地址",
                 "lxr": "联系人",
                 "lxsj": "联系电话",
                 "lxyx": "联系邮箱",
                 "qq": "联系QQ",
                 "khxdz": "开户行地址",
                 "zhmc":"账户名称",
                 "yxzh":"银行账户"}

child_with_value = parent_div.find(attrs={'value': True})
value = child_with_value['value'] if child_with_value else None
