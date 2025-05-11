from flask import Flask, request
import urllib.parse
import qrcode
from PIL import Image, ImageDraw, ImageFont
import argparse
import os
import random
import datetime
from PIL import Image

""""
    # 【启动case】 python jiekou.py --port 8080 --path "\Pictures\paper-ppt"


    @Author: 中山大学 计算机系 吴远健
    @Updated time: 2025/5/10
    @Description: 用于生成二维码的网络接口

    @Case: /py/api/qrcode/build?label=abc&type=image&pinghao=001&text=https%3A%2F%2Fxxx.com

    分两种情况：（参数：type（tong；chengping））
        1. 原桶：多一个品号
        2. 成品：保持原本的版本

    两部分参数（text & label）

    因此总参数 = {
            type: [String]
            text: [String 注意需要转义]
            label: [String]
            pinghao:[String]
        }
"""

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--port', required=True, default=5000)
parser.add_argument('--path', required=None, default='')

args = parser.parse_args()


def generate_fixed_layout_qr(text, label, type, pinghao, save_path='output.png'):
    # 常量配置
    dpi = 300
    width_px = int(60 / 25.4 * dpi)  # ≈ 708px
    qr_size = 200  # 固定二维码为 250x250 像素
    # 生成二维码（固定尺寸）
    qr = qrcode.QRCode(box_size=10, border=1)

    batchid = label

    if type == "yuanliao":
        print("生成原料二维码")
        # 常量配置
        dpi = 300
        width_px = int(60 / 25.4 * dpi)  # ≈ 708px
        height_px = int(40 / 25.4 * dpi)  #
        qr_size = 200  # 固定二维码为 250x250 像素
        # 生成二维码（固定尺寸）
        qr = qrcode.QRCode(box_size=10, border=1)

        qr.add_data(text + '/' + label)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

        # 创建最终图像
        result = Image.new('RGB', (width_px, height_px), color='white')
        draw = ImageDraw.Draw(result)
        # 左侧文字区域宽度
        text_area_width = width_px - qr_size
        # 加载两种字体
        try:
            font_large = ImageFont.truetype("msyhbd.ttc", 64)  # 用于品号部分
            font_small = ImageFont.truetype("msyhbd.ttc", 42)  # 用于批号
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 文本内容
        pinghao_label = "品号："
        pinghao_value = pinghao
        label_text = f"批号：{label}"

        # 计算文字高度
        pinghao_label_bbox = font_large.getbbox(pinghao_label)
        pinghao_label_height = pinghao_label_bbox[3] - pinghao_label_bbox[1]

        pinghao_value_bbox = font_large.getbbox(pinghao_value)
        pinghao_value_height = pinghao_value_bbox[3] - pinghao_value_bbox[1]

        label_bbox = font_small.getbbox(label_text)
        label_height = label_bbox[3] - label_bbox[1]

        line_spacing = 20  # 行间距

        total_text_height = pinghao_label_height + line_spacing + pinghao_value_height + line_spacing + label_height
        start_y = (height_px - total_text_height) // 2  # 整体垂直居中

        # 左边对齐
        x_left = 10

        # 绘制三行内容
        y1 = start_y
        draw.text((x_left, y1), pinghao_label, font=font_large, fill='black')

        y2 = y1 + pinghao_label_height + line_spacing
        draw.text((x_left, y2), pinghao_value, font=font_large, fill='black')

        y3 = y2 + pinghao_value_height + line_spacing
        draw.text((x_left, y3), label_text, font=font_small, fill='black')

        # 粘贴二维码到右边（垂直居中）
        qr_x = text_area_width - 10
        qr_y = (height_px - qr_size) // 2
        result.paste(qr_img, (qr_x, qr_y))

        # 保存
        return successf_(data=save_image(result, "yuanliao", args.path))

    else:
        print("生成成品二维码")
        height_px = int(30 / 25.4 * dpi)

        qr.add_data(text + '/' + label)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

        # 创建最终图像
        result = Image.new('RGB', (width_px, height_px), color='white')
        draw = ImageDraw.Draw(result)

        # 加载字体（字号固定）
        try:
            font = ImageFont.truetype("arial.ttf", 55)
        except:
            font = ImageFont.load_default()

        # 文本位置（居中对齐左边区域）
        text_area_width = width_px - qr_size
        text_bbox = font.getbbox(batchid)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x_text = (text_area_width - text_width) // 2
        y_text = (height_px - text_height) // 2
        draw.text((x_text, y_text), batchid, font=font, fill='black')

        # 粘贴二维码到右边（垂直居中）
        qr_x = text_area_width - 10
        qr_y = (height_px - qr_size) // 2
        result.paste(qr_img, (qr_x, qr_y))

        # 保存
        return successf_(data=save_image(result, "chengping", args.path))


# 示例函数 f
def f(label, text, type, pinghao):
    # 这里可以写你的处理逻辑
    print(f"label: {label}")
    print(f"text: {text}")
    print(f"type: {type}")
    print(f"pinghao: {pinghao}")
    return {"status": "success", "received": [label, text, type, pinghao]}


def successf_(code=200, data=None, msg="ok"):
    return {"status": "success", "code": code, "data": data, "msg": msg}


def save_image(img, img_type, save_dir):
    """
    保存图片到指定目录，文件名格式为：<type>_<时间>_<随机数>.png

    参数:
        img: PIL.Image 对象
        img_type: 字符串，表示图片类型
        save_dir: 图片保存的绝对目录路径（默认可替换为你的实际路径）
    """
    # 确保保存目录存在
    os.makedirs(save_dir, exist_ok=True)

    # 获取当前时间，格式如 20250511_153245
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 生成一个随机数
    rand_num = random.randint(1000, 9999)

    # 构造文件名
    filename = f"{img_type}_{current_time}_{rand_num}.png"

    # 构造完整路径
    full_path = os.path.join(save_dir, filename)

    # 保存图片
    img.save(full_path)

    print(f"图片已保存到: {full_path}")
    return full_path


@app.route('/py/api/qrcode/build', methods=['GET'])
def handle_get_request():
    # 获取参数
    label = request.args.get('label')
    text = request.args.get('text')
    type_ = request.args.get('type')
    pinghao = request.args.get('pinghao')

    # 参数校验
    if not all([label, text, type_]):
        return {"error": "Missing parameters"}, 400

    # 对 text 参数进行 URL 解码
    decoded_text = urllib.parse.unquote(text)

    # 调用你的处理函数
    return generate_fixed_layout_qr(decoded_text, label, type_, pinghao)


if __name__ == '__main__':
    app.run(debug=True, port=args.port)
