# 二维码定位与识别Demo

> 基于OpenCV的图像中二维码检测、定位与解码

## 项目目标

实现"图像预处理 → 二维码定位 → 透视校正 → 解码"的完整流水线。理解机器视觉中**定位→校正→识别**的标准思维模式。

## 两种检测方法

### 1. OpenCV内置检测器（推荐）
OpenCV 4.5+ 内置的 `QRCodeDetector`，端到端完成检测+解码：
```
data, points, straight_qrcode = detector.detectAndDecode(image)
```
- `data`：解码后的字符串
- `points`：二维码四个角点坐标
- `straight_qrcode`：校正后的二维码图像

### 2. 基于轮廓分析的定位（教学备用）
展示了如何通过轮廓层级关系找到 QR 码的"回"字形定位图案——这是理解传统视觉定位思维的好例子。

## 用法

```bash
# 1. 生成测试二维码图
python test_images/generate_test_qr.py

# 2. 运行检测
python qrcode_detect.py

# 3. 测试旋转二维码
python qrcode_detect.py --image test_images/qr_rotated_30.png

# 4. 测试透视失真二维码
python qrcode_detect.py --image test_images/qr_distorted.png

# 5. 用轮廓法分析
python qrcode_detect.py --method contour
```

## 关键知识点

### 二维码的定位原理
QR 码的三个角落有"回"字形定位图案（7x7 黑白相间），即使二维码被旋转或部分遮挡，也能通过这些图案定位。

### 为什么需要预处理？
- **CLAHE增强**：改善光照不均，提高对比度
- **自适应阈值**：比固定阈值更适合光照变化场景

## 进阶练习

1. 用自己的手机拍二维码图片，放在各种背景下测试
2. 试试部分遮挡的二维码能否被检测到
3. 对比 `--method auto` 和 `--method contour` 的效果差异
