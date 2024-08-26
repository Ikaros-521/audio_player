# 导入所需的库
import time
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pyaudio
import os
import requests
import json
import logging
import traceback

class Common:
    def __init__(self) -> None:
        self.audio_out_path = "./out"

    # 获取北京时间
    def get_bj_time(self, type=0):
        """获取北京时间

        Args:
            type (int, str): 返回时间类型. 默认为 0.
                0 返回数据：年-月-日 时:分:秒
                1 返回数据：年-月-日
                2 返回数据：当前时间的秒
                3 返回数据：自1970年1月1日以来的秒数
                4 返回数据：返回自1970年1月1日以来的毫秒数 % 100
                5 返回数据：当前 时点分
                6 返回数据：当前时间的 时, 分

        Returns:
            str: 返回指定格式的时间字符串
            int, int
        """
        if type == 0:
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)  # 获取当前 UTC 时间
            SHA_TZ = timezone(
                timedelta(hours=8),
                name='Asia/Shanghai',
            )
            beijing_now = utc_now.astimezone(SHA_TZ)  # 将 UTC 时间转换为北京时间
            fmt = '%Y-%m-%d %H:%M:%S'
            now_fmt = beijing_now.strftime(fmt)
            return now_fmt
        elif type == 1:
            now = datetime.now()  # 获取当前时间
            year = now.year  # 获取当前年份
            month = now.month  # 获取当前月份
            day = now.day  # 获取当前日期

            return str(year) + "-" + str(month) + "-" + str(day)
        elif type == 2:
            now = time.localtime()  # 获取当前时间

            # hour = now.tm_hour   # 获取当前小时
            # minute = now.tm_min  # 获取当前分钟 
            second = now.tm_sec  # 获取当前秒数

            return str(second)
        elif type == 3:
            current_time = time.time()  # 返回自1970年1月1日以来的秒数

            return str(current_time)
        elif type == 4:
            current_time = time.time()  # 返回自1970年1月1日以来的秒数
            current_milliseconds = int(current_time * 1000) # 毫秒为单位
            tgt_time = current_milliseconds % 100 # 用于生成音频文件名

            return str(tgt_time)
        elif type == 5:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour   # 获取当前小时
            minute = now.tm_min  # 获取当前分钟

            return str(hour) + "点" + str(minute) + "分"
        elif type == 6:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour   # 获取当前小时
            minute = now.tm_min  # 获取当前分钟 

            return hour, minute
    
    # 获取新的音频路径
    def get_new_audio_path(self, audio_out_path, file_name):
        # 判断路径是否为绝对路径
        if os.path.isabs(audio_out_path):
            # 如果是绝对路径，直接使用
            voice_tmp_path = os.path.join(audio_out_path, file_name)
        else:
            # 如果不是绝对路径，检查是否包含 ./，如果不包含，添加 ./，然后拼接路径
            if not audio_out_path.startswith('./'):
                audio_out_path = './' + audio_out_path
            voice_tmp_path = os.path.normpath(os.path.join(audio_out_path, file_name))

        return voice_tmp_path
    
    def get_all_audio_device_info(self):
        audio = pyaudio.PyAudio()

        device_infos = {}
        device_count = audio.get_device_count()
        index = 0

        for device_index in range(device_count):
            device_info = audio.get_device_info_by_index(device_index)
            if device_info['maxOutputChannels'] > 0:
                device_infos[index] = {"device_index": device_index, "device_info": device_info['name']}
                index += 1

        return device_infos
    
    # 请求web字幕打印机
    def send_to_web_captions_printer(self, api_ip_port, data):
        """请求web字幕打印机

        Args:
            api_ip_port (str): api请求地址
            data (dict): 包含用户名,弹幕内容

        Returns:
            bool: True/False
        """

        # user_name = data["username"]
        content = data["content"]

        # 记录数据库):
        try:
            response = requests.get(url=api_ip_port + f'/send_message?content={content}')
            response.raise_for_status()  # 检查响应的状态码

            result = response.content
            ret = json.loads(result)

            logging.debug(ret)

            if ret['code'] == 200:
                logging.debug(ret['message'])
                return True
            else:
                logging.error(ret['message'])
                return False
        except Exception as e:
            logging.error('web字幕打印机请求失败！请确认配置是否正确或者服务端是否运行！')
            logging.error(traceback.format_exc())
            return False
        

    def send_request(self, url, method='GET', json_data=None, resp_data_type="json", timeout=60):
        """
        发送 HTTP 请求并返回结果

        Parameters:
            url (str): 请求的 URL
            method (str): 请求方法，'GET' 或 'POST'
            json_data (dict): JSON 数据，用于 POST 请求
            resp_data_type (str): 返回数据的类型（json | content）
            timeout (int): 请求超时时间

        Returns:
            dict|str: 包含响应的 JSON数据 | 字符串数据
        """
        headers = {'Content-Type': 'application/json'}

        try:
            if method in ['GET', 'get']:
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method in ['POST', 'post']:
                response = requests.post(url, headers=headers, data=json.dumps(json_data), timeout=timeout)
            else:
                raise ValueError('无效 method. 支持的 methods 为 GET 和 POST.')

            # 检查请求是否成功
            response.raise_for_status()

            if resp_data_type == "json":
                # 解析响应的 JSON 数据
                result = response.json()
            else:
                result = response.content
                # 使用 'utf-8' 编码来解码字节串
                result = result.decode('utf-8')

            return result

        except requests.exceptions.RequestException as e:
            logging.error(traceback.format_exc())
            logging.error(f"请求出错: {e}")
            return None

    # 下载音频
    def download_audio(self, type: str, file_url: str, timeout: int = 30, request_type: str = "get", data=None, json_data=None, audio_suffix: str = "wav"):
        try:
            if request_type == "get":
                response = requests.get(file_url, params=data, timeout=timeout)
            else:
                response = requests.post(file_url, data=data, json=json_data, timeout=timeout)

            if response.status_code == 200:
                content = response.content
                file_name = type + '_' + self.get_bj_time(4) + '.' + audio_suffix
                voice_tmp_path = self.get_new_audio_path(self.audio_out_path, file_name)
                with open(voice_tmp_path, 'wb') as file:
                    file.write(content)
                return voice_tmp_path
            else:
                logging.error(f'{type} 下载音频失败: {response.status_code}')
                return None
        except requests.Timeout:
            logging.error(f"{type} 下载音频超时")
            return None

    def search_audio_file(self, directory: str, file_name: str, audio_suffixes: list = None):
        """
        从指定路径下搜索音频文件，搜到就返回音频文件绝对路径，搜不到就返回None。

        :param directory: 要搜索的目录
        :param file_name: 音频文件名（不含文件拓展名）
        :param audio_suffixes: 可能的音频文件后缀列表，如 ['wav', 'mp3', 'flac']。默认为 ['wav', 'mp3']。
        :return: 找到的音频文件绝对路径，或者 None
        """
        if audio_suffixes is None:
            audio_suffixes = ['wav', 'mp3']

        try:
            for root, _, files in os.walk(directory):
                for suffix in audio_suffixes:
                    target_file = f"{file_name}.{suffix}"
                    if target_file in files:
                        return os.path.join(root, target_file)
            return None
        except Exception as e:
            logging.error(f"搜索音频文件时发生异常: {str(e)}")
            return None  
        
    def copy_audio_file(self, source_path: str, destination_directory: str, rename: bool = False, new_name: str = None):
        """
        拷贝音频文件到指定路径，并支持自定义是否重命名。

        :param source_path: 源音频文件的绝对路径
        :param destination_directory: 目标目录路径
        :param rename: 是否重命名音频文件，默认为 False
        :param new_name: 新的文件名（不包括文件扩展名），仅在 rename=True 时有效
        :return: 拷贝后的音频文件绝对路径，或者 None
        """
        try:
            import shutil 

            if not os.path.exists(source_path):
                logging.error(f"源文件不存在: {source_path}")
                return None

            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
            
            file_extension = os.path.splitext(source_path)[1]
            if rename and new_name:
                destination_path = os.path.join(destination_directory, new_name + file_extension)
            else:
                destination_path = os.path.join(destination_directory, os.path.basename(source_path))

            shutil.copy2(source_path, destination_path)
            return destination_path
        except Exception as e:
            logging.error(f"拷贝音频文件时发生异常: {str(e)}")
            return None
    
    def clear_audio_files(self, directory: str, audio_suffixes: list = None):
        """
        清空指定文件夹内的所有音频文件。

        :param directory: 要清空的文件夹路径
        :param audio_suffixes: 需要删除的音频文件后缀列表，如 ['wav', 'mp3', 'flac']。默认为 ['wav', 'mp3']。
        :return: 成功清空返回 True，失败返回 False
        """
        if audio_suffixes is None:
            audio_suffixes = ['wav', 'mp3']

        try:
            if not os.path.exists(directory):
                logging.error(f"指定的目录不存在: {directory}")
                return False

            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(suffix) for suffix in audio_suffixes):
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                        logging.info(f"已删除音频文件: {file_path}")
            return True
        except Exception as e:
            logging.error(f"清空音频文件时发生异常: {str(e)}")
            return False
