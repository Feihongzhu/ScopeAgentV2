"""
SCOPE分析链 - 组合各种组件形成完整的分析流程
"""

from typing import Dict, Any, List, Optional
from langchain.chains.base import Chain
from langchain.llms.base import BaseLLM
from langchain.callbacks.manager import CallbackManagerForChainRun

from ..agents.scope_think_agent import ScopeThinkAgent
from ..tools.file_reader import FileReaderTool
from ..tools.file_recommendation import FileRecommendationTool
from ..models.analysis_models import AnalysisResult, ProblemType


class ScopeAnalysisChain(Chain):
    """SCOPE分析链"""
    
    agent: ScopeThinkAgent
    
    def __init__(self, 
                 llm: BaseLLM,
                 file_reader: FileReaderTool,
                 recommendation_tool: FileRecommendationTool,
                 **kwargs):
        """
        初始化分析链
        
        Args:
            llm: 语言模型
            file_reader: 文件读取工具
            recommendation_tool: 文件推荐工具
        """
        # 创建Agent
        agent = ScopeThinkAgent(
            llm=llm,
            file_reader=file_reader,
            recommendation_tool=recommendation_tool
        )
        
        super().__init__(agent=agent, **kwargs)
    
    @property
    def input_keys(self) -> List[str]:
        """输入键"""
        return ["question", "context"]
    
    @property
    def output_keys(self) -> List[str]:
        """输出键"""
        return ["result", "problem_type", "confidence", "solution"]
    
    def _call(self, 
              inputs: Dict[str, Any],
              run_manager: Optional[CallbackManagerForChainRun] = None) -> Dict[str, Any]:
        """
        执行分析链
        
        Args:
            inputs: 输入参数
            run_manager: 回调管理器
            
        Returns:
            分析结果
        """
        question = inputs["question"]
        context = inputs.get("context", {})
        
        # 执行分析
        result = self.agent.analyze(question, context)
        
        return {
            "result": result,
            "problem_type": result.problem_type.value,
            "confidence": result.confidence_score,
            "solution": result.final_solution,
            "files_analyzed": result.files_analyzed,
            "processing_time": result.processing_time
        }
    
    @property
    def _chain_type(self) -> str:
        return "scope_analysis_chain" 