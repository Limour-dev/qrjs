# qrjs
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
