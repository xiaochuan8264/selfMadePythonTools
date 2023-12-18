from docxtpl import DocxTemplate

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
