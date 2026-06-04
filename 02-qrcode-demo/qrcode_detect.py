"""二维码定位与识别Demo — 基于OpenCV

实现了"图像预处理 → 二维码定位 → 透视校正 → 解码"的
完整流水线。展示了机器视觉中"定位→校正→识别"的标准思维。

功能：
  1. 在图像中检测二维码位置
  2. 用 OpenCV 自带的 QRCodeDetector 解码
  3. 绘制定位框和识别结果
  4. 支持旋转/倾斜二维码的鲁棒识别

用法：
    python qrcode_detect.py [--image test_images/qr_normal.png]
"""

import argparse
import os
import cv2
import numpy as np


def preprocess_for_qr(image):
    """预处理增强二维码可读性

    针对模糊、光照不佳的场景做增强。
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # CLAHE 增强对比度
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    # 自适应阈值二值化（对光照不均的二维码效果更好）
    binary = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 21, 4)
    return gray, enhanced, binary


def detect_qr_opencv(image):
    """用 OpenCV 内置的 QRCodeDetector 检测并解码

    这是最简单的方法，OpenCV 4.5+ 版本内置了二维码检测器。
    """
    detector = cv2.QRCodeDetector()
    data, points, straight_qrcode = detector.detectAndDecode(image)

    return data, points, straight_qrcode


def detect_qr_contour_based(gray, image):
    """基于轮廓分析的二维码定位（备用方法）

    当 OpenCV 内置检测器失效时，用传统方法定位二维码。
    利用 QR 码三个角上的"回"字形定位图案。

    这是一个简化的实现，展示了定位的基本思路。
    """
    # 二值化
    _, binary = cv2.threshold(gray, 0, 255,
                               cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # 寻找"回"字形定位图案（父子轮廓关系）
    # 简化版：找面积适中的正方形区域
    qr_boxes = []
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:  # 四边形
            area = cv2.contourArea(c)
            if 500 < area < 50000:  # 面积过滤
                x, y, w, h = cv2.boundingRect(c)
                aspect = w / h
                if 0.7 < aspect < 1.3:  # 接近正方形
                    qr_boxes.append(c)

    result_img = image.copy()
    if len(qr_boxes) >= 3:
        # 如果找到3个以上的候选，画出来
        cv2.drawContours(result_img, qr_boxes[:3], -1, (255, 0, 255), 2)
        cv2.putText(result_img, "QR pattern candidates found",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 0, 255), 2)
        return True, result_img

    return False, result_img


def draw_result(image, data, points):
    """绘制检测结果"""
    result = image.copy()

    if points is not None and len(points) > 0:
        # 绘制二维码边界框
        pts = points.reshape((-1, 2)).astype(np.int32)
        cv2.polylines(result, [pts], True, (0, 255, 0), 3)

        # 标记四个角
        for i, (x, y) in enumerate(pts):
            cv2.circle(result, (x, y), 6, (0, 0, 255), -1)
            cv2.putText(result, str(i + 1), (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # 显示解码结果
    if data:
        # 在顶部显示解码内容
        text = f"Decoded: {data[:50]}{'...' if len(data) > 50 else ''}"
        cv2.putText(result, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)
        # 添加背景色块让文字更清晰
        overlay = result.copy()
        cv2.rectangle(overlay, (5, 5), (len(text) * 9 + 15, 45),
                      (0, 0, 0), -1)
        result = cv2.addWeighted(overlay, 0.3, result, 0.7, 0)
        cv2.putText(result, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)
    else:
        cv2.putText(result, "No QR code detected",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2)

    return result


def main():
    parser = argparse.ArgumentParser(description="二维码定位与识别Demo")
    parser.add_argument("--image", type=str, default=os.path.join(
        os.path.dirname(__file__), "test_images", "qr_normal.png"),
                        help="输入图像路径")
    parser.add_argument("--method", type=str, default="auto",
                        choices=["auto", "contour"],
                        help="检测方法：auto=OpenCV内置, contour=轮廓法")
    args = parser.parse_args()

    img_path = args.image
    if not os.path.exists(img_path):
        print(f"[错误] 图片不存在: {img_path}")
        print("请先运行 python test_images/generate_test_qr.py 生成测试图")
        return

    img = cv2.imread(img_path)
    if img is None:
        print(f"[错误] 无法读取图片: {img_path}")
        return

    print(f"读取图片: {img_path}  ({img.shape[1]}x{img.shape[0]})")

    # 预处理
    gray, enhanced, binary = preprocess_for_qr(img)

    # 检测二维码
    if args.method == "auto":
        data, points, straight = detect_qr_opencv(img)

        if data:
            print(f"\n✅ 成功解码！")
            print(f"   内容: {data}")
            print(f"   长度: {len(data)} 字符")
        else:
            # 如果原图检测失败，尝试增强图
            print("  ⚠ 原图未检测到，尝试增强图...")
            data, points, straight = detect_qr_opencv(enhanced)
            if data:
                print(f"\n✅ 增强图解码成功！")
                print(f"   内容: {data}")
            else:
                print("\n❌ 未检测到二维码")
                print("   可能原因：图片中没有二维码、二维码损坏")
                print("   > 尝试 --method contour 查看轮廓分析结果")

    elif args.method == "contour":
        found, result = detect_qr_contour_based(gray, img)
        if found:
            print("轮廓法定位到候选区域，尝试 OpenCV 解码...")
            data, points, straight = detect_qr_opencv(img)
            if data:
                print(f"✅ 解码成功: {data}")
            else:
                print("❌ 候选区域解码失败")
        else:
            data, points = "", None

    # 可视化
    result = draw_result(img, data, points)

    # 显示
    cv2.imshow("QR Detection Result", result)
    cv2.imshow("Enhanced (CLAHE)", enhanced)
    cv2.imshow("Binary", binary)

    if data:
        print("\n按任意键关闭窗口...")
    else:
        print("\n(无检测结果，按任意键继续)")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 保存
    out_dir = os.path.dirname(img_path) or "."
    out_path = os.path.join(out_dir, "result_" + os.path.basename(img_path))
    cv2.imwrite(out_path, result)
    print(f"结果已保存: {out_path}")


if __name__ == "__main__":
    main()
