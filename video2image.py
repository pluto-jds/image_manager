import cv2
import os
from pathlib import Path

def save_video_frames(video_path, output_dir, frame_count=4):
    # 创建以视频文件名为名的目录
    video_name = video_path.stem
    video_output_dir = os.path.join(output_dir, video_name)
    os.makedirs(video_output_dir, exist_ok=True)

    # 读取视频文件
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return

    # 获取视频的总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_step = total_frames // frame_count  # 计算每隔多少帧取一帧

    # 遍历指定帧数并保存图片
    number_to_letter = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g'}
    for i in range(frame_count):
        # 设置视频的当前帧位置
        frame_id = i * frame_step
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)

        # 读取当前帧
        ret, frame = cap.read()
        if not ret:
            print(f"无法读取帧 {frame_id} 从视频文件: {video_path}")
            continue

        # 保存帧为JPEG格式
        output_image_path = os.path.join(video_output_dir, f"frame_{number_to_letter[i]}_{frame_id}.jpg")
        cv2.imwrite(output_image_path, frame)
        print(f"已保存帧 {frame_id} 为: {output_image_path}")

    cap.release()
    return video_output_dir

def process_directory(input_dir, output_dir, frame_count=4):
    # 遍历目录并查找视频文件
    for file_path in Path(input_dir).rglob('*'):
        sample_video(file_path, output_dir, frame_count)

def sample_video(file_path, output_dir, frame_count=4):
    # 支持的扩展名（视频文件格式）
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')
    file_path = Path(file_path)
    if file_path.suffix.lower() in video_extensions:
        print(f"处理视频文件: {file_path}")
        video_output_dir = save_video_frames(file_path, output_dir, frame_count)
        return video_output_dir
    else:
        print("not suport")
        return None

if __name__ == '__main__':
    input_video = "./test_image/2203e97720bd7b73ddf5298a02739d54(1)(1).mp4"  # 替换为你的视频文件所在目录
    output_directory = "./video_sample_image"  # 替换为你希望保存图片的输出目录

    # 处理指定目录下的视频文件
    video_output_dir = sample_video(input_video, output_directory)
    print(video_output_dir)
