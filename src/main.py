"""
高德地图天气查询预制件

提供基于高德地图 API 的实时天气和天气预报查询功能。

📖 完整开发指南请查看：PREFAB_GUIDE.md
"""

import os
import csv
import requests
from pathlib import Path


def _load_city_codes():
    """
    加载城市编码数据（内部函数）

    Returns:
        dict: 城市名称到 adcode 的映射字典
    """
    city_codes = {}
    csv_path = Path(__file__).parent / "city_codes.csv"

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                city_name = row['中文名']
                adcode = row['adcode']
                if city_name and adcode:
                    city_codes[city_name] = adcode
        return city_codes
    except Exception:
        return {}


def _query_weather_api(adcode: str, extensions: str, api_key: str) -> dict:
    """
    调用高德地图天气 API（内部函数）

    Args:
        adcode: 城市编码
        extensions: 气象类型 "base" 或 "all"
        api_key: 高德地图 API Key

    Returns:
        API 响应结果
    """
    api_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": api_key,
        "city": adcode,
        "extensions": extensions,
        "output": "JSON"
    }

    response = requests.get(api_url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_weather(city_name: str, extensions: str = "base") -> dict:
    """
    通过城市名称查询天气信息

    支持直接使用中文城市名称查询实时天气或天气预报。

    Args:
        city_name: 城市名称，例如 "北京市"、"东城区"、"上海市"、"杭州" 等
                  支持模糊匹配，可以省略"市"、"区"、"县"等后缀
        extensions: 气象类型，可选值：
                   - "base": 返回实况天气（默认）
                   - "all": 返回预报天气（未来3-4天）

    Returns:
        包含天气信息的字典，格式为：
        {
            "success": bool,           # 操作是否成功
            "type": str,               # 查询类型 "live" 或 "forecast"
            "city_name": str,          # 城市名称
            "data": dict,              # 天气数据（成功时）
            "error": str,              # 错误信息（失败时）
            "error_code": str          # 错误代码（失败时）
        }

    实况天气数据格式 (extensions="base"):
        {
            "province": "省份名",
            "city": "城市名",
            "adcode": "区域编码",
            "weather": "天气现象（汉字描述）",
            "temperature": "实时气温，单位：摄氏度",
            "winddirection": "风向描述",
            "windpower": "风力级别，单位：级",
            "humidity": "空气湿度",
            "reporttime": "数据发布的时间"
        }

    预报天气数据格式 (extensions="all"):
        {
            "city": "城市名称",
            "adcode": "城市编码",
            "province": "省份名称",
            "reporttime": "预报发布时间",
            "casts": [
                {
                    "date": "日期",
                    "week": "星期几",
                    "dayweather": "白天天气现象",
                    "nightweather": "晚上天气现象",
                    "daytemp": "白天温度",
                    "nighttemp": "晚上温度",
                    "daywind": "白天风向",
                    "nightwind": "晚上风向",
                    "daypower": "白天风力",
                    "nightpower": "晚上风力"
                },
                ...
            ]
        }

    Examples:
        >>> # 查询北京市实况天气
        >>> get_weather(city_name="北京市")
        {
            'success': True,
            'type': 'live',
            'city_name': '北京市',
            'data': {
                'province': '北京',
                'city': '北京市',
                'weather': '晴',
                'temperature': '27',
                ...
            }
        }

        >>> # 查询上海天气预报（可以省略"市"）
        >>> get_weather(city_name="上海", extensions="all")
        {
            'success': True,
            'type': 'forecast',
            'city_name': '上海',
            'data': {
                'city': '上海市',
                'casts': [...]
            }
        }
    """
    try:
        # 从环境变量中获取高德地图 API Key
        api_key = os.environ.get('AMAP_API_KEY')

        # 验证 API Key 是否已配置
        if not api_key:
            return {
                "success": False,
                "error": "未配置 AMAP_API_KEY，请在平台上配置高德地图 API 密钥",
                "error_code": "MISSING_API_KEY"
            }

        # 验证 city_name 参数
        if not city_name or not isinstance(city_name, str):
            return {
                "success": False,
                "error": "city_name 参数必须是非空字符串",
                "error_code": "INVALID_CITY_NAME"
            }

        # 验证 extensions 参数
        if extensions not in ["base", "all"]:
            return {
                "success": False,
                "error": "extensions 参数必须是 'base' 或 'all'",
                "error_code": "INVALID_EXTENSIONS"
            }

        # 加载城市编码
        city_codes = _load_city_codes()

        if not city_codes:
            return {
                "success": False,
                "error": "无法加载城市编码数据",
                "error_code": "CITY_DATA_ERROR"
            }

        # 查找城市编码 - 精确匹配
        adcode = city_codes.get(city_name)
        matched_city_name = city_name

        # 如果精确匹配失败，尝试模糊匹配
        if not adcode:
            city_name_cleaned = city_name.rstrip('市区县')
            for name, code in city_codes.items():
                if name.rstrip('市区县') == city_name_cleaned:
                    adcode = code
                    matched_city_name = name
                    break

        # 如果仍未找到，返回错误和建议
        if not adcode:
            similar_cities = [name for name in city_codes.keys() if city_name[:2] in name]
            suggestion = f"，您是否想查询：{', '.join(similar_cities[:5])}" if similar_cities else ""

            return {
                "success": False,
                "error": f"未找到城市 '{city_name}'{suggestion}",
                "error_code": "CITY_NOT_FOUND"
            }

        # 调用高德地图天气 API
        result = _query_weather_api(adcode, extensions, api_key)

        # 检查 API 返回状态
        if result.get("status") != "1":
            error_msg = result.get("info", "未知错误")
            return {
                "success": False,
                "error": f"高德地图 API 返回错误: {error_msg}",
                "error_code": "API_ERROR",
                "api_infocode": result.get("infocode")
            }

        # 根据查询类型返回相应的数据
        if extensions == "base":
            # 实况天气
            lives = result.get("lives", [])
            if not lives:
                return {
                    "success": False,
                    "error": "未获取到天气数据",
                    "error_code": "NO_DATA"
                }

            return {
                "success": True,
                "type": "live",
                "city_name": matched_city_name,
                "data": lives[0]
            }
        else:
            # 预报天气
            forecasts = result.get("forecasts", [])
            if not forecasts:
                return {
                    "success": False,
                    "error": "未获取到天气预报数据",
                    "error_code": "NO_DATA"
                }

            return {
                "success": True,
                "type": "forecast",
                "city_name": matched_city_name,
                "data": forecasts[0]
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "请求超时，请稍后重试",
            "error_code": "TIMEOUT"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"网络请求失败: {str(e)}",
            "error_code": "NETWORK_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"未知错误: {str(e)}",
            "error_code": "UNEXPECTED_ERROR"
        }
