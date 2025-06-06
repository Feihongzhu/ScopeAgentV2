"""
迭代分析链 - 支持多轮对话和持续优化
"""

from typing import Dict, Any, List, Optional
from langchain.chains.base import Chain
from langchain.llms.base import BaseLLM
from langchain.callbacks.manager import CallbackManagerForChainRun

from .scope_analysis_chain import ScopeAnalysisChain
from ..models.analysis_models import IterationState, ContextInfo


class IterativeAnalysisChain(Chain):
    """迭代分析链 - 支持多轮分析和优化"""
    
    analysis_chain: ScopeAnalysisChain
    iteration_state: IterationState
    conversation_history: List[Dict[str, Any]]
    
    def __init__(self, 
                 llm: BaseLLM,
                 file_reader,
                 recommendation_tool,
                 max_iterations: int = 5,
                 **kwargs):
        """
        初始化迭代分析链
        
        Args:
            llm: 语言模型
            file_reader: 文件读取工具
            recommendation_tool: 文件推荐工具
            max_iterations: 最大迭代次数
        """
        analysis_chain = ScopeAnalysisChain(
            llm=llm,
            file_reader=file_reader,
            recommendation_tool=recommendation_tool
        )
        
        iteration_state = IterationState(max_iterations=max_iterations)
        conversation_history = []
        
        super().__init__(
            analysis_chain=analysis_chain,
            iteration_state=iteration_state,
            conversation_history=conversation_history,
            **kwargs
        )
    
    @property
    def input_keys(self) -> List[str]:
        """输入键"""
        return ["question", "user_feedback", "continue_analysis"]
    
    @property
    def output_keys(self) -> List[str]:
        """输出键"""
        return ["result", "iteration_info", "conversation_summary"]
    
    def _call(self, 
              inputs: Dict[str, Any],
              run_manager: Optional[CallbackManagerForChainRun] = None) -> Dict[str, Any]:
        """
        执行迭代分析
        
        Args:
            inputs: 输入参数
            run_manager: 回调管理器
            
        Returns:
            迭代分析结果
        """
        question = inputs["question"]
        user_feedback = inputs.get("user_feedback", "")
        continue_analysis = inputs.get("continue_analysis", False)
        
        # 如果是新问题，重置迭代状态
        if not continue_analysis:
            self.iteration_state = IterationState(max_iterations=self.iteration_state.max_iterations)
            self.conversation_history = []
        
        # 构建上下文
        context = self._build_context_from_history()
        if user_feedback:
            context["user_feedback"] = user_feedback
        
        # 执行分析
        analysis_result = self.analysis_chain.run(
            question=question,
            context=context
        )
        
        # 更新对话历史
        self.conversation_history.append({
            "question": question,
            "result": analysis_result,
            "user_feedback": user_feedback,
            "iteration": self.iteration_state.iteration_count
        })
        
        # 更新迭代状态
        self.iteration_state.increment_iteration()
        
        return {
            "result": analysis_result,
            "iteration_info": {
                "current_iteration": self.iteration_state.iteration_count,
                "max_iterations": self.iteration_state.max_iterations,
                "can_continue": self.iteration_state.can_continue(),
                "progress": self.iteration_state.analysis_progress
            },
            "conversation_summary": self._generate_conversation_summary()
        }
    
    def _build_context_from_history(self) -> Dict[str, Any]:
        """从对话历史构建上下文"""
        if not self.conversation_history:
            return {}
        
        context = {
            "previous_analyses": [],
            "user_feedbacks": [],
            "iteration_count": len(self.conversation_history)
        }
        
        for entry in self.conversation_history:
            context["previous_analyses"].append({
                "question": entry["question"],
                "problem_type": entry["result"]["problem_type"],
                "confidence": entry["result"]["confidence"]
            })
            
            if entry["user_feedback"]:
                context["user_feedbacks"].append(entry["user_feedback"])
        
        return context
    
    def _generate_conversation_summary(self) -> str:
        """生成对话摘要"""
        if not self.conversation_history:
            return "暂无对话历史"
        
        summary_parts = []
        summary_parts.append(f"已进行{len(self.conversation_history)}轮分析")
        
        # 统计问题类型
        problem_types = [entry["result"]["problem_type"] for entry in self.conversation_history]
        unique_types = list(set(problem_types))
        summary_parts.append(f"涉及问题类型: {', '.join(unique_types)}")
        
        # 平均置信度
        confidences = [entry["result"]["confidence"] for entry in self.conversation_history]
        avg_confidence = sum(confidences) / len(confidences)
        summary_parts.append(f"平均置信度: {avg_confidence:.2f}")
        
        return "；".join(summary_parts)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def reset(self):
        """重置迭代状态"""
        self.iteration_state = IterationState(max_iterations=self.iteration_state.max_iterations)
        self.conversation_history = []
    
    @property
    def _chain_type(self) -> str:
        return "iterative_analysis_chain" 