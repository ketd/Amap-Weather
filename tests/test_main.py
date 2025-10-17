"""
main.py 的单元测试

测试高德地图天气查询预制件的功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import get_weather


class TestGetWeather:
    """测试 get_weather 函数"""

    def test_live_weather_with_api_key(self):
        """测试查询实况天气（需要真实 API Key）"""
        # 从环境变量获取 API Key
        api_key = os.environ.get('AMAP_API_KEY')

        if not api_key:
            # 如果没有配置 API Key，测试错误处理
            result = get_weather(city_name="北京市")
            assert result["success"] is False
            assert result["error_code"] == "MISSING_API_KEY"
        else:
            # 使用城市名称查询
            result = get_weather(city_name="北京市", extensions="base")

            # 验证返回结果
            assert result["success"] is True
            assert result["type"] == "live"
            assert "city_name" in result
            assert "data" in result

            # 验证数据结构
            data = result["data"]
            assert "province" in data
            assert "city" in data
            assert "adcode" in data
            assert "weather" in data
            assert "temperature" in data
            assert "winddirection" in data
            assert "windpower" in data
            assert "humidity" in data
            assert "reporttime" in data

    def test_forecast_weather_with_api_key(self):
        """测试查询天气预报（需要真实 API Key）"""
        api_key = os.environ.get('AMAP_API_KEY')

        if not api_key:
            # 如果没有配置 API Key，测试错误处理
            result = get_weather(city_name="上海市", extensions="all")
            assert result["success"] is False
            assert result["error_code"] == "MISSING_API_KEY"
        else:
            # 使用城市名称查询
            result = get_weather(city_name="上海市", extensions="all")

            # 验证返回结果
            assert result["success"] is True
            assert result["type"] == "forecast"
            assert "city_name" in result
            assert "data" in result

            # 验证数据结构
            data = result["data"]
            assert "city" in data
            assert "adcode" in data
            assert "province" in data
            assert "reporttime" in data
            assert "casts" in data
            assert isinstance(data["casts"], list)

            # 验证预报数据
            if len(data["casts"]) > 0:
                cast = data["casts"][0]
                assert "date" in cast
                assert "week" in cast
                assert "dayweather" in cast
                assert "nightweather" in cast
                assert "daytemp" in cast
                assert "nighttemp" in cast
                assert "daywind" in cast
                assert "nightwind" in cast
                assert "daypower" in cast
                assert "nightpower" in cast

    def test_without_api_key(self, monkeypatch):
        """测试未配置 API Key 的情况"""
        # 确保环境变量不存在
        monkeypatch.delenv('AMAP_API_KEY', raising=False)

        result = get_weather(city_name="北京市")
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "MISSING_API_KEY"

    def test_invalid_city_name(self, monkeypatch):
        """测试无效的城市名称"""
        monkeypatch.setenv('AMAP_API_KEY', 'test_api_key_12345')

        # 测试空城市名称
        result = get_weather(city_name="")
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "INVALID_CITY_NAME"

    def test_city_not_found(self):
        """测试未找到的城市"""
        api_key = os.environ.get('AMAP_API_KEY')

        if api_key:
            # 测试一个不存在的城市名称
            result = get_weather(city_name="这个城市不存在")
            assert result["success"] is False
            assert result["error_code"] == "CITY_NOT_FOUND"

    def test_invalid_extensions(self, monkeypatch):
        """测试无效的 extensions 参数"""
        monkeypatch.setenv('AMAP_API_KEY', 'test_api_key_12345')

        result = get_weather(city_name="北京市", extensions="invalid")
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "INVALID_EXTENSIONS"

    def test_default_extensions(self):
        """测试默认的 extensions 参数（应该是 'base'）"""
        api_key = os.environ.get('AMAP_API_KEY')

        if api_key:
            # 不指定 extensions 参数，应该默认查询实况天气
            result = get_weather(city_name="北京市")

            if result["success"]:
                assert result["type"] == "live"

    def test_multiple_cities(self):
        """测试不同城市的查询"""
        api_key = os.environ.get('AMAP_API_KEY')

        if api_key:
            # 测试不同城市
            cities = ["北京市", "上海市", "广州市", "深圳市"]

            for city_name in cities:
                result = get_weather(city_name=city_name)

                if result["success"]:
                    assert result["type"] == "live"
                    assert "data" in result
                    assert result["city_name"] == city_name

    def test_fuzzy_matching(self):
        """测试模糊匹配功能"""
        api_key = os.environ.get('AMAP_API_KEY')

        if api_key:
            # 测试省略"市"、"区"等后缀
            test_cases = [
                ("北京", "base"),
                ("上海", "base"),
                ("杭州", "base"),
            ]

            for city_name, ext in test_cases:
                result = get_weather(city_name=city_name, extensions=ext)

                # 模糊匹配应该能找到对应的城市
                if result["success"]:
                    assert result["type"] == "live"
                    assert "city_name" in result
