import csv
import os
import shutil

def copy_files_from_csv(csv_file_path):
    # 打开CSV文件并读取内容
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # 遍历每一行
        for row in reader:
            # 从 CSV 行中获取 Path 和 NewPath 列的值
            source_path = row['Path']
            destination_path = row['NewPath']
            
            # 检查源文件是否存在
            if not os.path.exists(source_path):
                print(f"源文件不存在: {source_path}")
                continue

            destination_dir = os.path.dirname(destination_path)
            # 检查目标目录是否存在，不存在则创建
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
                print(f"创建目标目录: {destination_dir}")

            # 如果目标文件已经存在，则跳过
            if os.path.exists(destination_path):
                print(f"目标文件已存在，跳过拷贝: {destination_path}")
                continue

            # 拷贝文件到目标路径
            try:
                shutil.copy2(source_path, destination_path)
                print(f"已成功将文件从 {source_path} 拷贝到 {destination_path}")
            except Exception as e:
                print(f"拷贝文件 {source_path} 到 {destination_path} 时发生错误: {e}")

if __name__ == '__main__':
    csv_file_path = './database/media_info_20250204.csv'  # 替换为你自己的CSV文件路径
    copy_files_from_csv(csv_file_path)
