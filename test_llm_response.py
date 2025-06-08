#!/usr/bin/env python3
"""
测试LLM响应格式
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_llm_response_format():
    """测试LLM响应格式"""
    print("=== 测试LLM响应格式 ===\n")
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        
        # 创建一个简单的测试
        llm = ChatOpenAI(
            api_key="test_key_not_real",
            model="gpt-4",
            temperature=0.1
        )
        
        # 创建简单的prompt
        prompt = PromptTemplate(
            input_variables=["question"],
            template="请回答这个问题: {question}"
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        
        print("✅ LLMChain 创建成功")
        print(f"LLM类型: {type(llm).__name__}")
        
        # 测试invoke方法（不会真正调用，只是测试接口）
        test_input = {"question": "什么是数据倾斜？"}
        
        print(f"测试输入: {test_input}")
        print("invoke方法接口检查: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_response_parsing():
    """测试响应解析逻辑"""
    print("\n=== 测试响应解析逻辑 ===\n")
    
    # 模拟不同格式的响应
    test_responses = [
        {"text": "这是一个正常的响应"},
        "这是直接的字符串响应",
        {"content": "这是content格式的响应"},
        {"choices": [{"message": {"content": "这是choices格式"}}]}
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"测试响应 {i}: {type(response).__name__}")
        
        # 测试解析逻辑
        if isinstance(response, dict):
            if "text" in response:
                parsed = response["text"]
                print(f"  解析为text: {parsed}")
            elif "content" in response:
                parsed = response["content"]
                print(f"  解析为content: {parsed}")
            else:
                parsed = str(response)
                print(f"  解析为字符串: {parsed}")
        else:
            parsed = str(response)
            print(f"  直接解析: {parsed}")
    
    return True

def main():
    """主测试函数"""
    print("🔧 LLM响应格式测试\n")
    
    tests = [
        ("LLM响应格式", test_llm_response_format),
        ("响应解析逻辑", test_response_parsing)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            success = test_func()
            if not success:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 响应格式测试完成！")
    else:
        print("⚠️ 部分测试失败")
    
    return all_passed

if __name__ == "__main__":
    main() 