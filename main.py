"""
ScopeAgentV2 主程序入口
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_community.llms import OpenAI
from scope_agent import ScopeThinkAgent
from scope_agent.tools.file_reader import FileReaderTool
from scope_agent.tools.file_recommendation import FileRecommendationTool, DEFAULT_FILE_MAPPING, DEFAULT_PARSER_MAPPING
from config.settings import settings


def create_sample_data():
    """创建示例数据文件"""
    data_path = settings.get_data_path()
    
    # 创建示例用户脚本
    script_content = """
// 示例SCOPE脚本
data1 = EXTRACT FROM "table1.txt" 
        USING DefaultTextExtractor;

data2 = EXTRACT FROM "table2.txt"
        USING DefaultTextExtractor;

joined_data = SELECT *
              FROM data1 AS a
              JOIN data2 AS b
              ON a.key == b.key;

OUTPUT joined_data TO "output.txt"
USING DefaultTextOutputter;
"""
    
    with open(data_path / "user_script.txt", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 创建示例DAG日志
    dag_log = """
Stage 1: Extract data1 - running - 10s
Stage 2: Extract data2 - running - 15s  
Stage 3: Join operation - running - 120s
Stage 4: Output - completed - 5s
"""
    
    with open(data_path / "dag_stages.log", "w", encoding="utf-8") as f:
        f.write(dag_log)
    
    print(f"示例数据已创建在: {data_path}")


def main():
    """主函数"""
    print("=== ScopeAgentV2 启动 ===")
    print(f"版本: {settings.version}")
    print(f"数据路径: {settings.get_data_path()}")
    
    # 创建示例数据
    create_sample_data()
    
    # 初始化LLM（这里使用OpenAI作为示例）
    # 注意：需要设置OPENAI_API_KEY环境变量
    if not settings.openai_api_key:
        print("警告: 未设置OPENAI_API_KEY，请在.env文件中配置")
        print("示例配置:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("LLM_PROVIDER=openai")
        print("LLM_MODEL=gpt-4")
        return
    
    try:
        llm = OpenAI(
            openai_api_key=settings.openai_api_key,
            model_name=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
        
        # 初始化工具
        file_reader = FileReaderTool(
            base_path=str(settings.get_data_path()),
            parser_mapping=settings.default_parser_mapping
        )
        
        recommendation_tool = FileRecommendationTool(
            file_content_mapping=settings.default_file_mapping,
            parser_functions=settings.default_parser_mapping
        )
        
        # 初始化Agent
        agent = ScopeThinkAgent(
            llm=llm,
            file_reader=file_reader,
            recommendation_tool=recommendation_tool,
            max_iterations=settings.max_iterations
        )
        
        print("\n=== Agent初始化完成 ===")
        
        # 示例问题
        test_questions = [
            "我的SCOPE作业运行很慢，Join操作耗时特别长，可能是什么原因？",
            "作业中出现了大量的Shuffle操作，如何优化？",
            "数据处理过程中某些分区的数据量特别大，其他分区很小，怎么解决？"
        ]
        
        print("\n=== 开始分析测试 ===")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- 测试问题 {i} ---")
            print(f"问题: {question}")
            
            try:
                # 执行分析
                result = agent.analyze(question)
                
                print(f"问题类型: {result.problem_type.value}")
                print(f"置信度: {result.confidence_score:.2f}")
                print(f"处理时间: {result.processing_time:.2f}秒")
                print(f"分析的文件: {', '.join(result.files_analyzed)}")
                print(f"解决方案摘要: {result.final_solution[:200]}...")
                
            except Exception as e:
                print(f"分析失败: {str(e)}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        print("请检查API密钥和网络连接")


if __name__ == "__main__":
    main() 