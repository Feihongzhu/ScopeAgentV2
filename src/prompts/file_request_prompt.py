"""
文件请求Prompt模板
"""

from langchain.prompts import PromptTemplate
from typing import Dict, Any

class FileRequestPromptTemplate:
    """文件请求Prompt模板"""
    
    def __init__(self):
        self.template = """基于当前分析进度，我需要评估是否需要查看更多文件：

【当前分析状态】
问题类型：{problem_type}
已完成步骤：{completed_steps}
分析进度：{analysis_progress}%

【已读取文件】
{files_read}

【缺失信息类型】
{missing_info_types}

【文件推荐规则】
1. 数据倾斜问题 → 优先查看：用户脚本、Join操作分析、数据分布报告
2. 过多Shuffle问题 → 优先查看：用户脚本、Stage运行情况、算子使用统计
3. 其他问题 → 根据具体描述推断所需文件

请输出：
【是否需要更多文件】：是/否
【推荐文件列表】：
- 文件名：推荐原因
- 文件名：推荐原因
【推荐依据】：详细说明
"""
    
    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

