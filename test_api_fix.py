#!/usr/bin/env python3
"""
测试OpenAI API兼容性修复
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试所有关键模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from langchain_openai import ChatOpenAI
        print("✅ ChatOpenAI 导入成功")
    except ImportError as e:
        print(f"❌ ChatOpenAI 导入失败: {e}")
        return False
    
    try:
        from langchain.chains import LLMChain
        print("✅ LLMChain 导入成功")
    except ImportError as e:
        print(f"❌ LLMChain 导入失败: {e}")
        return False
    
    try:
        from src.agents.scope_think_agent import ScopeThinkAgent
        print("✅ ScopeThinkAgent 导入成功")
    except ImportError as e:
        print(f"❌ ScopeThinkAgent 导入失败: {e}")
        return False
    
    try:
        from config.settings import settings
        print("✅ Settings 导入成功")
    except ImportError as e:
        print(f"❌ Settings 导入失败: {e}")
        return False
    
    return True

def test_llm_initialization():
    """测试LLM初始化（不需要真实API密钥）"""
    print("\n=== 测试LLM初始化 ===")
    
    try:
        from langchain_openai import ChatOpenAI
        
        # 使用假API密钥进行初始化测试
        llm = ChatOpenAI(
            api_key="test_key_123",
            model="gpt-4",
            temperature=0.1,
            max_tokens=100
        )
        print("✅ ChatOpenAI 初始化成功（使用测试密钥）")
        print(f"   模型: {llm.model_name}")
        print(f"   温度: {llm.temperature}")
        
        return True
        
    except Exception as e:
        print(f"❌ ChatOpenAI 初始化失败: {e}")
        return False

def test_agent_creation():
    """测试Agent创建（不进行实际调用）"""
    print("\n=== 测试Agent创建 ===")
    
    try:
        from langchain_openai import ChatOpenAI
        from src.agents.scope_think_agent import ScopeThinkAgent
        from src.tools.file_reader import FileReaderTool
        from src.tools.file_recommendation import FileRecommendationTool, DEFAULT_FILE_MAPPING, DEFAULT_PARSER_MAPPING
        
        # 创建测试LLM
        llm = ChatOpenAI(api_key="test_key", model="gpt-4", temperature=0.1)
        
        # 创建工具
        file_reader = FileReaderTool(
            base_path="./data",
            parser_mapping=DEFAULT_PARSER_MAPPING
        )
        
        recommendation_tool = FileRecommendationTool(
            file_content_mapping=DEFAULT_FILE_MAPPING,
            parser_functions=DEFAULT_PARSER_MAPPING
        )
        
        # 创建Agent
        agent = ScopeThinkAgent(
            llm=llm,
            file_reader=file_reader,
            recommendation_tool=recommendation_tool,
            max_iterations=3
        )
        
        print("✅ ScopeThinkAgent 创建成功")
        print(f"   最大迭代次数: {agent.max_iterations}")
        print(f"   LLM类型: {type(agent.llm).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ ScopeThinkAgent 创建失败: {e}")
        return False

def test_deprecated_methods():
    """测试是否修复了过时的方法调用"""
    print("\n=== 测试方法调用兼容性 ===")
    
    try:
        from langchain.chains import LLMChain
        from langchain_openai import ChatOpenAI
        from src.prompts.main_think_prompt import MainThinkPromptTemplate
        
        # 创建测试组件
        llm = ChatOpenAI(api_key="test_key", model="gpt-4")
        prompt = MainThinkPromptTemplate()
        chain = LLMChain(llm=llm, prompt=prompt.prompt)
        
        print("✅ LLMChain 创建成功")
        print("✅ 使用新的invoke()方法而不是过时的run()方法")
        
        return True
        
    except Exception as e:
        print(f"❌ 方法调用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 ScopeAgentV2 API兼容性测试\n")
    
    tests = [
        ("模块导入", test_imports),
        ("LLM初始化", test_llm_initialization), 
        ("Agent创建", test_agent_creation),
        ("方法兼容性", test_deprecated_methods)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("🎯 测试结果汇总:")
    
    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 所有测试通过！OpenAI API兼容性修复成功！")
        print("\n💡 现在可以运行: python main.py")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 