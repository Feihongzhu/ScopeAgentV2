"""
上下文增强器 - 改善文件选择和分析质量
"""

from typing import Dict, Any, List, Optional
from ..models.analysis_models import ProblemType, ContextInfo, ThinkStep


class ContextEnhancer:
    """上下文增强器类"""
    
    def __init__(self):
        """初始化上下文增强器"""
        self.enhancement_rules = self._init_enhancement_rules()
    
    def _init_enhancement_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化增强规则"""
        return {
            ProblemType.DATA_SKEW.value: {
                "key_concepts": ["数据倾斜", "热点键", "分区不均", "Join操作"],
                "priority_files": ["user_script.txt", "data_skew_report.json", "join_analysis.txt"],
                "analysis_focus": ["分区策略", "Join键分布", "数据量统计"],
                "common_solutions": ["PartitionBy优化", "热点键处理", "随机盐值"]
            },
            ProblemType.EXCESSIVE_SHUFFLE.value: {
                "key_concepts": ["Shuffle操作", "数据重分布", "网络传输", "Stage性能"],
                "priority_files": ["user_script.txt", "shuffle_stats.log", "dag_stages.log"],
                "analysis_focus": ["Shuffle次数", "数据传输量", "Stage依赖关系"],
                "common_solutions": ["PartitionBy优化", "广播Join", "数据预聚合"]
            },
            ProblemType.OTHER.value: {
                "key_concepts": ["性能问题", "配置优化", "资源使用"],
                "priority_files": ["user_script.txt", "error.log", "config.properties"],
                "analysis_focus": ["错误信息", "配置参数", "资源瓶颈"],
                "common_solutions": ["配置调优", "资源扩容", "算法优化"]
            }
        }
    
    def enhance_context_for_file_selection(self, 
                                         problem_type: ProblemType, 
                                         user_input: str, 
                                         previous_analysis: str,
                                         current_step: Optional[ThinkStep] = None) -> str:
        """
        为文件选择增强上下文信息
        
        Args:
            problem_type: 问题类型
            user_input: 用户输入
            previous_analysis: 之前的分析结果
            current_step: 当前分析步骤
            
        Returns:
            增强后的上下文信息
        """
        enhancement_rule = self.enhancement_rules.get(problem_type.value, {})
        
        enhanced_context = f"""
【问题分析上下文】
问题类型: {problem_type.value}
用户输入: {user_input}

【关键概念】
{self._format_list(enhancement_rule.get('key_concepts', []))}

【分析重点】
{self._format_list(enhancement_rule.get('analysis_focus', []))}

【已有分析结果】
{previous_analysis if previous_analysis else '暂无'}

【文件选择指导】
基于{problem_type.value}问题的特点，优先考虑以下类型的文件：
{self._format_list(enhancement_rule.get('priority_files', []))}

【关键点检查】
- 是否涉及数据处理的核心逻辑？
- 是否涉及性能关键路径？
- 是否涉及配置或参数设置？
- 当前分析阶段：{current_step.value if current_step else '未指定'}

【解决方案线索】
常见解决方案包括：
{self._format_list(enhancement_rule.get('common_solutions', []))}
"""
        
        return enhanced_context
    
    def enhance_analysis_context(self, 
                                context_info: ContextInfo,
                                file_contents: Dict[str, str] = None) -> Dict[str, Any]:
        """
        增强分析上下文
        
        Args:
            context_info: 基础上下文信息
            file_contents: 文件内容字典
            
        Returns:
            增强后的上下文字典
        """
        enhanced = {
            "problem_type": context_info.problem_type.value if context_info.problem_type else "未确定",
            "user_input": context_info.user_input,
            "analysis_progress": self._calculate_analysis_progress(context_info),
            "key_findings": context_info.key_findings,
            "files_analyzed": context_info.files_read,
            "missing_info": self._identify_missing_information(context_info),
            "next_steps": self._suggest_next_steps(context_info),
            "context_summary": self._generate_context_summary(context_info)
        }
        
        # 如果有文件内容，进行内容分析增强
        if file_contents:
            enhanced["file_analysis"] = self._analyze_file_contents(
                file_contents, context_info.problem_type
            )
        
        return enhanced
    
    def enhance_prompt_context(self, 
                             base_context: Dict[str, Any],
                             enhancement_type: str = "analysis") -> Dict[str, Any]:
        """
        增强Prompt上下文
        
        Args:
            base_context: 基础上下文
            enhancement_type: 增强类型 ("analysis", "file_selection", "solution")
            
        Returns:
            增强后的上下文
        """
        enhanced_context = base_context.copy()
        
        if enhancement_type == "analysis":
            enhanced_context.update(self._add_analysis_enhancements(base_context))
        elif enhancement_type == "file_selection":
            enhanced_context.update(self._add_file_selection_enhancements(base_context))
        elif enhancement_type == "solution":
            enhanced_context.update(self._add_solution_enhancements(base_context))
        
        return enhanced_context
    
    def _format_list(self, items: List[str], prefix: str = "- ") -> str:
        """格式化列表为字符串"""
        if not items:
            return "暂无"
        return "\n".join([f"{prefix}{item}" for item in items])
    
    def _calculate_analysis_progress(self, context_info: ContextInfo) -> float:
        """计算分析进度"""
        total_aspects = 5  # 对应THINK 1-5步骤
        completed_aspects = 0
        
        # 简单的进度估算
        if context_info.problem_type:
            completed_aspects += 1  # THINK 1完成
        
        if context_info.files_read:
            completed_aspects += min(len(context_info.files_read), 2)  # 文件分析
        
        if context_info.key_findings:
            completed_aspects += 1  # 有关键发现
        
        if context_info.current_analysis and len(context_info.current_analysis) > 500:
            completed_aspects += 1  # 分析较充分
        
        return min(completed_aspects / total_aspects, 1.0)
    
    def _identify_missing_information(self, context_info: ContextInfo) -> List[str]:
        """识别缺失的信息"""
        missing = []
        
        if not context_info.problem_type:
            missing.append("问题类型分类")
        
        if not context_info.files_read:
            missing.append("相关文件内容")
        
        if not context_info.key_findings:
            missing.append("关键发现总结")
        
        # 基于问题类型检查特定信息
        if context_info.problem_type:
            problem_requirements = {
                ProblemType.DATA_SKEW: ["数据分布信息", "Join操作详情", "分区策略"],
                ProblemType.EXCESSIVE_SHUFFLE: ["Shuffle统计", "Stage信息", "数据流路径"],
                ProblemType.OTHER: ["错误日志", "配置信息"]
            }
            
            requirements = problem_requirements.get(context_info.problem_type, [])
            analysis_lower = context_info.current_analysis.lower() if context_info.current_analysis else ""
            
            for req in requirements:
                # 简单的关键词检查
                if not any(keyword in analysis_lower for keyword in req.lower().split()):
                    missing.append(req)
        
        return missing
    
    def _suggest_next_steps(self, context_info: ContextInfo) -> List[str]:
        """建议下一步行动"""
        steps = []
        
        progress = self._calculate_analysis_progress(context_info)
        
        if progress < 0.3:
            steps.append("进行问题类型分类")
            steps.append("收集基础文件信息")
        elif progress < 0.6:
            steps.append("深入分析关键文件")
            steps.append("总结关键发现")
        elif progress < 0.8:
            steps.append("制定解决方案")
            steps.append("评估方案可行性")
        else:
            steps.append("完善方案细节")
            steps.append("准备实施建议")
        
        return steps
    
    def _generate_context_summary(self, context_info: ContextInfo) -> str:
        """生成上下文摘要"""
        parts = []
        
        if context_info.problem_type:
            parts.append(f"问题类型：{context_info.problem_type.value}")
        
        if context_info.files_read:
            parts.append(f"已分析{len(context_info.files_read)}个文件")
        
        if context_info.key_findings:
            parts.append(f"发现{len(context_info.key_findings)}个关键点")
        
        progress = self._calculate_analysis_progress(context_info)
        parts.append(f"分析进度：{progress:.1%}")
        
        return "；".join(parts) if parts else "分析刚开始"
    
    def _analyze_file_contents(self, file_contents: Dict[str, str], 
                             problem_type: Optional[ProblemType]) -> Dict[str, Any]:
        """分析文件内容并提取关键信息"""
        analysis = {
            "total_files": len(file_contents),
            "file_types": [],
            "key_patterns": [],
            "relevance_scores": {}
        }
        
        for file_name, content in file_contents.items():
            # 文件类型分析
            if file_name.endswith('.txt'):
                analysis["file_types"].append("脚本文件")
            elif file_name.endswith('.log'):
                analysis["file_types"].append("日志文件")
            elif file_name.endswith('.json'):
                analysis["file_types"].append("配置文件")
            
            # 关键模式识别
            content_lower = content.lower()
            
            if problem_type == ProblemType.DATA_SKEW:
                if 'join' in content_lower:
                    analysis["key_patterns"].append(f"{file_name}中发现Join操作")
                if any(word in content_lower for word in ['倾斜', 'skew', '不均']):
                    analysis["key_patterns"].append(f"{file_name}中发现数据倾斜相关信息")
            
            elif problem_type == ProblemType.EXCESSIVE_SHUFFLE:
                if 'shuffle' in content_lower:
                    analysis["key_patterns"].append(f"{file_name}中发现Shuffle操作")
                if 'stage' in content_lower:
                    analysis["key_patterns"].append(f"{file_name}中发现Stage信息")
            
            # 计算相关性得分
            analysis["relevance_scores"][file_name] = self._calculate_file_relevance(
                content, problem_type
            )
        
        return analysis
    
    def _calculate_file_relevance(self, content: str, 
                                problem_type: Optional[ProblemType]) -> float:
        """计算文件内容的相关性得分"""
        if not problem_type or not content:
            return 0.5
        
        content_lower = content.lower()
        score = 0.0
        
        # 基于问题类型的关键词权重
        keyword_weights = {
            ProblemType.DATA_SKEW: {
                'join': 0.3, 'partition': 0.2, 'skew': 0.3, '倾斜': 0.3,
                'hot': 0.2, '热点': 0.2, 'distribute': 0.1
            },
            ProblemType.EXCESSIVE_SHUFFLE: {
                'shuffle': 0.4, 'stage': 0.2, 'network': 0.1, 'broadcast': 0.2,
                'reduce': 0.1, 'partition': 0.1
            },
            ProblemType.OTHER: {
                'error': 0.3, 'exception': 0.3, 'config': 0.2, 'performance': 0.2
            }
        }
        
        weights = keyword_weights.get(problem_type, {})
        
        for keyword, weight in weights.items():
            if keyword in content_lower:
                score += weight
        
        return min(score, 1.0)
    
    def _add_analysis_enhancements(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """添加分析相关的增强"""
        return {
            "analysis_guidelines": [
                "结合具体的代码和数据进行分析",
                "考虑多种可能的原因和解决方案",
                "评估每种方案的优缺点和适用场景"
            ],
            "quality_checks": [
                "分析是否基于具体证据",
                "建议是否具有可操作性",
                "方案是否考虑了潜在风险"
            ]
        }
    
    def _add_file_selection_enhancements(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """添加文件选择相关的增强"""
        return {
            "selection_criteria": [
                "文件与问题类型的相关性",
                "文件信息的完整性和准确性",
                "文件对解决问题的重要程度"
            ],
            "prioritization_rules": [
                "优先选择直接相关的核心文件",
                "考虑信息互补性避免重复",
                "平衡广度和深度的信息需求"
            ]
        }
    
    def _add_solution_enhancements(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """添加解决方案相关的增强"""
        return {
            "solution_framework": [
                "根本原因分析",
                "多种方案对比",
                "实施步骤规划",
                "风险评估和缓解"
            ],
            "validation_criteria": [
                "方案的技术可行性",
                "实施的复杂度和成本",
                "预期的效果和风险"
            ]
        }