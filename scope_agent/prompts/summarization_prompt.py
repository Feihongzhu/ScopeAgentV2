"""
总结Prompt模板
"""

from langchain.prompts import PromptTemplate
from typing import Dict, Any

class SummarizationPromptTemplate:
    """总结Prompt模板"""
    
    def __init__(self):
        self.template = """当前分析内容过长，请进行结构化总结：

【原始分析内容】
{original_content}

请按以下格式输出简洁摘要：

## 分析摘要

**问题类别**：{problem_type}

**关键发现**：
- 核心问题点
- 主要影响因素
- 关键性能瓶颈

**推荐文件**：
- 文件1：查看原因
- 文件2：查看原因

**解决方案要点**：
1. 优先措施
2. 备选方案
3. 实施建议

**置信度**：{confidence_score}/10

保持内容简洁，突出重点。
"""
    
    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs) 