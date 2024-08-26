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
            