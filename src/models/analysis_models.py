"""
分析相关的数据模型定义
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Union
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


# === Cosmos SCOPE Job 特定的数据模型 ===

class ScopeFileType(Enum):
    """SCOPE Job 文件类型枚举"""
    # 脚本和命令文件
    SCOPE_SCRIPT = "scope.script"
    COMMAND_LINE = "NebulaCommandLine.txt"
    
    # 代码生成相关
    CODE_GEN_DLL = "__ScopeCodeGen__.dll"
    CODE_GEN_CS = "__ScopeCodeGen__.dll.cs"
    COMPILE_OUTPUT = "__ScopeCodeGenCompileOutput__.txt"
    COMPILE_OPTIONS = "__ScopeCodeGenCompileOptions__.txt"
    COMPILER_TIMERS = "__CompilerTimers.xml"
    
    # 作业信息文件
    JOB_INFO = "JobInfo.xml"
    JOB_STATISTICS = "JobStatistics.xml"
    DIAGNOSTICS = "diagnosticsjson"
    ERROR_LOG = "Error"
    
    # 执行计划和数据流
    ALGEBRA = "Algebra.xml"
    VERTEX_DEF = "ScopeVertexDef.xml"
    DATA_FLOW_GRAPH = "__DataMapDfg__.json"
    
    # 运行时信息
    WARNINGS = "__Warnings__.xml"
    RUNTIME_STATS = "__ScopeRuntimeStatistics__.xml"
    INTERNAL_INFO = "__ScopeInternalInfo__.xml"
    STREAM_INFO = "__SStreamInfo__.xml"
    
    # 性能分析
    PROFILE = "profile"


class FileAnalysisStatus(Enum):
    """文件分析状态"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ScopeJobInfo:
    """SCOPE 作业基本信息"""
    job_id: str
    submit_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = ""
    resource_requirements: Dict[str, Any] = None
    input_tables: List[Dict[str, Any]] = None
    output_tables: List[Dict[str, Any]] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.resource_requirements is None:
            self.resource_requirements = {}
        if self.input_tables is None:
            self.input_tables = []
        if self.output_tables is None:
            self.output_tables = []
        if self.parameters is None:
            self.parameters = {}


@dataclass
class StageInfo:
    """Stage 执行信息"""
    stage_id: str
    stage_name: str
    duration: str
    task_count: int
    data_processed: str = ""
    data_output: str = ""
    status: str = ""
    warnings: List[str] = None
    skewed_tasks: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.skewed_tasks is None:
            self.skewed_tasks = []


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: Union[str, float, int]
    stage: Optional[str] = None
    threshold: Optional[float] = None
    status: str = ""
    description: str = ""


@dataclass
class ScopeJobStatistics:
    """SCOPE 作业统计信息"""
    job_id: str
    total_duration: str
    data_processed: str
    data_output: str
    tasks_completed: int
    tasks_failed: int = 0
    retry_count: int = 0
    stages: List[StageInfo] = None
    performance_metrics: List[PerformanceMetric] = None
    
    def __post_init__(self):
        if self.stages is None:
            self.stages = []
        if self.performance_metrics is None:
            self.performance_metrics = []
    
    def get_stage_by_id(self, stage_id: str) -> Optional[StageInfo]:
        """根据 stage_id 获取 stage 信息"""
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None
    
    def get_skew_ratio(self) -> Optional[float]:
        """获取数据倾斜比率"""
        for metric in self.performance_metrics:
            if metric.name == "SkewRatio":
                return float(metric.value) if isinstance(metric.value, (str, int, float)) else None
        return None


@dataclass
class CompilerInfo:
    """编译器信息"""
    compile_options: Dict[str, Any] = None
    compile_output: str = ""
    timers: Dict[str, Any] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.compile_options is None:
            self.compile_options = {}
        if self.timers is None:
            self.timers = {}
        if self.warnings is None:
            self.warnings = []


@dataclass
class DataFlowGraph:
    """数据流图信息"""
    vertices: List[Dict[str, Any]] = None
    edges: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.vertices is None:
            self.vertices = []
        if self.edges is None:
            self.edges = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ScopeFileAnalysis:
    """SCOPE 文件分析结果"""
    file_type: ScopeFileType
    file_path: str
    analysis_status: FileAnalysisStatus
    content_summary: str = ""
    key_findings: List[str] = None
    parsed_data: Optional[Union[ScopeJobInfo, ScopeJobStatistics, CompilerInfo, DataFlowGraph]] = None
    analysis_timestamp: Optional[datetime] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.key_findings is None:
            self.key_findings = []
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.now()


@dataclass
class ScopeAnalysisContext:
    """SCOPE 分析上下文"""
    job_info: Optional[ScopeJobInfo] = None
    job_statistics: Optional[ScopeJobStatistics] = None
    compiler_info: Optional[CompilerInfo] = None
    data_flow_graph: Optional[DataFlowGraph] = None
    file_analyses: List[ScopeFileAnalysis] = None
    original_script: str = ""
    
    def __post_init__(self):
        if self.file_analyses is None:
            self.file_analyses = []
    
    def get_file_analysis(self, file_type: ScopeFileType) -> Optional[ScopeFileAnalysis]:
        """获取特定文件类型的分析结果"""
        for analysis in self.file_analyses:
            if analysis.file_type == file_type:
                return analysis
        return None
    
    def has_data_skew_indicators(self) -> bool:
        """检查是否有数据倾斜指标"""
        if self.job_statistics:
            skew_ratio = self.job_statistics.get_skew_ratio()
            if skew_ratio and skew_ratio > 3.0:
                return True
            
            # 检查是否有倾斜任务
            for stage in self.job_statistics.stages:
                if stage.skewed_tasks:
                    return True
        
        return False
    
    def get_problem_indicators(self) -> Dict[ProblemType, List[str]]:
        """获取问题指标"""
        indicators = {
            ProblemType.DATA_SKEW: [],
            ProblemType.EXCESSIVE_SHUFFLE: [],
            ProblemType.OTHER: []
        }
        
        # 数据倾斜指标
        if self.has_data_skew_indicators():
            indicators[ProblemType.DATA_SKEW].append("检测到数据倾斜")
        
        # Shuffle 相关指标
        if self.job_statistics:
            for metric in self.job_statistics.performance_metrics:
                if "Shuffle" in metric.name and isinstance(metric.value, str):
                    if "GB" in metric.value:  # 简单的大数据量检查
                        indicators[ProblemType.EXCESSIVE_SHUFFLE].append(f"大量Shuffle数据: {metric.value}")
        
        # 其他问题指标
        error_analysis = self.get_file_analysis(ScopeFileType.ERROR_LOG)
        if error_analysis and error_analysis.analysis_status == FileAnalysisStatus.COMPLETED:
            indicators[ProblemType.OTHER].append("检测到错误日志")
        
        return indicators 