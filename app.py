import sys, json, os, time, re
from PIL import Image
from aip import AipOcr
from utlis.ai import Ai
import config
import logging

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')

# 使用OCR
def handler_image(img_path):
    img = Image.open(img_path)
    if not img.size == (1280, 720):
        img = img.transpose(Image.ROTATE_90)
        if not img.size == (1280, 720):
            logging.info('暂时只支持 720 * 1280 分辨率')
            return

    start_w = 495
    start_h = 125
    end_w = 1100
    end_h = 500

    img = img.crop((start_w, start_h, end_w, end_h))
    client = AipOcr(config.APP_ID, config.API_KEY, config.SECRET_KEY)

    # 用完500次后可改 respon = client.basicAccurate(image) 这个还可用50次
    respon = client.basicGeneral(img.tobytes('jpeg', ('RGB')))
    return respon['words_result']

def handler_question(words):
    issue = ''
    answers = []
    for index, word in enumerate(words):
        if re.search(r'[a-zA-Z]', words[index+1]['words']):
            issue = re.sub(r'第\d+题(.+?时[:\sA-Za-z0-9]+)?', '',
                ''.join([words[i]['words'] for i in range(index + 1)]))
            for i in range(index + 1, len(words)):
                answers.append(re.sub(r'^[A-Za-z]\s?', '', words[i]['words']))
            break
    return issue, answers

def screenshot():
    t = os.popen(f'adb devices').read()
    if t.count('device') < 2:
        t = os.popen(f'adb connect {config.HOST}:{config.POST}').read()
        if 'unable' in t:
            logging.info('找不到设备，请检查连接地址、端口或设备是否已启动')
            exit()
    elif t.count('device') != 2:
        logging.info('请勿连接多个设备，同时间只能有一个设备进行工作')
        exit()
    index = 0
    if config.SAVE_CACHE:
        while True:
            path = '%sscreenshot%03d.png' % (config.IMG_CACHE_PATH, index)
            if not os.path.exists(path):
                os.system('adb shell /system/bin/screencap -p /sdcard/screenshot.png')
                os.system(f'adb pull /sdcard/screenshot.png {path}')
                break
            index += 1
    else:
        path = '%sscreenshot.png' % (config.IMG_CACHE_PATH)
        os.system('adb shell /system/bin/screencap -p /sdcard/screenshot.png')
        os.system(f'adb pull /sdcard/screenshot.png {path}')
    return path

if __name__ == '__main__':
    # Android 截图
    path = screenshot()
    start_time = time.time()
    words = handler_image(path)
    issue, answers = handler_question(words)
    if not issue or not answers:
        logging.info('ORC 识别失败')
        exit()
    print(f'Q: {issue}')
    ai = Ai(issue, answers)
    answers, clear = ai.tell_me_result()
    for i in answers:
        print(f'\n搜索引擎：{i}')
        print('------------答案出现统计------------')
        print(answers[i])
        if config.DETAILS:
            print('--------------相关内容--------------')
            for i in clear:
                print(i)
    print(f'程序用时：{time.time() - start_time}')


