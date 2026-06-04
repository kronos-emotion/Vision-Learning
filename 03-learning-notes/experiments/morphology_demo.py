"""形态学操作实验 — 直观理解腐蚀、膨胀、开运算、闭运算

使用合成图像展示每种操作的数学效果。
"""

import cv2
import numpy as np


def create_test_image():
    """创建包含噪点和孔洞的测试图像"""
    img = np.zeros((300, 400), dtype=np.uint8)
    # 绘制矩形主体
    img[60:240, 80:320] = 255
    # 添加内部孔洞
    cv2.circle(img, (150, 150), 25, 0, -1)
    cv2.circle(img, (250, 150), 18, 0, -1)
    # 外部噪点（白色小点）
    np.random.seed(42)
    for _ in range(80):
        x, y = np.random.randint(0, 400, 2)
        if img[y, x] == 0:
            img[y, x] = 255
    return img


def main():
    img = create_test_image()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    operations = [
        ("Original", img),
        ("Erosion (腐蚀)\n缩小白色区域", cv2.erode(img, kernel, iterations=1)),
        ("Dilation (膨胀)\n扩大白色区域", cv2.dilate(img, kernel, iterations=1)),
        ("Opening (开运算)\n去白色噪点",
         cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)),
        ("Closing (闭运算)\n填黑色孔洞",
         cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)),
    ]

    for i, (name, result) in enumerate(operations):
        # 添加文字标签
        h, w = result.shape
        display = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        cv2.putText(display, name.split("\n")[0], (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        if "\n" in name:
            cv2.putText(display, name.split("\n")[1], (10, 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        cv2.imshow(f"Operation {i + 1}", display)
        # 移动到不同位置避免重叠
        cv2.moveWindow(f"Operation {i + 1}", i * 220, 0)

    print("观察每种形态学操作的效果：")
    print("  腐蚀 → 白色边界被"吃掉"一圈")
    print("  膨胀 → 白色边界向外扩张")
    print("  开运算 → 去掉了外部白点，保留了形状")
    print("  闭运算 → 填平了内部孔洞")
    print("\n按任意键退出...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
