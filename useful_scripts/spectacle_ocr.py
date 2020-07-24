#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @UpdateTime   : 2020/07/10 17:23:27
# @Author       : Violetu
# @File         : spectacle_ocr.py
# @Function     : screenshoot ocr

from aip import AipOcr
from PIL import Image
import pytesseract
import pyperclip
import re
import os

TEMP_IMG_PATH = "/home/violetv/Documents/temp.png"  # 临时图片位置，每次覆写
PARAGRAPH_OCR = False  # 识别的是否是段落，即：是否进行段落整理
INTERNET = True  # True 有网，用 baidu


def screen():
    # 利用截图软件（KDE 自带 Spectacle）截图到剪贴板

    os.system(f"spectacle -b -n -r -o {TEMP_IMG_PATH} 2>/dev/null")


def shrink_img():
    # 压缩过大的图片，便于网络传输、识别
    img = Image.open(TEMP_IMG_PATH)
    width, height = img.size
    while(width*height > 4000000):  # 该数值压缩后的图片大约 两百多k
        width = width // 2
        height = height // 2
    new_img = img.resize((width, height), Image.BILINEAR)
    new_img.save(TEMP_IMG_PATH)


def baidu_ocr():
    # OCR by baidu API 通用文字识别（高精度版）,500 times per day

    # 判断并压缩过大的图片
    shrink_img()

    # authorization information
    # Notice： 创建百度文字识别应用，并将信息填到这里
    APP_ID = ''
    API_KEY = ''
    SECRET_KEY = ''

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    # 读取图片
    with open(TEMP_IMG_PATH, 'rb') as f:
        image = f.read()

    # 如果有可选参数
    options = {}
    options["detect_direction"] = "true"

    # 带参数调用通用文字识别（高精度版），提取图片中的内容
    response = client.basicAccurate(image, options)
    raw_result = "\n".join(i["words"] for i in response["words_result"])

    # 默认 True, 说明你识别的是段落
    if PARAGRAPH_OCR:
        # 利用正则进行简单段落整理，规则: 凡是句号问号感叹号之后的换行符均保留，其余换行符一律替换为空。
        pattern = r"(?m)(?<![\.。\?!])\n"
        result = re.sub(pattern, "", raw_result)
        return result
    else:
        return raw_result


def tesserocr():
    # OCR by tesseract

    # 放大图片，提高准确率 (谁让它准确率低呢)
    os.system(f"mogrify -modulate 100,0 -resize 400% {TEMP_IMG_PATH}")

    text = pytesseract.image_to_string(Image.open(
        TEMP_IMG_PATH), lang='eng+chi_sim', config='testing/bilingual-engchi_sim -c preserve_interword_spaces=1')

    return text


def main():

    # 1. 截取图片，放到指定目录
    screen()

    # 2. OCR 识别
    # INTERNET  = True， 有网，用 baidu, INTERNET  = False， 无网，用 tesserocr
    if INTERNET:
        # baidu ocr
        text = baidu_ocr()
    else:
        # tesserocr ocr
        text = tesserocr()

    # 3.写到剪切板
    pyperclip.copy(text)
    pyperclip.paste(text)

    # 4. 弹窗提示 OCR 结束

    os.system("notify-send -a OCR 'Done' -t 1500 ")


if __name__ == "__main__":
    main()
