"""
文件读取工具 - 支持普通文件读取和特殊格式解析
"""

import os
import json
from typing import Dict, Any, Optional, List
from langchain.tools import Tool
from ..parsers import get_parser_function


class FileReaderTool:
    """文件读取工具类"""
    
    def __init__(self, base_path: str = "./data", parser_mapping: Dict[str, str] = None):
        """
        初始化文件读取工具
        
        Args:
            base_path: 文件基础路径
            parser_mapping: 文件到解析器的映射
        """
        self.base_path = base_path
        self.parser_mapping = parser_mapping or {}
        self.read_history = []  # 读取历史记录
    
    def read_files(self, filenames: List[str]) -> str:
        """
        读取多个文件的内容
        
        Args:
            filenames: 文件名列表
            
        Returns:
            合并的文件内容
        """
        contents = []
        
        for filename in filenames:
            try:
                content = self.read_single_file(filename)
                if content:
                    contents.append(f"=== 文件: {filename} ===\n{content}\n")
                    self.read_history.append(filename)
            except Exception as e:
                contents.append(f"=== 文件: {filename} ===\n读取失败: {str(e)}\n")
        
        return "\n".join(contents)
    
    def read_single_file(self, filename: str) -> str:
        """
        读取单个文件
        
        Args:
            filename: 文件名
            
        Returns:
            文件内容
        """
        file_path = os.path.join(self.base_path, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"文件 {filename} 不存在"
        
        # 检查是否需要特殊解析
        if filename in self.parser_mapping:
            parser_name = self.parser_mapping[filename]
            parser_func = get_parser_function(parser_name)
            if parser_func:
                return parser_func(file_path)
        
        # 普通文件读取
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 如果文件太大，进行截断
            if len(content) > 10000:  # 10KB限制
                content = content[:10000] + "\n\n... (文件内容已截断，如需完整内容请使用专门的解析器) ..."
            
            return content
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                return content[:10000] if len(content) > 10000 else content
            except:
                return f"无法读取文件 {filename}，编码格式不支持"
        except Exception as e:
            return f"读取文件 {filename} 时发生错误: {str(e)}"
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            filename: 文件名
            
        Returns:
            文件信息字典
        """
        file_path = os.path.join(self.base_path, filename)
        
        if not os.path.exists(file_path):
            return {"exists": False, "error": "文件不存在"}
        
        try:
            stat = os.stat(file_path)
            return {
                "exists": True,
                "size": stat.st_size,
                "modified_time": stat.st_mtime,
                "is_file": os.path.isfile(file_path),
                "requires_parser": filename in self.parser_mapping,
                "parser": self.parser_mapping.get(filename)
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}
    
    def list_available_files(self) -> List[str]:
        """列出可用的文件"""
        try:
            if not os.path.exists(self.base_path):
                return []
            
            files = []
            for item in os.listdir(self.base_path):
                item_path = os.path.join(self.base_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
            return sorted(files)
        except Exception:
            return []
    
    def get_read_history(self) -> List[str]:
        """获取读取历史"""
        return self.read_history.copy()
    
    def clear_read_history(self):
        """清空读取历史"""
        self.read_history.clear()
    
    def create_langchain_tool(self) -> Tool:
        """创建LangChain工具"""
        return Tool(
            name="ReadRelevantCodeFiles",
            func=self.read_files,
            description="读取相关文件以完善上下文分析。输入应该是文件名列表，用逗号分隔。"
        )


class SmartFileReader:
    """智能文件读取器，结合文件推荐功能"""
    
    def __init__(self, file_reader: FileReaderTool, recommendation_tool):
        self.file_reader = file_reader
        self.recommendation_tool = recommendation_tool
    
    def smart_read(self, problem_type, context, current_analysis: str, max_files: int = 3) -> Dict[str, Any]:
        """
        智能读取文件
        
        Args:
            problem_type: 问题类型
            context: 上下文信息
            current_analysis: 当前分析内容
            max_files: 最大读取文件数
            
        Returns:
            读取结果字典
        """
        # 获取文件推荐
        recommendations = self.recommendation_tool.recommend_files(
            problem_type, context, current_analysis
        )
        
        if not recommendations:
            return {
                "success": False,
                "message": "没有找到相关文件",
                "files_read": [],
                "content": ""
            }
        
        # 选择前N个文件
        selected_files = [rec.file_name for rec in recommendations[:max_files]]
        
        # 读取文件
        content = self.file_reader.read_files(selected_files)
        
        return {
            "success": True,
            "message": f"成功读取 {len(selected_files)} 个文件",
            "files_read": selected_files,
            "content": content,
            "recommendations": recommendations[:max_files]
        } 