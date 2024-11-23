import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class DragDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件拖拽和余弦相似度比对")
        self.root.geometry("800x650")  # 增加窗口高度以容纳新控件

        self.create_widgets()
        self.left_data = None
        self.right_data = None

    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 创建左侧拖拽区域
        self.left_frame = tk.Frame(main_frame)
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.left_label = tk.Label(self.left_frame, text="左侧拖拽区域")
        self.left_label.pack()

        # 左侧文件地址控件
        self.left_path_frame = tk.Frame(self.left_frame)
        self.left_path_frame.pack(fill=tk.X, pady=5)
        self.left_path_entry = tk.Entry(self.left_path_frame)
        self.left_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.left_browse_button = tk.Button(self.left_path_frame, text="浏览", command=lambda: self.browse_file(self.left_path_entry, self.left_text))
        self.left_browse_button.pack(side=tk.RIGHT)

        self.left_text = tk.Text(self.left_frame, width=40, height=25)
        self.left_text.pack(expand=True, fill=tk.BOTH)
        self.left_text.insert(tk.END, "将第一个文件拖拽到这里")

        # 创建中间分隔符
        separator = tk.Frame(main_frame, width=10)
        separator.pack(side=tk.LEFT, fill=tk.Y)

        # 创建右侧拖拽区域
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.right_label = tk.Label(self.right_frame, text="右侧拖拽区域")
        self.right_label.pack()

        # 右侧文件地址控件
        self.right_path_frame = tk.Frame(self.right_frame)
        self.right_path_frame.pack(fill=tk.X, pady=5)
        self.right_path_entry = tk.Entry(self.right_path_frame)
        self.right_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.right_browse_button = tk.Button(self.right_path_frame, text="浏览", command=lambda: self.browse_file(self.right_path_entry, self.right_text))
        self.right_browse_button.pack(side=tk.RIGHT)

        self.right_text = tk.Text(self.right_frame, width=40, height=25)
        self.right_text.pack(expand=True, fill=tk.BOTH)
        self.right_text.insert(tk.END, "将第二个文件拖拽到这里")

        # 创建结果显示区域（使用Label）
        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.result_label = tk.Label(self.result_frame, text="余弦相似度结果：", anchor="w")
        self.result_label.pack(side=tk.LEFT)

        self.result_value = tk.Label(self.result_frame, text="", anchor="w")
        self.result_value.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 注册拖拽事件
        for text_widget, path_entry in [(self.left_text, self.left_path_entry), (self.right_text, self.right_path_entry)]:
            text_widget.drop_target_register(DND_FILES)
            text_widget.dnd_bind('<<Drop>>', lambda e, t=text_widget, p=path_entry: self.on_drop(e, t, p))
            text_widget.bind('<Enter>', self.on_enter)
            text_widget.bind('<Leave>', self.on_leave)

    def on_drop(self, event, text_widget, path_entry):
        file_path = event.data
        text_widget.delete('1.0', tk.END)
        path_entry.delete(0, tk.END)
        path_entry.insert(0, file_path)
        self.show_file_content(text_widget, file_path)
        self.calculate_similarity()

    def on_enter(self, event):
        event.widget.config(bg='lightblue')

    def on_leave(self, event):
        event.widget.config(bg='white')

    def browse_file(self, path_entry, text_widget):
        file_path = filedialog.askopenfilename()
        if file_path:
            path_entry.delete(0, tk.END)
            path_entry.insert(0, file_path)
            self.show_file_content(text_widget, file_path)
            self.calculate_similarity()

    def show_file_content(self, text_widget, file_path):
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                text_widget.delete('1.0', tk.END)
                text_widget.insert(tk.END, f"{content}")
                
                # 解析数据
                data = self.parse_data(content)
                if text_widget == self.left_text:
                    self.left_data = data
                else:
                    self.right_data = data
            except Exception as e:
                text_widget.delete('1.0', tk.END)
                text_widget.insert(tk.END, f"无法读取文件 {file_path}: {str(e)}\n")
        else:
            text_widget.delete('1.0', tk.END)
            text_widget.insert(tk.END, f"文件不存在: {file_path}\n")

    def parse_data(self, content):
        # 解析文本内容为浮点数列表
        numbers = []
        for line in content.split('\n'):
            numbers.extend([float(num) for num in line.replace(',', ' ').split() if num.strip()])
        return numbers

    def calculate_similarity(self):
        if self.left_data and self.right_data:
            # 确保两个向量长度相同
            min_length = min(len(self.left_data), len(self.right_data))
            left_vector = np.array(self.left_data[:min_length]).reshape(1, -1)
            right_vector = np.array(self.right_data[:min_length]).reshape(1, -1)

            # 计算余弦相似度
            similarity = cosine_similarity(left_vector, right_vector)[0][0]
            
            self.result_value.config(text=f"余弦相似度: {similarity:.4f} (使用的数据点数: {min_length})")
        else:
            self.result_value.config(text="请确保两个文件都已加载")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = DragDropApp(root)
    root.mainloop()
