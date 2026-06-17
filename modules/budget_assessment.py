import pandas as pd
from modules.expense_tracker import get_all_expense_data, get_monthly_total, get_monthly_by_category
from datetime import datetime

def analyze_consumption():
    """分析消费数据"""
    df = get_all_expense_data()
    if df.empty:
        return None
    
    current_month = datetime.now().strftime('%Y-%m')
    monthly_data = df[df['date'].str.startswith(current_month)]
    
    if monthly_data.empty:
        return None
    
    total_amount = monthly_data['amount'].sum()
    category_totals = monthly_data.groupby('category')['amount'].sum().to_dict()
    
    return {
        'total': total_amount,
        'categories': category_totals,
        'record_count': len(monthly_data)
    }

def calculate_score(budget_data, consumption_data):
    """计算消费评分"""
    total = budget_data.get('monthly_budget', 0)
    food = budget_data.get('food', 0)
    entertainment = budget_data.get('entertainment', 0)
    social = budget_data.get('social', 0)
    
    actual_total = consumption_data.get('total', 0)
    categories = consumption_data.get('categories', {})
    
    score = 60  # 基础分
    
    # 预算控制分 (0-20)
    if total > 0:
        if actual_total <= total:
            score += 20
        elif actual_total <= total * 1.1:
            score += 10
    
    # 分类合理分 (0-15)
    if actual_total > 0:
        # 餐饮占比 40%-55%
        food_ratio = categories.get('餐饮', 0) / actual_total
        if 0.4 <= food_ratio <= 0.55:
            score += 5
        
        # 娱乐占比 ≤20%
        entertainment_ratio = categories.get('娱乐', 0) / actual_total
        if entertainment_ratio <= 0.2:
            score += 5
        
        # 人情占比 ≤15%
        social_ratio = categories.get('人情', 0) / actual_total
        if social_ratio <= 0.15:
            score += 5
    
    # 节约奖励分 (0-5)
    # 简单实现：与预算对比
    if total > 0 and actual_total < total * 0.9:
        score += 5
    elif total > 0 and actual_total < total * 0.95:
        score += 3
    
    return min(score, 100)

def identify_issues(budget_data, consumption_data):
    """识别消费问题"""
    issues = []
    total = budget_data.get('monthly_budget', 0)
    actual_total = consumption_data.get('total', 0)
    categories = consumption_data.get('categories', {})
    
    if total > 0 and actual_total > total * 1.1:
        issues.append(f"⚠️ 本月消费超出预算 {((actual_total - total) / total * 100):.1f}%")
    
    if actual_total > 0:
        food_ratio = categories.get('餐饮', 0) / actual_total
        if food_ratio > 0.55:
            issues.append(f"⚠️ 餐饮支出占比过高 ({(food_ratio * 100):.1f}%)，建议适当控制")
        
        entertainment_ratio = categories.get('娱乐', 0) / actual_total
        if entertainment_ratio > 0.2:
            issues.append(f"⚠️ 娱乐支出占比过高 ({(entertainment_ratio * 100):.1f}%)，建议减少不必要的娱乐消费")
        
        social_ratio = categories.get('人情', 0) / actual_total
        if social_ratio > 0.15:
            issues.append(f"⚠️ 人情支出占比过高 ({(social_ratio * 100):.1f}%)，建议合理规划社交开销")
    
    if not issues:
        issues.append("✅ 消费结构健康，继续保持！")
    
    return issues

def generate_suggestions(budget_data, consumption_data):
    """生成省钱优化方案"""
    suggestions = []
    total = budget_data.get('monthly_budget', 0)
    actual_total = consumption_data.get('total', 0)
    categories = consumption_data.get('categories', {})
    
    if total > 0 and actual_total > total:
        suggestions.append("💡 建议制定详细的每日消费计划，避免冲动消费")
        suggestions.append("💡 可以尝试使用「信封预算法」，将钱分成不同类别管理")
    
    if actual_total > 0:
        food_ratio = categories.get('餐饮', 0) / actual_total
        if food_ratio > 0.5:
            suggestions.append("💡 餐饮支出较高，建议多自己做饭，既健康又省钱")
        
        entertainment_ratio = categories.get('娱乐', 0) / actual_total
        if entertainment_ratio > 0.15:
            suggestions.append("💡 可以寻找一些免费或低成本的娱乐方式，如运动、阅读等")
    
    suggestions.append("💡 建议养成记账习惯，定期回顾消费记录")
    suggestions.append("💡 设置消费提醒，当接近预算上限时及时调整")
    
    return suggestions

def calculate_free_hours(budget_data, consumption_data):
    """计算每日空闲时长"""
    base_hours = 24 - 8 - 6 - 2 - 1 - 2  # 24 - 睡眠 - 学习 - 吃饭 - 通勤 - 其他必要
    
    # 计算消费相关耗时
    categories = consumption_data.get('categories', {})
    entertainment_hours = categories.get('娱乐', 0) / 50  # 每50元约1小时
    social_hours = (categories.get('人情', 0) / 100) * 2  # 每100元约2小时
    
    free_hours = base_hours - 1.5 - entertainment_hours - social_hours  # 1.5小时餐饮时间
    
    return max(free_hours, 1.0)  # 最少保留1小时空闲时间
