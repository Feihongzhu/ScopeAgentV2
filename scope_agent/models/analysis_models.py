"""
分析相关的数据模型定义
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


class ProblemType(Enum):
    """问题类型枚举"""
    DATA_SKEW = "数据倾斜"
    EXCESSIVE_SHUFFLE = "过多Shuffle"
    OTHER = "其他"


class ThinkStep(Enum):
    """思考步骤枚举"""
    PROBLEM_CLASSIFICATION = "THINK_1"  # 问题分类
    CODE_ANALYSIS = "THINK_2"           # 关键代码分析
    EXPERIENCE_ANALYSIS = "THINK_3"     # 经验推导分析
    INFO_COMPLETENESS = "THINK_4"       # 信息完整性检查
    FINAL_SOLUTION = "THINK_5"          # 最终方案建议


@dataclass
class FileRecommendation:
    """文件推荐信息"""
    file_name: str
    content_description: str
    relevance_score: float
    reason: str
    requires_parser: bool = False
    parser_function: Optional[str] = None


@dataclass
class ContextInfo:
    """上下文信息"""
    problem_type: Optional[ProblemType] = None
    user_input: str = ""
    current_analysis: str = ""
    files_read: List[str] = None
    key_findings: List[str] = None
    
    def __post_init__(self):
        if self.files_read is None:
            self.files_read = []
        if self.key_findings is None:
            self.key_findings = []


@dataclass
class ThinkStepResult:
    """单个思考步骤的结果"""
    step: ThinkStep
    content: str
    confidence: float = 0.0
    needs_more_info: bool = False
    recommended_files: List[FileRecommendation] = None
    
    def __post_init__(self):
        if self.recommended_files is None:
            self.recommended_files = []


@dataclass
class AnalysisResult:
    """完整分析结果"""
    problem_type: ProblemType
    think_steps: List[ThinkStepResult]
    final_solution: str
    confidence_score: float
    files_analyzed: List[str]
    processing_time: float
    timestamp: datetime
    
    def get_step_result(self, step: ThinkStep) -> Optional[ThinkStepResult]:
        """获取特定步骤的结果"""
        for result in self.think_steps:
            if result.step == step:
                return result
        return None
    
    def is_analysis_complete(self) -> bool:
        """检查分析是否完整"""
        required_steps = list(ThinkStep)
        completed_steps = [result.step for result in self.think_steps]
        return all(step in completed_steps for step in required_steps)


@dataclass
class IterationState:
    """迭代状态信息"""
    iteration_count: int = 0
    max_iterations: int = 5
    analysis_progress: float = 0.0
    information_sufficient: bool = False
    last_action: str = ""
    
    def can_continue(self) -> bool:
        """判断是否可以继续迭代"""
        return (self.iteration_count < self.max_iterations and 
                not self.information_sufficient)
    
    def increment_iteration(self):
        """增加迭代次数"""
        self.iteration_count += 1


@dataclass
class FileAnalysisInfo:
    """文件分析信息"""
    file_name: str
    content: str
    content_summary: str
    file_type: str
    analysis_timestamp: datetime
    key_insights: List[str] = None
    
    def __post_init__(self):
        if self.key_insights is None:
            self.key_insights = []


@dataclass
class ExperienceKnowledge:
    """经验知识条目"""
    problem_type: ProblemType
    title: str
    description: str
    solution_pattern: str
    confidence: float
    examples: List[str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = [] 