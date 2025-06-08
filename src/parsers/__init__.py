"""
文件解析器模块 - 处理特殊格式的文件解析
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Callable, Optional
from datetime import datetime
import re


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


# === Cosmos SCOPE Job 文件解析器 ===

def parse_job_info_xml(file_path: str) -> str:
    """解析 JobInfo.xml 文件"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        summary = ["作业基本信息:"]
        
        job_id = root.find('JobId')
        if job_id is not None:
            summary.append(f"- 作业ID: {job_id.text}")
        
        status = root.find('Status')
        if status is not None:
            summary.append(f"- 状态: {status.text}")
        
        submit_time = root.find('SubmitTime')
        if submit_time is not None:
            summary.append(f"- 提交时间: {submit_time.text}")
        
        # 资源需求
        resource_req = root.find('ResourceRequirements')
        if resource_req is not None:
            summary.append("- 资源需求:")
            for child in resource_req:
                summary.append(f"  {child.tag}: {child.text}")
        
        # 输入表信息
        input_tables = root.find('InputTables')
        if input_tables is not None:
            summary.append("- 输入表:")
            for table in input_tables.findall('Table'):
                name = table.find('Name')
                size = table.find('Size')
                row_count = table.find('RowCount')
                if name is not None:
                    table_info = f"  {name.text}"
                    if size is not None:
                        table_info += f" (大小: {size.text}"
                    if row_count is not None:
                        table_info += f", 行数: {row_count.text})"
                    summary.append(table_info)
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析JobInfo.xml失败: {str(e)}"


def parse_job_statistics_xml(file_path: str) -> str:
    """解析 JobStatistics.xml 文件"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        summary = ["作业统计信息:"]
        
        job_id = root.find('JobId')
        if job_id is not None:
            summary.append(f"- 作业ID: {job_id.text}")
        
        # 整体统计
        overall_stats = root.find('OverallStatistics')
        if overall_stats is not None:
            summary.append("- 整体统计:")
            for child in overall_stats:
                summary.append(f"  {child.tag}: {child.text}")
        
        # Stage统计
        stage_stats = root.find('StageStatistics')
        if stage_stats is not None:
            summary.append("- Stage统计:")
            for stage in stage_stats.findall('Stage'):
                stage_id = stage.find('StageId')
                stage_name = stage.find('StageName')
                duration = stage.find('Duration')
                
                stage_info = f"  Stage {stage_id.text if stage_id is not None else 'Unknown'}"
                if stage_name is not None:
                    stage_info += f" ({stage_name.text})"
                if duration is not None:
                    stage_info += f" - 耗时: {duration.text}"
                
                summary.append(stage_info)
                
                # 检查倾斜任务
                skewed_tasks = stage.find('SkewedTasks')
                if skewed_tasks is not None:
                    tasks = skewed_tasks.findall('Task')
                    if tasks:
                        summary.append(f"    检测到 {len(tasks)} 个倾斜任务")
                        for task in tasks[:3]:  # 只显示前3个
                            task_id = task.find('TaskId')
                            skew_reason = task.find('SkewReason')
                            if task_id is not None and skew_reason is not None:
                                summary.append(f"    - {task_id.text}: {skew_reason.text}")
        
        # 性能指标
        performance_metrics = root.find('PerformanceMetrics')
        if performance_metrics is not None:
            summary.append("- 性能指标:")
            for metric in performance_metrics.findall('Metric'):
                name = metric.find('Name')
                value = metric.find('Value')
                status = metric.find('Status')
                
                if name is not None and value is not None:
                    metric_info = f"  {name.text}: {value.text}"
                    if status is not None and status.text == "Exceeded":
                        metric_info += " (超出阈值)"
                    summary.append(metric_info)
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析JobStatistics.xml失败: {str(e)}"


def parse_algebra_xml(file_path: str) -> str:
    """解析 Algebra.xml 执行计划文件"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        summary = ["查询执行计划:"]
        
        # 简单提取算子信息
        operators = []
        
        def extract_operators(element):
            if element.tag and 'Operator' in element.tag or 'Node' in element.tag:
                operators.append(element.tag)
            for child in element:
                extract_operators(child)
        
        extract_operators(root)
        
        if operators:
            summary.append(f"- 检测到 {len(operators)} 个算子")
            operator_counts = {}
            for op in operators:
                operator_counts[op] = operator_counts.get(op, 0) + 1
            
            for op, count in operator_counts.items():
                summary.append(f"  {op}: {count}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析Algebra.xml失败: {str(e)}"


def parse_data_flow_graph_json(file_path: str) -> str:
    """解析 __DataMapDfg__.json 数据流图文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = ["数据流图信息:"]
        
        if 'vertices' in data:
            vertices = data['vertices']
            summary.append(f"- 顶点数: {len(vertices)}")
            
            # 统计顶点类型
            vertex_types = {}
            for vertex in vertices:
                vertex_type = vertex.get('type', 'Unknown')
                vertex_types[vertex_type] = vertex_types.get(vertex_type, 0) + 1
            
            summary.append("- 顶点类型分布:")
            for v_type, count in vertex_types.items():
                summary.append(f"  {v_type}: {count}")
        
        if 'edges' in data:
            edges = data['edges']
            summary.append(f"- 边数: {len(edges)}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析数据流图文件失败: {str(e)}"


def parse_warnings_xml(file_path: str) -> str:
    """解析 __Warnings__.xml 警告文件"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        summary = ["编译/运行警告:"]
        
        warnings = []
        
        def extract_warnings(element):
            if element.text and element.text.strip():
                if any(keyword in element.text.lower() for keyword in ['warning', 'warn', '警告']):
                    warnings.append(element.text.strip())
            for child in element:
                extract_warnings(child)
        
        extract_warnings(root)
        
        if warnings:
            summary.append(f"- 共发现 {len(warnings)} 个警告")
            for warning in warnings[:10]:  # 显示前10个警告
                summary.append(f"  - {warning}")
        else:
            summary.append("- 无警告信息")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析警告文件失败: {str(e)}"


def parse_compile_output_txt(file_path: str) -> str:
    """解析编译输出文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        summary = ["编译输出摘要:"]
        
        error_count = 0
        warning_count = 0
        
        important_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if 'error' in line_lower:
                error_count += 1
                important_lines.append(f"错误: {line.strip()}")
            elif 'warning' in line_lower:
                warning_count += 1
                important_lines.append(f"警告: {line.strip()}")
            elif any(keyword in line_lower for keyword in ['success', 'completed', 'failed']):
                important_lines.append(line.strip())
        
        summary.append(f"- 错误数: {error_count}")
        summary.append(f"- 警告数: {warning_count}")
        
        if important_lines:
            summary.append("- 重要信息:")
            for line in important_lines[:10]:  # 显示前10条
                summary.append(f"  {line}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析编译输出文件失败: {str(e)}"


def parse_scope_script(file_path: str) -> str:
    """解析 SCOPE 脚本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = ["SCOPE脚本分析:"]
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        # 统计关键操作
        select_count = len([line for line in lines if re.search(r'\bSELECT\b', line, re.IGNORECASE)])
        join_count = len([line for line in lines if re.search(r'\bJOIN\b', line, re.IGNORECASE)])
        group_by_count = len([line for line in lines if re.search(r'\bGROUP BY\b', line, re.IGNORECASE)])
        partition_by_count = len([line for line in lines if re.search(r'\bPARTITION BY\b', line, re.IGNORECASE)])
        
        summary.append(f"- 脚本行数: {total_lines}")
        summary.append(f"- SELECT语句: {select_count}")
        summary.append(f"- JOIN操作: {join_count}")
        summary.append(f"- GROUP BY操作: {group_by_count}")
        summary.append(f"- PARTITION BY操作: {partition_by_count}")
        
        # 潜在问题检测
        issues = []
        if join_count > 0 and partition_by_count == 0:
            issues.append("发现JOIN操作但无PARTITION BY，可能导致数据倾斜")
        if group_by_count > 2:
            issues.append("多次聚合操作，可能导致性能问题")
        
        if issues:
            summary.append("- 潜在问题:")
            for issue in issues:
                summary.append(f"  - {issue}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析SCOPE脚本失败: {str(e)}"


def parse_error_file(file_path: str) -> str:
    """解析错误文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return "错误文件为空 - 作业执行成功"
        
        summary = ["错误信息分析:"]
        
        lines = content.split('\n')
        error_lines = [line.strip() for line in lines if line.strip()]
        
        summary.append(f"- 错误行数: {len(error_lines)}")
        
        # 错误类型分析
        error_types = []
        for line in error_lines:
            line_lower = line.lower()
            if 'outofmemory' in line_lower or 'memory' in line_lower:
                error_types.append("内存错误")
            elif 'timeout' in line_lower:
                error_types.append("超时错误")
            elif 'skew' in line_lower or 'imbalance' in line_lower:
                error_types.append("数据倾斜错误")
            elif 'shuffle' in line_lower:
                error_types.append("Shuffle错误")
        
        if error_types:
            summary.append("- 错误类型:")
            for error_type in set(error_types):
                summary.append(f"  - {error_type}")
        
        # 显示前几行错误信息
        summary.append("- 错误详情:")
        for line in error_lines[:5]:
            summary.append(f"  {line}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析错误文件失败: {str(e)}"


# 注册默认解析器
register_parser("parse_dag_stages", parse_dag_stages)
register_parser("parse_performance_metrics", parse_performance_metrics)
register_parser("parse_skew_report", parse_skew_report)
register_parser("parse_shuffle_stats", parse_shuffle_stats)

# 注册新的SCOPE Job解析器
register_parser("parse_job_info_xml", parse_job_info_xml)
register_parser("parse_job_statistics_xml", parse_job_statistics_xml)
register_parser("parse_algebra_xml", parse_algebra_xml)
register_parser("parse_data_flow_graph_json", parse_data_flow_graph_json)
register_parser("parse_warnings_xml", parse_warnings_xml)
register_parser("parse_compile_output_txt", parse_compile_output_txt)
register_parser("parse_scope_script", parse_scope_script)
register_parser("parse_error_file", parse_error_file)


__all__ = [
    "register_parser",
    "get_parser_function", 
    "list_available_parsers",
    "parse_dag_stages",
    "parse_performance_metrics",
    "parse_skew_report", 
    "parse_shuffle_stats",
    # 新增的SCOPE Job解析器
    "parse_job_info_xml",
    "parse_job_statistics_xml", 
    "parse_algebra_xml",
    "parse_data_flow_graph_json",
    "parse_warnings_xml",
    "parse_compile_output_txt",
    "parse_scope_script",
    "parse_error_file"
] 