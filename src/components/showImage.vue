<template>
  <div class="show-image">
    <div class="image canvas" ref="canvasDiv" v-loading="loading">
      <img class="base-img" :src="url" :style="controlStyle" crossorigin="" />
      <div class="canvas-div-post edit-canvas" :style="controlStyle">
        <canvas ref="canvas" />
      </div>

      <div class="button-list">
        <el-icon @click="refresh">
          <Refresh />
        </el-icon>
        <el-icon @click="del">
          <CircleClose />
        </el-icon>
      </div>
    </div>
    <div class="value">
      <el-input v-model="textarea" autosize type="textarea" placeholder="" />
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { fabric } from 'fabric'
import Control from "../assets/control.js"
import { ElMessage } from 'element-plus'

export default {
  name: 'showImage',
  props: {
    obj: Object
  },
  data() {
    return {
      loading: true,
      res: {},
      url: '',
      textarea: "",
      toolType: 'move',
      canvas: {},
      controlObj: {},
      controlStyle: {}
    }
  },
  methods: {
    upload() {
      const urlWithoutPort = window.location.origin.replace(/:(\d+)/, '')
      const formData = new FormData();
      formData.append('file', this.obj.file);
      axios.post(urlWithoutPort + ':5000/api/ocr', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      }).then(response => {
        console.log('上传成功', response.data);
        this.res = response.data
        this.res.res.forEach(element => {
          this.textarea += element.value + '\n'
        });
        this.renderCanvas()
        this.loading = false

      }).catch(error => {
        console.error('上传失败', error);
      });
    },
    readImage() {
      let canvas = this.canvas
      let that = this
      const reader = new FileReader();
      reader.readAsDataURL(this.obj.file);
      reader.onload = () => {
        this.url = reader.result;
        that.init()
        // 这里的reader.result就是文件的base64了。如果是图片的话，就可以直接放到src中展示了

        // fabric.Image.fromURL(this.url, function (img) {
        //   // 获取画布尺寸
        //   // var canvasWidth = canvas.width;
        //   // var canvasHeight = canvas.height;

        //   // // 获取图片原始尺寸
        //   // var imgWidth = img.width;
        //   // var imgHeight = img.height;

        //   // 计算缩放比例以适应画布
        //   // var scale = Math.min(canvasWidth / imgWidth, canvasHeight / imgHeight);

        //   // // 应用缩放比例
        //   // img.set({
        //   //   scaleX: scale,
        //   //   scaleY: scale,
        //   //   evented: false,
        //   //   hasControls: false,
        //   //   hasBorders: false,
        //   // });

        //   // // 居中图片（可选）
        //   // img.set({
        //   //   left: (canvasWidth - imgWidth * scale) / 2,
        //   //   top: (canvasHeight - imgHeight * scale) / 2
        //   // });

        //   // 添加图片到画布
        //   // canvas.add(img);
        //   that.init()
        // });
      };
    },
    renderCanvas() {
      let that = this
      this.res.res.forEach(obj => {
        // 2. 定义梯形的四个点
        var points = [
          { x: obj.points[0][0], y: obj.points[0][1] },  // 左下角
          { x: obj.points[1][0], y: obj.points[1][1] },  // 右上角
          { x: obj.points[2][0], y: obj.points[2][1] },  // 右下角
          { x: obj.points[3][0], y: obj.points[3][1] }   // 左上角
        ];
        // 3. 使用 fabric.Polygon 创建梯形
        var trapezoid = new fabric.Polygon(points, {
          fill: 'blue',           // 填充颜色
          stroke: 'black',        // 边框颜色
          strokeWidth: 2,         // 边框宽度
          opacity: 0.2,
          hasControls: false,
          // evented: false,
          lockMovementX: true,    // 锁定 X 轴移动
          lockMovementY: true,     // 锁定 Y 轴移动
          selectable: true,
          hasBorders: false,
          objectCaching: false    // 禁用对象缓存，使得动态更新更流畅
        });
        this.canvas.add(trapezoid);

        trapezoid.on('mousedown', function (e) {
          const now = new Date().getTime();
          if (this.lastClick && now - this.lastClick < 300) {
            // 双击时的逻辑
            console.log('双击事件！', obj.value);
          } else {
            // 单击时的逻辑
            try {
              navigator.clipboard.writeText(obj.value)
                .then(() => {
                  ElMessage('内容已成功复制到剪切板')
                })
                .catch(err => {
                  that.copyToClipboard(obj.value)
                });
            } catch (error) {
              that.copyToClipboard(obj.value)
            }

          }
          this.lastClick = now;
        });
      })




    },
    init() {
      let that = this
      fabric.Image.fromURL(
        this.url,
        async function (img, error) {
          that.canvas.setDimensions({ width: img.width, height: img.height })
          that.canvas.renderAll()
          that.controlObj.w = img.width
          that.controlObj.h = img.height
          that.controlObj.scale = img.width / img.height
          that.controlStyle.width = img.width + "px"
          that.controlStyle.height = img.height + "px"
          console.log('controlStyle: ', that.controlStyle);
          let prevDomControl = new Control(that.$refs.canvasDiv, "domControl")
          prevDomControl.addListeners(that.changeControl)
          that.changeSize(0)
        },
        {
          crossOrigin: "anonymous",
        }
      )

    },
    changeControl(type, arg, id) {
      let controlObj = this.controlObj, controlStyle = this.controlStyle
      switch (type) {
        case "zoom":
          let zoom = arg[0] > 0 ? 0.9 : 1.1
          let rate = Math.floor((((controlObj.nw || controlObj.w) * zoom) / controlObj.w) * 100)
          if (rate < 5) {
            return false
          } else if (rate > 500) {
            zoom = (5 * controlObj.w) / (controlObj.nw || controlObj.w)
          }
          controlObj.nw = (controlObj.nw || controlObj.w) * zoom
          controlObj.nh = (controlObj.nh || controlObj.h) * zoom

          controlStyle.width = controlObj.nw + "px"
          controlStyle.height = controlObj.nh + "px"
          controlObj.t = (-controlObj.t + arg[2]) * (1 - zoom) + controlObj.t
          controlObj.l = (-controlObj.l + arg[1]) * (1 - zoom) + controlObj.l
          controlStyle.top = controlObj.t + "px"
          controlStyle.left = controlObj.l + "px"
          break
        case "move":
          // if (id == "editDomControl") {
          if (arg[0] == "mouse" && this.toolType !== "move") {
            return
          }
          // }
          controlObj.t = controlObj.t - arg[2]
          controlObj.l = controlObj.l - arg[1]
          controlStyle.top = controlObj.t + "px"
          controlStyle.left = controlObj.l + "px"

          break
        case "init":
          controlObj.t = arg[0]
          controlObj.l = arg[1]
          controlStyle.top = controlObj.t + "px"
          controlStyle.left = controlObj.l + "px"
          controlObj.nw = controlObj.w
          controlObj.nh = controlObj.h

          controlStyle.width = controlObj.nw + "px"
          controlStyle.height = controlObj.nh + "px"
          break
        case "size":
          controlObj.t = arg[2]
          controlObj.l = arg[3]
          controlStyle.top = controlObj.t + "px"
          controlStyle.left = controlObj.l + "px"
          controlObj.nw = arg[0]
          controlObj.nh = arg[1]

          controlStyle.width = controlObj.nw + "px"
          controlStyle.height = controlObj.nh + "px"
          break
        case "click":
          if (this.toolType == "zoom") {
            // console.log(arg);
            let zoom = 1.1
            let rate = Math.floor((((controlObj.nw || controlObj.w) * zoom) / controlObj.w) * 100)
            if (rate > 500) {
              zoom = (5 * controlObj.w) / (controlObj.nw || controlObj.w)
            }
            controlObj.nw = (controlObj.nw || controlObj.w) * zoom
            controlObj.nh = (controlObj.nh || controlObj.h) * zoom

            controlStyle.width = controlObj.nw + "px"
            controlStyle.height = controlObj.nh + "px"

            controlObj.t = (-controlObj.t + arg[2]) * (1 - zoom) + controlObj.t
            controlObj.l = (-controlObj.l + arg[1]) * (1 - zoom) + controlObj.l
            controlStyle.top = controlObj.t + "px"
            controlStyle.left = controlObj.l + "px"
          } else if (this.toolType == "less") {
            // console.log(arg);
            let zoom = 0.9
            let rate = Math.floor((((controlObj.nw || controlObj.w) * zoom) / controlObj.w) * 100)
            if (rate < 5) {
              return false
            }
            controlObj.nw = (controlObj.nw || controlObj.w) * zoom
            controlObj.nh = (controlObj.nh || controlObj.h) * zoom

            controlStyle.width = controlObj.nw + "px"
            controlStyle.height = controlObj.nh + "px"

            controlObj.t = (-controlObj.t + arg[2]) * (1 - zoom) + controlObj.t
            controlObj.l = (-controlObj.l + arg[1]) * (1 - zoom) + controlObj.l
            controlStyle.top = controlObj.t + "px"
            controlStyle.left = controlObj.l + "px"
          }
          break


        default:
          break
      }
    },
    changeSize(size) {
      let controlObj = this.controlObj

      let width = this.$refs.canvasDiv.offsetWidth,
        height = this.$refs.canvasDiv.offsetHeight,
        centerW = this.$refs.canvasDiv.offsetWidth / 2,
        centerH = this.$refs.canvasDiv.offsetHeight / 2
      switch (size) {
        case 1:
          this.changeControl("init", [-controlObj.h / 2 + centerH, -controlObj.w / 2 + centerW])
          break
        case 0:
          if (controlObj.w / width > controlObj.h / height) {
            let top = -width / controlObj.scale / 2 + centerH,
              left = -width / 2 + centerW
            this.changeControl("size", [width, width / controlObj.scale, top, left])
          } else {
            let top = -height / 2 + centerH,
              left = (-height * controlObj.scale) / 2 + centerW
            this.changeControl("size", [height * controlObj.scale, height, top, left])
          }
          break

        default:
          this.changeControl("zoom", [size > 1 ? -1.1 : 1.1, centerW, centerH])
          break
      }
    },
    copyToClipboard(text) {
      // 创建一个临时的 textarea 元素
      const tempInput = document.createElement('textarea');
      tempInput.value = text;

      // 隐藏到页面中
      tempInput.style.position = 'absolute';
      tempInput.style.left = '-9999px';
      document.body.appendChild(tempInput);

      // 选中文本并复制
      tempInput.select();
      try {
        const success = document.execCommand('copy');
        if (success) {
          ElMessage('内容已成功复制到剪切板')
        } else {
          ElMessage('复制失败');
        }
      } catch (err) {
        console.error('复制异常:', err);
      }

      // 移除临时元素
      document.body.removeChild(tempInput);
    },
    del() {
      this.$emit('delFile', this.obj.id)
    },
    refresh() {
      this.textarea = ''
      this.res.res.forEach(element => {
        this.textarea += element.value + '\n'
      });
    }

  },
  created() {

  },
  mounted() {
    this.canvas = new fabric.Canvas(this.$refs.canvas);
    this.readImage()
    this.upload()
  }
}
</script>
<style scoped lang="less">
.show-image {
  display: flex;
  width: 98vw;

  .image {
    flex: 1;
    padding: 10px;

    img {
      width: 100%;
    }
  }

  .canvas {
    height: 60vh;
    // height:100%;
    position: relative;
    overflow: hidden;
    box-shadow: 1px 1px 3px 2px #0000004d;
    margin: 5px;

    // &>div {
    //   flex: 1;
    //   overflow: hidden;
    //   height: 100%;
    //   position: relative;
    // }
    .button-list {
      position: absolute;
      right: 10px;
      top: 10px;
      .el-icon{
        margin-left:10px
      }
    }

    .base-img {
      max-width: unset;
      position: absolute;
    }


    .canvas-div-post {
      position: absolute;

      & :deep(.canvas-container) {
        width: auto !important;
        height: 100% !important;
      }
    }



    .canvas-div-post.edit-canvas {
      background-color: transparent !important;
    }

    & :deep(canvas) {
      width: auto !important;
      height: 100% !important;
    }
  }

  .value {
    flex: 1;
    padding: 10px;

  }
}
</style>
