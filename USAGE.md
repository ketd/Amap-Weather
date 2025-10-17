# 高德地图天气查询预制件使用指南

## 简介

这是一个基于高德地图 API 的天气查询预制件，提供实时天气和天气预报查询功能。

## 功能特性

- ✅ 实时天气查询（实况天气）
- ✅ 天气预报查询（未来3-4天）
- ✅ 支持全国城市查询
- ✅ 完善的错误处理
- ✅ 结构化的数据返回

## 配置要求

### 1. 获取高德地图 API Key

1. 访问 [高德地图开放平台](https://console.amap.com/dev/key/app)
2. 注册并登录账号
3. 创建应用，选择 **Web 服务** 类型
4. 获取 API Key

### 2. 配置环境变量

将获取的 API Key 配置为环境变量：

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export AMAP_API_KEY="your_api_key_here"

# 使配置生效
source ~/.zshrc
```

## 函数说明

### `get_weather(city: str, extensions: str = "base") -> dict`

查询指定城市的天气信息。

#### 参数

- `city` (必需): 城市编码（adcode）
  - 例如：`"110101"` 代表北京市东城区
  - 城市编码可参考 [高德地图城市编码表](https://lbs.amap.com/api/webservice/download)

- `extensions` (可选): 气象类型
  - `"base"`: 返回实况天气（默认）
  - `"all"`: 返回天气预报（未来3-4天）

#### 返回值

成功时返回：
```python
{
    "success": True,
    "type": "live" | "forecast",  # 查询类型
    "data": {
        # 实况天气数据或预报数据
    }
}
```

失败时返回：
```python
{
    "success": False,
    "error": "错误信息",
    "error_code": "错误代码"
}
```

## 使用示例

### 示例 1: 查询实况天气

```python
from src.main import get_weather

# 查询北京东城区的实况天气
result = get_weather(city="110101")

if result["success"]:
    data = result["data"]
    print(f"城市: {data['province']} {data['city']}")
    print(f"天气: {data['weather']}")
    print(f"温度: {data['temperature']}℃")
    print(f"风向: {data['winddirection']}")
    print(f"风力: {data['windpower']}级")
    print(f"湿度: {data['humidity']}%")
    print(f"发布时间: {data['reporttime']}")
else:
    print(f"查询失败: {result['error']}")
```

输出示例：
```
城市: 北京 东城区
天气: 阴
温度: 13℃
风向: 东北
风力: ≤3级
湿度: 69%
发布时间: 2025-10-17 10:33:26
```

### 示例 2: 查询天气预报

```python
from src.main import get_weather

# 查询北京东城区的天气预报
result = get_weather(city="110101", extensions="all")

if result["success"]:
    data = result["data"]
    print(f"城市: {data['province']} {data['city']}")
    print(f"预报发布时间: {data['reporttime']}\n")
    
    for cast in data["casts"]:
        print(f"日期: {cast['date']} (周{cast['week']})")
        print(f"  白天: {cast['dayweather']}, {cast['daytemp']}℃, {cast['daywind']}风 {cast['daypower']}级")
        print(f"  夜间: {cast['nightweather']}, {cast['nighttemp']}℃, {cast['nightwind']}风 {cast['nightpower']}级")
        print()
else:
    print(f"查询失败: {result['error']}")
```

输出示例：
```
城市: 北京 东城区
预报发布时间: 2025-10-17 10:33:26

日期: 2025-10-17 (周5)
  白天: 多云, 16℃, 东北风 1-3级
  夜间: 晴, 4℃, 东北风 1-3级

日期: 2025-10-18 (周6)
  白天: 多云, 11℃, 东北风 1-3级
  夜间: 多云, 5℃, 东北风 1-3级

...
```

### 示例 3: 查询多个城市

```python
from src.main import get_weather

# 常用城市编码
cities = {
    "110101": "北京东城区",
    "310101": "上海黄浦区",
    "440106": "广州天河区",
    "440305": "深圳南山区"
}

for code, name in cities.items():
    result = get_weather(city=code)
    
    if result["success"]:
        data = result["data"]
        print(f"{name}: {data['weather']}, {data['temperature']}℃")
    else:
        print(f"{name}: 查询失败")
```

## 常用城市编码

| 城市 | 区域 | adcode |
|------|------|--------|
| 北京 | 东城区 | 110101 |
| 上海 | 黄浦区 | 310101 |
| 广州 | 天河区 | 440106 |
| 深圳 | 南山区 | 440305 |
| 杭州 | 西湖区 | 330106 |
| 成都 | 武侯区 | 510107 |

更多城市编码请访问：[高德地图城市编码表](https://lbs.amap.com/api/webservice/download)

## 错误处理

### 常见错误代码

| 错误代码 | 说明 | 解决方法 |
|---------|------|---------|
| `MISSING_API_KEY` | 未配置 API Key | 设置 `AMAP_API_KEY` 环境变量 |
| `INVALID_CITY` | 无效的城市编码 | 检查城市编码是否正确 |
| `INVALID_EXTENSIONS` | 无效的气象类型 | 使用 "base" 或 "all" |
| `API_ERROR` | 高德 API 返回错误 | 检查 API Key 是否有效，配额是否充足 |
| `NO_DATA` | 未获取到数据 | 城市编码可能不存在或 API 暂无数据 |
| `TIMEOUT` | 请求超时 | 检查网络连接，稍后重试 |
| `NETWORK_ERROR` | 网络请求失败 | 检查网络连接 |

### 错误处理示例

```python
from src.main import get_weather

result = get_weather(city="110101")

if not result["success"]:
    error_code = result["error_code"]
    
    if error_code == "MISSING_API_KEY":
        print("请配置 AMAP_API_KEY 环境变量")
    elif error_code == "INVALID_CITY":
        print("城市编码无效，请检查")
    elif error_code == "API_ERROR":
        print(f"API 错误: {result.get('api_infocode', 'unknown')}")
    else:
        print(f"未知错误: {result['error']}")
```

## 测试

运行测试以验证功能：

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_main.py::TestGetWeather::test_live_weather_with_api_key -v
```

## 开发和调试

### 本地测试

```bash
# 1. 设置 API Key
export AMAP_API_KEY="your_api_key"

# 2. 快速测试实况天气
uv run python -c "from src.main import get_weather; import json; print(json.dumps(get_weather('110101'), ensure_ascii=False, indent=2))"

# 3. 快速测试天气预报
uv run python -c "from src.main import get_weather; import json; print(json.dumps(get_weather('110101', 'all'), ensure_ascii=False, indent=2))"
```

### 代码检查

```bash
# 代码风格检查
uv run --with flake8 flake8 src/ --max-line-length=120

# Manifest 验证
uv run python scripts/validate_manifest.py

# 完整验证
uv run python scripts/quick_start.py
```

## API 限制

### 高德地图免费配额

- 个人认证用户：每日 30 万次
- 企业认证用户：每日 100 万次

### 更新频率

- **实况天气**: 每小时更新多次
- **预报天气**: 每天更新 3 次（约 8:00、11:00、18:00）

具体更新时间以 API 返回的 `reporttime` 字段为准。

## 相关链接

- [高德地图开放平台](https://lbs.amap.com/)
- [天气查询 API 文档](https://lbs.amap.com/api/webservice/guide/api/weatherinfo)
- [城市编码表下载](https://lbs.amap.com/api/webservice/download)
- [错误码对照表](https://lbs.amap.com/api/webservice/guide/tools/info)

## 许可证

MIT License

