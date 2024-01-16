import logging, json
import webbrowser
from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import asyncio
import os, sys

from utils.common import Common
from utils.logger import Configure_logger
from utils.audio_play_center import AUDIO_PLAY_CENTER


common = Common()

# 日志文件路径
log_file = "./log/log-" + common.get_bj_time(1) + ".txt"
Configure_logger(log_file)

# 配置文件路径
config_file_path = "config.json"

audio_play_center = None

async def start_play_thread():
    audio_play_center.start_play_thread()

if __name__ == '__main__':
    os.environ['GEVENT_SUPPORT'] = 'True'

    with open(config_file_path, 'r', encoding="utf-8") as file:
        config = json.load(file)
    audio_play_center = AUDIO_PLAY_CENTER(config)

    # 创建并启动服务器线程
    # server_thread = threading.Thread(target=lambda: asyncio.run(audio_play_center.start_play_thread()))
    # server_thread.start()
    asyncio.run(audio_play_center.start_play_thread())

    app = Flask(__name__, static_folder='./')
    CORS(app)  # 允许跨域请求
    socketio = SocketIO(app, cors_allowed_origins="*")

    def self_restart():
        try:
            # 获取当前 Python 解释器的可执行文件路径
            python_executable = sys.executable

            # 获取当前脚本的文件路径
            script_file = os.path.abspath(__file__)

            # 重启当前程序
            os.execv(python_executable, ['python', script_file])
        except Exception as e:
            print(f"Failed to restart the program: {e}")


    @app.route('/index.html')
    def serve_file():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/css/index.css')
    def serve_file2():
        return send_from_directory(app.static_folder, 'css/index.css')

    @app.route('/js/index.js')
    def serve_file3():
        return send_from_directory(app.static_folder, 'js/index.js')

    @app.route('/get_all_audio_device_info', methods=['GET'])
    def get_all_audio_device_info():
        try:
            all_audio_device_info = common.get_all_audio_device_info()

            return jsonify(all_audio_device_info)
        except Exception as e:
            return jsonify({"code": -1, "message": f"获取所有声卡信息失败{e}"})

    @app.route('/get_config', methods=['GET'])
    def get_config():
        try:
            
            # 打开文件并解析JSON数据
            with open(config_file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)

            return jsonify(data)
        except Exception as e:
            return jsonify({"code": -1, "message": f"获取本地配置失败{e}"})
        
    @app.route('/save_config', methods=['POST'])
    def save_config():
        try:
            content = request.get_json()
            logging.info(content)

            try:
                with open(config_file_path, 'w', encoding="utf-8") as config_file:
                    json.dump(content, config_file, indent=2, ensure_ascii=False)
                    config_file.flush()  # 刷新缓冲区，确保写入立即生效

                logging.info("配置数据已成功写入文件！")
                return jsonify({"code": 200, "message": "配置数据已成功写入文件！"})
            except Exception as e:
                logging.error(f"无法写入配置文件！{e}")
                return jsonify({"code": -1, "message": "无法写入配置文件！{e}"})

            
        except Exception as e:
            return jsonify({"code": -1, "message": f"无法写入配置文件！{e}"})

    @app.route('/clear', methods=['GET'])
    def clear():
        try:
            audio_play_center.clear_audio_json()

            return jsonify({"code": 200, "message": "清空列表成功！"})
        except Exception as e:
            return jsonify({"code": -1, "message": f"清空列表失败！{e}"})

    @app.route('/get_list', methods=['GET'])
    def get_list():
        try:
            json_str = audio_play_center.get_audio_json_list()
            data_json = json.loads(json_str)

            return jsonify({"code": 200, "message": data_json})
        except Exception as e:
            return jsonify({"code": -1, "message": f"清空列表失败！{e}"})

    
    @app.route('/run', methods=['POST'])
    def run():
        global audio_play_center

        try:
            content = request.get_json()
            logging.info(content)

            try:
                self_restart()

                logging.info("配置数据已成功写入文件！")
                return jsonify({"code": 200, "message": "配置数据已成功写入文件！"})
            except Exception as e:
                logging.error(f"无法写入配置文件！{e}")
                return jsonify({"code": -1, "message": "无法写入配置文件！{e}"})

        except Exception as e:
            return jsonify({"code": -1, "message": f"无法写入配置文件！{e}"})

    @app.route('/play', methods=['POST'])
    def play():
        global audio_play_center

        try:
            try:
                content = request.get_json()
                logging.info(content)

                audio_play_center.add_audio_json(content)

                logging.info("添加音频信息成功！")
                return jsonify({"code": 200, "message": "添加音频信息成功！"})
            except Exception as e:
                logging.error(f"添加音频信息失败！{e}")
                return jsonify({"code": -1, "message": f"添加音频信息失败！{e}"})

        except Exception as e:
            return jsonify({"code": -1, "message": f"添加音频信息失败！{e}"})

    @app.route('/pause_stream', methods=['GET'])
    def pause_stream():
        try:
            audio_play_center.pause_stream()

            return jsonify({"code": 200, "message": "暂停成功！"})
        except Exception as e:
            return jsonify({"code": -1, "message": f"暂停失败！{e}"})
        
    @app.route('/resume_stream', methods=['GET'])
    def resume_stream():
        try:
            audio_play_center.resume_stream()

            return jsonify({"code": 200, "message": "恢复成功！"})
        except Exception as e:
            return jsonify({"code": -1, "message": f"恢复失败！{e}"})

    @app.route('/skip_current_stream', methods=['GET'])
    def skip_current_stream():
        try:
            audio_play_center.skip_current_stream()

            return jsonify({"code": 200, "message": "跳过当前播放文件成功！"})
        except Exception as e:
            return jsonify({"code": -1, "message": f"跳过当前播放文件失败！{e}"})

    port = 5600
    url = f'http://localhost:{port}/index.html'
    webbrowser.open(url)
    logging.info(f"浏览器访问地址：{url}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
