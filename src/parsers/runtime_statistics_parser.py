"""
Scope运行时统计解析器 - 参考TypeScript版本优化
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class MemoryStats:
    """内存统计信息"""
    avg_execution_memory_peak_size: int = 0
    avg_io_memory_peak_size: int = 0
    avg_overall_memory_peak_size: int = 0
    avg_private_memory_peak_size: int = 0
    avg_working_set_peak_size: int = 0
    max_execution_memory_peak_size: int = 0
    max_overall_memory_peak_size: int = 0
    max_private_memory_peak_size: int = 0


@dataclass
class TimeStats:
    """时间统计信息"""
    inclusive_time: int = 0
    elapsed_time: int = 0
    execute_elapsed_time: int = 0
    execute_total_cpu_time: int = 0
    total_cpu_time: int = 0


@dataclass
class DataStats:
    """数据统计信息"""
    input_bytes: int = 0
    input_compressed_bytes: int = 0
    output_bytes: int = 0
    output_compressed_bytes: int = 0


@dataclass
class ExceptionStats:
    """异常统计信息"""
    cpp_exception_count: int = 0
    csharp_exception_count: int = 0
    other_exception_count: int = 0


@dataclass
class OperatorStats:
    """操作符统计信息"""
    id: str
    row_count: Optional[int] = None
    inclusive_time: Optional[int] = None
    exclusive_time: Optional[int] = None


@dataclass
class VertexStats:
    """顶点统计信息"""
    id: str
    type: str
    memory_stats: MemoryStats
    time_stats: TimeStats
    data_stats: DataStats
    exception_stats: ExceptionStats
    operators: List[OperatorStats]
    avg_total_page_fault_count: int = 0
    max_total_page_fault_count: int = 0


def parse_scope_runtime_statistics(file_path: str) -> str:
    """解析__ScopeRuntimeStatistics__文件 - 优化版本"""
    try:
        # 读取整个文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加调试信息
        print(f"文件大小: {len(content)} 字符")
        print(f"文件前500字符: {content[:500]}")
        
        # 提取所有顶点数据
        vertices = extract_vertices(content)
        
        print(f"找到 {len(vertices)} 个顶点")
        
        if not vertices:
            # 提供更详细的调试信息
            debug_info = _analyze_content_structure(content)
            return f"无法解析运行时统计信息 - 未找到有效的SV顶点\n\n调试信息:\n{debug_info}"
        
        # 分析重要顶点
        analysis = analyze_significant_vertices(vertices)
        
        # 格式化统计报告
        report = format_statistics_report(analysis)
        
        return report
        
    except Exception as e:
        return f"解析失败: {str(e)}"


def _analyze_content_structure(content: str) -> str:
    """分析内容结构以帮助调试"""
    info = []
    
    # 检查文件是否包含XML标记
    if '<' in content and '>' in content:
        info.append("✓ 文件包含XML标记")
    else:
        info.append("✗ 文件不包含XML标记")
    
    # 检查是否包含SV相关内容
    sv_count = content.count('SV')
    info.append(f"SV出现次数: {sv_count}")
    
    # 查找可能的SV模式
    sv_patterns = [
        r'<\w*SV\w*',
        r'id="[^"]*SV[^"]*"',
        r'SV_\w+',
        r'<SV\d+'
    ]
    
    for pattern in sv_patterns:
        matches = re.findall(pattern, content)
        if matches:
            info.append(f"找到模式 '{pattern}': {len(matches)} 个匹配")
            info.append(f"  示例: {matches[:3]}")
    
    # 检查文件开头
    lines = content.split('\n')[:10]
    info.append("文件前10行:")
    for i, line in enumerate(lines):
        info.append(f"  {i+1}: {line[:100]}")
    
    return '\n'.join(info)


def extract_vertices(xml_content: str) -> List[VertexStats]:
    """提取所有顶点信息 - 参考TypeScript版本"""
    vertices = []
    
    # 尝试多种解析方法
    # 方法1: 尝试标准XML解析
    try:
        root = ET.fromstring(xml_content)
        vertices = _extract_from_xml_tree(root)
        if vertices:
            return vertices
    except ET.ParseError as e:
        print(f"XML解析失败: {e}")
    
    # 方法2: 尝试包装为根元素
    try:
        wrapped_content = f"<root>{xml_content}</root>"
        root = ET.fromstring(wrapped_content)
        vertices = _extract_from_xml_tree(root)
        if vertices:
            return vertices
    except ET.ParseError:
        pass
    
    # 方法3: 使用正则表达式解析（备用方法）
    vertices = _extract_with_regex(xml_content)
    if vertices:
        return vertices
    
    # 方法4: 按行解析（最后的备用方法）
    return _extract_by_lines(xml_content)


def _extract_from_xml_tree(root: ET.Element) -> List[VertexStats]:
    """从XML树中提取顶点信息"""
    vertices = []
    
    # 查找所有以SV开头的元素（id属性）
    sv_nodes = []
    for elem in root.iter():
        elem_id = elem.get('id', '')
        if elem_id.startswith('SV'):
            sv_nodes.append(elem)
    
    # 如果没找到id以SV开头的，查找标签名以SV开头的
    if not sv_nodes:
        for elem in root.iter():
            if elem.tag.startswith('SV'):
                sv_nodes.append(elem)
    
    # 处理每个SV节点
    for node in sv_nodes:
        vertex = process_sv_node(node)
        if vertex:
            vertices.append(vertex)
    
    return vertices


def _extract_with_regex(content: str) -> List[VertexStats]:
    """使用正则表达式提取顶点信息（备用方法）"""
    vertices = []
    
    # 查找SV元素的模式
    sv_patterns = [
        r'<(\w*SV\w*)[^>]*id="([^"]*SV[^"]*)"[^>]*>(.*?)</\1>',
        r'<(\w*SV\w*)[^>]*>(.*?)</\1>',
        r'<(\w*SV\w*)[^>]*/>'
    ]
    
    for pattern in sv_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            for match in matches:
                vertex = _parse_sv_match(match, content)
                if vertex:
                    vertices.append(vertex)
            break
    
    return vertices


def _extract_by_lines(content: str) -> List[VertexStats]:
    """按行解析顶点信息（最后的备用方法）"""
    vertices = []
    lines = content.split('\n')
    
    current_vertex_data = {}
    in_sv_block = False
    
    for line in lines:
        line = line.strip()
        
        # 查找SV开始标记
        if 'SV' in line and ('id=' in line or line.startswith('<SV')):
            if current_vertex_data:
                vertex = _create_vertex_from_data(current_vertex_data)
                if vertex:
                    vertices.append(vertex)
            
            current_vertex_data = {'raw_line': line}
            in_sv_block = True
            
            # 提取ID
            id_match = re.search(r'id="([^"]*)"', line)
            if id_match:
                current_vertex_data['id'] = id_match.group(1)
            elif line.startswith('<SV'):
                tag_match = re.search(r'<(\w*SV\w*)', line)
                if tag_match:
                    current_vertex_data['id'] = tag_match.group(1)
        
        elif in_sv_block and line:
            # 收集属性信息
            _extract_attributes_from_line(line, current_vertex_data)
            
            # 检查是否是结束标记
            if line.startswith('</') or line.endswith('/>'):
                in_sv_block = False
    
    # 处理最后一个顶点
    if current_vertex_data:
        vertex = _create_vertex_from_data(current_vertex_data)
        if vertex:
            vertices.append(vertex)
    
    return vertices


def _parse_sv_match(match: tuple, content: str) -> Optional[VertexStats]:
    """解析正则表达式匹配的SV元素"""
    try:
        if len(match) >= 2:
            tag_name = match[0]
            sv_content = match[-1] if len(match) > 2 else ""
            
            # 尝试解析为XML片段
            try:
                if sv_content:
                    xml_fragment = f"<{tag_name}>{sv_content}</{tag_name}>"
                else:
                    xml_fragment = f"<{tag_name}/>"
                
                elem = ET.fromstring(xml_fragment)
                return process_sv_node(elem)
            except:
                # 如果XML解析失败，使用文本解析
                vertex_data = {'id': tag_name}
                _extract_attributes_from_line(sv_content, vertex_data)
                return _create_vertex_from_data(vertex_data)
    except:
        pass
    
    return None


def _extract_attributes_from_line(line: str, vertex_data: dict):
    """从行中提取属性信息"""
    # 提取各种属性
    attributes = [
        'avgExecutionMemoryPeakSize', 'avgIOMemoryPeakSize', 'avgOverallMemoryPeakSize',
        'maxExecutionMemoryPeakSize', 'maxOverallMemoryPeakSize', 'elapsedTime',
        'executeElapsedTime', 'inclusiveTime', 'totalCpuTime', 'totalBytes',
        'totalCompressedBytes', 'cppExceptionCount', 'csharpExceptionCount',
        'avgTotalPageFaultCount', 'maxTotalPageFaultCount'
    ]
    
    for attr in attributes:
        pattern = rf'{attr}="([^"]*)"'
        match = re.search(pattern, line)
        if match:
            try:
                vertex_data[attr] = int(match.group(1))
            except:
                vertex_data[attr] = match.group(1)


def _create_vertex_from_data(vertex_data: dict) -> Optional[VertexStats]:
    """从收集的数据创建VertexStats对象"""
    try:
        vertex_id = vertex_data.get('id', 'Unknown')
        vertex_type = vertex_id.split('_', 1)[1] if '_' in vertex_id else ''
        
        # 创建各种统计对象
        memory_stats = MemoryStats(
            avg_execution_memory_peak_size=vertex_data.get('avgExecutionMemoryPeakSize', 0),
            avg_io_memory_peak_size=vertex_data.get('avgIOMemoryPeakSize', 0),
            avg_overall_memory_peak_size=vertex_data.get('avgOverallMemoryPeakSize', 0),
            max_execution_memory_peak_size=vertex_data.get('maxExecutionMemoryPeakSize', 0),
            max_overall_memory_peak_size=vertex_data.get('maxOverallMemoryPeakSize', 0)
        )
        
        time_stats = TimeStats(
            elapsed_time=vertex_data.get('elapsedTime', 0),
            execute_elapsed_time=vertex_data.get('executeElapsedTime', 0),
            inclusive_time=vertex_data.get('inclusiveTime', 0),
            total_cpu_time=vertex_data.get('totalCpuTime', 0)
        )
        
        data_stats = DataStats(
            input_bytes=vertex_data.get('totalBytes', 0),
            input_compressed_bytes=vertex_data.get('totalCompressedBytes', 0)
        )
        
        exception_stats = ExceptionStats(
            cpp_exception_count=vertex_data.get('cppExceptionCount', 0),
            csharp_exception_count=vertex_data.get('csharpExceptionCount', 0)
        )
        
        return VertexStats(
            id=vertex_id,
            type=vertex_type,
            memory_stats=memory_stats,
            time_stats=time_stats,
            data_stats=data_stats,
            exception_stats=exception_stats,
            operators=[],
            avg_total_page_fault_count=vertex_data.get('avgTotalPageFaultCount', 0),
            max_total_page_fault_count=vertex_data.get('maxTotalPageFaultCount', 0)
        )
    except Exception as e:
        print(f"创建顶点对象失败: {e}")
        return None


def process_sv_node(node: ET.Element) -> Optional[VertexStats]:
    """处理单个SV节点 - 参考TypeScript版本"""
    try:
        # 提取顶点ID和类型
        node_id = node.tag or node.get('id', '')
        vertex_type = node_id.split('_', 1)[1] if '_' in node_id else ''
        
        # 创建内存统计
        memory_stats = MemoryStats(
            avg_execution_memory_peak_size=_get_int_attr(node, 'avgExecutionMemoryPeakSize'),
            avg_io_memory_peak_size=_get_int_attr(node, 'avgIOMemoryPeakSize'),
            avg_overall_memory_peak_size=_get_int_attr(node, 'avgOverallMemoryPeakSize'),
            avg_private_memory_peak_size=_get_int_attr(node, 'avgPrivateMemoryPeakSize'),
            avg_working_set_peak_size=_get_int_attr(node, 'avgWorkingSetPeakSize'),
            max_execution_memory_peak_size=_get_int_attr(node, 'maxExecutionMemoryPeakSize'),
            max_overall_memory_peak_size=_get_int_attr(node, 'maxOverallMemoryPeakSize'),
            max_private_memory_peak_size=_get_int_attr(node, 'maxPrivateMemoryPeakSize')
        )
        
        # 提取时间信息
        time_stats = TimeStats()
        time_element = node.find('./Time')
        if time_element is not None:
            time_stats.elapsed_time = _get_int_attr(time_element, 'elapsedTime')
            time_stats.execute_elapsed_time = _get_int_attr(time_element, 'executeElapsedTime')
            time_stats.inclusive_time = _get_int_attr(time_element, 'inclusiveTime')
            time_stats.execute_total_cpu_time = _get_int_attr(time_element, 'executeTotalCpuTime')
            time_stats.total_cpu_time = _get_int_attr(time_element, 'totalCpuTime')
        
        # 提取输入统计
        data_stats = DataStats()
        input_stats = node.find('./InputStatistics')
        if input_stats is not None:
            data_stats.input_bytes = _get_int_attr(input_stats, 'totalBytes')
            data_stats.input_compressed_bytes = _get_int_attr(input_stats, 'totalCompressedBytes')
        
        # 提取输出统计
        output_stats = node.find('./OutputStatistics')
        if output_stats is not None:
            data_stats.output_bytes = _get_int_attr(output_stats, 'totalBytes')
            data_stats.output_compressed_bytes = _get_int_attr(output_stats, 'totalCompressedBytes')
        
        # 提取异常统计
        exception_stats = ExceptionStats()
        exception_element = node.find('./ExceptionCounts')
        if exception_element is not None:
            exception_stats.cpp_exception_count = _get_int_attr(exception_element, 'cppExceptionCount')
            exception_stats.csharp_exception_count = _get_int_attr(exception_element, 'csharpExceptionCount')
            exception_stats.other_exception_count = _get_int_attr(exception_element, 'otherExceptionCount')
        
        # 提取页面错误信息
        avg_page_fault = 0
        max_page_fault = 0
        job_object = node.find('./VertexExecutionJobObject')
        if job_object is not None:
            avg_page_fault = _get_int_attr(job_object, 'avgTotalPageFaultCount')
            max_page_fault = _get_int_attr(job_object, 'maxTotalPageFaultCount')
        
        # 提取操作符信息
        operators = []
        operator_elements = node.findall('.//*[@opId]')
        for op_elem in operator_elements:
            op_id = op_elem.get('opId', '')
            if op_id:
                operator = OperatorStats(
                    id=op_id,
                    row_count=_get_int_attr(op_elem, 'rowCount') or None,
                    exclusive_time=_get_int_attr(op_elem, 'exclusiveTime') or None,
                    inclusive_time=_get_int_attr(op_elem, 'inclusiveTime') or None
                )
                operators.append(operator)
        
        # 创建顶点统计对象
        vertex = VertexStats(
            id=node_id,
            type=vertex_type,
            memory_stats=memory_stats,
            time_stats=time_stats,
            data_stats=data_stats,
            exception_stats=exception_stats,
            operators=operators,
            avg_total_page_fault_count=avg_page_fault,
            max_total_page_fault_count=max_page_fault
        )
        
        return vertex
        
    except Exception:
        return None


def _get_int_attr(element: ET.Element, attr_name: str) -> int:
    """安全地获取整数属性"""
    try:
        value = element.get(attr_name, '0')
        return int(value) if value else 0
    except (ValueError, TypeError):
        return 0


def analyze_significant_vertices(vertices: List[VertexStats]) -> Dict:
    """分析重要顶点 - 参考TypeScript版本"""
    # 按内存使用排序
    by_memory = sorted(vertices, 
                      key=lambda v: v.memory_stats.avg_overall_memory_peak_size, 
                      reverse=True)
    
    # 按执行时间排序
    by_time = sorted(vertices, 
                    key=lambda v: v.time_stats.elapsed_time, 
                    reverse=True)
    
    # 按数据处理量排序
    by_data = sorted(vertices, 
                    key=lambda v: v.data_stats.input_bytes + v.data_stats.output_bytes, 
                    reverse=True)
    
    return {
        'most_memory_intensive': by_memory[:5],
        'most_time_consuming': by_time[:5],
        'most_data_intensive': by_data[:5],
        'all_vertices': vertices
    }


def format_statistics_report(analysis: Dict) -> str:
    """格式化统计报告 - 参考TypeScript版本"""
    report = ["# Scope运行时统计摘要\n"]
    
    vertices = analysis['all_vertices']
    
    # 总体统计
    total_elapsed_time = sum(v.time_stats.elapsed_time for v in vertices)
    total_cpu_time = sum(v.time_stats.total_cpu_time for v in vertices)
    total_input_data = sum(v.data_stats.input_bytes for v in vertices)
    total_output_data = sum(v.data_stats.output_bytes for v in vertices)
    
    report.append("## 总体作业统计")
    report.append(f"- **总执行时间**: {_format_time(total_elapsed_time/1000)}")
    report.append(f"- **总CPU时间**: {_format_time(total_cpu_time/1000)}")
    report.append(f"- **总输入数据**: {_format_bytes(total_input_data)}")
    report.append(f"- **总输出数据**: {_format_bytes(total_output_data)}")
    report.append(f"- **顶点数量**: {len(vertices)}\n")
    
    # TOP5内存密集型顶点
    report.append("## TOP5内存密集型顶点")
    for i, vertex in enumerate(analysis['most_memory_intensive']):
        report.append(f"{i+1}. **{vertex.id}** ({vertex.type})")
        report.append(f"   - 内存: {_format_bytes(vertex.memory_stats.avg_overall_memory_peak_size)} 平均, "
                     f"{_format_bytes(vertex.memory_stats.max_overall_memory_peak_size)} 最大")
        if vertex.operators:
            report.append("   - 操作符:")
            for op in vertex.operators[:3]:  # 只显示前3个
                row_info = f"{op.row_count:,}" if op.row_count else "N/A"
                time_info = _format_time((op.inclusive_time or 0)/1000)
                report.append(f"     * operator_{op.id}: {row_info} 行, {time_info} 包含时间")
        report.append("")
    
    # TOP5时间消耗型顶点
    report.append("## TOP5时间消耗型顶点")
    for i, vertex in enumerate(analysis['most_time_consuming']):
        percentage = (vertex.time_stats.elapsed_time / total_elapsed_time * 100) if total_elapsed_time > 0 else 0
        report.append(f"{i+1}. **{vertex.id}** ({vertex.type})")
        report.append(f"   - 时间: {_format_time(vertex.time_stats.elapsed_time/1000)} ({percentage:.1f}% 总时间)")
        if vertex.operators:
            report.append("   - 操作符:")
            for op in vertex.operators[:3]:
                row_info = f"{op.row_count:,}" if op.row_count else "N/A"
                time_info = _format_time((op.inclusive_time or 0)/1000)
                report.append(f"     * operator_{op.id}: {row_info} 行, {time_info} 包含时间")
        report.append("")
    
    # TOP5数据密集型顶点
    report.append("## TOP5数据密集型顶点")
    for i, vertex in enumerate(analysis['most_data_intensive']):
        report.append(f"{i+1}. **{vertex.id}** ({vertex.type})")
        report.append(f"   - 数据: {_format_bytes(vertex.data_stats.input_bytes)} 输入, "
                     f"{_format_bytes(vertex.data_stats.output_bytes)} 输出")
        if vertex.operators:
            report.append("   - 操作符:")
            for op in vertex.operators[:3]:
                row_info = f"{op.row_count:,}" if op.row_count else "N/A"
                time_info = _format_time((op.inclusive_time or 0)/1000)
                report.append(f"     * operator_{op.id}: {row_info} 行, {time_info} 包含时间")
        report.append("")
    
    return "\n".join(report)


def _format_bytes(bytes_count: int) -> str:
    """格式化字节数"""
    if bytes_count == 0:
        return '0 B'
    k = 1024
    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while bytes_count >= k and i < len(sizes) - 1:
        bytes_count /= k
        i += 1
    return f"{bytes_count:.2f} {sizes[i]}"


def _format_time(seconds: float) -> str:
    """格式化时间"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


# 所有旧函数已被新的优化版本替换 