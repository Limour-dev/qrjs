# qrjs

## Demo
+ 演示 Demo，勉强能用，识别效率不如后面的 Python 版译码器
+ 靶机选择文件生成喷泉码：https://hexo.limour.top/qrjs.c.html
+ 手机打开相机对准喷泉码：https://hexo.limour.top/qrjs.s.html
+ 如果靶机无法联网，请参考下文的 Bad USB 技术

## Bad USB
购买一个10元的 [pico zero](https://www.waveshare.net/wiki/RP2040-Zero) 板
1. 按住 `boot` 键插入电脑，松开按钮 ，将 [pico-badusb.uf2](https://github.com/Limour-dev/qrjs/releases) 拖入根目录
2. 自动重启后，将 [修改后](https://github.com/Limour-dev/qrjs/tree/main/pico-badusb) 的 `boot.py` 和 `main.py` 拖入根目录
3. 再次自动重启后，会发现不再挂载存储，此时按一下 `reset` 键
4. 第三次重启后，将 [payload.txt](https://github.com/Limour-dev/qrjs/blob/main/payload.txt) 拖入根目录
5. 右下角安全删除U盘硬件，`Bad USB` 就做好了。使用时直接插入靶机，等 6 秒就会开始执行。
6. 要更新 `payload.txt` 的话，只需要在 6 秒内，按下 `reset` 键重启，就会挂载为U盘了。

## 预览
![image](https://github.com/user-attachments/assets/b41effcc-df05-417e-9e25-e729e27e6429)
![image](https://github.com/user-attachments/assets/d83730cb-487c-4ba8-8b8f-5ddffd38a4eb)

## 配置环境
```bash
conda create -n qrjs conda-forge::opencv
pip install pyzbar -i https://pypi.tuna.tsinghua.edu.cn/simple
安装依赖：https://www.microsoft.com/zh-cn/download/details.aspx?id=40784
```
## 如何使用
1. 将 `client.html` 发送的靶机
2. 在自己电脑上配置好环境后运行 `server.py`
3. 靶机上浏览器打开 `client.html` 后，选择要传输的文件
4. 将自己电脑的摄像头对准动态的二维码
