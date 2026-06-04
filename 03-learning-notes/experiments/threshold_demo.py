"""阈值分割实验 — 对比不同阈值方法的效果

演示：全局阈值、Otsu、自适应阈值在光照均匀/不均场景下的差异。
用合成图像展示每种方法的优缺点。
"""

import cv2
import numpy as np


def create_test_images():
    """创建测试图像：均匀光照 + 不均匀光照"""
    # 1. 均匀光照图像
    img1 = np.zeros((300, 400), dtype=np.uint8)
    img1[50:250, 80:320] = 150
    noise = np.random.normal(0, 20, img1.shape).astype(np.int16)
    img1 = np.clip(img1 + noise, 0, 255).astype(np.uint8)

    # 2. 不均匀光照（从左到右渐暗）
    gradient = np.tile(np.linspace(1.0, 0.4, 400), (300, 1))
    img2 = np.clip(img1 * gradient, 0, 255).astype(np.uint8)

    return img1, img2


def main():
    img1, img2 = create_test_images()

    # 各种阈值方法
    methods = [
        ("Global (127)", lambda x: cv2.threshold(x, 127, 255,
                                                  cv2.THRESH_BINARY)[1]),
        ("Otsu", lambda x: cv2.threshold(x, 0, 255,
                                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
        ("Adaptive Mean",
         lambda x: cv2.adaptiveThreshold(x, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY, 21, 5)),
        ("Adaptive Gaussian",
         lambda x: cv2.adaptiveThreshold(x, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 21, 5)),
    ]

    for name, func in methods:
        r1 = func(img1)
        r2 = func(img2)
        stack = np.hstack([r1, r2])
        cv2.imshow(f"{name}  (均匀 | 不均匀光照)", stack)

    # 显示原图做对比
    orig = np.hstack([img1, img2])
    cv2.imshow("Original (均匀 | 不均匀光照)", orig)

    print("观察不同阈值方法对光照变化的敏感程度")
    print("自适应阈值对不均匀光照的适应性明显更好")
    print("按任意键退出...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
