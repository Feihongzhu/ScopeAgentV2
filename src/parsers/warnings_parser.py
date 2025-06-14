"""
警告解析器 - 解析__Warnings__.xml文件
"""

import xml.etree.ElementTree as ET


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