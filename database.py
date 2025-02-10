import os
import csv

def create_csv(directory_path, filename, headers):

    # 检查目标目录是否存在，不存在则创建
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"创建目标目录: {directory_path}")
        
    # 拼接完整的文件路径
    file_path = os.path.join(directory_path, filename)

        
    # 检查文件是否存在
    if not os.path.exists(file_path):
        # 如果文件不存在，则创建文件并写入表头
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 写入表头
            writer.writerow(headers)
        print(f"CSV 文件 '{filename}' 已创建，包含标签：{headers}")
    else:
        print(f"CSV 文件 '{filename}' 已存在，无需创建。")

def append_to_csv(file_path, row_data):
    # 检查文件是否存在
    file_exists = os.path.exists(file_path)
    if not file_exists:
        print(f"CSV 文件 '{file_path}' 不存在。")
    else:
        # 打开文件，'a'表示追加模式
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # 写入一行数据
            writer.writerow(row_data)
            print(f"已成功将数据插入文件：{file_path}")

def find_by_name(file_path, name):
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"CSV 文件 '{file_path}' 不存在。")
        return None
    
    # 打开文件并读取内容
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # 跳过表头
        for row in reader:
            if row[0] == name:  # 假设 Name 列是第2列（索引为1），你可以根据实际情况调整
                print(f"找到匹配的行数据：{row}")
                return row
    print(f"未找到 Name 为 '{name}' 的数据。")
    return None



if __name__ == '__main__':
    # 使用示例
    directory = './database'  # 替换为你需要存放CSV的目录路径
    filename = 'media_info_20250204.csv'  # CSV文件名称
    headers = ['Name', 'Path', 'Extension', 'Content', 'Categorys','NewName', 'NewPath']  # 用户提供的标签
    create_csv(directory, filename, headers)

    file_path = directory+"/"+filename
    row_data = ['image1', '/path/to/image1.jpg', '.jpg', 'Image content here', 'hair,food', 'new_image1', '/path/to/new_image1.jpg']
    append_to_csv(file_path, row_data)