## python
conda python 3.8
```bash

conda create -n selfocr python=3.8
conda activate selfocr
pip install -r requirements.txt
```
### build python 
```bash
pyinstaller -y ocr.py --collect-all paddleocr --collect-all pyclipper --collect-all imghdr --collect-all skimage --collect-all imgaug --collect-all scipy.io --collect-all lmdb --collect-all paddle
```

## node
node 16
```bash
npm i 
npm run dev
```
### build html
```bash
npm run build
npm run move
```

## window 执行
dist\ocr\ocr.exe

### api
post  127.0.0.1:5000/api/ocr  multipart/form-data  File

### html
127.0.0.1:5000/