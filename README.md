# Vision Learning · 机器视觉学习与实践

> 机器视觉调试工程师方向 · 自学项目 & 实验笔记

本仓库包含三个实践项目，覆盖机器视觉入门核心技能：**图像处理基础、目标定位与识别、测量检测**。每个项目均可独立运行，配有详细中文注释，适合求职作品集和自学练习。

---

## 项目概览

| 项目 | 说明 | 核心技能 |
|------|------|---------|
| [01-工件尺寸测量](./01-dimension-measurement/) | 基于OpenCV的工件边缘检测与尺寸测量原型 | 图像预处理、边缘检测、轮廓分析、像素当量标定 |
| [02-二维码定位识别](./02-qrcode-demo/) | 图像中QR码的定位框选、透视校正与解码 | 图像变换、特征定位、透视校正、条码解码 |
| [03-学习笔记与实验](./03-learning-notes/) | 机器视觉知识点整理与配套实验脚本 | 图像滤波、阈值分割、形态学、特征提取 |

---

## 环境配置

```bash
# 克隆仓库
git clone https://github.com/你的用户名/vision-learning.git
cd vision-learning

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import cv2; print('OpenCV', cv2.__version__)"
```

### 依赖清单

- Python 3.8+
- opencv-python
- numpy
- Pillow
- pyzbar（二维码识别用）

---

## 使用建议

1. **按顺序学习**：从项目1开始，理解图像处理基础流水线
2. **动手修改参数**：每个脚本顶部都有可调参数，试着改改看效果变化
3. **用自己的图片测试**：拍一些身边的工件或二维码，看看算法的鲁棒性
4. **配合笔记理解原理**：项目3的笔记解释了每个步骤背后的理论基础

---

## GitHub 提交建议

```bash
git init
git add .
git commit -m "init: 机器视觉学习项目 - 尺寸测量、二维码识别、学习笔记"
git branch -M main
git remote add origin https://github.com/你的用户名/vision-learning.git
git push -u origin main
```

---

*持续更新中 · 欢迎Star*
