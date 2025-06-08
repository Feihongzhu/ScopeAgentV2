"""
ScopeAgentV2 主程序入口
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_openai import ChatOpenAI
from src import ScopeThinkAgent
from src.tools.file_reader import FileReaderTool
from src.tools.file_recommendation import FileRecommendationTool, DEFAULT_FILE_MAPPING, DEFAULT_PARSER_MAPPING
from src.models.analysis_models import ScopeFileType
from config.settings import settings


def scan_scope_jobs():
    """扫描并返回可用的SCOPE Job目录"""
    jobs_path = settings.get_data_path() / "scope_jobs"
    
    if not jobs_path.exists():
        print(f"SCOPE Jobs目录不存在: {jobs_path}")
        return []
    
    job_dirs = []
    for item in jobs_path.iterdir():
        if item.is_dir():
            job_dirs.append(item)
    
    return sorted(job_dirs)


def analyze_job_structure(job_path):
    """分析Job目录结构，识别可用的文件"""
    available_files = {}
    
    # 检查我们配置的文件类型
    file_mappings = {
        # 使用实际文件名映射到我们的配置
        "request.script": ScopeFileType.SCOPE_SCRIPT,
        "scope.script": ScopeFileType.SCOPE_SCRIPT,
        "NebulaCommandLine.txt": ScopeFileType.COMMAND_LINE,
        "JobInfo.xml": ScopeFileType.JOB_INFO,
        "JobStatistics.xml": ScopeFileType.JOB_STATISTICS,
        "JobAnalysisResult.xml": ScopeFileType.JOB_STATISTICS,  # 使用相同解析器
        "ScopeVertexDef.xml": ScopeFileType.VERTEX_DEF,
        "__DataMapDfg__.json": ScopeFileType.DATA_FLOW_GRAPH,
        "__Warnings__.xml": ScopeFileType.WARNINGS,
        "__CompilerTimers.xml": ScopeFileType.COMPILER_TIMERS,
        "__ScopeCodeGenCompileOutput__.txt": ScopeFileType.COMPILE_OUTPUT,
        "__SStreamInfo__.xml": ScopeFileType.STREAM_INFO,
        "diagnosticsjson": ScopeFileType.DIAGNOSTICS,
        "profile": ScopeFileType.PROFILE,
        "Error": ScopeFileType.ERROR_LOG
    }
    
    print(f"\n=== 分析Job目录: {job_path.name} ===")
    
    for file_path in job_path.iterdir():
        if file_path.is_file():
            file_name = file_path.name
            if file_name in file_mappings:
                file_type = file_mappings[file_name]
                available_files[file_name] = {
                    'path': file_path,
                    'type': file_type,
                    'size': file_path.stat().st_size
                }
                
                # 格式化文件大小
                size = file_path.stat().st_size
                if size > 1024*1024:
                    size_str = f"{size/(1024*1024):.1f}MB"
                elif size > 1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                    
                print(f"  ✓ {file_name} ({size_str})")
    
    print(f"共发现 {len(available_files)} 个可分析文件")
    return available_files


def select_job():
    """选择要分析的Job"""
    job_dirs = scan_scope_jobs()
    
    if not job_dirs:
        print("未找到任何SCOPE Job目录")
        return None
    
    if len(job_dirs) == 1:
        print(f"发现1个Job: {job_dirs[0].name}")
        return job_dirs[0]
    
    print(f"发现 {len(job_dirs)} 个Job:")
    for i, job_dir in enumerate(job_dirs, 1):
        print(f"  {i}. {job_dir.name}")
    
    while True:
        try:
            choice = input(f"请选择要分析的Job (1-{len(job_dirs)}): ")
            index = int(choice) - 1
            if 0 <= index < len(job_dirs):
                return job_dirs[index]
            else:
                print("无效选择，请重新输入")
        except ValueError:
            print("请输入数字")
        except KeyboardInterrupt:
            print("\n用户取消")
            return None


def main():
    """主函数"""
    print("=== ScopeAgentV2 启动 ===")
    print(f"版本: {settings.version}")
    print(f"数据路径: {settings.get_data_path()}")
    
    # 选择要分析的Job
    selected_job = select_job()
    if not selected_job:
        print("未选择Job，程序退出")
        return
    
    # 分析Job结构
    available_files = analyze_job_structure(selected_job)
    if not available_files:
        print("该Job目录中没有可分析的文件")
        return
    
    # 初始化LLM（这里使用OpenAI作为示例）
    # 注意：需要设置OPENAI_API_KEY环境变量
    if not settings.openai_api_key:
        print("\n警告: 未设置OPENAI_API_KEY，请在.env文件中配置")
        print("示例配置:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("LLM_PROVIDER=openai")
        print("LLM_MODEL=gpt-4")
        return
    
    try:
        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
        
        # 初始化工具 - 使用选中的Job目录
        file_reader = FileReaderTool(
            base_path=str(selected_job),
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
        
        print(f"\n=== Agent初始化完成 ===")
        print(f"正在分析Job: {selected_job.name}")
        
        # 交互式分析模式
        print("\n=== 交互式分析模式 ===")
        print("您可以询问关于这个SCOPE Job的任何问题。")
        print("输入 'quit' 或 'exit' 退出程序")
        print("输入 'files' 查看可用文件")
        print("输入 'demo' 运行演示问题")
        
        while True:
            try:
                user_input = input("\n请输入您的问题: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                elif user_input.lower() == 'files':
                    print("\n可用文件:")
                    for file_name, info in available_files.items():
                        size_str = f"{info['size']/(1024*1024):.1f}MB" if info['size'] > 1024*1024 else f"{info['size']/1024:.1f}KB"
                        print(f"  ✓ {file_name} ({size_str}) - {info['type'].value}")
                    continue
                elif user_input.lower() == 'demo':
                    # 运行演示问题
                    demo_questions = [
                        "这个作业的执行时间如何？有性能问题吗？",
                        "是否存在数据倾斜问题？",
                        "有哪些编译警告或运行时警告？",
                        "作业的资源使用情况如何？"
                    ]
                    
                    for question in demo_questions:
                        print(f"\n🤖 演示问题: {question}")
                        try:
                            result = agent.analyze(question)
                            print(f"问题类型: {result.problem_type.value}")
                            print(f"置信度: {result.confidence_score:.2f}")
                            print(f"分析的文件: {', '.join(result.files_analyzed)}")
                            print(f"解决方案: {result.final_solution[:300]}...")
                        except Exception as e:
                            print(f"分析失败: {str(e)}")
                    continue
                elif not user_input:
                    print("请输入问题")
                    continue
                
                print(f"\n🔍 分析问题: {user_input}")
                
                # 执行分析
                result = agent.analyze(user_input)
                
                print(f"\n📊 分析结果:")
                print(f"  问题类型: {result.problem_type.value}")
                print(f"  置信度: {result.confidence_score:.2f}")
                print(f"  处理时间: {result.processing_time:.2f}秒")
                print(f"  分析的文件: {', '.join(result.files_analyzed)}")
                print(f"\n💡 解决方案:")
                print(result.final_solution)
                
            except KeyboardInterrupt:
                print("\n\n用户中断，程序退出")
                break
            except Exception as e:
                print(f"\n❌ 分析失败: {str(e)}")
                print("请检查输入或稍后重试")
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        print("请检查API密钥和网络连接")


if __name__ == "__main__":
    main() 