"""生成合成工件测试图 — 用于尺寸测量原型验证

在没有真实相机的情况下，用 NumPy + Pillow 生成模拟的
"金属工件"图像，包含已知尺寸的几何形状，便于调试测量算法。

生成的图像特征：
- 深色背景上的浅色"金属"工件
- 包含矩形、圆形、六边形等多种形状
- 可添加模拟噪声和光照不均匀

用法：
    python generate_samples.py

输出：
    ./test_images/ 目录下生成 part_*.png 多张测试图
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_images")


def create_test_part_rect():
    """生成矩形工件：80x60px 的金属块"""
    img = np.full((200, 280), 60, dtype=np.uint8)  # 深灰背景
    # 加一点高斯噪声
    noise = np.random.normal(0, 8, img.shape).astype(np.int16)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)

    # 绘制矩形"工件"
    cv = np.zeros((200, 280), dtype=np.uint8)
    cv = Image.fromarray(cv)
    draw = ImageDraw.Draw(cv)
    draw.rectangle([40, 30, 200, 150], fill=180)  # 浅灰工件
    # 内部挖一个圆孔（模拟特征）
    draw.ellipse([90, 60, 150, 120], fill=60)
    cv = np.array(cv)

    # 合成：背景上叠加工件
    mask = cv > 0
    img[mask] = cv[mask]
    return img


def create_test_part_washer():
    """生成垫片状工件：外圆内圆"""
    img = np.full((240, 240), 55, dtype=np.uint8)
    noise = np.random.normal(0, 10, img.shape).astype(np.int16)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)

    cv = np.zeros((240, 240), dtype=np.uint8)
    cv = Image.fromarray(cv)
    draw = ImageDraw.Draw(cv)
    # 外圆
    draw.ellipse([20, 20, 220, 220], fill=200)
    # 内孔
    draw.ellipse([80, 80, 160, 160], fill=55)
    cv = np.array(cv)

    mask = cv > 0
    img[mask] = cv[mask]
    return img


def create_test_part_multi():
    """生成包含多个特征的复杂工件"""
    img = np.full((240, 320), 50, dtype=np.uint8)
    noise = np.random.normal(0, 6, img.shape).astype(np.int16)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)

    cv = np.zeros((240, 320), dtype=np.uint8)
    cv = Image.fromarray(cv)
    draw = ImageDraw.Draw(cv)

    # 主基底 — 矩形
    draw.rectangle([30, 20, 290, 220], fill=170)
    # 左上圆孔
    draw.ellipse([50, 40, 110, 100], fill=50)
    # 右下矩形槽
    draw.rectangle([180, 130, 260, 200], fill=50)
    # 右侧半圆槽
    draw.ellipse([220, 60, 280, 120], fill=50)

    cv = np.array(cv)
    mask = cv > 0
    img[mask] = cv[mask]
    return img


def add_lighting_gradient(img):
    """模拟不均匀光照 — 从左到右渐暗"""
    h, w = img.shape
    gradient = np.tile(np.linspace(1.0, 0.65, w), (h, 1))
    return np.clip(img * gradient, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 生成测试图
    parts = [
        ("part_rect.png", create_test_part_rect()),
        ("part_washer.png", create_test_part_washer()),
        ("part_multi.png", create_test_part_multi()),
        ("part_rect_lighting.png",
         add_lighting_gradient(create_test_part_rect())),
    ]

    for name, arr in parts:
        path = os.path.join(OUTPUT_DIR, name)
        Image.fromarray(arr).save(path)
        print(f"  ✓ {name}  ({arr.shape[1]}x{arr.shape[0]}px)")

    print(f"\n所有测试图已生成至: {OUTPUT_DIR}")
    print("运行 python measurement.py 开始测量")
