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
    
    # 发送音频播放信息给AI Vtuber的http服务端
    def send_audio_play_info_to_callback(self, data: dict=None):
        """发送音频播放信息给AI Vtuber的http服务端

        Args:
            data (dict): 音频播放信息
        """
        if data is None:
            data = {
                "type": "audio_playback_completed",
                "data": {
                    # 待播放音频数量
                    "wait_play_audio_num": len(self.audio_json_list),
                }
            }

        logging.debug(f"data={data}")

        resp = self.common.send_request(f'http://{self.config_data["ai_vtuber"]["api_ip"]}:{self.config_data["ai_vtuber"]["api_port"]}/callback', "POST", data)

        return resp
    

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
                    # 是否读取并删除
                    if self.config_data["pop_audio_when_read"]:
                        data_json = self.audio_json_list.pop(0)  # 从列表中获取第一个元素并删除
                    else:
                        data_json = self.audio_json_list[0]
                
                voice_path = None
                # 是否存在此参数
                if "voice_name" in data_json:
                    if data_json["voice_name"] != "":
                        voice_name = data_json["voice_name"]
                        voice_path = self.common.search_audio_file("cache", voice_name)
                
                # 本地没有检索到就加载别的
                if voice_path is None:
                    voice_path = data_json["voice_path"]
                    
                    # 区分音频路径类型
                    if "mode" in data_json:
                        if data_json["mode"] == "url":
                            # logging.info(f"下载音频文件 {voice_path}")
                            # 下载音频文件
                            voice_path = self.common.download_audio("URL", voice_path, 60, "get")
                            # 失败就跳过
                            if voice_path is None:
                                # 是否读取并删除
                                if not self.config_data["pop_audio_when_read"]:
                                    data_json = self.audio_json_list.pop(0)  # 从列表中获取第一个元素并删除
                                
                                continue
                            
                    # 备份音频到cache目录
                    if "voice_name" in data_json:
                        if data_json["voice_name"] != "":
                            new_voice_path = self.common.copy_audio_file(voice_path, "cache", True, data_json["voice_name"])
 
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

                # 播放完毕

                # 是否读取并删除
                if not self.config_data["pop_audio_when_read"]:
                    data_json = self.audio_json_list.pop(0)  # 从列表中获取第一个元素并删除

                # 启用音频信息回传AI Vtuber功能
                if self.config_data["ai_vtuber"]["callback_enable"]:
                    self.send_audio_play_info_to_callback()

                # 启用随机音频间隔功能
                if self.config_data["random_audio_interval"]["enable"]:
                    time.sleep(random.uniform(self.config_data["random_audio_interval"]["min"], self.config_data["random_audio_interval"]["max"]))
                else:
                    time.sleep(self.config_data["audio_interval"])
            except AttributeError as e:
                # 处理异常
                logging.error(traceback.format_exc())
                # 初始化核心变量
                self.audio = pyaudio.PyAudio()
                self.stream = None
                self.audio_json_list = []  # 重置列表
            except Exception as e:
                logging.error(traceback.format_exc())

                # 是否读取并删除，不管啥异常 删了再说
                if not self.config_data["pop_audio_when_read"]:
                    data_json = self.audio_json_list.pop(0)  # 从列表中获取第一个元素并删除

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

    # 数据根据优先级排队插入
    def data_priority_insert(self, audio_json):
        """
        type目前有
            reread_top_priority 最高优先级-复读
            comment 弹幕
            local_qa_audio 本地问答音频
            song 歌曲
            reread 复读
            direct_reply 直接回复
            read_comment 念弹幕
            gift 礼物
            entrance 用户入场
            follow 用户关注
            schedule 定时任务
            idle_time_task 闲时任务
            abnormal_alarm 异常报警
            image_recognition_schedule 图像识别定时任务
            trends_copywriting 动态文案
        """
        logging.debug(f"audio_json: {audio_json}")

        # 定义 type 到优先级的映射，相同优先级的 type 映射到相同的值，值越大优先级越高
        priority_mapping = self.config_data["priority_mapping"]
        
        def get_priority_level(audio_json):
            """根据 audio_json 的 'type' 键返回优先级，未定义的 type 或缺失 'type' 键将返回 None"""
            # 检查 audio_json 是否包含 'type' 键且该键的值在 priority_mapping 中
            audio_type = audio_json.get("type")
            return priority_mapping.get(audio_type, None)

        # 查找插入位置
        new_data_priority = get_priority_level(audio_json)

        logging.info(f"new_data_priority: {new_data_priority}")
        
        # 如果新数据没有 'type' 键或其类型不在 priority_mapping 中，直接插入到末尾
        if new_data_priority is None:
            insert_position = len(self.audio_json_list)
        else:
            insert_position = 0  # 默认插入到列表开头
            # 从列表的最后一个元素开始，向前遍历列表，直到第一个元素
            for i in range(len(self.audio_json_list) - 1, -1, -1):
                item_priority = get_priority_level(self.audio_json_list[i])
                # 确保比较时排除未定义类型的元素
                if item_priority is not None and item_priority >= new_data_priority:
                    # 如果找到一个元素，其优先级小于或等于新数据，则将新数据插入到此元素之后
                    insert_position = i + 1
                    break

        # 在计算出的位置插入新数据
        self.audio_json_list.insert(insert_position, audio_json)


    def add_audio_json(self, audio_json):
        with self.list_lock:  # 使用锁保护列表操作
            logging.info(f"audio_json: {audio_json}")

            # 是否传入了指定的插入索引
            if "insert_index" in audio_json:
                if audio_json["insert_index"] == -1:
                    self.audio_json_list.append(audio_json)  # 将音频数据添加到列表末尾
                else:
                    self.audio_json_list.insert(audio_json["insert_index"], audio_json)
            else:
                self.data_priority_insert(audio_json)
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
