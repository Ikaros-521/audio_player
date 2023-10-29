# 前言
用于做为独立的音频播放器使用。  
支持HTTP API，可以配合其他程序协同工作。  

# 使用&部署
开发系统：win11  
python：3.10  
安装依赖：`pip install -r requirements.txt`  
运行：`python app.py`  
浏览器访问：`http://127.0.0.1:5600/index.html`  

## 整合包
 

# FAQ
1.5600端口冲突  
可以修改`app.py`和`js/index.js`中，搜索`5600`，全部改成你的新端口即可。  

# 更新日志
- v0.0.1
  - 开发中