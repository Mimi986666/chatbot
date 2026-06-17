# 🤖 三合一智能助手

基于 Streamlit 的智能聊天系统，整合生活费测评、对话记账、期末备考规划三大模块，支持 DeepSeek AI 增强智能对话。

## ✨ 功能特性

### 💰 对话记账
- 支持口语化输入消费记录（示例：今天晚饭22元）
- 自动提取日期、消费分类、金额
- 支持查询本月消费统计
- 数据自动保存到 CSV 文件

### 📊 生活费规划测评
- 自动读取历史消费数据
- AI 智能分析消费习惯
- 生成消费评分报告
- 提供个性化省钱建议
- 测算每日空闲学习时间

### 📚 期末备考规划
- AI 智能生成学习计划
- 支持对话内调整计划
- 自动同步空闲时长
- 一键导出 TXT 格式计划

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 DeepSeek API（可选）

**方式一：环境变量**
```bash
export DEEPSEEK_API_KEY=sk-your-api-key-here  # Linux/Mac
set DEEPSEEK_API_KEY=sk-your-api-key-here    # Windows
```

**方式二：配置文件**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

**方式三：界面输入**
- 启动应用后在侧边栏输入 API 密钥

> 💡 不配置 API 密钥也可以使用规则引擎模式

### 3. 启动应用

```bash
streamlit run main.py
```

应用将在浏览器中打开，默认地址：`http://localhost:8505`

## 📖 使用说明

### 对话记账
1. 在侧边栏选择「对话记账」模式
2. 输入消费记录，例如：
   - `今天晚饭22元`
   - `昨天买了本书花了45元`
   - `6月15日交通费5元`
3. 输入「查看本月开销」查询统计

### 生活费规划测评
1. 选择「生活费规划测评」模式
2. AI 会引导你回答几个问题
3. 自动分析消费习惯并生成报告
4. 每日空闲时长会自动同步到备考模块

### 期末备考规划
1. 选择「期末备考规划」模式
2. 告诉 AI 你的考试日期和科目
3. AI 会生成个性化学习计划
4. 可以调整计划（如：每天多1小时刷题）
5. 输入「导出」保存为 TXT 文件

## 📁 项目结构

```
chatbot/
├── main.py                      # 主程序
├── modules/                     # 功能模块
│   ├── chat_framework.py        # 通用聊天框架
│   ├── deepseek_api.py          # DeepSeek API 集成
│   ├── expense_tracker.py       # 对话记账模块
│   ├── budget_assessment.py     # 生活费测评模块
│   └── study_planner.py         # 期末备考模块
├── config.py                    # 配置文件
├── data/                        # 数据存储
│   └── consume.csv              # 消费记录
├── exports/                     # 导出文件
├── .env                         # 环境变量（API密钥）
├── .env.example                  # 环境变量示例
├── .gitignore                   # Git忽略配置
└── requirements.txt             # 依赖清单
```

## 🔧 配置选项

### DeepSeek API
- **API 密钥**：在 [DeepSeek 平台](https://platform.deepseek.com/) 获取
- **模型**：默认使用 `deepseek-chat`
- **温度参数**：0.7（控制回复随机性）
- **最大 Token**：2000

### 评分参数
可在 `config.py` 中调整消费评分规则和权重。

## 🤝 数据互通

1. **记账 → 测评**：消费数据自动供给测评模块
2. **测评 → 备考**：每日空闲时长自动同步
3. **会话保持**：使用 session_state 持久化对话历史

## 📝 开发指南

### Git 版本控制

```bash
# 初始化仓库
git init

# 基础版本提交
git add .
git commit -m "feat: 完成三合一聊天系统开发"
git tag v1.0.0

# 推送 GitHub
git remote add origin https://github.com/yourusername/chatbot.git
git push -u origin main
git push origin --tags
```

### 添加新模块

1. 在 `modules/` 目录创建新模块文件
2. 在 `main.py` 中导入并处理
3. 更新 `chat_framework.py` 添加通用组件

## ⚠️ 注意事项

- API 密钥仅保存在本地，不会上传到任何服务器
- 消费数据存储在本地 CSV 文件中
- 切换模块会自动清空对话缓存
- 建议定期备份 `data/consume.csv` 文件

## 📄 许可证

MIT License

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - Web 框架
- [DeepSeek](https://deepseek.com/) - AI 大模型
- [Pandas](https://pandas.pydata.org/) - 数据处理

---

**享受智能助手带来的便利吧！** 🎉
