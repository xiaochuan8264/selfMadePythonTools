import win32com.client
from pywintypes import com_error
import json
import tkinter as tk
from tkinter import filedialog

def judgeifgroup(layer):
    # 判断是否属于组
    try:
        temp = layer.layers
        return True
    except AttributeError as e:
        print(e)
        return False

def judgeiftextlayer(layer):
    # 判断是否属于文字图层
    try:
        temp = layer.TextItem
        return True
    except com_error as e:
        print(e)
        return False
    except AttributeError as e2:
        print(e2)
        return False

def get_translated_text():
    # 在chatgpt翻译好后，输出到本地文本，并输入本地文本绝对地址（包括后缀名）
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    path = filedialog.askopenfilename(title="Select translated text file")
    root.destroy()  # Close the root window

    with open(path, 'r') as f:
        translated_dict = json.loads(f.read())
    return translated_dict

def select_psd_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title="Select PSD file", filetypes=[("PSD files", "*.psd")])
    root.destroy()  # Close the root window
    return file_path

file_path = select_psd_file()

app = win32com.client.Dispatch("Photoshop.Application")

psd_api = app.Open(file_path)

# 读取psd并得到所有文本图层内容，保存对象
content_dic = {}
counter = 1

for layer in psd_api.Layers:
    if judgeifgroup(layer):
        for layer2 in layer.Layers:
            if judgeiftextlayer(layer2):
                content_dic[counter] = layer2
            counter += 1
    else:
        if judgeiftextlayer(layer):
            content_dic[counter] = layer
        counter += 1

# 提取出所有的实际文本内容，得到文本内容后需要到chatgpt手动发送并获取到json格式的输出，然后保存到本地
raw_content = {}

for k, v in content_dic.items():
    raw_content[k] = v.TextItem.Contents
raw_content = json.dumps(raw_content, indent=4, ensure_ascii=False)
print(raw_content)

# 读取本地翻译后的文档
translated_dic = get_translated_text()

# 对psd中的文本进行替换
for k, v in content_dic.items():
    v.TextItem.Contents = translated_dic[str(k)]

psd_api.Save()
