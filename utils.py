import os
from pathlib import Path
from database import create_csv,append_to_csv,find_by_name

def count_files(directory):
    file_count = 0
    for root, dirs, files in os.walk(directory):
        file_count += len(files)  # 统计当前目录中的文件数
    return file_count

def iterate_media_files(directory):
    # 创建Path对象
    dir_path = Path(directory)

    # 支持的图片和视频文件扩展名
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')

    # 遍历目录并检查文件扩展名
    for file_path in dir_path.rglob('*'):
        if file_path.suffix.lower() in image_extensions or file_path.suffix.lower() in video_extensions:
            # 规范化路径，确保没有多余的路径分隔符或无效字符
            valid_path = file_path.as_posix()  # 返回Unix样式的路径
            valid_file_name = file_path.name
            valid_extension = file_path.suffix

            # 可以根据需要返回绝对路径或者相对路径
            yield valid_file_name, valid_path, valid_extension


if __name__ == '__main__':

    directory = './database'  # 替换为你需要存放CSV的目录路径
    filename = 'media_info_20250204.csv'  # CSV文件名称
    headers = ['Name', 'Path', 'Extension', 'Content', 'Categorys','NewName', 'NewPath']  # 用户提供的标签
    create_csv(directory, filename, headers)

    file_path = directory+"/"+filename
    row_data = ['image1', '/path/to/image1.jpg', '.jpg', 'Image content here', 'hair,food', 'new_image1', '/path/to/new_image1.jpg']
    append_to_csv(file_path, row_data)

    directory = './test_image'
    for name, path, suffix in iterate_media_files(directory):
        print(f"Path: {path}, Name: {name}, Extension: {suffix}")
        row_data = [name,path,suffix]
        append_to_csv(file_path, row_data)
    find_by_name(file_path,'1a9a37d61ic472b538c6abd03c365224 (1).jpeg')
