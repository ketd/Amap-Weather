"""
预制件模块

这个模块暴露所有可被 AI 调用的函数。
"""

from .main import (
    greet,
    echo,
    add_numbers,
)

__all__ = [
    "greet",
    "echo",
    "add_numbers",
]

__version__ = "0.1.0"
