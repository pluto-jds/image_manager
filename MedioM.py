import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
import shutil
from database import create_csv,append_to_csv,find_by_name
from utils import iterate_media_files,count_files
from aiclient import ImageAnalyzer,ChatBot

from datetime import datetime
from move2dir import copy_files_from_csv
import time

global_file_path = ""

prompt_template = """你是一个{0}素材库AI助手，需要按照要求分析图片或者视频内容，并对他们分类。类别包括{1}。
输出格式为yaml 
image_describe:描述图片或者视频中的场景和人物，特别是{2}相关的内容，严格包括以下方面：
{3}
请尽可能详细地描述图片或者视频中的每个要素，以帮助分类到合适的标签。
image_label:以数组方式给出最合适的2个标签
image_title:结合image_describe为图片或者视频生成小于20字的标题"""

def create_prompt(category_input, api_key_input):
    
    global prompt_template
    api_key = api_key_input
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 你的API Base URL
    chatbot = ChatBot(api_key, base_url)
    title_prompt_text = """你是一个自媒体素材库AI助手，你根据用户提供的素材分类标签，总结6字以内的用户素材库主题。注意仅输出素材库主题"""
    title_text = chatbot.chat_something(title_prompt_text, category_input)
    
    
    parase_prompt_text = f"""你是一个自媒体素材库AI助手，素材类型是图片、视频。素材主题是{title_text}，请为用户提供的每个素材标签添加描述辅助AI分析图片是否有该标签具备的特征或者场景，每个标签的描述内容不超过
30字。注意仅输出素材标签描述内容，输出格式
序号.标签，描述
"""
    parase_text = chatbot.chat_something(parase_prompt_text, category_input)
    
    prompt_text = prompt_template.format(title_text, category_input.replace(" ", "、"), title_text, parase_text)
    return prompt_text
    

categroy_default="""发际线 头顶 生发产品 生发液 生发食品 医院和药物 整体发量 头皮按摩 掉发 截图 其他"""

api_key_debug = "sk-d5b2b41547054643a192264be3cd88ec"  # 替换为你的API Key

input_directory_default = './test_image'

output_directory_default = "./image"

def analyze_medio_fn(input_directory, output_dir_input, prompt_text, api_key, category_input):
    
    global global_file_path

    if not os.path.isabs(input_directory):
        input_directory = "..//..//..//"+input_directory

    if not os.path.isabs(output_dir_input):
        output_dir_input = "..//..//..//"+output_dir_input

    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    analyzer = ImageAnalyzer(api_key, base_url, prompt_text)
    directory = '..//..//..//database'  # 替换为你需要存放CSV的目录路径
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'media_info_{current_time}.csv'  # CSV文件名称
    headers = ['Name', 'Path', 'Extension', 'Content', 'Categorys','NewName', 'NewPath']
    create_csv(directory, filename, headers)
    global_file_path = directory+"/"+filename
    
    if not os.path.exists(input_directory):
        yield None, f"目录不存在: {input_directory}"

    all_medio_count = count_files(input_directory)
    if all_medio_count == 0:
        yield None, "目标目录没有素材文件"
    current_file_id = 1
    
    yield None, "开始解析图片"
    
    for name, path, suffix in iterate_media_files(input_directory):    
        # 指定图片路径并进行分析
        result = analyzer.analyze_medio(path, suffix)
        
        fit_cls = result['image_label'][0]
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = output_dir_input+"/"+fit_cls+"/"+result['image_title']+current_time + suffix

        row_data = [name,path,suffix, result['image_describe'], ", ".join(result['image_label']), result['image_title'], new_path]
        append_to_csv(global_file_path, row_data)
        
        process = f"{current_file_id}/{all_medio_count}"
        
        medio_type = "图片"
        if analyzer.is_video:
            medio_type = "视频"
        image_describe = "\n".join(f"{key}: {value}" for key, value in result['image_describe'].items())
        image_label = ", ".join(result['image_label'])
        debug_info = f"【素材描述】：\n{image_describe}\n【标签】：{image_label}\n【新名称】：{result['image_title']}\n【类型】：{medio_type}\n【归档路径】：{new_path}\n【处理进度】：{process}"
        
        if analyzer.is_video:
            path = analyzer.video_first_frame_path
        current_file_id = current_file_id + 1
        yield path, debug_info
        print(debug_info)

    time.sleep(4)
    yield None, "完成素材解析，可以开始素材拷贝，在database目录的csv文件查看准备拷贝的信息"


class AnalyzeThread(QThread):
    # 定义一个信号用于发送实时数据
    update_signal = pyqtSignal(str)
    image_signal = pyqtSignal(str)

    def __init__(self, input_directory, output_directory, prompt_text, api_key, category_input):
        super().__init__()
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.prompt_text = prompt_text
        self.api_key = api_key
        self.category_input = category_input

    def run(self):
        # 这里调用 analyze_medio_fn，并通过信号发送实时数据
        for image_path, info in analyze_medio_fn(self.input_directory, self.output_directory, self.prompt_text, self.api_key, self.category_input):
            # 通过信号发送实时更新
            self.update_signal.emit(info)
            if image_path:
                self.image_signal.emit(image_path)

class GeneratePromptThread(QThread):
    progress_updated = pyqtSignal(str)
    # 定义一个信号，用来传递生成的提示词
    prompt_generated = pyqtSignal(str)
    
    def __init__(self, category_input, api_key_input):
        super().__init__()
        self.category_input = category_input
        self.api_key_input = api_key_input

    def run(self):
        self.progress_updated.emit("正在生成提示词...")
        prompt_text = create_prompt(self.category_input, self.api_key_input)
        self.prompt_generated.emit(prompt_text)

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('素材管理')
        self.resize(1000, 800)
        
        # 创建主布局
        main_layout = QHBoxLayout()  # 使用水平布局，将左侧和右侧部分分开
        
        # 左侧布局（输入区域）
        left_layout = QVBoxLayout()
        
        form_layout = QVBoxLayout()
        self.category_input = QLineEdit(self)
        self.category_input.setPlaceholderText('请输入类别，以空格分隔')
        self.category_input.setText(categroy_default)
        form_layout.addWidget(self.category_input)

        self.prompt_input = QTextEdit(self)
        self.prompt_input.setPlaceholderText('请输入提示词')
        form_layout.addWidget(self.prompt_input)

        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText('请输入API Key')
        self.api_key_input.setText(api_key_debug)
        form_layout.addWidget(self.api_key_input)

        self.prompt_button = QPushButton("给出素材分析提示词", self)
        self.prompt_button.clicked.connect(self.generate_prompt)
        
        # 输入输出目录区域
        input_output_layout = QHBoxLayout()
        self.input_dir_input = QLineEdit(self)
        self.input_dir_input.setPlaceholderText('请输入输入目录路径')
        self.input_dir_input.setText(input_directory_default)
        input_output_layout.addWidget(self.input_dir_input)

        self.output_dir_input = QLineEdit(self)
        self.output_dir_input.setPlaceholderText('请输入输出目录路径')
        self.output_dir_input.setText(output_directory_default)
        input_output_layout.addWidget(self.output_dir_input)

        # 按钮
        self.analyze_button = QPushButton("步骤1 生成素材解析", self)
        self.analyze_button.clicked.connect(self.analyze_media)
        
        self.copy_button = QPushButton("步骤2 完成素材拷贝", self)
        self.copy_button.clicked.connect(self.copy_media)

        # 添加到左侧布局
        left_layout.addLayout(form_layout)
        left_layout.addWidget(self.prompt_button)
        left_layout.addLayout(input_output_layout)
        left_layout.addWidget(self.analyze_button)
        left_layout.addWidget(self.copy_button)

        # 右侧布局（输出区域）
        right_layout = QVBoxLayout()
        
        # 图像显示区
        self.image_output = QLabel(self)
        self.image_output.setFixedHeight(400)
        self.image_output.setAlignment(Qt.AlignCenter)
        self.image_output.setText("处理图像显示区")

        # 内容显示区
        self.button_output = QTextEdit(self)
        self.button_output.setReadOnly(True)
        
        # 添加到右侧布局
        right_layout.addWidget(self.image_output)
        right_layout.addWidget(self.button_output)
        
        # 主布局：将左侧和右侧布局加入
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def generate_prompt(self):
        category_input = self.category_input.text()
        api_key_input = self.api_key_input.text()
        
        self.thread = GeneratePromptThread(category_input, api_key_input)
        
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.prompt_generated.connect(self.on_prompt_generated)
        self.thread.start()
        
    def update_progress(self, progress_message):
        # 将生成过程中的信息显示在进度区域
        self.prompt_input.setText(progress_message)
        
    def on_prompt_generated(self, prompt_text):
        # 将生成的提示词设置到文本框中
        self.prompt_input.clear()
        self.prompt_input.setText(prompt_text)
        

    def analyze_media(self):
        input_directory = self.input_dir_input.text()
        output_directory = self.output_dir_input.text()
        prompt_text = self.prompt_input.toPlainText()
        api_key = self.api_key_input.text()
        category_input = self.category_input.text()
        
        # 创建后台线程
        self.analyze_thread = AnalyzeThread(input_directory, output_directory, prompt_text, api_key, category_input)

        # 连接信号
        self.analyze_thread.update_signal.connect(self.update_output_text)
        self.analyze_thread.image_signal.connect(self.update_image)
        # 启动线程
        self.analyze_thread.start()
        
    def update_output_text(self, text):
        # 更新 QTextEdit
        self.button_output.setText(text)  # 使用append()添加新文本
        
    def update_image(self, image_path):
        # 显示图像
        pixmap = QPixmap(image_path)
        
        # 计算 QLabel 的大小
        label_size = self.image_output.size()
        
        # 进行缩放
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.FastTransformation)
        
        # 更新 QLabel 显示的图像
        self.image_output.setPixmap(scaled_pixmap)
        
    def copy_media(self):
        global global_file_path
        copy_files_from_csv(global_file_path)
        self.button_output.setText("素材拷贝完成！")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
