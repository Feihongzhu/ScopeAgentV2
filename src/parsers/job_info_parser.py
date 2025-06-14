"""
作业信息解析器 - 解析JobInfo.xml文件
"""

import xml.etree.ElementTree as ET


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