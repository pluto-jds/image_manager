#需要有提示词填写区、输入目录填写区域、输出目录填写区域，APIKey填写区域
#https://help.aliyun.com/zh/model-studio/user-guide/vision/?spm=0.0.0.i2
#https://zhuanlan.zhihu.com/p/719272755
#nuitka --include-data-dir="C:/Users/x/Anaconda3/envs/video/Lib/site-packages/gradio/icons=gradio/icons" --onefile --standalone ui_main.py

import gradio as gr
import os
import shutil
from pathlib import Path
from database import create_csv,append_to_csv,find_by_name
from utils import iterate_media_files
from aiclient import ImageAnalyzer,ChatBot

from datetime import datetime
from move2dir import copy_files_from_csv
import time

global_file_path = ""

# 假设你已经有图片解析和图片拷贝的函数
def analyze_medio(input_directory, output_dir_input, prompt_text, api_key, category_input):
    global global_file_path

    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    analyzer = ImageAnalyzer(api_key, base_url, prompt_text)
    directory = './database'  # 替换为你需要存放CSV的目录路径
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'media_info_{current_time}.csv'  # CSV文件名称
    headers = ['Name', 'Path', 'Extension', 'Content', 'Categorys','NewName', 'NewPath']
    create_csv(directory, filename, headers)
    global_file_path = directory+"/"+filename

    for name, path, suffix in iterate_media_files(input_directory):

        # 指定图片路径并进行分析
        result = analyzer.analyze_medio(path, suffix)
        
        # 打印解析后的字典结果
        debug_info = f"Path: {path}, Name: {name}, Extension: {suffix}，Content： {result}"
        yield debug_info
        print(debug_info)
        fit_cls = result['image_label'][0]
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = output_dir_input+"/"+fit_cls+"/"+result['image_title']+current_time + suffix

        row_data = [name,path,suffix, result['image_describe'], ", ".join(result['image_label']), result['image_title'], new_path]
        append_to_csv(global_file_path, row_data)
    
    yield "完成素材解析，可以开始素材拷贝，在database目录的csv文件查看准备拷贝的信息"

def copy_medio():
    global global_file_path
    copy_files_from_csv(global_file_path)
    return "完成素材拷贝"

def generate_prompt(category_input):
    global prompt_template
    api_key = "sk-xx"  # 替换为你的API Key
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


prompt_template = """你是一个{0}素材库AI助手，需要按照要求分析图片或者视频内容，并对他们分类。类别包括{1}。
输出格式为yaml 
image_describe:描述图片或者视频中的场景和人物，特别是{2}相关的内容，严格包括以下方面：
{3}
请尽可能详细地描述图片或者视频中的每个要素，以帮助分类到合适的标签。
image_label:以数组方式给出最合适的2个标签
image_title:结合image_describe为图片或者视频生成小于20字的标题"""

categroy_default="""发际线 头顶 生发产品 生发液 生发食品 医院和药物 整体发量 头皮按摩 掉发 截图 其他"""

api_key_debug = "sk-xx"  # 替换为你的API Key
input_directory_default = './test_image'
output_directory_default = "./image"

def create_gradio_ui():
    with gr.Blocks() as demo:
    
        # 创建一个行布局
        with gr.Row():
            with gr.Column():
                category_input = gr.Textbox(label="类别", placeholder="请输入类别以空格分隔，例如：发际线 头顶 生发产品 其他", lines=1, value=categroy_default)
                prompt_input = gr.Textbox(label="提示词", placeholder="请输入提示词，例如：图片分析", lines=4)
                prompt_button = gr.Button("给出素材分析提示词")
                prompt_button.click(fn=generate_prompt, inputs=[category_input], outputs=prompt_input)
                button_output = gr.Textbox(label="步骤结果", lines=2, interactive=False)
            with gr.Column():
                input_dir_input = gr.Textbox(label="输入目录", placeholder="请输入输入目录路径", lines=1, value=input_directory_default)
                output_dir_input = gr.Textbox(label="输出目录", placeholder="请输入输出目录路径", lines=1, value=output_directory_default)
                api_key_input = gr.Textbox(label="API Key", placeholder="请输入API Key", lines=1, value=api_key_debug)

                # 第二部分：生成图片解析按钮
                analyze_button = gr.Button("步骤1 生成素材解析")
                # 按钮点击后执行的操作
                analyze_button.click(fn=analyze_medio, inputs=[input_dir_input, output_dir_input, prompt_input, api_key_input, category_input], outputs=button_output)
                
                # 第三部分：完成图片拷贝按钮
                copy_button = gr.Button("步骤2 完成素材拷贝")
                # 按钮点击后执行的操作
                copy_button.click(fn=copy_medio, inputs=[], outputs=button_output)

    return demo


# 启动Gradio应用
if __name__ == "__main__":
    demo = create_gradio_ui()
    demo.launch()
