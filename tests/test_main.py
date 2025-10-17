"""
main.py 的单元测试

测试所有预制件函数的功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import greet, echo, add_numbers, fetch_weather


class TestGreet:
    """测试 greet 函数"""

    def test_default_greeting(self):
        """测试默认问候"""
        result = greet()
        assert result["success"] is True
        assert result["message"] == "Hello, World!"
        assert result["name"] == "World"

    def test_custom_name(self):
        """测试自定义名字"""
        result = greet(name="Alice")
        assert result["success"] is True
        assert result["message"] == "Hello, Alice!"
        assert result["name"] == "Alice"

    def test_empty_name(self):
        """测试空名字"""
        result = greet(name="")
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "INVALID_NAME"


class TestEcho:
    """测试 echo 函数"""

    def test_basic_echo(self):
        """测试基本回显"""
        result = echo(text="Hello")
        assert result["success"] is True
        assert result["original"] == "Hello"
        assert result["echo"] == "Hello"
        assert result["length"] == 5

    def test_long_text(self):
        """测试长文本"""
        text = "This is a longer text message for testing"
        result = echo(text=text)
        assert result["success"] is True
        assert result["original"] == text
        assert result["length"] == len(text)

    def test_empty_text(self):
        """测试空文本"""
        result = echo(text="")
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "EMPTY_TEXT"


class TestAddNumbers:
    """测试 add_numbers 函数"""

    def test_positive_integers(self):
        """测试正整数"""
        result = add_numbers(a=5, b=3)
        assert result["success"] is True
        assert result["a"] == 5
        assert result["b"] == 3
        assert result["sum"] == 8

    def test_negative_numbers(self):
        """测试负数"""
        result = add_numbers(a=-5, b=3)
        assert result["success"] is True
        assert result["sum"] == -2

    def test_float_numbers(self):
        """测试浮点数"""
        result = add_numbers(a=1.5, b=2.3)
        assert result["success"] is True
        assert abs(result["sum"] - 3.8) < 0.0001

    def test_zero(self):
        """测试零"""
        result = add_numbers(a=0, b=0)
        assert result["success"] is True
        assert result["sum"] == 0


class TestFetchWeather:
    """测试 fetch_weather 函数（演示 secrets 的使用）"""

    def test_with_api_key(self, monkeypatch):
        """测试配置了 API Key 的情况"""
        # 模拟环境变量
        monkeypatch.setenv('WEATHER_API_KEY', 'test_api_key_12345')

        result = fetch_weather(city="北京")
        assert result["success"] is True
        assert result["city"] == "北京"
        assert "temperature" in result
        assert "condition" in result
        assert result["note"] == "这是演示数据，未调用真实 API"

    def test_without_api_key(self, monkeypatch):
        """测试未配置 API Key 的情况"""
        # 确保环境变量不存在
        monkeypatch.delenv('WEATHER_API_KEY', raising=False)

        result = fetch_weather(city="上海")
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "MISSING_API_KEY"

    def test_invalid_city(self, monkeypatch):
        """测试无效的城市名称"""
        monkeypatch.setenv('WEATHER_API_KEY', 'test_api_key_12345')

        result = fetch_weather(city="")
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "INVALID_CITY"

    def test_multiple_cities(self, monkeypatch):
        """测试不同城市"""
        monkeypatch.setenv('WEATHER_API_KEY', 'test_api_key_12345')

        cities = ["北京", "上海", "广州", "深圳"]
        for city in cities:
            result = fetch_weather(city=city)
            assert result["success"] is True
            assert result["city"] == city
