# 机器视觉学习笔记与实验

> 从零开始系统学习机器视觉核心知识，配合代码实践加深理解

## 笔记目录

| 笔记 | 内容 | 配套实验 |
|------|------|---------|
| [01-图像预处理](./01-图像预处理.md) | 灰度化、滤波、直方图均衡化、形态学 | threshold_demo.py, morphology_demo.py |
| [02-边缘检测](./02-边缘检测.md) | Sobel、Canny、边缘连接 | edge_detection_demo.py |
| [03-特征提取](./03-特征提取.md) | 角点检测、轮廓分析、模板匹配 | — |
| [04-相机与镜头选型](./04-相机与镜头选型.md) | 相机分类、镜头参数、视野计算 | — |
| [05-光源选型](./05-光源选型.md) | 光源类型、打光方式、典型场景 | — |

## 学习路径建议

```
基础夯实 ──→ 核心技能 ──→ 进阶方向
  图像处理      边缘检测      深度学习视觉
  滤波去噪      轮廓分析        Halcon
  直方图        特征提取        3D视觉
  形态学        模板匹配        视觉定位
```

## 配套实验

```bash
# 阈值分割实验
python experiments/threshold_demo.py

# 形态学操作实验
python experiments/morphology_demo.py

# 边缘检测对比实验
python experiments/edge_detection_demo.py
```
