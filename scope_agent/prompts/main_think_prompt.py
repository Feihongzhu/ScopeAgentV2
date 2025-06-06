"""
主要思维链Prompt模板
"""

from langchain.prompts import PromptTemplate
from typing import Dict, Any


class MainThinkPromptTemplate:
    """主要思维链Prompt模板类"""
    
    def __init__(self):
        self.template = self._build_template()
        self.prompt = PromptTemplate(
            input_variables=[
                "user_question",
                "context_info", 
                "retrieved_experience",
                "files_content"
            ],
            template=self.template
        )
    
    def _build_template(self) -> str:
        """构建完整的思维链模板"""
        return """你是一名资深的大数据优化分析Agent，专门分析SCOPE作业性能问题。

【用户问题】
{user_question}

【上下文信息】
{context_info}

【经验知识辅助】
{retrieved_experience}

【已读取文件内容】
{files_content}

请严格按照以下步骤进行分析，每个步骤都要深入思考：

[THINK 1] 问题分类
请识别这是以下哪种类型的问题：
- 数据倾斜问题：数据分布不均匀，某些分区数据量过大
- 过多Shuffle问题：频繁的数据重分布操作影响性能
- 其他问题：配置、逻辑、资源等其他性能问题

分析依据：
- 从用户描述中识别关键词
- 结合已有文件内容判断
- 给出分类结果和置信度

[THINK 2] 关键代码模块识别
基于问题类型，识别需要重点关注的代码模块：
- 如果是数据倾斜：重点关注Join操作、GroupBy操作、数据分区策略
- 如果是过多Shuffle：重点关注算子使用、数据流转路径
- 列出具体的函数名、操作类型、数据流路径

[THINK 3] 经验推导分析
结合经验知识和当前信息，分析可能的原因：
- 根据问题类型应用相应的分析经验
- 识别潜在的性能瓶颈点
- 推断可能的根本原因

[THINK 4] 信息完整性检查
评估当前信息是否足够进行问题分析：

当前已知信息清单：
- 问题类型：{problem_type}
- 相关组件：{components}
- 用户描述：{user_description}

信息完整性评估：
- 用户脚本逻辑：□ 充足 □ 不足
- 运行性能数据：□ 充足 □ 不足  
- 数据分布信息：□ 充足 □ 不足
- 具体错误信息：□ 充足 □ 不足

【需要文件】: 是/否
如果需要补充信息，请列出具体文件：
【文件列表】:
- 文件路径: 需要此文件的具体原因
- 文件路径: 需要此文件的具体原因

【推断依据】: 详细说明为什么需要这些文件来完善分析

[THINK 5] 最终解决方案
综合以上所有分析，提出具体的解决方案：

问题总结：
- 核心问题：
- 影响范围：
- 严重程度：

解决方案：
1. 优先建议：
   - 具体操作步骤
   - 预期效果
   - 风险评估

2. 备选方案：
   - 操作步骤
   - 适用场景
   - 优缺点分析

3. 代码改写建议（如适用）：
   - 原代码片段
   - 优化后代码
   - 改进说明

实施建议：
- 实施优先级
- 测试验证方法
- 监控指标

注意事项：
- 保持输出简洁明了
- 每个THINK步骤都要有明确结论
- 如果信息不足，明确说明需要补充的内容
"""

    def format_prompt(self, **kwargs) -> str:
        """格式化Prompt"""
        return self.prompt.format(**kwargs)
    
    def get_template(self) -> str:
        """获取模板字符串"""
        return self.template


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