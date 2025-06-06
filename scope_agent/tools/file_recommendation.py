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
        
        # 预定义信息需求映射
        self.info_requirements = {
            ProblemType.DATA_SKEW: [
                "用户脚本逻辑", "Join操作详情", "数据分布情况", 
                "分区策略", "热点键分析", "运行性能指标"
            ],
            ProblemType.EXCESSIVE_SHUFFLE: [
                "用户脚本逻辑", "算子使用情况", "数据流转路径",
                "Shuffle操作统计", "Stage运行情况", "数据规模信息"
            ],
            ProblemType.OTHER: [
                "用户脚本逻辑", "错误日志", "配置信息", "系统资源使用"
            ]
        }
        
        # 关键词映射
        self.keyword_mapping = {
            "用户脚本逻辑": ["脚本", "代码", "逻辑", "算法", "def", "class"],
            "Join操作详情": ["join", "连接", "关联", "合并"],
            "数据分布情况": ["分布", "倾斜", "热点", "统计", "skew"],
            "Stage运行情况": ["stage", "阶段", "运行", "执行", "任务"],
            "Shuffle操作统计": ["shuffle", "重分区", "数据传输", "网络"],
            "数据规模信息": ["数据量", "规模", "大小", "行数", "size"],
            "算子使用情况": ["算子", "操作符", "operator", "函数调用"],
            "数据流转路径": ["数据流", "pipeline", "流程", "path"],
            "运行性能指标": ["性能", "耗时", "延迟", "throughput", "performance"],
            "错误日志": ["错误", "异常", "error", "exception", "失败"],
            "配置信息": ["配置", "参数", "设置", "config", "property"],
            "系统资源使用": ["内存", "CPU", "磁盘", "网络", "资源"]
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
            keywords = self.keyword_mapping.get(info_type, [])
            
            if info_type == "用户脚本逻辑" and any(kw in content_lower for kw in ["脚本", "代码"]):
                reasons.append("包含用户脚本逻辑，有助于理解业务处理流程")
            elif info_type == "Stage运行情况" and any(kw in content_lower for kw in ["stage", "运行"]):
                reasons.append("包含Stage运行信息，可分析性能瓶颈")
            elif info_type == "数据分布情况" and any(kw in content_lower for kw in ["分布", "倾斜"]):
                reasons.append("包含数据分布信息，有助于分析倾斜问题")
            elif info_type == "Shuffle操作统计" and any(kw in content_lower for kw in ["shuffle", "重分区"]):
                reasons.append("包含Shuffle操作信息，可优化数据传输")
            elif info_type == "Join操作详情" and "join" in content_lower:
                reasons.append("包含Join操作详情，有助于优化连接策略")
        
        # 基于问题类型添加特定原因
        if problem_type == ProblemType.DATA_SKEW:
            if "数据" in content_lower and "分析" in content_lower:
                reasons.append("可提供数据倾斜分析的关键信息")
        elif problem_type == ProblemType.EXCESSIVE_SHUFFLE:
            if "性能" in content_lower or "优化" in content_lower:
                reasons.append("可提供Shuffle优化的性能分析")
        
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


# 默认文件内容映射配置
DEFAULT_FILE_MAPPING = {
    "user_script.txt": "用户提交的原始SCOPE脚本代码",
    "dag_stages.log": "DAG中每个stage的运行情况和性能数据", 
    "data_skew_report.json": "数据倾斜统计分析报告",
    "shuffle_stats.log": "Shuffle操作的性能统计日志",
    "join_analysis.txt": "Join操作的详细分析结果",
    "config.properties": "作业运行的配置参数设置",
    "error.log": "作业运行过程中的错误和异常日志",
    "performance_metrics.json": "整体性能指标和监控数据"
}

# 默认解析函数映射
DEFAULT_PARSER_MAPPING = {
    "dag_stages.log": "parse_dag_stages",
    "data_skew_report.json": "parse_skew_report", 
    "shuffle_stats.log": "parse_shuffle_stats",
    "performance_metrics.json": "parse_performance_metrics"
} 