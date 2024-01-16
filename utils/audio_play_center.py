import pyaudio
from pydub import AudioSegment
import wave
import threading
import logging, time
import threading
import random
import json
import traceback
import requests

from utils.common import Common
from utils.logger import Configure_logger


class AUDIO_PLAY_CENTER:

    def __init__(self, config_data):
        self.common = Common()

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.audio_out_path = "./out"

        self.audio = pyaudio.PyAudio()
        self.config_data = config_data
        self.stream = None
        self.play_thread = None

        self.pause_event = threading.Event()  # 用于暂停音频播放
        self.audio_data_event = threading.Event()  # 用于在有新数据时通知线程

        self.audio_json_list = []  # 使用列表替换原先的列表

        self.list_lock = threading.Lock()  # 列表操作的锁
        

    def play_audio(self):
        # common = Common()

        while True:
            try:
                # 暂停事件阻塞
                if self.pause_event.is_set():
                    time.sleep(0.1)
                    continue

                if self.stream and self.stream.is_active():
                    time.sleep(0.1)
                    # 如果当前有活跃的流，则继续播放，不获取新的音频数据
                    continue

                if len(self.audio_json_list) <= 0:
                    self.audio_data_event.clear()  # 没有数据，清除事件
                    self.audio_data_event.wait()  # 等待新数据
                    continue

                with self.list_lock:  # 使用锁保护列表操作
                    data_json = self.audio_json_list.pop(0)  # 从列表中获取第一个元素并删除
                voice_path = data_json["voice_path"]
                audio = AudioSegment.from_file(voice_path)
                # 获取新的音频路径
                tmp_audio_path = self.common.get_new_audio_path(self.audio_out_path, file_name='tmp_' + self.common.get_bj_time(4) + '.wav')
                audio.export(tmp_audio_path, format="wav")
                wf = wave.open(tmp_audio_path, 'rb')

                def callback(in_data, frame_count, time_info, status):
                    data = wf.readframes(frame_count)
                    return (data, pyaudio.paContinue)

                # 调节音量，示例：提高或降低 6 分贝(没有效果)
                # if "volume_change" in data_json:
                #     volume_change = data_json["volume_change"]
                #     audio += volume_change  # 调整音量

                # 请求传参是否包含了相关参数，包含则优先使用传参的参数
                if "random_speed" in data_json:
                    # 是否启用了随机播放功能
                    if data_json["random_speed"]["enable"]:
                        random_speed = random.uniform(data_json["random_speed"]["min"], data_json["random_speed"]["max"])
                        new_rate = int(wf.getframerate() * random_speed)
                    else:
                        new_rate = int(wf.getframerate() * data_json["speed"])
                elif "speed" in data_json:
                    new_rate = int(wf.getframerate() * data_json["speed"])
                else:
                    # 是否启用了随机播放功能
                    if self.config_data["random_speed"]["enable"]:
                        random_speed = random.uniform(self.config_data["random_speed"]["min"], self.config_data["random_speed"]["max"])
                        new_rate = int(wf.getframerate() * random_speed)
                    else:
                        new_rate = int(wf.getframerate() * self.config_data["speed"])

                self.stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                    channels=wf.getnchannels(),
                                    rate=new_rate,
                                    output=True,
                                    output_device_index=self.config_data["device_index"],
                                    stream_callback=callback)
                
                # 是否启用了web字幕打印机的对接
                if self.config_data["captions_printer"]["enable"]:
                    if "content" in data_json:
                        self.common.send_to_web_captions_printer(self.config_data["captions_printer"]["api_ip_port"], data_json)
                
                self.stream.start_stream()

                while self.stream.is_active() and not self.pause_event.is_set():
                    pass  # 持续播放

                # self.stream.stop_stream()
                # self.stream.close()
                # wf.close()
            except AttributeError as e:
                # 处理异常
                logging.error(traceback.format_exc())
                # 初始化核心变量
                self.audio = pyaudio.PyAudio()
                self.stream = None
                self.audio_json_list = []  # 重置列表
            except Exception as e:
                logging.error(traceback.format_exc())

    async def start_play_thread(self):
        logging.info("启动音频播放线程...")
        self.play_thread = threading.Thread(target=self.play_audio)
        # self.play_thread.daemon = True
        self.play_thread.start()
        logging.info("启动音频播放线程")

    """
    配置相关
    """
    def get_all_audio_device_info(self):
        device_infos = []
        device_count = self.audio.get_device_count()

        for device_index in range(device_count):
            device_info = self.audio.get_device_info_by_index(device_index)
            if device_info['maxOutputChannels'] > 0:
                device_infos.append({"device_index": device_index, "device_info": device_info['name']})

        return device_infos

    def set_device_index(self, device_index: int):
        self.device_index = device_index

    """
    数据相关
    """
    def add_audio_json(self, audio_json):
        with self.list_lock:  # 使用锁保护列表操作
            # 是否传入了指定的插入索引
            if "insert_index" in audio_json:
                if audio_json["insert_index"] == -1:
                    self.audio_json_list.append(audio_json)  # 将音频数据添加到列表末尾
                else:
                    self.audio_json_list.insert(audio_json["insert_index"], audio_json)
            else:
                # 找到最后一个 type 不是 'copywriting' 的索引，如果所有 type 都是 'copywriting'，则返回 0
                last_non_copywriting_index = next((i for i in range(len(self.audio_json_list) - 1, -1, -1) if self.audio_json_list[i]["type"] != "copywriting"), -1)

                # 根据找到的索引决定插入位置
                insert_position = 0 if last_non_copywriting_index == -1 else last_non_copywriting_index + 1

                # 在计算出的位置插入新数据
                self.audio_json_list.insert(insert_position, audio_json)
        self.audio_data_event.set()  # 有新数据，设置事件
        logging.info(f"添加音频数据={audio_json}")

    def clear_audio_json(self):
        with self.list_lock:  # 使用锁保护列表操作
            self.audio_json_list.clear()  # 清空列表
        logging.info("清空音频数据列表")

    def get_audio_json_list(self):
        # 将列表数据转换为 JSON 字符串
        json_data = {"list": self.audio_json_list}
        json_str = json.dumps(json_data)
        return json_str

    """
    播放相关控制
    """
    def pause_stream(self):
        self.pause_event.set()
        if self.stream:
            self.stream.stop_stream()

    def resume_stream(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            if self.stream:
                self.stream.start_stream()

    def stop_stream_and_clear(self):
        self.pause_event.set()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        self.audio_json_list.clear()

    def skip_current_stream(self):
        with self.list_lock:
            if self.stream and (self.stream.is_active() or self.pause_event.is_set()):
                # 停止并关闭当前流，无论是否处于暂停状态
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

            # 清除暂停事件，以便继续播放下一个音频
            self.pause_event.clear()

            # 设置事件以确保从列表中取出下一个音频（如果有）
            if len(self.audio_json_list) > 0:
                self.audio_data_event.set()


if __name__ == '__main__':
    audio_play_center = AUDIO_PLAY_CENTER("config.json")
    audio_play_center.get_all_audio_device_info()
    audio_play_center.set_device_index(4)
    audio_play_center.start_play_thread()

    data_json = {
        "voice_path": "out\\2.mp3"
    }

    audio_play_center.add_audio_json(data_json)

    # 等待一段时间后暂停播放
    import time
    time.sleep(3)
    audio_play_center.pause_stream()

    # 等待一段时间后恢复播放
    time.sleep(3)
    audio_play_center.add_audio_json(data_json)
    audio_play_center.resume_stream()

    # 等待一段时间后中断播放
    time.sleep(3)
    audio_play_center.stop_stream()

    audio_play_center.terminate_audio()
