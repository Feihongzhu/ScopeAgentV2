"""
系统配置文件
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseSettings, Field


class ScopeAgentSettings(BaseSettings):
    """ScopeAgent配置类"""
    
    # 基础设置
    app_name: str = "ScopeAgentV2"
    version: str = "2.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # 文件路径设置
    data_path: str = Field(default="./data", env="DATA_PATH")
    log_path: str = Field(default="./logs", env="LOG_PATH")
    knowledge_path: str = Field(default="./data/knowledge", env="KNOWLEDGE_PATH")
    
    # LLM设置
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    # Agent设置
    max_iterations: int = Field(default=5, env="MAX_ITERATIONS")
    max_files_per_iteration: int = Field(default=3, env="MAX_FILES_PER_ITERATION")
    file_size_limit: int = Field(default=10000, env="FILE_SIZE_LIMIT")  # bytes
    
    # 分析设置
    confidence_threshold: float = Field(default=0.7, env="CONFIDENCE_THRESHOLD")
    relevance_threshold: float = Field(default=0.3, env="RELEVANCE_THRESHOLD")
    
    # 默认文件映射
    default_file_mapping: Dict[str, str] = {
        "user_script.txt": "用户提交的原始SCOPE脚本代码",
        "dag_stages.log": "DAG中每个stage的运行情况和性能数据", 
        "data_skew_report.json": "数据倾斜统计分析报告",
        "shuffle_stats.log": "Shuffle操作的性能统计日志",
        "join_analysis.txt": "Join操作的详细分析结果",
        "config.properties": "作业运行的配置参数设置",
        "error.log": "作业运行过程中的错误和异常日志",
        "performance_metrics.json": "整体性能指标和监控数据"
    }
    
    # 默认解析器映射
    default_parser_mapping: Dict[str, str] = {
        "dag_stages.log": "parse_dag_stages",
        "data_skew_report.json": "parse_skew_report", 
        "shuffle_stats.log": "parse_shuffle_stats",
        "performance_metrics.json": "parse_performance_metrics"
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_data_path(self) -> Path:
        """获取数据路径"""
        return Path(self.data_path)
    
    def get_log_path(self) -> Path:
        """获取日志路径"""
        return Path(self.log_path)
    
    def get_knowledge_path(self) -> Path:
        """获取知识库路径"""
        return Path(self.knowledge_path)
    
    def ensure_directories(self):
        """确保所需目录存在"""
        for path in [self.get_data_path(), self.get_log_path(), self.get_knowledge_path()]:
            path.mkdir(parents=True, exist_ok=True)


class LLMConfig:
    """LLM配置类"""
    
    SUPPORTED_PROVIDERS = {
        "openai": {
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "default_model": "gpt-4"
        },
        "anthropic": {
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "default_model": "claude-3-opus"
        },
        "qwen": {
            "models": ["qwen-2.5-72b", "qwen-2.5-32b"],
            "default_model": "qwen-2.5-72b"
        },
        "deepseek": {
            "models": ["deepseek-chat", "deepseek-coder"],
            "default_model": "deepseek-chat"
        }
    }
    
    @classmethod
    def get_supported_models(cls, provider: str) -> List[str]:
        """获取支持的模型列表"""
        return cls.SUPPORTED_PROVIDERS.get(provider, {}).get("models", [])
    
    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """获取默认模型"""
        return cls.SUPPORTED_PROVIDERS.get(provider, {}).get("default_model", "")


# 全局设置实例
settings = ScopeAgentSettings()

# 确保目录存在
settings.ensure_directories() 