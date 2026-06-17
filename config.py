import os

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 对话参数
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000

# 数据存储路径
DATA_DIR = "data"
EXPORTS_DIR = "exports"
CSV_FILENAME = "consume.csv"

# 消费分类
EXPENSE_CATEGORIES = [
    "餐饮", "娱乐", "交通", "学习", "人情", "购物", "其他"
]

# 评分参数
SCORE_PARAMS = {
    "base_score": 60,
    "budget_control": {
        "excellent": 20,      # 实际消费 ≤ 预算
        "good": 10,           # 预算 < 实际消费 ≤ 预算×1.1
        "poor": 0             # 实际消费 > 预算×1.1
    },
    "category_ratios": {
        "food": {"min": 0.4, "max": 0.55, "score": 5},      # 餐饮占比
        "entertainment": {"max": 0.2, "score": 5},          # 娱乐占比
        "social": {"max": 0.15, "score": 5}                 # 人情占比
    },
    "savings_bonus": {
        "high": 5,     # 消费环比下降≥10%
        "medium": 3,   # 消费环比下降≥5%
        "low": 0       # 其他
    }
}

# 每日时间分配（小时）
DAILY_TIME_BUDGET = {
    "sleep": 8,
    "study": 6,
    "meals": 2,
    "commute": 1,
    "others": 2,
    "expense_consumption": 1.5  # 消费活动耗时
}

# 学习时段分配
STUDY_PERIODS = {
    "morning": {"time": "08:00-12:00", "ratio": 0.4, "type": "理论学习"},
    "afternoon": {"time": "14:00-18:00", "ratio": 0.4, "type": "刷题练习"},
    "evening": {"time": "19:00-22:00", "ratio": 0.2, "type": "总结复习"}
}
