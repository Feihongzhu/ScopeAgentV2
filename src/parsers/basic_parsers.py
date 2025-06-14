"""
基础解析器函数
"""

import json


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