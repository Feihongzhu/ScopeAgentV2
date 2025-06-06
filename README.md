# ScopeAgentV2 - AI 作业优化 Agent

一个基于 LangChain 的智能系统，用于分析和优化 SCOPE 作业性能问题。主要功能包括数据倾斜分析、Shuffle 优化、代码重写建议等。

## 🚀 特性

- **智能问题分类**: 自动识别数据倾斜、过多Shuffle等问题类型
- **多步思维链**: 采用THINK 1-5的结构化分析流程
- **智能文件推荐**: 基于问题类型和分析进度智能推荐相关文件
- **迭代分析**: 支持多轮信息补充和深度分析
- **多LLM支持**: 支持OpenAI、Anthropic、Qwen、DeepSeek等模型
- **可扩展架构**: 模块化设计，易于扩展新功能

## 📁 项目结构

```
ScopeAgentV2/
├── scope_agent/                 # 主包
│   ├── __init__.py
│   ├── agents/                  # Agent模块
│   │   ├── __init__.py
│   │   ├── base_agent.py       # 基础Agent类
│   │   └── scope_think_agent.py # 核心分析Agent
│   ├── tools/                   # 工具模块
│   │   ├── __init__.py
│   │   ├── file_reader.py      # 文件读取工具
│   │   ├── file_recommendation.py # 文件推荐工具
│   │   └── iterative_feedback.py # 迭代反馈处理器
│   ├── prompts/                 # Prompt模板
│   │   ├── __init__.py
│   │   └── main_think_prompt.py # 主要思维链模板
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   └── analysis_models.py  # 分析相关数据结构
│   ├── parsers/                 # 文件解析器
│   │   └── __init__.py
│   └── chains/                  # LangChain链
│       └── __init__.py
├── config/                      # 配置文件
│   └── settings.py
├── data/                        # 数据目录
├── logs/                        # 日志目录
├── doc/                         # 文档
│   └── ScopeAgentTwo系统设计文档.md
├── main.py                      # 主程序入口
├── requirements.txt             # 依赖包
└── README.md                    # 项目说明
```

## 🛠️ 安装和配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd ScopeAgentV2
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# LLM配置
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000

# 路径配置
DATA_PATH=./data
LOG_PATH=./logs
KNOWLEDGE_PATH=./data/knowledge

# Agent配置
MAX_ITERATIONS=5
MAX_FILES_PER_ITERATION=3
CONFIDENCE_THRESHOLD=0.7
```

## 🚀 快速开始

### 基本使用

```python
from langchain.llms import OpenAI
from scope_agent import ScopeThinkAgent
from scope_agent.tools.file_reader import FileReaderTool
from scope_agent.tools.file_recommendation import FileRecommendationTool
from config.settings import settings

# 初始化LLM
llm = OpenAI(openai_api_key="your_api_key")

# 初始化工具
file_reader = FileReaderTool(base_path="./data")
recommendation_tool = FileRecommendationTool(
    file_content_mapping=settings.default_file_mapping,
    parser_functions=settings.default_parser_mapping
)

# 创建Agent
agent = ScopeThinkAgent(
    llm=llm,
    file_reader=file_reader,
    recommendation_tool=recommendation_tool
)

# 执行分析
question = "我的SCOPE作业运行很慢，Join操作耗时特别长，可能是什么原因？"
result = agent.analyze(question)

print(f"问题类型: {result.problem_type.value}")
print(f"解决方案: {result.final_solution}")
```

### 运行示例

```bash
python main.py
```

## 🧠 核心功能

### 1. 问题分类

系统能自动识别以下问题类型：
- **数据倾斜问题**: 数据分布不均匀，某些分区数据量过大
- **过多Shuffle问题**: 频繁的数据重分布操作影响性能  
- **其他问题**: 配置、逻辑、资源等其他性能问题

### 2. 思维链分析

采用5步结构化思考过程：
- **THINK 1**: 问题分类
- **THINK 2**: 关键代码模块识别
- **THINK 3**: 经验推导分析
- **THINK 4**: 信息完整性检查
- **THINK 5**: 最终解决方案

### 3. 智能文件推荐

基于以下因素智能推荐相关文件：
- 问题类型
- 当前分析进度
- 缺失信息类型
- 文件内容相关性

### 4. 支持的文件类型

- `user_script.txt`: 用户SCOPE脚本
- `dag_stages.log`: DAG运行日志
- `data_skew_report.json`: 数据倾斜报告
- `shuffle_stats.log`: Shuffle统计
- `performance_metrics.json`: 性能指标
- 其他自定义文件类型

## 🔧 扩展开发

### 添加新的解析器

```python
from scope_agent.parsers import register_parser

def custom_parser(file_path: str) -> str:
    # 自定义解析逻辑
    return "解析结果"

register_parser("custom_parser", custom_parser)
```

### 添加新的问题类型

```python
from scope_agent.models.analysis_models import ProblemType

# 在ProblemType枚举中添加新类型
class ProblemType(Enum):
    DATA_SKEW = "数据倾斜"
    EXCESSIVE_SHUFFLE = "过多Shuffle"
    MEMORY_ISSUE = "内存问题"  # 新增
    OTHER = "其他"
```

### 自定义Prompt模板

```python
from scope_agent.prompts.main_think_prompt import MainThinkPromptTemplate

class CustomPromptTemplate(MainThinkPromptTemplate):
    def _build_template(self) -> str:
        # 自定义模板逻辑
        return "自定义模板内容"
```

## 📊 性能优化建议

系统能提供以下类型的优化建议：

### 数据倾斜优化
- 使用PartitionBy合理重新分区
- 热点键单独处理或加随机盐值
- 避免过度集中的Join键

### Shuffle优化
- 合理利用PartitionBy减少重复Shuffle
- 提前投影减少数据规模
- 避免多次全网重分布
- 使用广播Join处理小表

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至项目维护者

## 🙏 致谢

感谢以下开源项目的支持：
- [LangChain](https://github.com/hwchase17/langchain)
- [OpenAI](https://openai.com/)
- [Anthropic](https://www.anthropic.com/)

---

**ScopeAgentV2** - 让SCOPE作业优化更智能 🚀 