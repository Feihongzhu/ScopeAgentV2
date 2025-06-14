"""
文件推荐工具 - 智能推荐需要查看的文件
"""

import time
from typing import List, Dict, Any, Optional
from ..models.analysis_models import ProblemType, FileRecommendation, ContextInfo


class FileRecommendationTool:
    """文件推荐工具类"""
    
    def __init__(self, file_content_mapping: Dict[str, str], parser_functions: Dict[str, str]):
        """
        初始化文件推荐工具
        
        Args:
            file_content_mapping: 文件名到内容描述的映射
            parser_functions: 需要特殊解析的文件及其解析函数映射
        """
        self.file_content_mapping = file_content_mapping
        self.parser_functions = parser_functions
        
        # 预定义信息需求映射 - 基于实际SCOPE Job文件结构
        self.info_requirements = {
            ProblemType.DATA_SKEW: [
                "SCOPE脚本逻辑", "Join操作详情", "数据倾斜统计", 
                "分区策略", "热点键分析", "Stage性能指标", "倾斜任务信息"
            ],
            ProblemType.EXCESSIVE_SHUFFLE: [
                "SCOPE脚本逻辑", "算子执行计划", "数据流图分析",
                "Shuffle操作统计", "Stage运行情况", "顶点配置信息"
            ],
            ProblemType.OTHER: [
                "SCOPE脚本逻辑", "错误日志", "编译输出", "作业配置信息", 
                "警告信息", "诊断数据"
            ]
        }
        
        # 关键词映射 - 基于实际SCOPE Job文件内容
        self.keyword_mapping = {
            "SCOPE脚本逻辑": ["scope", "script", "脚本", "SELECT", "FROM", "JOIN", "GROUP BY"],
            "Join操作详情": ["join", "连接", "关联", "合并", "inner", "outer", "left", "right"],
            "数据倾斜统计": ["倾斜", "skew", "SkewRatio", "热点", "不均", "imbalance", "SkewedTasks"],
            "Stage性能指标": ["stage", "阶段", "执行", "Duration", "TaskCount", "性能", "耗时"],
            "Shuffle操作统计": ["shuffle", "重分区", "ShuffleDataSize", "数据传输", "网络"],
            "倾斜任务信息": ["SkewedTasks", "倾斜任务", "热点键", "task", "TaskId"],
            "算子执行计划": ["算子", "operator", "执行计划", "查询计划", "algebra", "vertex"],
            "数据流图分析": ["数据流", "DataFlow", "vertices", "edges", "依赖关系"],
            "顶点配置信息": ["vertex", "顶点", "配置", "参数", "ScopeVertexDef"],
            "错误日志": ["错误", "异常", "error", "exception", "失败", "failed"],
            "编译输出": ["编译", "compile", "CodeGen", "warning", "CompilerTimers"],
            "作业配置信息": ["JobInfo", "配置", "参数", "ResourceRequirements", "设置"],
            "警告信息": ["warning", "警告", "Warnings", "潜在问题"],
            "诊断数据": ["diagnostic", "诊断", "监控", "统计", "Statistics"]
        }
    
    def recommend_files(self, problem_type: ProblemType, context: ContextInfo, 
                       current_analysis: str) -> List[FileRecommendation]:
        """
        基于问题类型、上下文和当前分析状态推荐文件
        
        Args:
            problem_type: 问题类型
            context: 上下文信息
            current_analysis: 当前分析内容
            
        Returns:
            推荐文件列表，按相关性得分排序
        """
        # 1. 识别缺失的信息类型
        missing_info_types = self._identify_missing_information(
            problem_type, context.user_input, current_analysis
        )
        
        recommendations = []
        
        # 2. 基于文件内容描述匹配需求
        for file_name, content_desc in self.file_content_mapping.items():
            # 跳过已读取的文件
            if file_name in context.files_read:
                continue
                
            relevance_score = self._calculate_content_relevance(
                content_desc, missing_info_types, problem_type
            )
            
            if relevance_score > 0.3:  # 设置相关性阈值
                recommendation = FileRecommendation(
                    file_name=file_name,
                    content_description=content_desc,
                    relevance_score=relevance_score,
                    reason=self._generate_recommendation_reason(
                        content_desc, missing_info_types, problem_type
                    ),
                    requires_parser=file_name in self.parser_functions,
                    parser_function=self.parser_functions.get(file_name)
                )
                recommendations.append(recommendation)
        
        # 3. 按相关性得分排序
        return sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)
    
    def _identify_missing_information(self, problem_type: ProblemType, 
                                    user_input: str, current_analysis: str) -> List[str]:
        """识别当前分析中缺失的信息类型"""
        missing_info = []
        
        # 获取该问题类型需要的信息
        required_info = self.info_requirements.get(problem_type, [])
        
        # 检查当前分析中已包含哪些信息
        for info_type in required_info:
            if not self._is_info_present_in_analysis(info_type, current_analysis):
                missing_info.append(info_type)
        
        return missing_info
    
    def _is_info_present_in_analysis(self, info_type: str, analysis: str) -> bool:
        """检查特定类型的信息是否已包含在分析中"""
        if not analysis:
            return False
            
        keywords = self.keyword_mapping.get(info_type, [])
        analysis_lower = analysis.lower()
        
        # 至少要匹配一个关键词才认为信息存在
        return any(keyword.lower() in analysis_lower for keyword in keywords)
    
    def _calculate_content_relevance(self, content_desc: str, missing_info: List[str], 
                                   problem_type: ProblemType) -> float:
        """计算文件内容与缺失信息的相关性得分"""
        if not missing_info:
            return 0.0
            
        score = 0.0
        content_lower = content_desc.lower()
        
        # 基于缺失信息类型计算得分
        for missing_type in missing_info:
            keywords = self.keyword_mapping.get(missing_type, [])
            
            # 关键词匹配得分
            matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            if matches > 0:
                # 每个匹配的关键词贡献0.2分，最高1.0分
                type_score = min(matches * 0.2, 1.0)
                score += type_score
        
        # 根据问题类型给予权重加成
        if problem_type == ProblemType.DATA_SKEW:
            if any(keyword in content_lower for keyword in ["join", "倾斜", "分布"]):
                score *= 1.2
        elif problem_type == ProblemType.EXCESSIVE_SHUFFLE:
            if any(keyword in content_lower for keyword in ["shuffle", "stage", "重分区"]):
                score *= 1.2
        
        return min(score, 1.0)  # 限制最大得分为1.0
    
    def _generate_recommendation_reason(self, content_desc: str, missing_info: List[str], 
                                      problem_type: ProblemType) -> str:
        """生成推荐文件的原因说明"""
        reasons = []
        content_lower = content_desc.lower()
        
        # 基于缺失信息生成原因
        for info_type in missing_info:
            if info_type == "SCOPE脚本逻辑" and any(kw in content_lower for kw in ["scope", "脚本", "script"]):
                reasons.append("包含SCOPE脚本逻辑，有助于理解业务处理流程")
            elif info_type == "Stage性能指标" and any(kw in content_lower for kw in ["stage", "统计", "性能"]):
                reasons.append("包含Stage性能信息，可分析执行瓶颈")
            elif info_type == "数据倾斜统计" and any(kw in content_lower for kw in ["倾斜", "skew", "统计"]):
                reasons.append("包含数据倾斜统计信息，有助于分析倾斜问题")
            elif info_type == "Shuffle操作统计" and any(kw in content_lower for kw in ["shuffle", "重分区"]):
                reasons.append("包含Shuffle操作统计，可优化数据传输")
            elif info_type == "Join操作详情" and "join" in content_lower:
                reasons.append("包含Join操作详情，有助于优化连接策略")
            elif info_type == "倾斜任务信息" and any(kw in content_lower for kw in ["task", "倾斜", "热点"]):
                reasons.append("包含倾斜任务详情，有助于定位热点问题")
            elif info_type == "算子执行计划" and any(kw in content_lower for kw in ["执行计划", "algebra", "算子"]):
                reasons.append("包含算子执行计划，有助于优化查询逻辑")
            elif info_type == "数据流图分析" and any(kw in content_lower for kw in ["数据流", "dataflow", "vertices"]):
                reasons.append("包含数据流图信息，有助于理解数据依赖关系")
            elif info_type == "顶点配置信息" and any(kw in content_lower for kw in ["vertex", "顶点", "配置"]):
                reasons.append("包含顶点配置信息，有助于分析计算节点设置")
            elif info_type == "错误日志" and any(kw in content_lower for kw in ["错误", "error", "异常"]):
                reasons.append("包含错误信息，有助于问题诊断")
            elif info_type == "编译输出" and any(kw in content_lower for kw in ["编译", "compile", "codegen"]):
                reasons.append("包含编译输出信息，有助于分析编译阶段问题")
            elif info_type == "作业配置信息" and any(kw in content_lower for kw in ["作业", "job", "配置"]):
                reasons.append("包含作业配置信息，有助于理解资源设置")
            elif info_type == "警告信息" and any(kw in content_lower for kw in ["警告", "warning"]):
                reasons.append("包含警告信息，有助于发现潜在问题")
            elif info_type == "诊断数据" and any(kw in content_lower for kw in ["诊断", "diagnostic", "监控"]):
                reasons.append("包含诊断数据，有助于全面分析作业状态")
        
        # 基于问题类型添加特定原因
        if problem_type == ProblemType.DATA_SKEW:
            if any(kw in content_lower for kw in ["倾斜", "skew", "热点"]):
                reasons.append("可提供数据倾斜分析的关键信息")
        elif problem_type == ProblemType.EXCESSIVE_SHUFFLE:
            if any(kw in content_lower for kw in ["shuffle", "数据流", "性能"]):
                reasons.append("可提供Shuffle优化的性能分析")
        elif problem_type == ProblemType.OTHER:
            if any(kw in content_lower for kw in ["错误", "警告", "诊断"]):
                reasons.append("可提供问题诊断的重要信息")
        
        return "；".join(reasons) if reasons else "可能包含相关分析信息"
    
    def get_file_priority_score(self, file_name: str, problem_type: ProblemType) -> float:
        """获取文件的优先级得分"""
        content_desc = self.file_content_mapping.get(file_name, "")
        
        # 基础得分
        base_score = 0.5
        
        # 根据文件名模式调整得分
        if "script" in file_name.lower() or "脚本" in file_name:
            base_score += 0.3  # 脚本文件优先级高
        
        if "log" in file_name.lower() or "日志" in file_name:
            base_score += 0.2  # 日志文件次优先
        
        if "config" in file_name.lower() or "配置" in file_name:
            base_score += 0.1  # 配置文件最低优先
        
        # 根据问题类型调整
        if problem_type == ProblemType.DATA_SKEW:
            if any(kw in content_desc.lower() for kw in ["join", "倾斜", "分布"]):
                base_score += 0.2
        elif problem_type == ProblemType.EXCESSIVE_SHUFFLE:
            if any(kw in content_desc.lower() for kw in ["shuffle", "stage"]):
                base_score += 0.2
        
        return min(base_score, 1.0)


# Cosmos SCOPE Job 文件内容映射配置
DEFAULT_FILE_MAPPING = {
    # 原始脚本和命令
    "scope.script": "用户提交的原始SCOPE脚本代码",
    "NebulaCommandLine.txt": "作业实际提交运行时的命令行参数",
    
    # 代码生成相关文件
    "__ScopeCodeGen__.dll": "编译后的动态链接库，包含作业的实际执行代码",
    "__ScopeCodeGen__.dll.cs": "生成的C#源代码，包含编译时生成的所有执行逻辑",
    "__ScopeCodeGenCompileOutput__.txt": "编译阶段生成C#代码时的输出信息",
    "__ScopeCodeGenCompileOptions__.txt": "编译选项文件，包含编译器使用的具体编译参数",
    "__CompilerTimers.xml": "编译阶段各个步骤所花费时间的信息",
    
    # 作业执行信息文件
    "JobInfo.xml": "作业的基本信息，如Job ID、提交时间、作业类型、资源需求等",
    "JobStatistics.xml": "作业执行完成后的统计信息，包括每个阶段执行时长、数据量统计等",
    "diagnosticsjson": "诊断信息，以JSON格式提供作业执行期间的问题或状态",
    "Error": "作业执行过程中的错误详细信息",
    
    # 数据映射与执行计划文件
    "Algebra.xml": "以XML格式记录作业执行的查询计划，展现底层算子逻辑与依赖关系",
    "ScopeVertexDef.xml": "定义作业中的各个计算节点（Vertex）的详细配置信息和参数",
    "__DataMapDfg__.json": "作业数据流图的JSON表示，提供数据流关系、阶段间的数据依赖关系",
    
    # 警告和运行状态信息
    "__Warnings__.xml": "编译或运行阶段的警告信息，反映可能潜在影响性能的点",
    "__ScopeRuntimeStatistics__.xml": "作业执行期间运行时的详细统计数据",
    "__ScopeInternalInfo__.xml": "内部状态信息，用于进一步的故障诊断和分析",
    "__SStreamInfo__.xml": "Stream流的元数据信息，用于跟踪数据流之间的传输细节",
    
    # 性能分析
    "profile": "作业性能分析数据，可用来深入分析节点级别的资源占用情况"
}

# Cosmos SCOPE Job 解析函数映射
DEFAULT_PARSER_MAPPING = {
    # XML文件解析器
    "JobInfo.xml": "parse_job_info_xml",
    "JobStatistics.xml": "parse_job_statistics_xml",
    "Algebra.xml": "parse_algebra_xml",
    "ScopeVertexDef.xml": "parse_vertex_def_xml",
    "__CompilerTimers.xml": "parse_compiler_timers_xml",
    "__Warnings__.xml": "parse_warnings_xml",
    "__ScopeRuntimeStatistics__.xml": "parse_runtime_statistics_xml",
    "__ScopeInternalInfo__.xml": "parse_internal_info_xml",
    "__SStreamInfo__.xml": "parse_stream_info_xml",
    
    # JSON文件解析器
    "__DataMapDfg__.json": "parse_data_flow_graph_json",
    "diagnosticsjson": "parse_diagnostics_json",
    
    # 文本文件解析器
    "__ScopeCodeGenCompileOutput__.txt": "parse_compile_output_txt",
    "__ScopeCodeGenCompileOptions__.txt": "parse_compile_options_txt",
    "NebulaCommandLine.txt": "parse_command_line_txt",
    
    # C#代码文件解析器
    "__ScopeCodeGen__.dll.cs": "parse_csharp_code",
    
    # SCOPE脚本解析器
    "request.script": "parse_scope_script",
    "scope.script": "parse_scope_script",
    
    # 性能分析文件解析器
    "profile": "parse_profile_data",
    
    # 错误文件解析器
    "Error": "parse_error_file"
} 