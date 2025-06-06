"""
ScopeAgentV2 - AI 作业优化 Agent

一个基于 LangChain 的智能系统，用于分析和优化 SCOPE 作业性能问题。
主要功能包括数据倾斜分析、Shuffle 优化、代码重写建议等。
"""

__version__ = "2.0.0"
__author__ = "ScopeAgent Team"

from .agents import ScopeThinkAgent
from .tools import FileReaderTool, FileRecommendationTool
from .chains import ScopeAnalysisChain

__all__ = [
    "ScopeThinkAgent",
    "FileReaderTool", 
    "FileRecommendationTool",
    "ScopeAnalysisChain"
] 