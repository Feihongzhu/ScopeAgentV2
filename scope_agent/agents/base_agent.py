"""
基础Agent类 - 定义Agent的通用接口和方法
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain.llms.base import BaseLLM


class BaseThinkAgent(ABC):
    """基础思考Agent抽象类"""
    
    def __init__(self, llm: BaseLLM, max_iterations: int = 5):
        """
        初始化基础Agent
        
        Args:
            llm: 语言模型
            max_iterations: 最大迭代次数
        """
        self.llm = llm
        self.max_iterations = max_iterations
        self.analysis_history = []
    
    @abstractmethod
    def analyze(self, user_question: str, context_info: Optional[Dict] = None) -> Any:
        """
        分析方法 - 子类必须实现
        
        Args:
            user_question: 用户问题
            context_info: 上下文信息
            
        Returns:
            分析结果
        """
        pass
    
    def get_analysis_history(self) -> list:
        """获取分析历史"""
        return self.analysis_history.copy()
    
    def clear_history(self):
        """清空分析历史"""
        self.analysis_history.clear()
    
    def add_to_history(self, analysis_result: Any):
        """添加分析结果到历史"""
        self.analysis_history.append(analysis_result) 