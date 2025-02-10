from pathlib import Path
from database import create_csv,append_to_csv,find_by_name
from utils import iterate_media_files
from aiclient import ImageAnalyzer

from datetime import datetime
from move2dir import copy_files_from_csv


if __name__ == '__main__':

    api_key = "sk-xx"  # 替换为你的API Key
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 你的API Base URL
    
    # 设置用户自定义的提示词
    prompt_text = """你是一个头发护理自媒体素材库AI助手，需要按照要求分析图片或者视频内容，并对他们分类。类别包括发际线、头顶、生发产品、生发液、生发食品、医院和药物、整体发量、头皮按摩、掉发、截图和其他。
输出格式为yaml 
image_describe:描述图片中的场景和人物，特别是与头发护理相关的内容，严格包括以下方面：
    1. 发际线状况，发际线深还是正常，发际线深表示额头头发少，是否是M型发际线
    2. 头顶的发量和密度
    3. 是否使用或展示了生发产品或生发液
    4. 与生发食品相关的元素
    5. 是否涉及医院或药物
    6. 整体发量的视觉效果
    7. 是否有头皮按摩的情景
    8. 掉发的具体表现
    9. 图片是否为手机截屏
    10. 其他与头发护理相关的内容
    请尽可能详细地描述图片中的每个要素，以帮助分类到合适的标签。
image_label:以数组方式给2个图片标签
image_title:结合image_describe为图片生成小于20字的标题"""
    
    # 创建 ImageAnalyzer 实例
    analyzer = ImageAnalyzer(api_key, base_url, prompt_text)
    
    directory = './database'  # 替换为你需要存放CSV的目录路径
    filename = 'media_info_20250204.csv'  # CSV文件名称
    headers = ['Name', 'Path', 'Extension', 'Content', 'Categorys','NewName', 'NewPath']  # 用户提供的标签
    create_csv(directory, filename, headers)
    file_path = directory+"/"+filename

    labels = {
        "发际线": "hairline",
        "头顶": "top_of_the_head",
        "生发产品": "hair_growth_products",
        "生发液": "hair_growth_serum",
        "生发食品": "hair_growth_supplements",
        "医院和药物": "hospital_and_medications",
        "整体发量": "overall_hair_volume",
        "头皮按摩": "scalp_massage",
        "掉发": "hair_loss",
        "截图": "screenshot",
        "其他": "other"
    }


    input_directory = './test_image'
    output__directory = "./image"
    for name, path, suffix in iterate_media_files(input_directory):
        print(f"Path: {path}, Name: {name}, Extension: {suffix}")
        
        # 指定图片路径并进行分析
        result = analyzer.analyze_medio(path, suffix)
        
        # 打印解析后的字典结果
        print(result) 
        fit_cls = result['image_label'][0]
        
        label = labels[fit_cls]
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = output__directory+"/"+label+"/"+result['image_title']+current_time + suffix

        row_data = [name,path,suffix, result['image_describe'], ", ".join(result['image_label']), result['image_title'], new_path]
        append_to_csv(file_path, row_data)
        
        
    copy_files_from_csv(file_path)
