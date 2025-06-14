"""
代数执行计划解析器 - 解析Algebra.xml文件
"""

import xml.etree.ElementTree as ET


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