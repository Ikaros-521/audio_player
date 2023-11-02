import pyaudio
from pydub import AudioSegment
import wave
import threading
import logging, time
from queue import Queue
import random
import json
import traceback

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
        self.audio_json_queue = Queue()

    def play_audio(self):
        # common = Common()

        while True:
            try:
                # 暂停事件阻塞
                if self.pause_event.is_set():
                    time.sleep(0.1)
                    continue

                # if self.audio_json_queue.qsize() > 0:
                data_json = self.audio_json_queue.get(block=True)
                voice_path = data_json["voice_path"]
                audio = AudioSegment.from_file(voice_path)
                # 获取新的音频路径
                tmp_audio_path = self.common.get_new_audio_path(self.audio_out_path, file_name='tmp_' + self.common.get_bj_time(4) + '.wav')
                audio.export(tmp_audio_path, format="wav")
                wf = wave.open(tmp_audio_path, 'rb')

                def callback(in_data, frame_count, time_info, status):
                    data = wf.readframes(frame_count)
                    return (data, pyaudio.paContinue)

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
                
                self.stream.start_stream()

                while self.stream.is_active() and not self.pause_event.is_set():
                    pass  # 持续播放

                self.stream.stop_stream()
                self.stream.close()
                wf.close()
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
        self.audio_json_queue.put(audio_json)
        logging.info(f"添加音频数据={audio_json}")

    def clear_audio_json_queue(self):
        self.audio_json_queue.queue.clear()
        logging.info("清空音频数据队列")

    def get_audio_json_queue_list(self):
        # 获取队列中的数据，但不出队列
        queue_data = list(self.audio_json_queue.queue)

        # 查看获取的数据
        # 创建一个包含队列数据的字典
        json_data = {"list": []}
        for item in queue_data:
            json_data["list"].append(item)

        # 将数据存入 JSON 格式
        json_str = json.dumps(json_data)

        return json_str

    """
    播放相关控制
    """
    def pause_stream(self):
        self.pause_event.set()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def resume_stream(self):
        self.pause_event.clear()

    def stop_stream(self):
        self.pause_event.set()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio_json_queue.queue.clear()  # 清空音频队列

    def skip_current_stream(self):
        self.pause_stream()
        self.resume_stream()


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
