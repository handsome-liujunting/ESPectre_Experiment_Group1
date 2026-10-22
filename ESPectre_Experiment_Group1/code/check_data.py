import numpy as np
import glob
import os
import sys
import io

# 解决 Windows 终端中文乱码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 自动找到 data/motion 文件夹下的第一个 npz 文件
search_path = os.path.join("data", "motion", "*.npz")
file_list = glob.glob(search_path)

if not file_list:
    print("❌ 没找到文件，请检查路径是否正确。")
else:
    file_path = file_list[0]
    print(f"✅ 正在加载文件: {file_path}\n")

    # 2. 加载数据
    with np.load(file_path) as data:
        print("📦 文件中包含的数组 (Keys):", data.files)
        
        # 3. 提取原始数据 (注意键名是 csi_data)
        if 'csi_data' in data.files:
            csi_data = data['csi_data']
            print("\n📊 CSI 数据形状 (Shape):", csi_data.shape)
            print("🔢 数据类型 (dtype):", csi_data.dtype)
            
            # 打印第一帧数据的部分值看看长啥样
            print("\n👀 数据预览 (第一帧的前5个值):")
            print(csi_data[0, :5])
            
            # 顺便看看标签
            if 'label' in data.files:
                 print("\n🏷️ 标签:", data['label'])
        else:
            print("⚠️ 没找到 'csi_data' 这个键，请查看上面的 Keys 列表。")