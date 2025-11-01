# Strands Multi-Agent System

企业级多智能体协作系统，基于 AWS Strands Agents SDK 框架构建，提供股票分析、HR规章查询等专业服务。

## 功能特性

- **主协调器**: 智能路由用户查询到相应的专业 Agent
- **股票分析代理**: 提供实时股票数据分析和投资建议
- **HR规章代理**: 基于 AWS Bedrock Knowledge Base 的员工规章查询
- **用户画像代理**: 获取用户风险承受能力等个人信息
- **通用助手**: 处理其他通用问题

## 系统架构

```
main_agent.py (主协调器)
├── stock_analysis (股票分析)
├── hr_employee_regulation_search (HR规章查询)
├── get_user_risk_tolerance_level (用户画像)
└── general_assistant (通用助手)
```

## 环境要求

- Python 3.8+
- AWS 账户及凭证配置
- AWS Bedrock 访问权限

## 安装

```bash
pip install -r src/requirements.txt
```

## 配置

设置以下环境变量：

```bash
export LOG_LEVEL=INFO
export AWS_DEFAULT_REGION=us-west-2
export KNOWLEDGE_BASE_ID=<your-knowledge-base-id>  # HR知识库ID
```

## 运行

```bash
./run.sh
```

或直接运行：

```bash
python src/main_agent.py
```

## 使用示例

```
> 帮我分析一下AAPL股票
> 公司的年假政策是什么？
> 查询用户123的风险承受能力
```

## 项目结构

```
src/
├── agents/              # 专业代理
│   ├── stock_analysis.py
│   ├── hr_employee_regulation.py
│   ├── user_profile.py
│   └── general_assist.py
├── tools/               # 工具函数
│   ├── stock_data.py
│   └── web_search.py
├── main_agent.py        # 主入口
└── requirements.txt     # 依赖包
```

## 技术栈

- **Strands Agents**: 多智能体框架
- **AWS Bedrock**: Claude 4.5 Sonnet, Claude 4.5 Haiku 模型
- **AWS Bedrock Knowledge Base**: 知识库检索增强生成
- **boto3**: AWS SDK

## License

MIT
