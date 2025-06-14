"""
编译输出解析器 - 解析编译输出文件
"""


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