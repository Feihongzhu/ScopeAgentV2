"""
系统配置文件
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings


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
    
    # 文件类型优先级设置
    high_priority_files: List[str] = [
        "scope.script",  # 原始脚本
        "Error",  # 错误信息
        "JobStatistics.xml",  # 作业统计
        "__Warnings__.xml",  # 警告信息
        "Algebra.xml"  # 执行计划
    ]
    
    medium_priority_files: List[str] = [
        "JobInfo.xml",
        "__ScopeRuntimeStatistics__.xml", 
        "__DataMapDfg__.json",
        "diagnosticsjson"
    ]
    
    # 文件大小限制（按文件类型）
    file_size_limits: Dict[str, int] = {
        "__ScopeCodeGen__.dll": 50 * 1024 * 1024,  # 50MB
        "__ScopeCodeGen__.dll.cs": 10 * 1024 * 1024,  # 10MB
        "profile": 20 * 1024 * 1024,  # 20MB  
        "default": 5 * 1024 * 1024  # 5MB默认限制
    }
    
    # 默认文件映射 - 基于实际Cosmos SCOPE Job文件结构
    default_file_mapping: Dict[str, str] = {
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
    
    # 默认解析器映射 - 基于实际Cosmos SCOPE Job文件结构
    default_parser_mapping: Dict[str, str] = {
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
        "scope.script": "parse_scope_script",
        
        # 性能分析文件解析器
        "profile": "parse_profile_data",
        
        # 错误文件解析器
        "Error": "parse_error_file"
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略额外的环境变量
    
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