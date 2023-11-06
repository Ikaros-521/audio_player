from audio_player import AUDIO_PLAYER
import os, time, logging

log_format = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("log.txt", encoding='utf-8', mode='a+')
stream_handler = logging.StreamHandler()

handlers = [file_handler, stream_handler]
logger.handlers = handlers

formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 定义一个函数来获取文件夹内的音频文件
def get_audio_files(folder_path):
    audio_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.mp3', '.wav', '.ogg', '.flac')):  # 根据你的需要添加其他音频文件扩展名
                audio_files.append(os.path.abspath(os.path.join(root, file)))
    return audio_files

# 指定包含音频文件的文件夹路径
folder_path = 'data'  # 请将此路径替换为你的文件夹路径

# 获取音频文件的绝对路径列表
audio_files = get_audio_files(folder_path)
logging.info(audio_files)

data_json = {
    "api_ip_port": "http://127.0.0.1:5600"
}

audio_player = AUDIO_PLAYER(data_json)

while True:
    # 打印所有音频文件的绝对路径
    for audio_file in audio_files:
        logging.info(audio_file)
        params = {
            "voice_path": audio_file,
            "content": audio_file
        }

        audio_player.play(params)

        time.sleep(1)
    
    # 此处填写全部音频的总时长合-音频个数*1秒，转换为秒数
    time.sleep(60)