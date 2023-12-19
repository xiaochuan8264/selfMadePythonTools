import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from docxtpl import DocxTemplate
from bs4 import BeautifulSoup as bf
import time

class App:
    def __init__(self, root):
        self.root = root
        root.title('模板合同填充-试用')
        root.geometry('600x400')

        # 文件路径变量
        self.html_file_path = tk.StringVar()
        self.template_file_path = tk.StringVar()

        # 按钮：选择 HTML 文件
        self.btn_select_html = tk.Button(root, text='选择入库html文件', command=self.select_html_file)
        self.btn_select_html.pack()

        # 显示 HTML 文件路径
        self.lbl_html_file_path = tk.Label(root, textvariable=self.html_file_path)
        self.lbl_html_file_path.pack()

        # 按钮：选择合同模板文件
        self.btn_select_template = tk.Button(root, text='选择合同模板', command=self.select_template_file)
        self.btn_select_template.pack()

        # 显示合同模板文件路径
        self.lbl_template_file_path = tk.Label(root, textvariable=self.template_file_path)
        self.lbl_template_file_path.pack()

        # 表格：用于展示和编辑信息
        self.table = ttk.Treeview(root, columns=('字段', '对应信息'), show='headings')
        self.table.heading('字段', text='字段')
        self.table.heading('对应信息', text='对应信息')
        self.table.pack(expand=True, fill='both')

        # 按钮：确认
        self.btn_confirm = tk.Button(root, text='确认文件选择', command=self.confirm)
        self.btn_confirm.pack()
        
        self.btn_submit = tk.Button(root, text='填充合同', command=self.submit)
        self.btn_submit.pack()

    def select_html_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('HTML files', '*.html;*.htm')])
        if file_path:
            self.html_file_path.set(file_path)

    def select_template_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Word files', '*.docx')])
        if file_path:
            self.template_file_path.set(file_path)
    
    def process_files(self, html):
        temp_time = time.localtime()
        sign_year = temp_time.tm_year
        sign_month = temp_time.tm_mon
        sign_day = temp_time.tm_mday
        with open(html,'r',encoding='utf-8') as f:
            soup = bf(f.read(),'lxml')
        data_fieldnames={"gysmc" : "partyb",
                 "frsfzh": "id",
                 "dz": "adress",
                 "lxr": "contact",
                 "lxsj": "phone",
                 "lxyx": "email",
                 "qq": "qq",
                 "khxdz": "bankinfo",
                 "zhmc":"partyb",
                 "yxzh":"bankaccount"}
        context = {"year":str(sign_year),
                   "month":str(sign_month),
                   "day":str(sign_day)}
        for fieldname, chinese in data_fieldnames.items():    
            # 找到指定的fieldname
            element = soup.find(attrs={"data-fieldname": fieldname})
            # print(element.text)
            child_with_value = element.find(attrs={'value': True})
            value = child_with_value['value'] if child_with_value else None
            context[data_fieldnames[fieldname]] = value
            # print("%s: %s"%(fieldname, value))
        return context
    
    def confirm(self):
        # 这里执行代码，处理文件路径
        html_path = self.html_file_path.get()
        template_path = self.template_file_path.get()
        if not html_path or not template_path:
            messagebox.showerror('Error', 'Please select both HTML and contract template files.')
            return

        # 假设这里是处理文件的代码，且结果存储在 result 变量中
        result = []
        self.context = self.process_files(html_path)
        for key, value in self.context.items():
            result.append((key, value))
        # 假设的处理结果
        # result = [('Item1', 'Info1'), ('Item2', 'Info2')]

        # 清空并填充表格
        for item in self.table.get_children():
            self.table.delete(item)

        for item, info in result:
            self.table.insert('', 'end', values=(item, info))
        
        # 弹出确认框
        #if messagebox.askyesno('Confirm', 'Do you want to proceed with the provided information?'):
            # 点击了确认，继续执行剩余代码
            #doc = DocxTemplate(template_path)
            #doc.render(context)
            # print('Confirmed')
            # continue_processing()  # 调用其他处理函数
        #else:
            # 点击了取消
            #print('Cancelled')
    def submit(self):
        # 收集表格数据
        #data = [(self.table.item(row_id, 'values')[0], self.table.item(row_id, 'values')[1]) for row_id in self.table.get_children()]
        #print(data)  # 打印或处理数据
        # 这里执行提交后的操作
        doc = DocxTemplate(self.template_file_path.get())
        doc.render(self.context)
        doc.save("filled_document.docx")
        messagebox.showinfo('已填充', '已将识别到的信息填充到模板合同')


# 创建窗口并运行应用
root = tk.Tk()
app = App(root)
root.mainloop()
