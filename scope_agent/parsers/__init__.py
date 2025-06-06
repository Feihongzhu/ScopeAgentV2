"""
文件解析器模块 - 处理特殊格式的文件解析
"""

import json
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


# 基础解析器函数
def parse_dag_stages(file_path: str) -> str:
    """解析DAG stages日志文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析逻辑，实际可以更复杂
        lines = content.split('\n')
        parsed_info = []
        
        for line in lines:
            if 'Stage' in line and ('running' in line or 'completed' in line):
                parsed_info.append(line.strip())
        
        return f"DAG Stages 解析结果:\n" + "\n".join(parsed_info[:20])  # 限制行数
    except Exception as e:
        return f"解析DAG stages文件失败: {str(e)}"


def parse_performance_metrics(file_path: str) -> str:
    """解析性能指标JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = []
        summary.append("性能指标摘要:")
        
        if 'execution_time' in data:
            summary.append(f"- 执行时间: {data['execution_time']}")
        if 'cpu_usage' in data:
            summary.append(f"- CPU使用率: {data['cpu_usage']}")
        if 'memory_usage' in data:
            summary.append(f"- 内存使用: {data['memory_usage']}")
        if 'shuffle_size' in data:
            summary.append(f"- Shuffle数据量: {data['shuffle_size']}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析性能指标文件失败: {str(e)}"


def parse_skew_report(file_path: str) -> str:
    """解析数据倾斜报告"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = []
        summary.append("数据倾斜分析报告:")
        
        if 'partitions' in data:
            partitions = data['partitions']
            summary.append(f"- 分区数: {len(partitions)}")
            
            # 找出最大和最小的分区
            if partitions:
                sizes = [p.get('size', 0) for p in partitions]
                max_size = max(sizes)
                min_size = min(sizes)
                avg_size = sum(sizes) / len(sizes)
                
                summary.append(f"- 最大分区大小: {max_size}")
                summary.append(f"- 最小分区大小: {min_size}")
                summary.append(f"- 平均分区大小: {avg_size:.2f}")
                summary.append(f"- 倾斜比例: {max_size/avg_size:.2f}x")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析数据倾斜报告失败: {str(e)}"


def parse_shuffle_stats(file_path: str) -> str:
    """解析Shuffle统计日志"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        shuffle_ops = []
        
        for line in lines:
            if 'shuffle' in line.lower() and ('bytes' in line or 'records' in line):
                shuffle_ops.append(line.strip())
        
        summary = ["Shuffle操作统计:"]
        summary.extend(shuffle_ops[:10])  # 显示前10个操作
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析Shuffle统计文件失败: {str(e)}"


# 注册默认解析器
register_parser("parse_dag_stages", parse_dag_stages)
register_parser("parse_performance_metrics", parse_performance_metrics)
register_parser("parse_skew_report", parse_skew_report)
register_parser("parse_shuffle_stats", parse_shuffle_stats)


__all__ = [
    "register_parser",
    "get_parser_function", 
    "list_available_parsers",
    "parse_dag_stages",
    "parse_performance_metrics",
    "parse_skew_report", 
    "parse_shuffle_stats"
] 