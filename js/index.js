const server_port = 5600;
let config = null;
let tipCounter = 0;

/***
 * 通用工具
***/
// 获取输入框中的值并转为整数
function getNumber(input, defaultValue = 0) {
    let value = input.value;
    let number = parseInt(value);

    if (isNaN(number) || value === '') {
        number = defaultValue; 
    }

    return number;
}

function showtip(type, text, timeout=3000) {
    const tip = document.createElement("div");
    tip.className = "tip";
    tip.style.bottom = `${tipCounter * 40}px`; // 垂直定位
    tip.innerText = text;
    if (type == "error") {
      tip.style.backgroundColor = "#ff0000";
    }

    document.body.appendChild(tip);

    setTimeout(function () {
      document.body.removeChild(tip);
      tipCounter--;
    }, timeout);

    tipCounter++;
}
 
/***
 * 后端相关
***/
// 获取当前配置
function get_config() {
    var url = `http://127.0.0.1:${server_port}/get_config`;

    fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.text();
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            showtip("info", "获取当前配置成功");

            var data_json = JSON.parse(data);

            config = data_json;

            document.getElementById('input_speed').value = config["speed"];
            document.getElementById('input_audio_interval').value = config["audio_interval"];
            document.getElementById('input_random_speed_enable').checked = config["random_speed"]["enable"];
            document.getElementById('input_random_speed_min').value = config["random_speed"]["min"];
            document.getElementById('input_random_speed_max').value = config["random_speed"]["max"];
            document.getElementById('input_random_audio_interval_enable').checked = config["random_audio_interval"]["enable"];
            document.getElementById('input_random_audio_interval_min').value = config["random_audio_interval"]["min"];
            document.getElementById('input_random_audio_interval_max').value = config["random_audio_interval"]["max"];

            document.getElementById('input_captions_printer_enable').checked = config["captions_printer"]["enable"];
            document.getElementById('input_captions_printer_api_ip_port').value = config["captions_printer"]["api_ip_port"];
            
            document.getElementById('input_ai_vtuber_callback_enable').checked = config["ai_vtuber"]["callback_enable"];
            document.getElementById('input_ai_vtuber_api_ip').value = config["ai_vtuber"]["api_ip"];
            document.getElementById('input_ai_vtuber_api_port').value = config["ai_vtuber"]["api_port"];

            // 获取声卡设备列表
            get_deivce();
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

// 获取声卡设备列表
function get_deivce() {
    var url = `http://127.0.0.1:${server_port}/get_all_audio_device_info`;

    fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.text();
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            // console.log(data);
            showtip("info", "获取获取声卡设备列表成功");

            var data_json = JSON.parse(data);

            // 将原始数据转换为您需要的格式
            const dynamicData = [];

            for (const key in data_json) {
                const device = data_json[key];
                dynamicData.push({
                    value: device.device_index.toString(),
                    label: device.device_info
                });
            }

            console.log(dynamicData);

            // 获取下拉选择框元素
            const select = document.getElementById("select_device");

            // 清空现有选项
            select.innerHTML = "";

            // 创建新选项并添加到下拉框
            dynamicData.forEach(item => {
                const option = document.createElement("option");
                option.value = item.value;
                option.text = item.label;

                // 设置默认选中项的 value
                if (item.value === config["device_index"].toString()) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

// 保存配置
function save_config() {
    try {
        config["device_index"] = parseInt(document.getElementById('select_device').value);
        config["speed"] = parseFloat(document.getElementById('input_speed').value);
        config["audio_interval"] = parseFloat(document.getElementById('input_audio_interval').value);
        config["random_speed"]["enable"] = document.getElementById("input_random_speed_enable").checked;
        config["random_speed"]["min"] = parseFloat(document.getElementById('input_random_speed_min').value);
        config["random_speed"]["max"] = parseFloat(document.getElementById('input_random_speed_max').value);
        config["random_audio_interval"]["enable"] = document.getElementById("input_random_audio_interval_enable").checked;
        config["random_audio_interval"]["min"] = parseFloat(document.getElementById('input_random_audio_interval_min').value);
        config["random_audio_interval"]["max"] = parseFloat(document.getElementById('input_random_audio_interval_max').value);

        config["captions_printer"]["enable"] = document.getElementById('input_captions_printer_enable').checked;
        config["captions_printer"]["api_ip_port"] = document.getElementById('input_captions_printer_api_ip_port').value;

        config["ai_vtuber"]["callback_enable"] = document.getElementById('input_ai_vtuber_callback_enable').checked;
        config["ai_vtuber"]["api_ip"] = document.getElementById('input_ai_vtuber_api_ip').value;
        config["ai_vtuber"]["api_port"] = parseInt(document.getElementById('input_ai_vtuber_api_port').value);

    } catch (error) {
        console.error(error);
        showtip("error", error.toString());
        return;
    }

    // 构建请求选项对象
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json", // 指定请求体为JSON格式
        },
        body: JSON.stringify(config), // 将JSON数据序列化为字符串并作为请求体
    };

    console.log(requestOptions);

    // 构建完整的URL，包含查询参数
    const url = `http://127.0.0.1:${server_port}/save_config`;

    // 发送GET请求
    fetch(url, requestOptions)
        .then(function (response) {
            if (response.ok) {
                return response.json(); // 解析响应数据为JSON
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            showtip("info", "保存配置成功");
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

// 运行
function run() {
    config["device_index"] = parseInt(document.getElementById('select_device').value);
    config["speed"] = parseFloat(document.getElementById('input_speed').value);
    config["audio_interval"] = parseFloat(document.getElementById('input_audio_interval').value);
    config["random_speed"]["enable"] = document.getElementById("input_random_speed_enable").checked;
    config["random_speed"]["min"] = parseFloat(document.getElementById('input_random_speed_min').value);
    config["random_speed"]["max"] = parseFloat(document.getElementById('input_random_speed_max').value);
    config["random_audio_interval"]["enable"] = document.getElementById("input_random_audio_interval_enable").checked;
    config["random_audio_interval"]["min"] = parseFloat(document.getElementById('input_random_audio_interval_min').value);
    config["random_audio_interval"]["max"] = parseFloat(document.getElementById('input_random_audio_interval_max').value);

    // 构建请求选项对象
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json", // 指定请求体为JSON格式
        },
        body: JSON.stringify(config), // 将JSON数据序列化为字符串并作为请求体
    };

    console.log(requestOptions);

    // 构建完整的URL，包含查询参数
    const url = `http://127.0.0.1:${server_port}/run`;

    // 发送GET请求
    fetch(url, requestOptions)
        .then(function (response) {
            if (response.ok) {
                return response.json(); // 解析响应数据为JSON
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            showtip("info", "重新运行...");
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

// 播放
function play() {
    let audio_json = document.getElementById('textarea_audio_json').value;

    // 构建请求选项对象
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json", // 指定请求体为JSON格式
        },
        body: audio_json,
    };

    console.log(requestOptions);

    // 构建完整的URL，包含查询参数
    const url = `http://127.0.0.1:${server_port}/play`;

    // 发送GET请求
    fetch(url, requestOptions)
        .then(function (response) {
            if (response.ok) {
                return response.json(); // 解析响应数据为JSON
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            showtip("info", "发送数据成功");
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

// 暂停/恢复播放
function pause_stream(status) {
    if (status == 1) 
        var url = `http://127.0.0.1:${server_port}/pause_stream`;
    else
        var url = `http://127.0.0.1:${server_port}/resume_stream`;


    fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.text();
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            if (status == 1) 
                showtip("info", "暂停播放成功");
            else
                showtip("info", "恢复播放成功");
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

// 跳过当前播放
function skip_current_stream() {
    var url = `http://127.0.0.1:${server_port}/skip_current_stream`;


    fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.text();
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            
            showtip("info", "跳过当前播放成功");
            get_list();
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

function clear_list() {
    var url = `http://127.0.0.1:${server_port}/clear`;


    fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.text();
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            showtip("info", "清空播放列表成功");
            get_list();
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

// 获取当前播放列表
function get_list() {
    var url = `http://127.0.0.1:${server_port}/get_list`;


    fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.text();
            }
            throw new Error("网络响应失败");
        })
        .then(function (data) {
            // 处理响应数据
            console.log(data);
            // 解析 JSON 字符串
            let jsonObj = JSON.parse(data);
            // 重新格式化 JSON 字符串，缩进使用 4 个空格
            let formattedData = JSON.stringify(jsonObj, null, 4);
            document.getElementById('textarea_audio_list').value = formattedData;
            // showtip("info", "获取播放列表列表成功");
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
            showtip("error", error.toString());
        });
}

get_config();
get_list();

// 每5000毫秒调用一次get_list
setInterval(get_list, 5000);
