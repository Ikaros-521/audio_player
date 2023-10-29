import pyaudio
from pydub import AudioSegment
import wave
import threading
import logging, time
from queue import Queue

from utils.common import Common
from utils.logger import Configure_logger


class AUDIO_PLAY_CENTER:

    def __init__(self, device_index=0, rate=44100):
        self.common = Common()

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.audio_out_path = "./out"

        self.audio = pyaudio.PyAudio()
        self.device_index = device_index
        self.rate = rate
        self.stream = None
        self.play_thread = None
        self.pause_event = threading.Event()  # 用于暂停音频播放
        self.audio_json_queue = Queue()

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

    def set_rate(self, rate: int):
        self.rate = rate

    def play_audio(self):
        # common = Common()

        while True:
            # 暂停事件阻塞
            if self.pause_event.is_set():
                time.sleep(0.1)
                continue

            if self.audio_json_queue.qsize() > 0:
                data_json = self.audio_json_queue.get()
                voice_path = data_json["voice_path"]
                audio = AudioSegment.from_file(voice_path)
                # 获取新的音频路径
                tmp_audio_path = self.common.get_new_audio_path(self.audio_out_path, file_name='tmp_' + self.common.get_bj_time(4) + '.wav')
                audio.export(tmp_audio_path, format="wav")
                wf = wave.open(tmp_audio_path, 'rb')

                def callback(in_data, frame_count, time_info, status):
                    data = wf.readframes(frame_count)
                    return (data, pyaudio.paContinue)

                self.stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                    channels=wf.getnchannels(),
                                    rate=self.rate,
                                    output=True,
                                    output_device_index=self.device_index,
                                    stream_callback=callback)
                self.stream.start_stream()

                while self.stream.is_active() and not self.pause_event.is_set():
                    pass  # 持续播放

                self.stream.stop_stream()
                self.stream.close()
                wf.close()

    def add_audio_json(self, audio_json):
        self.audio_json_queue.put(audio_json)
        logging.info(f"添加音频数据={audio_json}")

    async def start_play_thread(self):
        logging.info("启动音频播放线程...")
        self.play_thread = threading.Thread(target=self.play_audio)
        self.play_thread.start()
        logging.info("启动音频播放线程")

    def pause_stream(self):
        self.pause_event.set()

    def resume_stream(self):
        self.pause_event.clear()

    def stop_stream(self):
        self.pause_event.set()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio_json_queue.queue.clear()  # 清空音频队列


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
