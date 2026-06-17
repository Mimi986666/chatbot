from datetime import datetime, timedelta
import os

OUTPUT_DIR = 'exports'

def parse_date(date_str):
    """解析日期字符串"""
    patterns = ['%Y-%m-%d', '%Y/%m/%d', '%m-%d', '%m/%d']
    for pattern in patterns:
        try:
            if pattern in ['%m-%d', '%m/%d']:
                date = datetime.strptime(date_str, pattern)
                return datetime(datetime.now().year, date.month, date.day)
            return datetime.strptime(date_str, pattern)
        except ValueError:
            continue
    return None

def calculate_days_left(exam_date):
    """计算距离考试的天数"""
    today = datetime.now().date()
    exam_date = exam_date.date()
    return max((exam_date - today).days, 0)

def generate_study_plan(study_data, daily_free_hours):
    """生成学习计划"""
    exam_date = study_data.get('exam_date')
    subjects = study_data.get('subjects', [])
    free_time = study_data.get('free_time', daily_free_hours)
    
    if not exam_date or not subjects:
        return []
    
    days_left = calculate_days_left(exam_date)
    if days_left == 0:
        return []
    
    total_hours = days_left * free_time
    
    # 为每个科目计算优先级和分配时长
    # 默认难度系数为3，重要程度为2
    plan = []
    total_priority = 0
    subject_plans = []
    
    for subject in subjects:
        difficulty = subject.get('difficulty', 3)
        importance = subject.get('importance', 2)
        priority = difficulty * importance
        total_priority += priority
        subject_plans.append({
            'name': subject['name'],
            'priority': priority,
            'difficulty': difficulty,
            'importance': importance
        })
    
    # 分配每日学习计划
    for day in range(1, days_left + 1):
        day_plan = {
            'day': day,
            'date': (datetime.now() + timedelta(days=day - 1)).strftime('%Y-%m-%d'),
            'schedule': []
        }
        
        morning_hours = min(3.0, free_time * 0.4)
        afternoon_hours = min(3.0, free_time * 0.4)
        evening_hours = free_time - morning_hours - afternoon_hours
        
        # 上午：理论学习、记忆类（难度高或重要性高）
        morning_subjects = sorted(subject_plans, key=lambda x: -x['difficulty'])[:2]
        for i, subj in enumerate(morning_subjects):
            if morning_hours > 0:
                hours = morning_hours / min(2, len(morning_subjects))
                day_plan['schedule'].append({
                    'time': '08:00-12:00',
                    'subject': subj['name'],
                    'hours': round(hours, 1),
                    'activity': '理论学习、知识点记忆'
                })
        
        # 下午：刷题、练习类
        afternoon_subjects = sorted(subject_plans, key=lambda x: -x['importance'])[:2]
        for i, subj in enumerate(afternoon_subjects):
            if afternoon_hours > 0:
                hours = afternoon_hours / min(2, len(afternoon_subjects))
                day_plan['schedule'].append({
                    'time': '14:00-18:00',
                    'subject': subj['name'],
                    'hours': round(hours, 1),
                    'activity': '刷题练习、真题模拟'
                })
        
        # 晚上：总结复习、查漏补缺
        if evening_hours > 0:
            day_plan['schedule'].append({
                'time': '19:00-22:00',
                'subject': '综合复习',
                'hours': round(evening_hours, 1),
                'activity': '错题回顾、知识点总结'
            })
        
        plan.append(day_plan)
    
    return plan

def export_plan_to_txt(study_plan, study_data):
    """导出学习计划到TXT文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    exam_date = study_data.get('exam_date')
    filename = f"学习计划_{exam_date.strftime('%Y%m%d')}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 40 + "\n")
        f.write(f"    期末备考学习计划\n")
        f.write("=" * 40 + "\n")
        f.write(f"考试日期：{exam_date.strftime('%Y年%m月%d日')}\n")
        f.write(f"剩余天数：{len(study_plan)}天\n")
        f.write("-" * 40 + "\n\n")
        
        for day_plan in study_plan:
            f.write(f"【第{day_plan['day']}天】{day_plan['date']}\n")
            f.write("-" * 20 + "\n")
            for schedule in day_plan['schedule']:
                f.write(f"  {schedule['time']}\n")
                f.write(f"    ├── 科目：{schedule['subject']}\n")
                f.write(f"    ├── 时长：{schedule['hours']}小时\n")
                f.write(f"    └── 任务：{schedule['activity']}\n")
            f.write("\n")
        
        f.write("=" * 40 + "\n")
        f.write("    加油！祝你考试顺利！\n")
        f.write("=" * 40 + "\n")
    
    return filepath

def adjust_plan(study_plan, adjustment):
    """调整学习计划"""
    # 简单实现：根据调整指令修改每日时长
    for day_plan in study_plan:
        for schedule in day_plan['schedule']:
            if '刷题' in adjustment:
                if '练习' in schedule['activity'] or '刷题' in schedule['activity']:
                    schedule['hours'] = min(schedule['hours'] + 1, 4)
            if '复习' in adjustment:
                if '复习' in schedule['activity']:
                    schedule['hours'] = min(schedule['hours'] + 0.5, 3)
    
    return study_plan
