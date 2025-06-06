## ScopeAgentV2 设计文档
### 背景

构建这个 AI 作业优化 Agent 的背景源于以下现实需求：微软大数据平台Cosmos生成的SCOPE作业日志结构复杂、信息量庞大，普通用户难以精准识别性能瓶颈、理解底层执行机制，也无法快速定位优化点。而现有系统大多提供静态诊断信息，缺乏自动推理能力、上下文理解与反馈闭环。

本系统的输入包括用户提交的 SCOPE script查询、作业运行日志、表的元数据信息（行数、基数等）。Agent 的任务是模拟一位具有分析经验的数据平台专家，具备“逐步思考、问题归类、自我问答式推理”的能力，能够识别作业中的潜在性能问题（如数据倾斜、Shuffle 开销过大、GC 异常等），并结合可检索知识库给出改写建议或配置参数优化。

其工作方式是：基于 LangChain 框架构建多步骤的推理链，通过多个 tool（如 script 分析器、元数据检索器、CodeGen 解释器等）驱动 Agent 在每一步做出决策；每一阶段产生结构化结论，存入 memory，供后续步骤调用；最终在充分分析基础上输出优化建议和改写参考，并可记录用户的采纳或忽略行为，形成可学习的反馈闭环。整套流程兼顾准确性、可解释性和可演进性，是 AI 在大数据计算平台上的一次智能化增强尝试。


### 一、系统目标

设计一个使用 LangChain + think模型构建的 THINK Agent，能系统地处理以下类型问题：

1. 数据倾斜问题
   - 使用PartitionBy合理重新分区
   - 热点键单独处理
   - 键加随机盐值

2. 过多Shuffle问题
   - 合理利用PartitionBy减少重复Shuffle
   - 提前投影减少数据规模
   - 避免多次全网重分布

3. 其他复杂性能或逻辑问题

Agent 应具备：

* 多步问题分类与分析能力
* 自动调用工具（如读取文件）补充信息
* 基于先验经验辅助分析
* 控制 LLM 输出规模，避免冗余

LLM 要求：
* think模型
如下选择：
  - GPT-4
  - Claude 3 Opus
  - Gemini Pro
  - Qwen 2.5
  - DeepSeek

### 二、系统架构（LangChain Agent 框架）

整体结构如下：

```
用户问题输入
  ↓
Agent 主链推理
├── 分类问题类型（数据倾斜、过多Shuffle、其它）
├── 识别关键代码模块
├── 使用经验辅助分析
├── 检查信息完整性 -> (若要补充，基于先验知识+上下文分析)
│   ├── 文件模式匹配
│   ├── 关键词提取
│   ├── 优先级评分
│   └── 生成文件列表 → 工具调用：读取文件
│          ↓
│      文件内容返回 + 反馈分析
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

### 五、[THINK 4] 信息完整性检查模块详细设计

#### 5.1 模块目标
[THINK 4] 模块负责：
- 评估当前信息是否足够进行问题分析
- 智能推断需要查看的关键文件
- 结合先验经验确定文件优先级
- 生成结构化的文件查看请求

#### 5.2 文件推断Prompt模板

```
[THINK 4] 信息完整性检查

基于以上分析，我需要评估信息完整性：

当前已知信息：
- 问题类型：{problem_type}
- 相关组件：{components}
- 用户描述：{user_description}

文件推断规则：
1. 数据倾斜问题 → 查看数据处理、Join操作相关文件
2. 过多Shuffle问题 → 查看算子使用、数据流转相关文件
3. 其他问题 → 根据具体描述推断

请按以下格式输出需要查看的文件：

【需要文件】: 是/否
【文件列表】:
- 文件路径: 原因
- 文件路径: 原因

【推断依据】: 具体说明为什么需要这些文件
```

#### 5.3 文件背景知识库（先验经验）

建立文件名模式与核心内容的映射关系：

```
文件1： 用户原始脚本
文件2: DAG中每个stage的运行情况，如果要读取文件2，需调用parser_file2函数
....
```

#### 5.4 智能文件推荐工具

```python
class FileRecommendationTool:
    def __init__(self, file_content_mapping, parser_functions):
        self.file_content_mapping = file_content_mapping  # 文件名->内容描述的映射
        self.parser_functions = parser_functions  # 特殊文件的解析函数映射
    
    def recommend_files(self, problem_type: str, context: str, current_analysis: str) -> List[Dict]:
        """基于问题类型、上下文和当前分析状态推荐文件"""
        recommendations = []
        
        # 1. 分析当前缺失的信息类型
        missing_info_types = self._identify_missing_information(
            problem_type, context, current_analysis
        )
        
        # 2. 基于文件内容描述匹配需求
        for file_name, content_desc in self.file_content_mapping.items():
            relevance_score = self._calculate_content_relevance(
                content_desc, missing_info_types, problem_type
            )
            
            if relevance_score > 0.3:  # 设置相关性阈值
                file_info = {
                    "file_name": file_name,
                    "content_description": content_desc,
                    "relevance_score": relevance_score,
                    "reason": self._generate_recommendation_reason(
                        content_desc, missing_info_types
                    ),
                    "requires_parser": file_name in self.parser_functions,
                    "parser_function": self.parser_functions.get(file_name, None)
                }
                recommendations.append(file_info)
        
        return sorted(recommendations, key=lambda x: x["relevance_score"], reverse=True)
    
    def _identify_missing_information(self, problem_type: str, context: str, current_analysis: str) -> List[str]:
        """识别当前分析中缺失的信息类型"""
        missing_info = []
        
        # 基于问题类型确定可能需要的信息
        info_requirements = {
            "数据倾斜": [
                "用户脚本逻辑", "Join操作详情", "数据分布情况", 
                "分区策略", "热点键分析", "运行性能指标"
            ],
            "过多Shuffle": [
                "用户脚本逻辑", "算子使用情况", "数据流转路径",
                "Shuffle操作统计", "Stage运行情况", "数据规模信息"
            ]
        }
        
        required_info = info_requirements.get(problem_type, [])
        
        # 检查当前分析中已包含哪些信息
        for info_type in required_info:
            if not self._is_info_present_in_analysis(info_type, current_analysis):
                missing_info.append(info_type)
        
        return missing_info
    
    def _calculate_content_relevance(self, content_desc: str, missing_info: List[str], problem_type: str) -> float:
        """计算文件内容与缺失信息的相关性得分"""
        score = 0.0
        
        # 关键词匹配评分
        keyword_mapping = {
            "用户脚本逻辑": ["脚本", "代码", "逻辑", "算法"],
            "Join操作详情": ["join", "连接", "关联"],
            "数据分布情况": ["分布", "倾斜", "热点", "统计"],
            "Stage运行情况": ["stage", "阶段", "运行", "执行"],
            "Shuffle操作统计": ["shuffle", "重分区", "数据传输"],
            "数据规模信息": ["数据量", "规模", "大小", "行数"]
        }
        
        for missing_type in missing_info:
            if missing_type in keyword_mapping:
                keywords = keyword_mapping[missing_type]
                for keyword in keywords:
                    if keyword.lower() in content_desc.lower():
                        score += 0.2
        
        return min(score, 1.0)  # 限制最大得分为1.0
    
    def _generate_recommendation_reason(self, content_desc: str, missing_info: List[str]) -> str:
        """生成推荐文件的原因说明"""
        reason_parts = []
        
        for info_type in missing_info:
            if any(keyword in content_desc.lower() 
                   for keyword in ["脚本", "代码"] if info_type == "用户脚本逻辑"):
                reason_parts.append("包含用户脚本逻辑，有助于理解业务处理流程")
            elif any(keyword in content_desc.lower() 
                     for keyword in ["stage", "运行"] if info_type == "Stage运行情况"):
                reason_parts.append("包含Stage运行信息，可分析性能瓶颈")
            elif any(keyword in content_desc.lower() 
                     for keyword in ["分布", "倾斜"] if info_type == "数据分布情况"):
                reason_parts.append("包含数据分布信息，有助于分析倾斜问题")
        
        return "；".join(reason_parts) if reason_parts else "可能包含相关分析信息"
    
    def read_file_with_parser(self, file_name: str) -> str:
        """读取文件，如果需要特殊解析则调用相应函数"""
        if file_name in self.parser_functions:
            parser_func = self.parser_functions[file_name]
            return parser_func(file_name)
        else:
            # 普通文件直接读取
            with open(file_name, 'r', encoding='utf-8') as f:
                return f.read()

# 使用示例
file_mapping = {
    "文件1": "用户原始脚本",
    "文件2": "DAG中每个stage的运行情况",
    "文件3": "数据倾斜统计报告",
    "文件4": "Shuffle操作性能日志"
}

parser_mapping = {
    "文件2": "parser_file2",  # DAG运行情况需要特殊解析
    "文件3": "parser_file3"   # 统计报告需要特殊解析
}

recommendation_tool = FileRecommendationTool(file_mapping, parser_mapping)
```

#### 5.5 上下文增强策略

```python
class ContextEnhancer:
    def enhance_context_for_file_selection(self, 
                                         problem_type: str, 
                                         user_input: str, 
                                         previous_analysis: str) -> str:
        """增强上下文信息以改善文件选择"""
        
        enhanced_context = f"""
        【问题分析上下文】
        问题类型: {problem_type}
        用户输入: {user_input}
        
        【已有分析结果】
        {previous_analysis}
        
        【文件选择指导】
        基于以上信息，优先考虑以下类型的文件：
        {self._get_file_selection_guidance(problem_type)}
        
        【关键点检查】
        - 是否涉及数据处理的核心逻辑？
        - 是否涉及性能关键路径？
        - 是否涉及配置或参数设置？
        """
        
        return enhanced_context
```

#### 5.6 迭代反馈机制

```python
class IterativeFeedbackProcessor:
    def __init__(self, file_recommendation_tool):
        self.recommendation_tool = file_recommendation_tool
        self.analysis_history = []
    
    def process_file_reading_result(self, 
                                  file_name: str,
                                  file_content: str, 
                                  problem_type: str,
                                  original_question: str,
                                  current_analysis: str) -> Dict:
        """处理文件读取结果，决定是否需要继续查看其他文件"""
        
        # 记录已读取的文件
        self.analysis_history.append({
            "file_name": file_name,
            "content_summary": self._summarize_content(file_content),
            "timestamp": time.time()
        })
        
        # 更新当前分析状态
        updated_analysis = current_analysis + f"\n\n[文件{file_name}信息]:\n{file_content}"
        
        # 评估信息充足性
        info_sufficiency = self._evaluate_information_sufficiency(
            problem_type, updated_analysis, original_question
        )
        
        analysis_result = {
            "information_sufficient": info_sufficiency["sufficient"],
            "sufficiency_score": info_sufficiency["score"],
            "missing_aspects": info_sufficiency["missing"],
            "next_files_needed": [],
            "analysis_progress": self._calculate_progress(problem_type, updated_analysis),
            "key_findings": self._extract_key_findings(file_content, problem_type)
        }
        
        # 如果信息不充足，推荐下一批文件
        if not info_sufficiency["sufficient"]:
            next_recommendations = self.recommendation_tool.recommend_files(
                problem_type, original_question, updated_analysis
            )
            
            # 过滤掉已读取的文件
            read_files = [item["file_name"] for item in self.analysis_history]
            filtered_recommendations = [
                rec for rec in next_recommendations 
                if rec["file_name"] not in read_files
            ]
            
            analysis_result["next_files_needed"] = filtered_recommendations[:3]  # 限制推荐数量
        
        return analysis_result
    
    def _evaluate_information_sufficiency(self, problem_type: str, analysis: str, question: str) -> Dict:
        """评估当前信息是否充足以回答问题"""
        sufficiency_criteria = {
            "数据倾斜": {
                "required_info": [
                    "用户脚本逻辑", "Join操作", "数据分布", "性能指标"
                ],
                "min_score": 0.7
            },
            "过多Shuffle": {
                "required_info": [
                    "用户脚本逻辑", "Shuffle操作", "Stage信息", "数据流"
                ],
                "min_score": 0.7
            }
        }
        
        criteria = sufficiency_criteria.get(problem_type, {"required_info": [], "min_score": 0.5})
        present_info = []
        missing_info = []
        
        for info_type in criteria["required_info"]:
            if self._is_info_present(info_type, analysis):
                present_info.append(info_type)
            else:
                missing_info.append(info_type)
        
        score = len(present_info) / len(criteria["required_info"]) if criteria["required_info"] else 1.0
        sufficient = score >= criteria["min_score"]
        
        return {
            "sufficient": sufficient,
            "score": score,
            "present": present_info,
            "missing": missing_info
        }
    
    def _calculate_progress(self, problem_type: str, analysis: str) -> float:
        """计算分析进度"""
        # 基于已获取信息的完整性计算进度
        total_aspects = {
            "数据倾斜": ["脚本理解", "问题定位", "原因分析", "解决方案"],
            "过多Shuffle": ["脚本理解", "Shuffle识别", "性能分析", "优化建议"]
        }
        
        aspects = total_aspects.get(problem_type, ["基本分析"])
        completed = sum(1 for aspect in aspects if self._aspect_completed(aspect, analysis))
        
        return completed / len(aspects)
    
    def _extract_key_findings(self, file_content: str, problem_type: str) -> List[str]:
        """从文件内容中提取关键发现"""
        findings = []
        
        # 基于问题类型提取不同的关键信息
        if problem_type == "数据倾斜":
            if "join" in file_content.lower():
                findings.append("发现Join操作")
            if any(word in file_content.lower() for word in ["倾斜", "热点", "不均匀"]):
                findings.append("检测到数据分布问题")
        
        elif problem_type == "过多Shuffle":
            if any(word in file_content.lower() for word in ["shuffle", "重分区"]):
                findings.append("发现Shuffle操作")
            if "stage" in file_content.lower():
                findings.append("获取到Stage运行信息")
        
        return findings
    
    def _is_info_present(self, info_type: str, analysis: str) -> bool:
        """检查特定类型的信息是否已包含在分析中"""
        info_keywords = {
            "用户脚本逻辑": ["def ", "class ", "import", "脚本"],
            "Join操作": ["join", "连接", "关联"],
            "数据分布": ["分布", "倾斜", "热点", "统计"],
            "Stage信息": ["stage", "阶段", "执行"],
            "Shuffle操作": ["shuffle", "重分区", "数据传输"],
            "性能指标": ["时间", "延迟", "耗时", "性能"]
        }
        
        keywords = info_keywords.get(info_type, [])
        return any(keyword.lower() in analysis.lower() for keyword in keywords)
    
    def get_analysis_summary(self) -> str:
        """获取分析过程摘要"""
        if not self.analysis_history:
            return "尚未读取任何文件"
        
        summary = f"已读取{len(self.analysis_history)}个文件：\n"
        for item in self.analysis_history:
            summary += f"- {item['file_name']}: {item['content_summary']}\n"
        
        return summary
```

### 六、迭代框架（递归式调用）

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

### 七、Prompt模板（详细定义）

主Prompt模板结构：

```
你是一名资深的大数据优化分析Agent，请依照以下步骤进行分析：

[THINK 1] 问题分类（数据倾斜、过多Shuffle、其它？）

[THINK 2] 识别关键代码模块和函数。

[THINK 3] 根据经验和已有信息，分析可能的原因。

[THINK 4] 信息完整性检查：
- 评估当前信息是否充足
- 如需补充，列出具体文件及原因
- 基于先验经验推断关键文件

[THINK 5] 根据以上所有信息，提出具体解决方案，分析优缺点。
```

### 八、Prompt注入经验（Prompt + RAG 结构）

使用Prompt动态注入经验知识：

```
[经验知识辅助]
{retrieved_experience}

根据上述经验知识，继续以下分析步骤……
```

### 九、LLM 输出规模控制（摘要总结）

额外加入一层摘要Prompt，控制输出内容过长时进行压缩总结：

```
当前输出内容过长，请用简洁的结构化摘要：

- 问题类别：
- 关键问题：
- 推荐查看文件：
- 解决方案建议：
```

### 十、附录：假设推理思维（待定功能）

后续考虑加入假设推理：

```
[假设推理]
提出可能的假设，并计划如何验证。

- 假设：
- 验证方式：
```

### 十一、项目结构示例

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
