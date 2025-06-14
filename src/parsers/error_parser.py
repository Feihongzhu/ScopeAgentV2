"""
错误文件解析器 - 处理Cosmos作业错误文件
"""

import json


def parse_error_file(file_path: str) -> str:
    """解析错误文件 - 支持JSON和文本格式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return "错误文件为空 - 作业执行成功"
        
        # 尝试解析为JSON格式
        try:
            error_data = json.loads(content)
            return _parse_json_error(error_data)
        except (json.JSONDecodeError, ValueError):
            # 如果不是JSON格式，使用原来的文本解析方式
            return _parse_text_error(content)
            
    except Exception as e:
        return f"解析错误文件失败: {str(e)}"


def _parse_json_error(error_data: dict) -> str:
    """解析JSON格式的错误信息"""
    summary = ["Cosmos作业错误分析:"]
    
    # 基本错误信息
    diagnostic_code = error_data.get("diagnosticCode", "未知")
    component = error_data.get("component", "未知")
    error_id = error_data.get("errorId", "未知")
    message = error_data.get("message", "无消息")
    
    summary.append(f"- 诊断代码: {diagnostic_code}")
    summary.append(f"- 组件: {component}")
    summary.append(f"- 错误ID: {error_id}")
    summary.append(f"- 错误消息: {message}")
    
    # 错误分类
    error_category = _categorize_cosmos_error(error_id, message)
    if error_category:
        summary.append(f"- 错误类别: {error_category}")
    
    # 解决方案
    resolution = error_data.get("resolution", "")
    if resolution:
        summary.append("- 解决方案:")
        # 分割解决方案文本
        resolution_steps = resolution.split("(")
        for i, step in enumerate(resolution_steps):
            if step.strip():
                if i == 0:
                    summary.append(f"  {step.strip()}")
                else:
                    summary.append(f"  ({step.strip()}")
    
    # 内部诊断信息
    internal_diagnostics = error_data.get("internalDiagnostics", "")
    if internal_diagnostics:
        summary.append("- 内部诊断信息:")
        diag_lines = internal_diagnostics.split('\n')
        for line in diag_lines[:10]:  # 限制显示行数
            if line.strip():
                summary.append(f"  {line.strip()}")
    
    # 特定错误类型的额外分析
    if "VERTEX_TIMEOUT" in error_id:
        summary.append("- 顶点超时分析:")
        summary.append("  这是一个典型的长时间运行任务超时错误")
        summary.append("  可能原因: 数据倾斜、低效查询、资源不足")
        
        # 从内部诊断中提取失败的顶点信息
        if internal_diagnostics:
            if "Failed vertex:" in internal_diagnostics:
                failed_vertex = _extract_failed_vertex(internal_diagnostics)
                if failed_vertex:
                    summary.append(f"  失败顶点: {failed_vertex}")
    
    return "\n".join(summary)


def _parse_text_error(content: str) -> str:
    """解析文本格式的错误信息（原有逻辑）"""
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


def _categorize_cosmos_error(error_id: str, message: str) -> str:
    """根据错误ID和消息对Cosmos错误进行分类"""
    error_id_lower = error_id.lower()
    message_lower = message.lower()
    
    if "timeout" in error_id_lower or "timeout" in message_lower:
        return "任务超时"
    elif "memory" in error_id_lower or "outofmemory" in message_lower:
        return "内存不足"
    elif "vertex" in error_id_lower:
        return "顶点执行错误"
    elif "container" in error_id_lower:
        return "容器错误"
    elif "shuffle" in error_id_lower or "shuffle" in message_lower:
        return "数据Shuffle错误"
    elif "skew" in message_lower or "imbalance" in message_lower:
        return "数据倾斜"
    else:
        return "运行时错误"


def _extract_failed_vertex(internal_diagnostics: str) -> str:
    """从内部诊断信息中提取失败的顶点名称"""
    lines = internal_diagnostics.split('\n')
    for line in lines:
        if "Failed vertex:" in line:
            # 提取顶点名称
            vertex_info = line.split("Failed vertex:")[-1].strip()
            return vertex_info
    return "" 