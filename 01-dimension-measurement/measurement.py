"""工件尺寸测量原型 — 基于OpenCV的边缘检测与像素当量测量

实现了机器视觉检测中典型的"图像预处理→边缘提取→轮廓分析→
尺寸测量"流水线。代码带有详细中文注释，适合初学者理解每一步。

功能：
  1. 读取图像 → 预处理（滤波、增强）
  2. 边缘检测（Canny） + 轮廓查找
  3. 基于已知参考尺寸计算像素当量（pixel/mm）
  4. 输出工件关键尺寸（长、宽、直径等）

用法：
    python measurement.py [--image test_images/part_rect.png]

默认使用合成测试图，也可以用 --image 指定自己的工件照片。
"""

import argparse
import os
import cv2
import numpy as np


# ============================================================
#  可调参数（根据实际拍摄条件调整）
# ============================================================
GAUSSIAN_KERNEL = (5, 5)        # 高斯滤波核大小（奇数）
CANNY_THRESH_LOW = 50            # Canny 低阈值
CANNY_THRESH_HIGH = 150          # Canny 高阈值
CLOSE_KERNEL = (5, 5)            # 闭运算核（填充小孔）
# 如果使用自己的图，在这里填入已知参考尺寸（mm）
REFERENCE_OBJECT_MM = 30.0       # 参考物体的实际尺寸（mm）
MIN_CONTOUR_AREA = 500           # 最小轮廓面积（过滤噪点）


def preprocess(image):
    """预处理流水线：灰度 → 高斯滤波 → 增强对比度

    Args:
        image: BGR 彩色图像 (OpenCV 默认格式)

    Returns:
        预处理后的灰度图
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 高斯滤波：平滑噪声，避免边缘检测误检
    blurred = cv2.GaussianBlur(gray, GAUSSIAN_KERNEL, 0)
    # 自适应直方图均衡化（CLAHE）：增强局部对比度
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    return enhanced


def find_object_contour(processed):
    """边缘检测 + 轮廓查找 + 筛选

    Args:
        processed: 预处理后的灰度图

    Returns:
        最大轮廓的点集，以及绘制了轮廓的彩色图（用于可视化）
    """
    # 1. Canny 边缘检测
    edges = cv2.Canny(processed, CANNY_THRESH_LOW, CANNY_THRESH_HIGH)

    # 2. 闭运算：连接断裂边缘
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, CLOSE_KERNEL)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # 3. 查找轮廓
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("未找到任何轮廓，请调整 Canny 阈值")

    # 4. 按面积排序，取最大轮廓（假设是目标工件）
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    obj_contour = None
    for c in contours:
        if cv2.contourArea(c) > MIN_CONTOUR_AREA:
            obj_contour = c
            break

    if obj_contour is None:
        raise ValueError(f"未找到面积 > {MIN_CONTOUR_AREA} 的轮廓")

    # 5. 可视化
    #    将处理后的图像转回 BGR 用于绘制彩色轮廓
    vis = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(vis, [obj_contour], -1, (0, 255, 0), 2)

    return obj_contour, vis, edges, closed


def measure_dimensions(contour, pixel_per_mm):
    """测量轮廓的关键几何尺寸

    计算：
      - 外接矩形尺寸（宽度、高度）
      - 最小外接圆直径
      - 轮廓面积
      - 轮廓周长

    Args:
        contour: OpenCV 轮廓点集
        pixel_per_mm: 像素当量（pixels/mm）

    Returns:
        尺寸字典（单位：mm）
    """
    # 最小外接矩形（旋转矩形）
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    # 外接矩形宽高（去旋转 → 取长边为 length, 短边为 width）
    (w, h) = rect[1]
    if w < h:
        w, h = h, w  # w 为长边

    # 最小外接圆
    (x, y), radius = cv2.minEnclosingCircle(contour)

    # 轮廓面积（像素单位）
    area_px = cv2.contourArea(contour)
    perimeter_px = cv2.arcLength(contour, True)

    return {
        "length_mm": round(w / pixel_per_mm, 2),
        "width_mm": round(h / pixel_per_mm, 2),
        "diameter_mm": round(radius * 2 / pixel_per_mm, 2),
        "area_mm2": round(area_px / (pixel_per_mm ** 2), 2),
        "perimeter_mm": round(perimeter_px / pixel_per_mm, 2),
        "width_px": round(w, 1),
        "height_px": round(h, 1),
        "box": box,
        "circle": (int(x), int(y), int(radius)),
    }


def calibrate_pixel_per_mm(contour, known_mm):
    """用已知参考尺寸标定像素当量

    通过参考物体的实际尺寸反推 pixel_per_mm。
    这里假设参考物体就是检测到的最大轮廓，
    取其外接矩形长边作为参考。

    如果使用自己的图像但不知道参考尺寸，可以先设为 1.0
    得到像素值，再用实际尺子量一下后换算。
    """
    rect = cv2.minAreaRect(contour)
    (w, h) = rect[1]
    if w < h:
        w, h = h, w
    pixel_per_mm = w / known_mm
    return pixel_per_mm


def draw_measurements(image, dimensions, pixel_per_mm):
    """在图像上绘制测量结果"""
    result = image.copy()
    box = dimensions["box"]
    cx, cy, radius = dimensions["circle"]

    # 绘制最小外接矩形
    cv2.drawContours(result, [box], 0, (0, 255, 255), 2)

    # 绘制最小外接圆
    cv2.circle(result, (cx, cy), radius, (255, 0, 0), 2)
    cv2.circle(result, (cx, cy), 3, (255, 0, 0), -1)

    # 显示尺寸文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    y_offset = 30
    for key, val in [
        ("Length", f"{dimensions['length_mm']} mm"),
        ("Width", f"{dimensions['width_mm']} mm"),
        ("Diameter", f"{dimensions['diameter_mm']} mm"),
        ("Area", f"{dimensions['area_mm2']} mm²"),
        ("Scale", f"{pixel_per_mm:.1f} px/mm"),
    ]:
        text = f"{key}: {val}"
        cv2.putText(result, text, (10, y_offset), font,
                    0.55, (0, 255, 0), 2)
        y_offset += 25

    return result


def main():
    parser = argparse.ArgumentParser(description="工件尺寸测量原型")
    parser.add_argument("--image", type=str,
                        default=os.path.join(os.path.dirname(__file__),
                                             "test_images", "part_rect.png"),
                        help="输入图像路径")
    parser.add_argument("--known-size", type=float,
                        default=REFERENCE_OBJECT_MM,
                        help="参考物体实际尺寸(mm)")
    args = parser.parse_args()

    # 1. 读取图像
    img_path = args.image
    if not os.path.exists(img_path):
        print(f"[错误] 图片不存在: {img_path}")
        print("请先运行 python test_images/generate_samples.py 生成测试图")
        return

    img = cv2.imread(img_path)
    if img is None:
        print(f"[错误] 无法读取图片: {img_path}")
        return

    print(f"读取图片: {img_path}  ({img.shape[1]}x{img.shape[0]})")

    # 2. 预处理
    processed = preprocess(img)
    print("✓ 预处理完成（灰度 → 高斯滤波 → CLAHE增强）")

    # 3. 查找轮廓
    try:
        contour, vis, edges, closed = find_object_contour(processed)
    except ValueError as e:
        print(f"[错误] {e}")
        return
    print(f"✓ 找到目标轮廓，面积: {cv2.contourArea(contour):.0f} px²")

    # 4. 标定像素当量
    pixel_per_mm = calibrate_pixel_per_mm(contour, args.known_size)
    print(f"✓ 像素当量: {pixel_per_mm:.2f} px/mm  (参考 {args.known_size} mm)")

    # 5. 测量
    dims = measure_dimensions(contour, pixel_per_mm)
    print("\n── 测量结果 ──")
    print(f"  长度: {dims['length_mm']} mm")
    print(f"  宽度: {dims['width_mm']} mm")
    print(f"  等效直径: {dims['diameter_mm']} mm")
    print(f"  面积: {dims['area_mm2']} mm²")
    print(f"  周长: {dims['perimeter_mm']} mm")

    # 6. 可视化
    result = draw_measurements(img, dims, pixel_per_mm)

    # 显示结果
    cv2.imshow("Original + Measurements", result)
    cv2.imshow("Edges (Canny)", edges)
    cv2.imshow("Closed (Morph)", closed)
    print("\n按任意键关闭窗口...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 保存结果
    out_dir = os.path.dirname(img_path) or "."
    out_path = os.path.join(out_dir, "result_" + os.path.basename(img_path))
    cv2.imwrite(out_path, result)
    print(f"\n结果已保存: {out_path}")


if __name__ == "__main__":
    main()
