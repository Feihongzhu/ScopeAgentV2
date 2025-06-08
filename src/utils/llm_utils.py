"""
LLM相关工具函数
"""

import re
from typing import Optional, Dict, Any


def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """
    估算文本的token数量
    
    Args:
        text: 输入文本
        model: 模型名称
        
    Returns:
        估算的token数量
    """
    if not text:
        return 0
    
    # 简单的token估算规则
    # 英文：大约4个字符 = 1个token
    # 中文：大约1.5个字符 = 1个token
    
    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 统计其他字符
    other_chars = len(text) - chinese_chars
    
    # 估算token数
    estimated_tokens = int(chinese_chars / 1.5 + other_chars / 4)
    
    return max(estimated_tokens, 1)


def truncate_text(text: str, max_tokens: int = 2000, model: str = "gpt-4", 
                 preserve_end: bool = False) -> str:
    """
    根据token限制截断文本
    
    Args:
        text: 输入文本
        max_tokens: 最大token数
        model: 模型名称
        preserve_end: 是否保留末尾而不是开头
        
    Returns:
        截断后的文本
    """
    if not text:
        return text
    
    current_tokens = estimate_tokens(text, model)
    
    if current_tokens <= max_tokens:
        return text
    
    # 计算需要保留的比例
    keep_ratio = max_tokens / current_tokens
    keep_length = int(len(text) * keep_ratio)
    
    if preserve_end:
        # 保留末尾
        truncated = "..." + text[-keep_length:]
    else:
        # 保留开头
        truncated = text[:keep_length] + "..."
    
    return truncated


def split_text_by_tokens(text: str, max_tokens_per_chunk: int = 2000, 
                        overlap_tokens: int = 200, model: str = "gpt-4") -> list:
    """
    按token数分割文本
    
    Args:
        text: 输入文本
        max_tokens_per_chunk: 每个块的最大token数
        overlap_tokens: 重叠的token数
        model: 模型名称
        
    Returns:
        文本块列表
    """
    if not text:
        return []
    
    total_tokens = estimate_tokens(text, model)
    
    if total_tokens <= max_tokens_per_chunk:
        return [text]
    
    chunks = []
    start_pos = 0
    
    while start_pos < len(text):
        # 计算这个块应该包含的字符数
        chars_per_token = len(text) / total_tokens
        chunk_chars = int(max_tokens_per_chunk * chars_per_token)
        
        end_pos = min(start_pos + chunk_chars, len(text))
        
        # 尝试在句子边界处断开
        if end_pos < len(text):
            # 向前查找句号、换行符等
            for sep in ['\n\n', '\n', '。', '.', '！', '!', '？', '?']:
                sep_pos = text.rfind(sep, start_pos, end_pos)
                if sep_pos > start_pos + chunk_chars // 2:
                    end_pos = sep_pos + len(sep)
                    break
        
        chunk = text[start_pos:end_pos].strip()
        if chunk:
            chunks.append(chunk)
        
        # 计算下一个开始位置，包含重叠
        overlap_chars = int(overlap_tokens * chars_per_token)
        start_pos = max(end_pos - overlap_chars, end_pos)
    
    return chunks


def format_prompt_with_context(template: str, context: Dict[str, Any], 
                              max_total_tokens: int = 3000) -> str:
    """
    格式化Prompt并控制总长度
    
    Args:
        template: Prompt模板
        context: 上下文变量
        max_total_tokens: 最大总token数
        
    Returns:
        格式化后的Prompt
    """
    # 首先进行变量替换
    formatted_prompt = template.format(**context)
    
    # 检查总长度
    total_tokens = estimate_tokens(formatted_prompt)
    
    if total_tokens <= max_total_tokens:
        return formatted_prompt
    
    # 如果超长，需要压缩上下文
    # 找出可能比较长的字段进行截断
    long_fields = ['context_info', 'files_content', 'retrieved_experience', 'current_analysis']
    
    for field in long_fields:
        if field in context and total_tokens > max_total_tokens:
            # 计算该字段应该占用的最大token数
            field_max_tokens = max_total_tokens // 4  # 假设平均分配
            
            # 截断该字段
            truncated_value = truncate_text(
                str(context[field]), 
                max_tokens=field_max_tokens
            )
            
            # 更新上下文
            updated_context = context.copy()
            updated_context[field] = truncated_value
            
            # 重新格式化
            formatted_prompt = template.format(**updated_context)
            total_tokens = estimate_tokens(formatted_prompt)
            
            if total_tokens <= max_total_tokens:
                break
    
    return formatted_prompt


def extract_structured_response(response: str, sections: list = None) -> Dict[str, str]:
    """
    从LLM响应中提取结构化内容
    
    Args:
        response: LLM的响应文本
        sections: 要提取的章节列表，如 ['问题分析', '解决方案']
        
    Returns:
        结构化的内容字典
    """
    if sections is None:
        sections = ['问题分析', '解决方案', '建议', '总结']
    
    result = {}
    
    for section in sections:
        # 尝试多种可能的章节标记格式
        patterns = [
            rf'{section}[:：]\s*(.*?)(?=\n(?:[一二三四五六七八九十]、|[0-9]+[、.]|\w+[:：])|$)',
            rf'#+\s*{section}\s*(.*?)(?=\n#+|$)',
            rf'\*\*{section}\*\*[:：]?\s*(.*?)(?=\n\*\*|\n[一二三四五六七八九十]、|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content:
                    result[section] = content
                break
    
    return result


def validate_llm_response(response: str, required_sections: list = None, 
                         min_length: int = 50) -> Dict[str, Any]:
    """
    验证LLM响应的质量
    
    Args:
        response: LLM响应
        required_sections: 必需的章节列表
        min_length: 最小长度要求
        
    Returns:
        验证结果字典
    """
    validation_result = {
        "is_valid": True,
        "issues": [],
        "score": 1.0
    }
    
    # 检查长度
    if len(response) < min_length:
        validation_result["is_valid"] = False
        validation_result["issues"].append(f"响应过短，少于{min_length}字符")
        validation_result["score"] -= 0.3
    
    # 检查必需章节
    if required_sections:
        extracted = extract_structured_response(response, required_sections)
        missing_sections = [sec for sec in required_sections if sec not in extracted]
        
        if missing_sections:
            validation_result["issues"].append(f"缺少章节: {', '.join(missing_sections)}")
            validation_result["score"] -= 0.2 * len(missing_sections)
    
    # 检查是否包含明显的错误标记
    error_indicators = ["抱歉", "无法", "不知道", "error", "failed"]
    
    for indicator in error_indicators:
        if indicator in response.lower():
            validation_result["issues"].append(f"包含错误指示词: {indicator}")
            validation_result["score"] -= 0.1
    
    # 更新整体有效性
    if validation_result["score"] < 0.5:
        validation_result["is_valid"] = False
    
    validation_result["score"] = max(0.0, validation_result["score"])
    
    return validation_result 