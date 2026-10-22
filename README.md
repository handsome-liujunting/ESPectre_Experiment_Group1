# ESPectre 室内运动检测实验

**小组成员**：刘俊廷、袁培淞
**实验设备**：ESP32-C6 (统一设备ID) + Windows + Python 3.11

## 实验进度
1. 成功完成 ESP32 局域网配网。
2. 成功采集 `motion`（运动）和 `static_presence`（静止）原始 CSI 数据。
3. 成功运行数据特征提取管线。
4. 模型训练已跑通（3-fold 分组 CV F1≈76.3%），但**部署安全门未通过、尚未导出可用模型，模型仍在调试中**（见 `results/TRAINING_RESULT.txt`）。

## 目录说明
- `code/`：数据加载与模型训练脚本。
- `data/`：截取的原始 CSI 数据样本（.npz格式）。
- `results/`：训练成绩记录及数据质量校验报告。

## 说明
- 数据包较短（约 600 包/文件，60 s @ 10 pps），低于仓库校验的 5000 包门槛，故 `validate_dataset_quality.py` 报告 `packet_count` FAIL；这不阻止特征提取与训练。
- 训练可正常跑通并给出 3-fold 分组 CV 指标，但由于数据量小、部署安全门（FP/Recall/Occupancy）未达标，训练脚本未导出运行时模型产物（.onnx/.pt）。
- 复现：`python tools/validate_dataset_quality.py`；`python tools/train_ml_model.py`。
