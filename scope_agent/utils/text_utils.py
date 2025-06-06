"""
文本处理工具函数
"""

import re
from typing import List, Set


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    从文本中提取关键词
    
    Args:
        text: 输入文本
        min_length: 最小关键词长度
        
    Returns:
        关键词列表
    """
    if not text:
        return []
    
    # 清理文本
    cleaned_text = clean_text(text)
    
    # 分词
    words = re.findall(r'\b\w+\b', cleaned_text.lower())
    
    # 过滤常见停用词
    stop_words = {
        'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 'was', 'were',
        'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'for', 'with', 'by',
        '的', '是', '在', '和', '有', '了', '我', '你', '他', '她', '我们', '你们', '他们',
        '这', '那', '也', '都', '很', '就', '但', '不', '没', '要', '会', '可以'
    }
    
    # 过滤关键词
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # 去重并保持顺序
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords


def clean_text(text: str) -> str:
    """
    清理文本，去除特殊字符和多余空格
    
    Args:
        text: 输入文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去除特殊字符，保留中文、英文、数字和基本标点
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'-]', ' ', text)
    
    # 处理多个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空格
    text = text.strip()
    
    return text


def highlight_keywords(text: str, keywords: List[str], 
                      highlight_format: str = "**{}**") -> str:
    """
    在文本中高亮关键词
    
    Args:
        text: 原始文本
        keywords: 要高亮的关键词列表
        highlight_format: 高亮格式，{}为关键词占位符
        
    Returns:
        高亮后的文本
    """
    if not text or not keywords:
        return text
    
    highlighted_text = text
    
    for keyword in keywords:
        # 使用正则表达式进行不区分大小写的替换
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted_text = pattern.sub(
            highlight_format.format(keyword), 
            highlighted_text
        )
    
    return highlighted_text


def extract_think_steps(text: str) -> dict:
    """
    从文本中提取THINK步骤
    
    Args:
        text: 包含THINK步骤的文本
        
    Returns:
        步骤字典 {step_name: content}
    """
    think_steps = {}
    
    # THINK步骤模式
    think_pattern = r'\[THINK[_\s]*(\d+)\](.*?)(?=\[THINK[_\s]*\d+\]|$)'
    
    matches = re.findall(think_pattern, text, re.DOTALL | re.IGNORECASE)
    
    for step_num, content in matches:
        step_name = f"THINK_{step_num}"
        think_steps[step_name] = content.strip()
    
    return think_steps


def format_analysis_result(result_dict: dict) -> str:
    """
    格式化分析结果为可读文本
    
    Args:
        result_dict: 分析结果字典
        
    Returns:
        格式化的文本
    """
    lines = []
    
    if 'problem_type' in result_dict:
        lines.append(f"问题类型: {result_dict['problem_type']}")
    
    if 'confidence' in result_dict:
        lines.append(f"置信度: {result_dict['confidence']:.2f}")
    
    if 'processing_time' in result_dict:
        lines.append(f"处理时间: {result_dict['processing_time']:.2f}秒")
    
    if 'files_analyzed' in result_dict:
        files = result_dict['files_analyzed']
        if files:
            lines.append(f"分析文件: {', '.join(files)}")
    
    if 'solution' in result_dict:
        lines.append(f"\n解决方案:\n{result_dict['solution']}")
    
    return "\n".join(lines)


def split_long_text(text: str, max_length: int = 2000, 
                   overlap: int = 200) -> List[str]:
    """
    将长文本分割为较短的片段
    
    Args:
        text: 输入文本
        max_length: 每个片段的最大长度
        overlap: 片段之间的重叠长度
        
    Returns:
        文本片段列表
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_length
        
        # 如果不是最后一个片段，尝试在句号处断开
        if end < len(text):
            # 向前查找句号
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            break_point = max(last_period, last_newline)
            
            if break_point > start + max_length // 2:
                end = break_point + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 计算下一个开始位置，包含重叠
        start = max(start + max_length - overlap, end)
    
    return chunks 