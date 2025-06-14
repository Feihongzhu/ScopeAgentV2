"""
SCOPE脚本解析器 - 解析SCOPE脚本文件
"""

import re


def parse_scope_script(file_path: str) -> str:
    """解析 SCOPE 脚本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = ["SCOPE脚本分析:"]
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        # 基本统计
        summary.append(f"- 脚本行数: {total_lines}")
        
        # 分析模块和引用
        module_count, reference_count, dll_references = _analyze_modules_and_references(content)
        summary.append(f"- MODULE引用: {module_count}")
        summary.append(f"- REFERENCE引用: {reference_count}")
        if dll_references:
            summary.append(f"- DLL文件: {', '.join(dll_references[:3])}{'...' if len(dll_references) > 3 else ''}")
        
        # 分析变量声明
        declare_count = _count_pattern(content, r'#DECLARE\s+\w+')
        summary.append(f"- 变量声明: {declare_count}")
        
        # 分析VIEW使用
        view_count = _count_pattern(content, r'VIEW\s+"[^"]+\.view"')
        summary.append(f"- VIEW使用: {view_count}")
        
        # 分析SQL操作
        sql_stats = _analyze_sql_operations(content)
        summary.append(f"- SELECT语句: {sql_stats['select']}")
        summary.append(f"- JOIN操作: {sql_stats['total_joins']}")
        summary.append(f"- GROUP BY操作: {sql_stats['group_by']}")
        summary.append(f"- PARTITION BY操作: {sql_stats['partition_by']}")
        
        # JOIN类型详细分析
        join_details = _analyze_join_types(content)
        if join_details:
            summary.append("- JOIN类型分布:")
            for join_type, count in join_details.items():
                summary.append(f"  {join_type}: {count}")
        
        # 分析聚合函数
        agg_functions = _analyze_aggregation_functions(content)
        if agg_functions:
            summary.append("- 聚合函数:")
            for func, count in agg_functions.items():
                summary.append(f"  {func}: {count}")
        
        # 分析UDF和自定义处理器
        udf_stats = _analyze_udf_and_processors(content)
        if udf_stats['cs_blocks'] > 0:
            summary.append(f"- C#代码块: {udf_stats['cs_blocks']}")
        if udf_stats['processors']:
            summary.append(f"- 自定义处理器: {', '.join(udf_stats['processors'])}")
        
        # 分析SET配置
        set_configs = _analyze_set_configurations(content)
        if set_configs:
            summary.append("- 性能配置:")
            for config in set_configs:
                summary.append(f"  {config}")
        
        # 分析复杂操作
        complex_ops = _analyze_complex_operations(content)
        if complex_ops:
            summary.append("- 复杂操作:")
            for op in complex_ops:
                summary.append(f"  - {op}")
        
        # 潜在性能问题检测
        issues = _detect_performance_issues(content, sql_stats, join_details, udf_stats)
        if issues:
            summary.append("- 潜在性能问题:")
            for issue in issues:
                summary.append(f"  ⚠️ {issue}")
        
        # 性能建议
        recommendations = _generate_recommendations(sql_stats, join_details, udf_stats, set_configs)
        if recommendations:
            summary.append("- 性能优化建议:")
            for rec in recommendations:
                summary.append(f"  💡 {rec}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析SCOPE脚本失败: {str(e)}"


def _analyze_modules_and_references(content: str) -> tuple:
    """分析模块和引用"""
    module_count = _count_pattern(content, r'MODULE\s+"[^"]+"')
    reference_count = _count_pattern(content, r'\[PIN\]REFERENCE\s+"[^"]+"')
    
    # 提取DLL引用
    dll_pattern = r'\[PIN\]REFERENCE\s+"[^"]*\.dll"'
    dll_matches = re.findall(dll_pattern, content, re.IGNORECASE)
    dll_references = [match.split('/')[-1].replace('"', '') for match in dll_matches]
    
    return module_count, reference_count, dll_references


def _analyze_sql_operations(content: str) -> dict:
    """分析SQL操作"""
    return {
        'select': _count_pattern(content, r'\bSELECT\b'),
        'total_joins': _count_pattern(content, r'\bJOIN\b'),
        'group_by': _count_pattern(content, r'\bGROUP\s+BY\b'),
        'partition_by': _count_pattern(content, r'\bPARTITION\s+BY\b')
    }


def _analyze_join_types(content: str) -> dict:
    """分析JOIN类型"""
    join_types = {
        'INNER JOIN': _count_pattern(content, r'\bINNER\s+JOIN\b'),
        'LEFT JOIN': _count_pattern(content, r'\bLEFT\s+JOIN\b'),
        'RIGHT JOIN': _count_pattern(content, r'\bRIGHT\s+JOIN\b'),
        'FULL JOIN': _count_pattern(content, r'\bFULL\s+JOIN\b'),
        'CROSS JOIN': _count_pattern(content, r'\bCROSS\s+JOIN\b'),
        'BROADCASTRIGHT JOIN': _count_pattern(content, r'\bBROADCASTRIGHT\s+JOIN\b'),
        'ANTISEMIJOIN': _count_pattern(content, r'\bANTISEMIJOIN\b'),
        'SEMIJOIN': _count_pattern(content, r'\bSEMIJOIN\b'),
        '普通JOIN': _count_pattern(content, r'(?<!INNER\s)(?<!LEFT\s)(?<!RIGHT\s)(?<!FULL\s)(?<!CROSS\s)(?<!BROADCASTRIGHT\s)(?<!ANTI)(?<!SEMI)\bJOIN\b')
    }
    
    return {k: v for k, v in join_types.items() if v > 0}


def _analyze_aggregation_functions(content: str) -> dict:
    """分析聚合函数"""
    agg_functions = {
        'COUNT': _count_pattern(content, r'\bCOUNT\s*\('),
        'COUNTIF': _count_pattern(content, r'\bCOUNTIF\s*\('),
        'SUM': _count_pattern(content, r'\bSUM\s*\('),
        'AVG': _count_pattern(content, r'\bAVG\s*\('),
        'MAX': _count_pattern(content, r'\bMAX\s*\('),
        'MIN': _count_pattern(content, r'\bMIN\s*\('),
        'LIST': _count_pattern(content, r'\bLIST\s*\('),
        'DISTINCT': _count_pattern(content, r'\bDISTINCT\b')
    }
    
    return {k: v for k, v in agg_functions.items() if v > 0}


def _analyze_udf_and_processors(content: str) -> dict:
    """分析UDF和自定义处理器"""
    cs_blocks = len(re.findall(r'#CS.*?#ENDCS', content, re.DOTALL))
    
    # 查找自定义处理器
    processor_pattern = r'USING\s+(\w+);'
    processors = re.findall(processor_pattern, content)
    processors = [p for p in processors if p not in ['Outputters', 'Privacy']]  # 排除系统处理器
    
    return {
        'cs_blocks': cs_blocks,
        'processors': list(set(processors))  # 去重
    }


def _analyze_set_configurations(content: str) -> list:
    """分析SET配置"""
    set_patterns = [
        (r'SET\s+@@Buckets\s*=\s*(\d+)', 'Buckets设置'),
        (r'SET\s+@@IgnoreMaxPartitionsThreshold\s*=\s*(\w+)', 'IgnoreMaxPartitionsThreshold'),
        (r'SET\s+@@FeaturePreviews\s*=\s*"([^"]+)"', 'FeaturePreviews'),
        (r'SET\s+@@(\w+)', '其他SET配置')
    ]
    
    configs = []
    for pattern, description in set_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            if 'Buckets' in description:
                configs.append(f"{description}: {matches[0]}")
            elif matches[0]:
                configs.append(f"{description}: {matches[0]}")
            else:
                configs.append(description)
    
    return configs


def _analyze_complex_operations(content: str) -> list:
    """分析复杂操作"""
    complex_ops = []
    
    # CROSS APPLY操作
    if _count_pattern(content, r'\bCROSS\s+APPLY\b') > 0:
        complex_ops.append("CROSS APPLY操作")
    
    # PROCESS操作
    process_count = _count_pattern(content, r'\bPROCESS\b.*?\bUSING\b')
    if process_count > 0:
        complex_ops.append(f"PROCESS操作: {process_count}")
    
    # 嵌套查询
    nested_query_count = content.count('(') - content.count(')')
    if abs(nested_query_count) > 10:  # 大量嵌套
        complex_ops.append("复杂嵌套查询")
    
    # UNION操作
    union_count = _count_pattern(content, r'\bUNION\s+(ALL\s+)?')
    if union_count > 0:
        complex_ops.append(f"UNION操作: {union_count}")
    
    return complex_ops


def _detect_performance_issues(content: str, sql_stats: dict, join_details: dict, udf_stats: dict) -> list:
    """检测潜在性能问题"""
    issues = []
    
    # JOIN相关问题
    if sql_stats['total_joins'] > 5:
        issues.append(f"过多JOIN操作({sql_stats['total_joins']}个)，可能导致性能下降")
    
    if 'CROSS JOIN' in join_details:
        issues.append("检测到CROSS JOIN，可能产生笛卡尔积")
    
    if sql_stats['total_joins'] > 0 and sql_stats['partition_by'] == 0:
        issues.append("有JOIN操作但无PARTITION BY，可能导致数据倾斜")
    
    # 聚合相关问题
    if sql_stats['group_by'] > 3:
        issues.append(f"多次GROUP BY操作({sql_stats['group_by']}次)，可能影响性能")
    
    # UDF相关问题
    if udf_stats['cs_blocks'] > 0:
        issues.append(f"包含{udf_stats['cs_blocks']}个C#代码块，UDF可能影响执行效率")
    
    if len(udf_stats['processors']) > 2:
        issues.append("使用多个自定义处理器，可能影响并行度")
    
    # 复杂查询问题
    if _count_pattern(content, r'\bDISTINCT\b') > 3:
        issues.append("多次使用DISTINCT，可能需要大量内存")
    
    # 数据倾斜风险
    if 'string.Join' in content:
        issues.append("检测到字符串连接操作，注意字符串长度限制")
    
    return issues


def _generate_recommendations(sql_stats: dict, join_details: dict, udf_stats: dict, set_configs: list) -> list:
    """生成性能优化建议"""
    recommendations = []
    
    # JOIN优化建议
    if sql_stats['total_joins'] > 0 and sql_stats['partition_by'] == 0:
        recommendations.append("建议添加PARTITION BY来优化JOIN性能")
    
    if 'BROADCASTRIGHT JOIN' not in join_details and sql_stats['total_joins'] > 2:
        recommendations.append("考虑使用BROADCASTRIGHT JOIN优化小表连接")
    
    # 聚合优化建议
    if sql_stats['group_by'] > 1:
        recommendations.append("考虑合并GROUP BY操作以减少中间结果")
    
    # UDF优化建议
    if udf_stats['cs_blocks'] > 0:
        recommendations.append("审查C#代码效率，考虑使用内置函数替代")
    
    # 配置优化建议
    if not any('Buckets' in config for config in set_configs):
        recommendations.append("考虑设置@@Buckets参数优化并行度")
    
    # 内存优化建议
    if _count_pattern(' '.join(set_configs), r'LIST\(') > 2:
        recommendations.append("注意LIST函数的内存使用，避免过大集合")
    
    return recommendations


def _count_pattern(content: str, pattern: str) -> int:
    """统计正则表达式匹配次数"""
    return len(re.findall(pattern, content, re.IGNORECASE)) 