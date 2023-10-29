import logging, json
import webbrowser
from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import asyncio

from utils.common import Common
from utils.logger import Configure_logger
from utils.audio_play_center import AUDIO_PLAY_CENTER

import os


common = Common()

# 日志文件路径
log_file = "./log/log-" + common.get_bj_time(1) + ".txt"
Configure_logger(log_file)

config_file_path = "config.json"

audio_play_center = None

app = Flask(__name__, static_folder='./')
CORS(app)  # 允许跨域请求
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/index.html')
def serve_file():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/css/index.css')
def serve_file2():
    return send_from_directory(app.static_folder, 'css/index.css')

@app.route('/js/index.js')
def serve_file3():
    return send_from_directory(app.static_folder, 'js/index.js')

@app.route('/send_message', methods=['GET'])
def send_message():
    try:
        content = request.args.get('content')
        
        # 将数据发送到 WebSocket
        socketio.emit('message', {'content': content})

        return jsonify({"code": 200, "message": "数据发送到WebSocket成功"})
    except Exception as e:
        return jsonify({"code": -1, "message": f"数据发送到WebSocket失败\n{e}"})

@app.route('/get_all_audio_device_info', methods=['GET'])
def get_all_audio_device_info():
    try:
        all_audio_device_info = common.get_all_audio_device_info()

        return jsonify(all_audio_device_info)
    except Exception as e:
        return jsonify({"code": -1, "message": f"获取所有声卡信息失败\n{e}"})

@app.route('/get_config', methods=['GET'])
def get_config():
    try:
        
        # 打开文件并解析JSON数据
        with open(config_file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)

        return jsonify(data)
    except Exception as e:
        return jsonify({"code": -1, "message": f"获取本地配置失败\n{e}"})
    
@app.route('/save_config', methods=['POST'])
def save_config():
    try:
        content = request.get_json()
        logging.info(content)

        try:
            with open(config_file_path, 'w', encoding="utf-8") as config_file:
                json.dump(content, config_file, ensure_ascii=False)
                config_file.flush()  # 刷新缓冲区，确保写入立即生效

            logging.info("配置数据已成功写入文件！")
            return jsonify({"code": 200, "message": "配置数据已成功写入文件！"})
        except Exception as e:
            logging.error(f"无法写入配置文件！\n{e}")
            return jsonify({"code": -1, "message": "无法写入配置文件！\n{e}"})

        
    except Exception as e:
        return jsonify({"code": -1, "message": f"获取所有声卡信息失败\n{e}"})

@app.route('/run', methods=['POST'])
async def run():
    global audio_play_center

    try:
        content = await request.get_json()
        logging.info(content)

        try:
            audio_play_center = AUDIO_PLAY_CENTER(int(content["device_index"]), int(content["rate"]))
            asyncio.run(audio_play_center.start_play_thread())

            data_json = {
                "voice_path": "out\\2.mp3"
            }

            audio_play_center.add_audio_json(data_json)

            logging.info("配置数据已成功写入文件！")
            return jsonify({"code": 200, "message": "配置数据已成功写入文件！"})
        except Exception as e:
            logging.error(f"无法写入配置文件！\n{e}")
            return jsonify({"code": -1, "message": "无法写入配置文件！\n{e}"})

        
    except Exception as e:
        return jsonify({"code": -1, "message": f"获取所有声卡信息失败\n{e}"})

if __name__ == '__main__':
    os.environ['GEVENT_SUPPORT'] = 'True'

    port = 5600
    url = f'http://localhost:{port}/index.html'
    webbrowser.open(url)
    logging.info(f"浏览器访问地址：{url}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
