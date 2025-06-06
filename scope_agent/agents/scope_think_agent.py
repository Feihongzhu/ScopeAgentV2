"""
ScopeThinkAgent - 核心分析Agent
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain.llms.base import BaseLLM
from langchain.chains import LLMChain

from ..models.analysis_models import (
    ProblemType, ThinkStep, AnalysisResult, ContextInfo, 
    IterationState, ThinkStepResult
)
from ..prompts.main_think_prompt import MainThinkPromptTemplate
from ..tools.file_reader import FileReaderTool, SmartFileReader
from ..tools.file_recommendation import FileRecommendationTool
from ..tools.iterative_feedback import IterativeFeedbackProcessor
from .base_agent import BaseThinkAgent


class ScopeThinkAgent(BaseThinkAgent):
    """SCOPE作业分析的智能Agent"""
    
    def __init__(self, 
                 llm: BaseLLM,
                 file_reader: FileReaderTool,
                 recommendation_tool: FileRecommendationTool,
                 max_iterations: int = 5):
        """
        初始化ScopeThinkAgent
        
        Args:
            llm: 语言模型
            file_reader: 文件读取工具
            recommendation_tool: 文件推荐工具
            max_iterations: 最大迭代次数
        """
        super().__init__(llm, max_iterations)
        
        self.file_reader = file_reader
        self.recommendation_tool = recommendation_tool
        self.smart_reader = SmartFileReader(file_reader, recommendation_tool)
        self.feedback_processor = IterativeFeedbackProcessor(recommendation_tool)
        
        # 初始化Prompt模板
        self.main_prompt = MainThinkPromptTemplate()
        
        # 初始化LLM链
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.main_prompt.prompt,
            verbose=True
        )
        
    def analyze(self, user_question: str, context_info: Optional[Dict] = None) -> AnalysisResult:
        """
        主要分析方法
        
        Args:
            user_question: 用户问题
            context_info: 额外上下文信息
            
        Returns:
            分析结果
        """
        start_time = time.time()
        
        # 初始化上下文
        context = ContextInfo(
            user_input=user_question,
            current_analysis="",
            files_read=[],
            key_findings=[]
        )
        
        # 初始化迭代状态
        iteration_state = IterationState(max_iterations=self.max_iterations)
        
        think_results = []
        files_analyzed = []
        
        try:
            # 迭代分析过程
            while iteration_state.can_continue():
                iteration_state.increment_iteration()
                
                # 构造当前分析的输入
                analysis_input = self._build_analysis_input(
                    user_question, context, iteration_state
                )
                
                # 执行LLM分析
                response = self.analysis_chain.run(analysis_input)
                
                # 解析分析结果
                step_results = self._parse_think_steps(response)
                think_results.extend(step_results)
                
                # 更新上下文
                context.current_analysis += f"\n\n=== 迭代 {iteration_state.iteration_count} ===\n{response}"
                
                # 检查是否需要读取更多文件
                think4_result = self._get_step_result(step_results, ThinkStep.INFO_COMPLETENESS)
                
                if think4_result and think4_result.needs_more_info:
                    # 智能读取文件
                    read_result = self._smart_read_files(
                        context, iteration_state, think4_result
                    )
                    
                    if read_result["success"]:
                        files_analyzed.extend(read_result["files_read"])
                        context.files_read.extend(read_result["files_read"])
                        context.current_analysis += f"\n\n=== 文件内容 ===\n{read_result['content']}"
                    else:
                        # 如果无法读取更多文件，则停止迭代
                        iteration_state.information_sufficient = True
                else:
                    # 如果不需要更多信息，则结束迭代
                    iteration_state.information_sufficient = True
            
            # 提取最终解决方案
            final_solution = self._extract_final_solution(think_results)
            
            # 确定问题类型
            problem_type = self._determine_problem_type(think_results)
            
            # 计算置信度
            confidence_score = self._calculate_confidence(think_results, iteration_state)
            
        except Exception as e:
            # 错误处理
            final_solution = f"分析过程中发生错误: {str(e)}"
            problem_type = ProblemType.OTHER
            confidence_score = 0.0
        
        processing_time = time.time() - start_time
        
        return AnalysisResult(
            problem_type=problem_type,
            think_steps=think_results,
            final_solution=final_solution,
            confidence_score=confidence_score,
            files_analyzed=files_analyzed,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    def _build_analysis_input(self, user_question: str, context: ContextInfo, 
                             iteration_state: IterationState) -> Dict[str, Any]:
        """构建分析输入"""
        return {
            "user_question": user_question,
            "context_info": self._format_context_info(context),
            "retrieved_experience": self._get_relevant_experience(user_question, context),
            "files_content": self._format_files_content(context),
            "problem_type": context.problem_type.value if context.problem_type else "未确定",
            "components": ", ".join(context.key_findings),
            "user_description": user_question
        }
    
    def _format_context_info(self, context: ContextInfo) -> str:
        """格式化上下文信息"""
        info_parts = []
        
        if context.problem_type:
            info_parts.append(f"问题类型: {context.problem_type.value}")
        
        if context.files_read:
            info_parts.append(f"已读取文件: {', '.join(context.files_read)}")
        
        if context.key_findings:
            info_parts.append(f"关键发现: {'; '.join(context.key_findings)}")
        
        return "\n".join(info_parts) if info_parts else "暂无上下文信息"
    
    def _get_relevant_experience(self, question: str, context: ContextInfo) -> str:
        """获取相关经验知识（简化实现）"""
        # 这里可以接入RAG系统或知识库
        base_experience = """
        [数据倾斜优化经验]
        1. 使用PartitionBy合理重新分区
        2. 热点键单独处理或加随机盐值
        3. 避免过度集中的Join键
        
        [Shuffle优化经验]
        1. 合理利用PartitionBy减少重复Shuffle
        2. 提前投影减少数据规模
        3. 避免多次全网重分布
        4. 使用广播Join处理小表
        """
        return base_experience
    
    def _format_files_content(self, context: ContextInfo) -> str:
        """格式化文件内容"""
        if not context.current_analysis:
            return "暂无文件内容"
        
        # 提取文件相关部分
        parts = context.current_analysis.split("=== 文件内容 ===")
        if len(parts) > 1:
            return parts[-1]
        return "暂无文件内容"
    
    def _parse_think_steps(self, response: str) -> List[ThinkStepResult]:
        """解析思考步骤结果"""
        steps = []
        
        # 简化的解析逻辑，实际可以更复杂
        for i, step in enumerate(ThinkStep):
            step_marker = f"[{step.value}]"
            if step_marker in response:
                # 提取该步骤的内容
                start_idx = response.find(step_marker)
                
                # 寻找下一个步骤的开始，如果没有则到结尾
                next_step_idx = len(response)
                for j, next_step in enumerate(list(ThinkStep)[i+1:], i+1):
                    next_marker = f"[{next_step.value}]"
                    if next_marker in response:
                        next_step_idx = response.find(next_marker)
                        break
                
                content = response[start_idx:next_step_idx].strip()
                
                # 检查是否需要更多信息
                needs_more_info = "需要文件" in content and "是" in content
                
                step_result = ThinkStepResult(
                    step=step,
                    content=content,
                    confidence=self._estimate_step_confidence(content),
                    needs_more_info=needs_more_info
                )
                
                steps.append(step_result)
        
        return steps
    
    def _smart_read_files(self, context: ContextInfo, iteration_state: IterationState,
                         think4_result: ThinkStepResult) -> Dict[str, Any]:
        """智能读取文件"""
        try:
            # 使用智能文件读取器
            read_result = self.smart_reader.smart_read(
                problem_type=context.problem_type or ProblemType.OTHER,
                context=context,
                current_analysis=context.current_analysis,
                max_files=3
            )
            
            return read_result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"文件读取失败: {str(e)}",
                "files_read": [],
                "content": ""
            }
    
    def _get_step_result(self, step_results: List[ThinkStepResult], 
                        target_step: ThinkStep) -> Optional[ThinkStepResult]:
        """获取特定步骤的结果"""
        for result in step_results:
            if result.step == target_step:
                return result
        return None
    
    def _extract_final_solution(self, think_results: List[ThinkStepResult]) -> str:
        """提取最终解决方案"""
        think5_result = self._get_step_result(think_results, ThinkStep.FINAL_SOLUTION)
        if think5_result:
            return think5_result.content
        
        # 如果没有THINK 5，则汇总其他步骤
        solution_parts = []
        for result in think_results:
            if result.step in [ThinkStep.EXPERIENCE_ANALYSIS, ThinkStep.CODE_ANALYSIS]:
                solution_parts.append(f"{result.step.value}: {result.content[:200]}...")
        
        return "\n\n".join(solution_parts) if solution_parts else "无法生成解决方案"
    
    def _determine_problem_type(self, think_results: List[ThinkStepResult]) -> ProblemType:
        """确定问题类型"""
        think1_result = self._get_step_result(think_results, ThinkStep.PROBLEM_CLASSIFICATION)
        if think1_result:
            content = think1_result.content.lower()
            if "数据倾斜" in content:
                return ProblemType.DATA_SKEW
            elif "shuffle" in content or "重分布" in content:
                return ProblemType.EXCESSIVE_SHUFFLE
        
        return ProblemType.OTHER
    
    def _calculate_confidence(self, think_results: List[ThinkStepResult], 
                            iteration_state: IterationState) -> float:
        """计算置信度"""
        if not think_results:
            return 0.0
        
        # 基于步骤完整性和内容质量计算
        step_scores = [result.confidence for result in think_results]
        base_confidence = sum(step_scores) / len(step_scores)
        
        # 根据迭代次数调整
        iteration_penalty = (iteration_state.iteration_count - 1) * 0.1
        
        return max(0.0, min(1.0, base_confidence - iteration_penalty))
    
    def _estimate_step_confidence(self, content: str) -> float:
        """估算单个步骤的置信度"""
        # 基于内容长度和关键词估算
        if len(content) < 50:
            return 0.3
        elif len(content) < 200:
            return 0.6
        else:
            return 0.8 