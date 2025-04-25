from paddleocr import PaddleOCR
import os
import cv2
import numpy as np
from io import BytesIO
import sys
import json
import time
import multiprocessing
def runOcr():
    startTime = time.time()
    ocr = PaddleOCR(lang='ch') # need to run only once to download and load model into memory
    img_path = '683.jpg'
    result = ocr.ocr(img_path, cls=False)
    list_str = []

    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            list_str.append(line[1][0])
    # print(sys.argv[1])
    # print(json.dumps(list_str, ensure_ascii=False))
    with open("example.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(list_str, ensure_ascii=False))
        print(time.time()-startTime)
    
# draw result
# from PIL import Image
# result = result[0]
# image = Image.open(img_path).convert('RGB')
# boxes = [line[0] for line in result]
# txts = [line[1][0] for line in result]
# scores = [line[1][1] for line in result]
# im_show = draw_ocr(image, boxes, txts, scores, font_path='/path/to/PaddleOCR/doc/fonts/simfang.ttf')
# im_show = Image.fromarray(im_show)
# im_show.save('result.jpg')

from flask import Flask, jsonify, request,send_from_directory
from flask_cors import CORS

app = Flask(__name__,static_folder='/')
CORS(app)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['JSON_AS_ASCII'] = False

# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    print('app.static_folder',app.static_folder)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/ocr', methods=['POST'])
def upload_file():
    # 判断请求中是否有文件
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']

    # 如果用户没有选择文件，浏览器会提交一个空文件名
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 检查文件扩展名是否合法
    if file and allowed_file(file.filename):
        # 使用安全的文件名
        # filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # 保存文件
        # file.save(filename)
        # return jsonify({"message": "File successfully uploaded", "filename": file.filename}), 200
        # 将文件读取为字节流
        img_bytes = file.read()
        # 使用 numpy 从字节流中解码图片
        nparr = np.frombuffer(img_bytes, np.uint8)
        # 使用 OpenCV imdecode 解码图像
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Could not read the image"}), 400

        # 在这里可以对图像进行各种处理
        # 例如获取图像的尺寸
        height, width, channels = img.shape
        ocr = PaddleOCR(lang='ch')
        result = ocr.ocr(img, cls=False)
        print( result[0])
        if result[0] == None:
            return jsonify({"message": "image not text","res":[]}), 200
        list_str = []
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                list_str.append({'points':line[0],'value':line[1][0],'score':line[1][1]})
        return jsonify({
            "message": "File successfully uploaded and processed",
            "image_size": {"height": height, "width": width, "channels": channels},
            "res": list_str
        }), 200
    
    else:
        return jsonify({"error": "File type not allowed"}), 400
if __name__ == '__main__':
    multiprocessing.freeze_support()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)