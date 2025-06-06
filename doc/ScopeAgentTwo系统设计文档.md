## THINK Agent 系统设计文档

### 一、系统目标

设计一个使用 LangChain + 大语言模型（如 o4-mini）构建的 THINK Agent，能系统地处理以下类型问题：

1. 数据不平衡问题
2. Shuffle 数据量过大问题
3. 其他复杂性能或逻辑问题

Agent 应具备：

* 多步问题分类与分析能力
* 自动调用工具（如读取文件）补充信息
* 基于先验经验辅助分析
* 控制 LLM 输出规模，避免冗余

### 二、系统架构（LangChain Agent 框架）

整体结构如下：

```
用户问题输入
  ↓
Agent 主链推理
├── 分类问题类型（数据不平衡、shuffle过大、其它）
├── 识别关键代码模块
├── 使用经验辅助分析
├── 检查信息完整性 →（不完整则调用工具）
│   └── 工具：读取文件（Tool Call）
│          ↓
│      文件内容返回
│          ↓
│   迭代继续思考（重新注入上下文）
└── 输出最终方案
```

### 三、问题分类分步思考（Prompt模板）

使用分步思维链结构：

* `[THINK 1]` 问题类别分类
* `[THINK 2]` 关键代码分析
* `[THINK 3]` 经验推导分析
* `[THINK 4]` 信息完整性检查（是否需调用工具）
* `[THINK 5]` 最终方案建议

### 四、工具调用（Tool Call）

* 工具类型：文件阅读工具（读取代码文件内容）
* 触发位置：THINK 4 中识别到信息不足时
* 具体实现方式：

  ```python
  def read_code_files(filenames: list[str]) -> str:
      # 读取文件内容
      return "文件内容"

  read_file_tool = Tool(
      name="ReadRelevantCodeFiles",
      func=read_code_files,
      description="读取相关文件以完善上下文"
  )
  ```

### 五、迭代框架（递归式调用）

使用循环迭代实现多轮信息补充与分析：

```python
while not done:
    response = agent_chain.run(question, context)
    if "需要查看文件" in response:
        filenames = extract_filenames(response)
        context += read_code_files(filenames)
    else:
        done = True
```

### 六、Prompt模板（详细定义）

主Prompt模板结构：

```
你是一名资深的机器学习问题分析Agent，请依照以下步骤进行分析：

[THINK 1] 问题分类（数据不平衡、shuffle 慢、其它？）

[THINK 2] 识别关键代码模块和函数。

[THINK 3] 根据经验和已有信息，分析可能的原因。

[THINK 4] 如果信息不足，明确说明需要查看哪些文件（给出列表）。

[THINK 5] 根据以上所有信息，提出具体解决方案，分析优缺点。
```

### 七、Prompt注入经验（Prompt + RAG 结构）

使用Prompt动态注入经验知识：

```
[经验知识辅助]
{retrieved_experience}

根据上述经验知识，继续以下分析步骤……
```

### 八、LLM 输出规模控制（摘要总结）

额外加入一层摘要Prompt，控制输出内容过长时进行压缩总结：

```
当前输出内容过长，请用简洁的结构化摘要：

- 问题类别：
- 关键问题：
- 推荐查看文件：
- 解决方案建议：
```

### 九、附录：假设推理思维（待定功能）

后续考虑加入假设推理：

```
[假设推理]
提出可能的假设，并计划如何验证。

- 假设：
- 验证方式：
```

### 十、项目结构示例

```
project/
├── prompts/
│   ├── main_think_prompt.txt
│   ├── file_request_prompt.txt
│   └── summarization_prompt.txt
├── tools/
│   └── read_files_tool.py
├── chains/
│   └── agent_runner.py
├── retriever/
│   └── experience_retriever.py
└── data/
    └── experience_knowledge.md
```

---

**以上设计文档提供了完整、清晰的架构指导，助力快速实现具有深度分析能力的 THINK Agent。**
