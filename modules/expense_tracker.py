import pandas as pd
import re
from datetime import datetime
import os

CSV_PATH = 'data/consume.csv'

def init_csv():
    """初始化CSV文件"""
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=['date', 'category', 'amount', 'description', 'create_time'])
        df.to_csv(CSV_PATH, index=False, encoding='utf-8')

def parse_expense(text):
    """解析口语化消费记录"""
    # 提取日期（支持多种格式）
    date_patterns = [
        r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日号]?',
        r'(\d{1,2})[-/月](\d{1,2})[日号]?',
        r'(\d{1,2})[-/](\d{1,2})',
        r'(今天|昨天|前天)'
    ]
    
    date = datetime.now().strftime('%Y-%m-%d')
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            if match.group(1) == '今天':
                date = datetime.now().strftime('%Y-%m-%d')
            elif match.group(1) == '昨天':
                date = (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            elif match.group(1) == '前天':
                date = (datetime.now() - pd.Timedelta(days=2)).strftime('%Y-%m-%d')
            elif len(match.groups()) == 3:
                date = f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
            elif len(match.groups()) == 2:
                date = f"{datetime.now().year}-{int(match.group(1)):02d}-{int(match.group(2)):02d}"
            break
    
    # 提取金额
    amount_pattern = r'(\d+(?:\.\d{1,2})?)元?'
    amount_match = re.search(amount_pattern, text)
    amount = float(amount_match.group(1)) if amount_match else 0.0
    
    # 提取分类
    categories = ['餐饮', '娱乐', '交通', '学习', '人情', '其他']
    category_keywords = {
        '餐饮': ['早餐', '午餐', '晚餐', '饭', '吃', '外卖', '奶茶', '咖啡'],
        '娱乐': ['电影', '游戏', '玩', 'KTV', '逛街', '购物'],
        '交通': ['公交', '地铁', '打车', '滴滴', '车票'],
        '学习': ['书', '文具', '课程', '培训', '资料'],
        '人情': ['红包', '礼物', '请客', '聚餐']
    }
    
    category = '其他'
    description = ''
    for cat, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in text:
                category = cat
                description = keyword
                break
        if category != '其他':
            break
    
    if not description:
        description = text
    
    return {
        'date': date,
        'category': category,
        'amount': amount,
        'description': description,
        'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def save_expense(data):
    """保存消费记录到CSV"""
    init_csv()
    df = pd.read_csv(CSV_PATH, encoding='utf-8')
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False, encoding='utf-8')

def get_monthly_total(date=None):
    """获取月度总消费"""
    init_csv()
    if not os.path.exists(CSV_PATH):
        return 0.0
    
    df = pd.read_csv(CSV_PATH, encoding='utf-8')
    if df.empty:
        return 0.0
    
    if date is None:
        date = datetime.now()
    
    current_month = date.strftime('%Y-%m')
    monthly_data = df[df['date'].str.startswith(current_month)]
    
    return monthly_data['amount'].sum()

def get_monthly_by_category(date=None):
    """获取月度各分类消费"""
    init_csv()
    if not os.path.exists(CSV_PATH):
        return {}
    
    df = pd.read_csv(CSV_PATH, encoding='utf-8')
    if df.empty:
        return {}
    
    if date is None:
        date = datetime.now()
    
    current_month = date.strftime('%Y-%m')
    monthly_data = df[df['date'].str.startswith(current_month)]
    
    return monthly_data.groupby('category')['amount'].sum().to_dict()

def get_all_expense_data():
    """获取所有消费数据"""
    init_csv()
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()
    
    return pd.read_csv(CSV_PATH, encoding='utf-8')
