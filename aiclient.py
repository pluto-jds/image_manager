import base64
import yaml
from openai import OpenAI
import os
from video2image import sample_video
from utils import iterate_media_files

class ChatBot:
    def __init__(self, api_key, base_url):
        """初始化，接收API Key、Base URL和提示词"""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    def chat_something(self, prompt_txt, content_txt):
        completion = self.client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {
                    "role": "system",
                    "content": [{"type":"text","text": prompt_txt}]  # 使用初始化时传入的提示词
                },
                {"role": "user","content": [
                    {
                        "type": "text",
                        "text": content_txt
                    },
                ]}
            ]
        )
        # 获取返回的内容
        result_text = completion.choices[0].message.content
        
        return result_text
        
class ImageAnalyzer:
    def __init__(self, api_key, base_url, prompt_text):
        """初始化，接收API Key、Base URL和提示词"""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.prompt_text = prompt_text  # 提示词在初始化时传入
        self.is_video = False
        self.video_first_frame_path = None

    def encode_image(self, image_path):
        """将图像编码为Base64格式，并根据后缀修改配置"""
        # 获取图片文件后缀名
        file_extension = image_path.split('.')[-1].lower()

        # 支持的图像格式
        valid_formats = ['jpg', 'jpeg', 'png', 'webp']
        
        if file_extension not in valid_formats:
            raise ValueError(f"不支持的文件格式: {file_extension}. 请使用jpg, jpeg, png, 或 webp格式的图片。")

        # 将图片编码为Base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        # 根据文件后缀动态设置格式
        image_url = f"data:image/{file_extension};base64,{base64_image}"
        
        return image_url

    def make_video_array(self, image_array_dir):
        """遍历目录并将图像文件编码为Base64，并存入数组"""
        image_array = []  # 用于存储所有Base64编码的图像
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']  # 支持的图像格式
        
        # 遍历目录
        for root, _, files in os.walk(image_array_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # 检查文件扩展名是否符合支持格式
                if any(file.lower().endswith(ext) for ext in valid_extensions):
                    try:
                        # 编码图像并添加到数组
                        print(file_path)
                        base64_image = self.encode_image(file_path)
                        image_array.append(base64_image)
                    except ValueError as e:
                        print(f"跳过文件 {file}: {e}")
        print(len(image_array))
        return image_array

    def analyze_medio(self, path, suffix):
        suffix = suffix.lower()
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')
        yaml_content = None
        
        if suffix in image_extensions:
            print("image:",path)
            yaml_content = self.analyze_image(path)
            self.is_video = False
        elif suffix in video_extensions:
            self.is_video = True
            output_directory = "./video_sample_image"
            video_sampe_dir = sample_video(path, output_directory)
            print("video:",video_sampe_dir)
            self.video_first_frame_path = video_sampe_dir + "//" + "frame_a_0.jpg"
            yaml_content = self.analyze_video(video_sampe_dir)
        else:
            print("not support ",suffix)
            self.is_video = False
        return yaml_content

    def analyze_video(self, image_array_dir):
    
        video_image_array = self.make_video_array(image_array_dir)
        
        completion = self.client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {
                    "role": "system",
                    "content": [{"type":"text","text": self.prompt_text}]  # 使用初始化时传入的提示词
                },
                {"role": "user","content": [
                    {
                        "type": "video",
                        "video": video_image_array
                    },
                ]}
            ]
        )
        # 获取返回的内容
        yaml_content = completion.choices[0].message.content
        
        # 提取并解析yaml格式内容
        return self.parse_yaml_to_dict(yaml_content)
        

    def analyze_image(self, image_path):
        """分析单张图片并返回分析结果"""
        # 将图片编码为Base64，并获取配置好的URL
        image_url = self.encode_image(image_path)

        # 调用 OpenAI API 进行图像分析
        completion = self.client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {
                    "role": "system",
                    "content": [{"type":"text","text": self.prompt_text}]  # 使用初始化时传入的提示词
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
        )

        # 获取返回的内容
        yaml_content = completion.choices[0].message.content
        
        # 提取并解析yaml格式内容
        return self.parse_yaml_to_dict(yaml_content)

    def clean_yaml_content(self, yaml_content):
            """去除yaml标记并清理字符串"""
            # 去除开头和结尾的```yaml和```
            cleaned_content = yaml_content.strip()
            if cleaned_content.startswith('```yaml'):
                cleaned_content = cleaned_content[7:].strip()  # 去掉 ```yaml
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3].strip()  # 去掉 ```
            return cleaned_content

    def parse_yaml_to_dict(self, yaml_content):
        """解析yaml格式的内容并返回字典"""
        try:
            # 将yaml内容加载为字典
            print(yaml_content)
            clean_yaml_content = self.clean_yaml_content(yaml_content)
            parsed_dict = yaml.safe_load(clean_yaml_content)
            return parsed_dict
        except yaml.YAMLError as e:
            print(f"YAML解析错误: {e}")
            return {}

# 示例：如何使用该类来分析图片
if __name__ == '__main__':
    api_key = "sk-xx"  # 替换为你的API Key
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 你的API Base URL
    chatbot = ChatBot(api_key, base_url)
    prompt_text = """你是一个自媒体素材库AI助手，你根据用户提供的素材分类标签，总结6字以内的用户素材库主题。注意仅输出素材库主题"""
    content_text = """发际线 头顶 生发产品 生发液 生发食品 医院和药物 整体发量 头皮按摩 掉发 截图 其他"""
    title_text = chatbot.chat_something(prompt_text, content_text)
    print(title_text)

    '''
    # 设置用户自定义的提示词
    prompt_text = """你是一个头发护理自媒体素材库AI助手，需要按照要求分析图片或者视频内容，并对他们分类。类别包括发际线、头顶、生发产品、生发液、生发食品、医院和药物、整体发量、头皮按摩、掉发、截图和其他。
输出格式为yaml 
image_describe:描述图片或者视频中的场景和人物，特别是与头发护理相关的内容，严格包括以下方面：
    1. 发际线状况，发际线深还是正常，发际线深表示额头头发少，是否是M型发际线
    2. 头顶的发量和密度
    3. 是否使用或展示了生发产品或生发液
    4. 与生发食品相关的元素
    5. 是否涉及医院或药物
    6. 整体发量的视觉效果
    7. 是否有头皮按摩的情景
    8. 掉发的具体表现
    9. 其他与头发护理相关的内容
    请尽可能详细地描述图片或者视频中的每个要素，以帮助分类到合适的标签。
image_label:以数组方式给2个标签
image_title:结合image_describe为图片或者视频生成小于20字的标题"""
    
    # 创建 ImageAnalyzer 实例
    analyzer = ImageAnalyzer(api_key, base_url, prompt_text)
    
    # 指定图片路径并进行分析
    #result = analyzer.analyze_image(r"test_image\0a4d831529ef206c398da4b0a333bd2a.jpg")
    
    # 打印解析后的字典结果
    #print(result)
    
    input_directory = './test_image'
    output__directory = "./image"
    for name, path, suffix in iterate_media_files(input_directory):
        print(f"Path: {path}, Name: {name}, Extension: {suffix}")
            
        result = analyzer.analyze_medio(path, suffix)
        print(result)
    '''
