"""
文件处理工具函数
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


def ensure_directory(path: str) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def safe_read_file(file_path: str, encoding: str = 'utf-8', 
                  fallback_encodings: list = None) -> Optional[str]:
    """
    安全地读取文件，支持多种编码格式
    
    Args:
        file_path: 文件路径
        encoding: 主要编码格式
        fallback_encodings: 备用编码格式列表
        
    Returns:
        文件内容，读取失败返回None
    """
    if fallback_encodings is None:
        fallback_encodings = ['gbk', 'latin-1', 'cp1252']
    
    if not os.path.exists(file_path):
        return None
    
    # 尝试主要编码
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        pass
    
    # 尝试备用编码
    for fallback_encoding in fallback_encodings:
        try:
            with open(file_path, 'r', encoding=fallback_encoding) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    
    # 如果所有编码都失败，尝试二进制读取
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            return content.decode('utf-8', errors='ignore')
    except Exception:
        return None


def safe_write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    安全地写入文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 编码格式
        
    Returns:
        是否写入成功
    """
    try:
        # 确保目录存在
        ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件大小（字节），文件不存在返回-1
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return -1


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件扩展名（不包含点号）
    """
    return Path(file_path).suffix.lower().lstrip('.')


def is_text_file(file_path: str) -> bool:
    """
    判断是否为文本文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否为文本文件
    """
    text_extensions = {
        'txt', 'log', 'md', 'py', 'js', 'html', 'css', 'xml', 'json',
        'csv', 'tsv', 'sql', 'sh', 'bat', 'properties', 'cfg', 'ini'
    }
    
    extension = get_file_extension(file_path)
    if extension in text_extensions:
        return True
    
    # 对于没有扩展名的文件，尝试读取前几个字节判断
    if not extension:
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                # 检查是否包含NULL字节（二进制文件的特征）
                return b'\0' not in chunk
        except Exception:
            return False
    
    return False


def backup_file(file_path: str, backup_suffix: str = '.bak') -> Optional[str]:
    """
    备份文件
    
    Args:
        file_path: 要备份的文件路径
        backup_suffix: 备份文件后缀
        
    Returns:
        备份文件路径，失败返回None
    """
    if not os.path.exists(file_path):
        return None
    
    backup_path = file_path + backup_suffix
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception:
        return None


def load_json_file(file_path: str) -> Optional[Dict[Any, Any]]:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的字典，失败返回None
    """
    content = safe_read_file(file_path)
    if content is None:
        return None
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def save_json_file(file_path: str, data: Dict[Any, Any], 
                  indent: int = 2, ensure_ascii: bool = False) -> bool:
    """
    保存数据到JSON文件
    
    Args:
        file_path: JSON文件路径
        data: 要保存的数据
        indent: 缩进空格数
        ensure_ascii: 是否确保ASCII编码
        
    Returns:
        是否保存成功
    """
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        return safe_write_file(file_path, content)
    except Exception:
        return False


def find_files_by_pattern(directory: str, pattern: str = "*", 
                         recursive: bool = True) -> list:
    """
    根据模式查找文件
    
    Args:
        directory: 搜索目录
        pattern: 文件名模式（支持通配符）
        recursive: 是否递归搜索
        
    Returns:
        匹配的文件路径列表
    """
    from glob import glob
    
    if not os.path.exists(directory):
        return []
    
    search_pattern = os.path.join(directory, "**", pattern) if recursive else os.path.join(directory, pattern)
    
    try:
        return glob(search_pattern, recursive=recursive)
    except Exception:
        return []


def clean_filename(filename: str) -> str:
    """
    清理文件名，去除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    import re
    
    # 去除Windows文件名中的非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(illegal_chars, '_', filename)
    
    # 去除首尾空格和点号
    cleaned = cleaned.strip(' .')
    
    # 确保不为空
    if not cleaned:
        cleaned = "unnamed_file"
    
    return cleaned 