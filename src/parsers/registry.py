"""
解析器注册表管理
"""

from typing import Dict, Callable, Optional

# 解析器注册表
_PARSER_REGISTRY: Dict[str, Callable] = {}


def register_parser(name: str, parser_func: Callable):
    """
    注册新的解析器
    
    Args:
        name: 解析器名称
        parser_func: 解析器函数
    """
    _PARSER_REGISTRY[name] = parser_func


def get_parser_function(parser_name: str) -> Optional[Callable]:
    """
    获取解析器函数
    
    Args:
        parser_name: 解析器名称
        
    Returns:
        解析器函数，如果不存在则返回None
    """
    return _PARSER_REGISTRY.get(parser_name)


def list_available_parsers() -> list:
    """列出所有可用的解析器"""
    return list(_PARSER_REGISTRY.keys()) 