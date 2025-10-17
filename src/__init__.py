"""
高德地图天气查询预制件

这个模块提供基于高德地图 API 的天气查询功能。
"""

from .main import get_weather

__all__ = [
    "get_weather",
]

__version__ = "1.0.0"
