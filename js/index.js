const server_port = 5600;
let config = null;

// 获取输入框中的值并转为整数
function getNumber(input, defaultValue = 0) {
    let value = input.value;
    let number = parseInt(value);

    if (isNaN(number) || value === '') {
        number = defaultValue; 
    }

    return number;
}
 
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

            var data_json = JSON.parse(data);

            config = data_json;

            document.getElementById('input_rate').value = config.rate;
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
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
        });
}

// 保存配置
function save_config() {
    config.rate = document.getElementById('input_rate').value;
    config.device_index = document.getElementById('select_device').value;

    // 构建请求选项对象
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json", // 指定请求体为JSON格式
        },
        body: JSON.stringify(config), // 将JSON数据序列化为字符串并作为请求体
    };

    console.log(requestOptions)

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
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
        });
}

// 运行
function run() {
    config.rate = document.getElementById('input_rate').value;
    config.device_index = document.getElementById('select_device').value;

    // 构建请求选项对象
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json", // 指定请求体为JSON格式
        },
        body: JSON.stringify(config), // 将JSON数据序列化为字符串并作为请求体
    };

    console.log(requestOptions)

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
        })
        .catch(function (error) {
            // 处理错误
            console.error(error);
        });
}

// 停止运行
function stop() {

}

get_config();
get_deivce();
