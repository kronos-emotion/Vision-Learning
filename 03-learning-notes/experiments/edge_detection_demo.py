"""边缘检测对比实验 — Sobel vs Canny vs Laplacian

在相同输入下对比三种边缘检测算法的表现，
直观理解为什么 Canny 是工业视觉的首选。
"""

import cv2
import numpy as np


def create_test_image():
    """创建包含各种边缘特征的测试图"""
    img = np.zeros((400, 500), dtype=np.uint8)

    # 不同角度的直线边缘
    cv2.line(img, (50, 80), (200, 80), 200, 2)    # 水平线
    cv2.line(img, (50, 120), (200, 120), 200, 2)
    cv2.line(img, (80, 30), (80, 180), 200, 2)    # 垂直线

    # 斜线
    cv2.line(img, (50, 200), (200, 350), 200, 2)

    # 圆形
    cv2.circle(img, (350, 100), 60, 200, 2)

    # 填充矩形（测试区域边缘 vs 内部）
    cv2.rectangle(img, (280, 200), (450, 350), 200, -1)

    # 渐变边缘（测试对弱边缘的响应）
    for i in range(40):
        y = 360 + i
        cv2.line(img, (50, y), (450, y), max(0, 200 - i * 5), 1)

    # 添加高斯噪声
    noise = np.random.normal(0, 15, img.shape).astype(np.int16)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)

    return img


def main():
    img = create_test_image()

    # 高斯滤波（所有方法都需要）
    blurred = cv2.GaussianBlur(img, (5, 5), 0)

    # 各边缘检测方法
    edges_sobel_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    edges_sobel_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    edges_sobel = cv2.magnitude(edges_sobel_x, edges_sobel_y)
    edges_sobel = np.uint8(np.clip(edges_sobel, 0, 255))

    edges_laplacian = cv2.Laplacian(blurred, cv2.CV_64F, ksize=3)
    edges_laplacian = np.uint8(np.clip(np.abs(edges_laplacian), 0, 255))

    edges_canny = cv2.Canny(blurred, 50, 150)

    # 展示对比
    results = [
        ("Original", img),
        ("Sobel (Gradient Mag)", edges_sobel),
        ("Laplacian", edges_laplacian),
        ("Canny (推荐)", edges_canny),
    ]

    for i, (name, result) in enumerate(results):
        display = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        cv2.putText(display, name, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 加一行说明文字
        notes = {
            "Original": "含直线/圆/矩形/渐变/噪声",
            "Sobel (Gradient Mag)": "边缘较粗，对噪声敏感",
            "Laplacian": "对噪声极敏感，双边缘效应",
            "Canny (推荐)": "边缘细、连续、噪声抑制好",
        }
        cv2.putText(display, notes.get(name, ""), (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1)

        cv2.imshow(f"Edge Detection {i + 1}", display)
        cv2.moveWindow(f"Edge Detection {i + 1}", i * 330, 0)

    print("边缘检测对比结果：")
    print("  Sobel → 边缘粗，对噪声敏感，双边缘效应")
    print("  Laplacian → 对噪声极敏感，定位不准")
    print("  Canny → 边缘细且连续，噪声抑制好 ← 工业首选")
    print("\n特别注意渐变区域（图像底部）的响应差异")
    print("按任意键退出...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
