# 前言
用于做为独立的音频播放器使用。  
支持HTTP API，可以配合其他程序协同工作。  

# 使用&部署
开发系统：win11  
python：3.10  
安装依赖：`pip install -r requirements.txt`  
其他依赖：ffmpeg  
运行：`python app.py`  
浏览器访问：`http://127.0.0.1:5600/index.html`  

## 整合包

github：[https://github.com/Ikaros-521/audio_player/releases](https://github.com/Ikaros-521/audio_player/releases)  
迅雷云盘： [https://pan.xunlei.com/s/VNitDF0Y3l-qwTpE0A5Rh4DaA1](https://pan.xunlei.com/s/VNitDF0Y3l-qwTpE0A5Rh4DaA1)  
夸克网盘： [https://pan.quark.cn/s/936dcae8aba0](https://pan.quark.cn/s/936dcae8aba0)  
 
## API

<section>
  <h3>添加音频数据到播放列表</h3>
  <p>使用 POST 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/play</code>
  <p>请求体（json字符串）：</p>
  <pre class="code-block">
      <code>
{
  "voice_path": "out\\2.mp3",
  "voice_name": "2",
  "mode": "local",
  "content": "音频文本内容",
  "random_speed": {
    "enable": false,
    "max": 1.3,
    "min": 0.8
  },
  "speed": 1,
  "insert_index": 0
}
      </code>
  </pre>
  <p>参数说明：</p>
  <ul>
      <li><strong>voice_path：</strong> 音频文件路径</li>
      <li><strong>voice_name：</strong> 音频文件名（非必填，传入情况下优先检索本地cache路径下的音频文件是否存在，不存在则转为使用voice_path）</li>
      <li><strong>mode：</strong> 音频加载模式（local/url）非必填，不传默认为local，本地路径。url情况下，voice_path可以是在线url链接</li>
      <li><strong>content：</strong> 音频文本内容</li>
      <li><strong>random_speed enable：</strong> 启用随机播放功能（非必填，不填默认读取本地配置）</li>
      <li><strong>random_speed max：</strong> 随机播放的最大速度（非必填，不填默认读取本地配置）</li>
      <li><strong>random_speed min：</strong> 随机播放的最小速度（非必填，不填默认读取本地配置）</li>
      <li><strong>speed：</strong> 播放速度（非必填，不填默认读取本地配置）</li>
      <li><strong>insert_index：</strong> 数据插入列表的索引值（非必填，不填默认末尾插入）</li>
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
  <h3>清空播放列表</h3>
  <p>使用 GET 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/clear</code>
</section>
<section>
  <h3>获取播放列表</h3>
  <p>使用 GET 请求到以下 URL：</p>
  <code>http://127.0.0.1:5600/get_list</code>
</section>

## 配置

<section>
  <pre class="code-block">
      <code>
{
  "device_index": 5,
  "captions_printer": {
    "api_ip_port": "http://127.0.0.1:5500",
    "enable": false
  },
  "random_speed": {
    "enable": false,
    "max": 1.3,
    "min": 0.8
  },
  "speed": 1,
  "random_audio_interval": {
    "enable": false,
    "max": 3,
    "min": 0.1
  },
  "audio_interval": 0.5,
  "priority_mapping": {
    "copywriting": 1, 
    "abnormal_alarm": 1, 
    "trends_copywriting": 10, 
    "idle_time_task": 10,
    "image_recognition_schedule": 10,
    "local_qa_audio": 20,
    "comment": 20,
    "song": 20,
    "read_comment": 20,
    "gift": 20,
    "follow": 20,
    "reread": 30,
    "direct_reply": 30
  },
  "ai_vtuber": {
    "api_ip": "127.0.0.1",
    "api_port": 8082,
    "callback_enable": false
  }
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
      <li><strong>captions_printer enable：</strong> 启用对接web字幕打印机</li>
      <li><strong>captions_printer api_ip_port：</strong> web字幕打印机服务的API地址</li>
      <li><strong>random_audio_interval enable：</strong> 启用随机音频间隔功能</li>
      <li><strong>random_audio_interval max：</strong> 随机音频播放的最大间隔</li>
      <li><strong>random_audio_interval min：</strong> 随机音频播放的最小间隔</li>
      <li><strong>audio_interval：</strong> 音频播放间隔</li>
      <li><strong>priority_mapping：</strong> 音频数据优先级（type键值，值越大优先级越高）</li>
      <li><strong>ai_vtuber enable：</strong> 启用ai_vtuber回传功能</li>
      <li><strong>ai_vtuber api_ip：</strong> ai_vtuber内部http服务ip</li>
      <li><strong>ai_vtuber api_port：</strong> ai_vtuber内部http服务端口</li>
  </ul>
</section>

# FAQ

1.5600端口冲突  
可以修改`app.py`和`js/index.js`中，搜索`5600`，全部改成你的新端口即可。  

# 更新日志

- 2024-08-30
  - 配置文件新增参数 pop_audio_when_read，支持控制 音频列表信息，在读取音频播放时是否在读取时就删除音频（true） 还是 播放完后再删除（false），在false情况下，第一个数据就是正在播放的音频信息

- 2024-08-26
  - 支持 mode传参，local/url，可以通过url模式，将voice_path换成url在线路径，实现云音频播放
  - 新增参数 voice_name 音频文件名（非必填，传入情况下优先检索本地cache路径下的音频文件是否存在，不存在则转为使用voice_path）
  - 运行自动清空缓存文件夹cache

- 2024-04-29
  - 新增 AI Vtuber回传功能，配合闲时任务的待播放音频数 功能

- 2024-03-20
  - 配置文件新增优先级配置项，针对各个音频数据类型，可以自定义优先级进行排队，用于实现弹幕优先于文案的这种效果。

- 2024-02-18
  - 更换协议为GPL3.0

- 2024-01-21
  - 修复传参不携带type键时的插入异常bug
  
- 2024-01-16
  - 支持传入随机速度等参数来控制输出音频效果
  - 新增实时刷新的当前播放列表显示框
  - 添加音频新增 插入索引字段，可以自定义插入的位置，用于让音频可以插队(默认非文案的音频自动插到文案前面)
  - 新增配置项 随机音频间隔和音频间隔，用于控制音频播放的间隔，让机器嘴歇会

- 2024-01-15
  - 修改列表为列表的形式，提高了数据可操作性
  - 增加了线程锁保护
  - 修改暂停、恢复播放功能实现，实现真正意义上的暂停和暂停点恢复播放。

- 2023-11-02
  - 给播放线程追加异常捕获，起码不会直接挂了
  - 新增web字幕打印机的对接
  - 美化UI

- 2023-11-01
  - 新增跳过当前播放、清空播放列表和获取播放列表功能
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