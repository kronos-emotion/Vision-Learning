# 工件尺寸测量原型

> 基于OpenCV的边缘检测与像素当量测量

## 项目目标

实现工业视觉检测中典型的尺寸测量流水线：**图像采集 → 预处理 → 边缘提取 → 轮廓分析 → 尺寸计算**。

## 工作流程

```
输入图像 → 高斯滤波 → CLAHE增强 → Canny边缘检测
    → 形态学闭运算 → 轮廓查找 → 轮廓筛选
    → 像素当量标定 → 几何尺寸计算 → 结果可视化
```

## 关键概念

### 像素当量（Pixel / mm）
相机测量的本质是**像素计数**，必须通过参考物体换算为物理尺寸：
```
pixel_per_mm = 参考物体的像素宽度 / 参考物体的实际宽度(mm)
```

### 预处理为什么重要？
- **高斯滤波**：消除传感器噪声，避免Canny检测到假边缘
- **CLAHE增强**：改善光照不均场景，让边缘更清晰
- **形态学闭运算**：连接断裂边缘（先膨胀后腐蚀），让轮廓闭合

## 用法

```bash
# 1. 生成合成测试图
python test_images/generate_samples.py

# 2. 运行测量
python measurement.py

# 3. 用自己的图片测量
python measurement.py --image 你的工件照片.jpg --known-size 50
```

## 结果示例

运行后会显示三个窗口：
- **Original + Measurements**：标注了尺寸的原图
- **Edges (Canny)**：Canny边缘检测结果
- **Closed (Morph)**：闭运算后的连通轮廓

按任意键关闭窗口，结果自动保存为 `result_*.png`。

## 进阶练习

1. **换阈值**：调整 `CANNY_THRESH_LOW/HIGH`，观察边缘检测变化
2. **换测试图**：用 `part_washer.png` 或 `part_multi.png` 运行
3. **不均匀光照**：`part_rect_lighting.png` 测试CLAHE的效果
4. **真实物体**：拍一个硬币（已知直径25mm），用 `--known-size 25` 测量
