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
 
## API

<section>
  <h3>添加音频数据到播放队列</h3>
  <p>使用 POST 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/play</code>
  <p>请求体（json字符串）：</p>
  <pre class="code-block">
      <code>
{
  "voice_path": "out\\2.mp3",
  "content": "音频文本内容，预留字段，暂未使用"
}
      </code>
  </pre>
  <p>参数说明：</p>
  <ul>
      <li><strong>voice_path：</strong> 音频文件路径</li>
      <li><strong>content：</strong> 音频文本内容，预留字段，暂未使用</li>
  </ul>
  <p>返回数据：</p>
  <pre class="code-block">
      <code>
// 成功返回
{"code": 200, "message": "添加音频信息成功！"}
    </code>
  </pre>
  <pre class="code-block">
    <code>
// 失败返回
{"code": -1, "message": "添加音频信息失败！{e}"}
      </code>
  </pre>
  
</section>
<section>
  <h3>暂停播放</h3>
  <p>使用 GET 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/pause_stream</code>
</section>
<section>
  <h3>恢复播放</h3>
  <p>使用 GET 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/resume_stream</code>
</section>
<section>
  <h3>跳过当前播放</h3>
  <p>使用 GET 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/skip_current_stream</code>
</section>
<section>
  <h3>清空播放队列</h3>
  <p>使用 GET 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/clear</code>
</section>
<section>
  <h3>获取播放队列</h3>
  <p>使用 GET 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/get_list</code>
</section>

## 配置

<section>
  <pre class="code-block">
      <code>
{
  "device_index": 5,
  "random_speed": {
    "enable": false,
    "max": 1.3,
    "min": 0.8
  },
  "speed": 1
}
      </code>
  </pre>
  <p>配置说明：</p>
  <ul>
      <li><strong>device_index：</strong> 声卡设备索引值</li>
      <li><strong>random_speed enable：</strong> 启用随机播放功能</li>
      <li><strong>random_speed max：</strong> 随机播放的最大速度</li>
      <li><strong>random_speed min：</strong> 随机播放的最小速度</li>
      <li><strong>speed：</strong> 播放速度</li>
  </ul>
</section>

# FAQ
1.5600端口冲突  
可以修改`app.py`和`js/index.js`中，搜索`5600`，全部改成你的新端口即可。  

# 更新日志

- 2023-11-01
  - 新增跳过当前播放、清空播放队列和获取播放队列功能
  - 优化文档

- 2023-10-31
  - 优化UI排版
  - 新增暂停/恢复播放功能
  - 补充API文档

- 2023-10-29
  - 基本功能通过，可以本地调用播放音频
  - 删除频率配置，新增播放速度、随机播放开关和上下限配置

- 2023-10-28
  - 开发中