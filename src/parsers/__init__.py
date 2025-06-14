"""
文件解析器模块 - 处理特殊格式的文件解析
"""

# 导入注册表管理
from .registry import register_parser, get_parser_function, list_available_parsers

# 导入基础解析器
from .basic_parsers import (
    parse_dag_stages,
    parse_performance_metrics,
    parse_skew_report,
    parse_shuffle_stats
)

# 导入Cosmos SCOPE Job解析器
from .job_info_parser import parse_job_info_xml
from .job_statistics_parser import parse_job_statistics_xml
from .algebra_parser import parse_algebra_xml
from .data_flow_graph_parser import parse_data_flow_graph_json
from .warnings_parser import parse_warnings_xml
from .compile_output_parser import parse_compile_output_txt
from .scope_script_parser import parse_scope_script
from .error_parser import parse_error_file
from .runtime_statistics_parser import parse_scope_runtime_statistics

# 注册所有解析器
def _register_all_parsers():
    """注册所有解析器函数"""
    # 注册基础解析器
    register_parser("parse_dag_stages", parse_dag_stages)
    register_parser("parse_performance_metrics", parse_performance_metrics)
    register_parser("parse_skew_report", parse_skew_report)
    register_parser("parse_shuffle_stats", parse_shuffle_stats)
    
    # 注册Cosmos SCOPE Job解析器
    register_parser("parse_job_info_xml", parse_job_info_xml)
    register_parser("parse_job_statistics_xml", parse_job_statistics_xml)
    register_parser("parse_algebra_xml", parse_algebra_xml)
    register_parser("parse_data_flow_graph_json", parse_data_flow_graph_json)
    register_parser("parse_warnings_xml", parse_warnings_xml)
    register_parser("parse_compile_output_txt", parse_compile_output_txt)
    register_parser("parse_scope_script", parse_scope_script)
    register_parser("parse_error_file", parse_error_file)
    register_parser("parse_scope_runtime_statistics", parse_scope_runtime_statistics)

# 初始化时注册所有解析器
_register_all_parsers()

# 导出的函数和类
__all__ = [
    # 注册表管理
    "register_parser",
    "get_parser_function", 
    "list_available_parsers",
    
    # 基础解析器
    "parse_dag_stages",
    "parse_performance_metrics",
    "parse_skew_report", 
    "parse_shuffle_stats",
    
    # Cosmos SCOPE Job解析器
    "parse_job_info_xml",
    "parse_job_statistics_xml", 
    "parse_algebra_xml",
    "parse_data_flow_graph_json",
    "parse_warnings_xml",
    "parse_compile_output_txt",
    "parse_scope_script",
    "parse_error_file",
    "parse_scope_runtime_statistics"
]

 