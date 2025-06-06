"""
迭代反馈处理器 - 管理分析过程中的反馈和迭代
"""

import time
from typing import Dict, List, Any, Optional
from ..models.analysis_models import ProblemType, ContextInfo


class IterativeFeedbackProcessor:
    """迭代反馈处理器"""
    
    def __init__(self, recommendation_tool):
        """
        初始化迭代反馈处理器
        
        Args:
            recommendation_tool: 推荐工具
        """
        self.recommendation_tool = recommendation_tool
        self.analysis_history = []
    
    def process_file_reading_result(self, 
                                  file_name: str,
                                  file_content: str, 
                                  problem_type: ProblemType,
                                  original_question: str,
                                  current_analysis: str) -> Dict[str, Any]:
        """
        处理文件读取结果，决定是否需要继续查看其他文件
        
        Args:
            file_name: 文件名
            file_content: 文件内容
            problem_type: 问题类型
            original_question: 原始问题
            current_analysis: 当前分析内容
            
        Returns:
            处理结果字典
        """
        # 记录已读取的文件
        self.analysis_history.append({
            "file_name": file_name,
            "content_summary": self._summarize_content(file_content),
            "timestamp": time.time()
        })
        
        # 更新当前分析状态
        updated_analysis = current_analysis + f"\n\n[文件{file_name}信息]:\n{file_content}"
        
        # 评估信息充足性
        info_sufficiency = self._evaluate_information_sufficiency(
            problem_type, updated_analysis, original_question
        )
        
        analysis_result = {
            "information_sufficient": info_sufficiency["sufficient"],
            "sufficiency_score": info_sufficiency["score"],
            "missing_aspects": info_sufficiency["missing"],
            "next_files_needed": [],
            "analysis_progress": self._calculate_progress(problem_type, updated_analysis),
            "key_findings": self._extract_key_findings(file_content, problem_type)
        }
        
        # 如果信息不充足，推荐下一批文件
        if not info_sufficiency["sufficient"]:
            context = ContextInfo(
                problem_type=problem_type,
                user_input=original_question,
                current_analysis=updated_analysis,
                files_read=[item["file_name"] for item in self.analysis_history]
            )
            
            next_recommendations = self.recommendation_tool.recommend_files(
                problem_type, context, updated_analysis
            )
            
            # 过滤掉已读取的文件
            read_files = [item["file_name"] for item in self.analysis_history]
            filtered_recommendations = [
                rec for rec in next_recommendations 
                if rec.file_name not in read_files
            ]
            
            analysis_result["next_files_needed"] = filtered_recommendations[:3]  # 限制推荐数量
        
        return analysis_result
    
    def _summarize_content(self, content: str, max_length: int = 100) -> str:
        """总结文件内容"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    def _evaluate_information_sufficiency(self, problem_type: ProblemType, 
                                        analysis: str, question: str) -> Dict[str, Any]:
        """评估当前信息是否充足以回答问题"""
        sufficiency_criteria = {
            ProblemType.DATA_SKEW: {
                "required_info": [
                    "用户脚本逻辑", "Join操作", "数据分布", "性能指标"
                ],
                "min_score": 0.7
            },
            ProblemType.EXCESSIVE_SHUFFLE: {
                "required_info": [
                    "用户脚本逻辑", "Shuffle操作", "Stage信息", "数据流"
                ],
                "min_score": 0.7
            },
            ProblemType.OTHER: {
                "required_info": ["用户脚本逻辑", "错误信息"],
                "min_score": 0.5
            }
        }
        
        criteria = sufficiency_criteria.get(problem_type, {"required_info": [], "min_score": 0.5})
        present_info = []
        missing_info = []
        
        for info_type in criteria["required_info"]:
            if self._is_info_present(info_type, analysis):
                present_info.append(info_type)
            else:
                missing_info.append(info_type)
        
        score = len(present_info) / len(criteria["required_info"]) if criteria["required_info"] else 1.0
        sufficient = score >= criteria["min_score"]
        
        return {
            "sufficient": sufficient,
            "score": score,
            "present": present_info,
            "missing": missing_info
        }
    
    def _is_info_present(self, info_type: str, analysis: str) -> bool:
        """检查特定类型的信息是否已包含在分析中"""
        info_keywords = {
            "用户脚本逻辑": ["def ", "class ", "import", "脚本"],
            "Join操作": ["join", "连接", "关联"],
            "数据分布": ["分布", "倾斜", "热点", "统计"],
            "Stage信息": ["stage", "阶段", "执行"],
            "Shuffle操作": ["shuffle", "重分区", "数据传输"],
            "性能指标": ["时间", "延迟", "耗时", "性能"],
            "错误信息": ["错误", "异常", "error", "exception"]
        }
        
        keywords = info_keywords.get(info_type, [])
        analysis_lower = analysis.lower()
        return any(keyword.lower() in analysis_lower for keyword in keywords)
    
    def _calculate_progress(self, problem_type: ProblemType, analysis: str) -> float:
        """计算分析进度"""
        total_aspects = {
            ProblemType.DATA_SKEW: ["脚本理解", "问题定位", "原因分析", "解决方案"],
            ProblemType.EXCESSIVE_SHUFFLE: ["脚本理解", "Shuffle识别", "性能分析", "优化建议"],
            ProblemType.OTHER: ["基本分析", "问题识别", "建议方案"]
        }
        
        aspects = total_aspects.get(problem_type, ["基本分析"])
        completed = sum(1 for aspect in aspects if self._aspect_completed(aspect, analysis))
        
        return completed / len(aspects)
    
    def _aspect_completed(self, aspect: str, analysis: str) -> bool:
        """检查某个分析方面是否已完成"""
        aspect_keywords = {
            "脚本理解": ["脚本", "代码", "逻辑"],
            "问题定位": ["问题", "瓶颈", "issue"],
            "原因分析": ["原因", "分析", "因为"],
            "解决方案": ["解决", "建议", "优化"],
            "Shuffle识别": ["shuffle", "重分区"],
            "性能分析": ["性能", "耗时", "延迟"],
            "优化建议": ["优化", "改进", "建议"],
            "基本分析": ["分析", "问题"]
        }
        
        keywords = aspect_keywords.get(aspect, [])
        analysis_lower = analysis.lower()
        return any(keyword in analysis_lower for keyword in keywords)
    
    def _extract_key_findings(self, file_content: str, problem_type: ProblemType) -> List[str]:
        """从文件内容中提取关键发现"""
        findings = []
        content_lower = file_content.lower()
        
        # 基于问题类型提取不同的关键信息
        if problem_type == ProblemType.DATA_SKEW:
            if "join" in content_lower:
                findings.append("发现Join操作")
            if any(word in content_lower for word in ["倾斜", "热点", "不均匀"]):
                findings.append("检测到数据分布问题")
        
        elif problem_type == ProblemType.EXCESSIVE_SHUFFLE:
            if any(word in content_lower for word in ["shuffle", "重分区"]):
                findings.append("发现Shuffle操作")
            if "stage" in content_lower:
                findings.append("获取到Stage运行信息")
        
        return findings
    
    def get_analysis_summary(self) -> str:
        """获取分析过程摘要"""
        if not self.analysis_history:
            return "尚未读取任何文件"
        
        summary = f"已读取{len(self.analysis_history)}个文件：\n"
        for item in self.analysis_history:
            summary += f"- {item['file_name']}: {item['content_summary']}\n"
        
        return summary

    def process_iteration(self, analysis_result: str) -> Dict[str, Any]:
        """处理一次迭代的结果"""
        return {
            "continue": True,
            "next_action": "analyze"
        } 