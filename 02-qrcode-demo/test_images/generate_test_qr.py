"""生成二维码测试图 — 用于二维码定位识别Demo验证

生成包含二维码的测试图像，支持多角度、多场景模拟。

用法：
    python generate_test_qr.py

依赖：
    pip install opencv-python pillow qrcode
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_images")

# 尝试导入 qrcode 库（如果没安装，用替代方案）
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("[提示] qrcode 库未安装，将生成模拟二维码图案")


def make_qr_code(data="https://github.com", box_size=3, border=2):
    """用 qrcode 库生成二维码 PIL Image"""
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def draw_simulated_qr(size=180):
    """模拟二维码图案（当 qrcode 库不可用时）"""
    img = Image.new("L", (size, size), 255)
    draw = ImageDraw.Draw(img)
    np.random.seed(42)
    # 绘制类似 QR 码的方格图案
    block = size // 21
    for r in range(21):
        for c in range(21):
            if np.random.random() > 0.5:
                x0, y0 = c * block, r * block
                draw.rectangle([x0, y0, x0 + block, y0 + block], fill=0)
    # 三个定位图案（QR 码特征）
    for (cx, cy) in [(3, 3), (3, 17), (17, 3)]:
        draw.rectangle([(cx - 2) * block, (cy - 2) * block,
                        (cx + 3) * block, (cy + 3) * block], fill=0)
        draw.rectangle([(cx - 1) * block, (cy - 1) * block,
                        (cx + 2) * block, (cy + 2) * block], fill=255)
        draw.rectangle([cx * block, cy * block,
                        (cx + 1) * block, (cy + 1) * block], fill=0)
    return img


def embed_qr_on_background(qr_img, bg_size=(400, 400), angle=0):
    """将二维码贴在背景上，支持旋转"""
    bg = Image.new("L", bg_size, 200)
    # 添加噪点背景
    noise = np.random.normal(0, 15, (bg_size[1], bg_size[0])).astype(np.int16)
    bg_arr = np.array(bg, dtype=np.int16)
    bg_arr = np.clip(bg_arr + noise, 0, 255).astype(np.uint8)
    bg = Image.fromarray(bg_arr)

    if angle != 0:
        qr_img = qr_img.rotate(angle, expand=False, fillcolor=255)

    # 居中放置
    x = (bg_size[0] - qr_img.width) // 2
    y = (bg_size[1] - qr_img.height) // 2
    bg.paste(qr_img, (x, y))
    return np.array(bg)


def create_distorted_qr():
    """生成带倾斜/透视失真的二维码测试图"""
    if HAS_QRCODE:
        qr = make_qr_code("https://github.com/vision-learning", box_size=5)
    else:
        qr = draw_simulated_qr(180)
    qr = qr.convert("L").resize((200, 200), Image.LANCZOS)

    bg = Image.new("L", (400, 400), 220)
    bg_arr = np.array(bg, dtype=np.uint8)

    # 在随机位置放置（模拟透视效果用仿射变换简化）
    pts_src = np.float32([[0, 0], [200, 0], [0, 200], [200, 200]])
    offset_x, offset_y = 60, 80
    pts_dst = np.float32([
        [offset_x, offset_y],
        [offset_x + 180, offset_y + 10],
        [offset_x + 10, offset_y + 180],
        [offset_x + 170, offset_y + 170],
    ])

    # 用 OpenCV 做透视变换（如果有 cv2）
    try:
        import cv2
        qr_arr = np.array(qr)
        M = cv2.getPerspectiveTransform(pts_src, pts_dst)
        warped = cv2.warpPerspective(qr_arr, M, (400, 400), borderValue=220)
        # 合成
        mask = warped < 220
        bg_arr[mask] = warped[mask]
    except ImportError:
        # 没有 OpenCV 时直接居中放
        bg_arr[100:300, 100:300] = np.array(qr)

    return bg_arr


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 生成各种测试图
    test_cases = []

    if HAS_QRCODE:
        # 正常二维码
        qr_normal = make_qr_code("https://github.com", box_size=5)
        qr_normal = qr_normal.convert("L").resize((200, 200), Image.LANCZOS)
        test_cases.append(("qr_normal.png",
                          embed_qr_on_background(qr_normal)))

        # 旋转 15 度
        test_cases.append(("qr_rotated_15.png",
                          embed_qr_on_background(qr_normal, angle=15)))

        # 旋转 30 度
        test_cases.append(("qr_rotated_30.png",
                          embed_qr_on_background(qr_normal, angle=30)))
    else:
        sim = draw_simulated_qr()
        test_cases.append(("qr_simulated.png",
                          embed_qr_on_background(sim)))

    # 透视失真
    test_cases.append(("qr_distorted.png", create_distorted_qr()))

    for name, arr in test_cases:
        path = os.path.join(OUTPUT_DIR, name)
        Image.fromarray(arr).save(path)
        print(f"  ✓ {name}  ({arr.shape[1]}x{arr.shape[0]}px)")

    print(f"\n所有测试图已生成至: {OUTPUT_DIR}")
