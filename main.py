import streamlit as st
import os
from dotenv import load_dotenv
from modules.chat_framework import init_session_state, add_message, clear_chat_history, render_chat_history, get_user_input
from modules.expense_tracker import init_csv, parse_expense, save_expense, get_monthly_total, get_monthly_by_category, get_all_expense_data
from modules.study_planner import parse_date, generate_study_plan, export_plan_to_txt, adjust_plan
from modules.deepseek_api import DeepSeekAPI, build_expense_prompt, build_emotion_prompt, build_study_prompt
from config import DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
from datetime import datetime
import json

# 加载.env文件中的环境变量
load_dotenv()

# 页面配置
st.set_page_config(page_title="三合一智能助手", page_icon="🤖", layout="wide")

# 初始化会话状态和CSV
init_session_state()
init_csv()

# 初始化DeepSeek API
def get_deepseek_api():
    """获取DeepSeek API实例"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key and 'deepseek_api_key' in st.session_state:
        api_key = st.session_state['deepseek_api_key']
    return DeepSeekAPI(api_key=api_key)

# 侧边栏
with st.sidebar:
    st.markdown("""
    <style>
        /* ===== 全局动画 ===== */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            25% { transform: translateY(-5px) rotate(2deg); }
            75% { transform: translateY(3px) rotate(-2deg); }
        }
        @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px rgba(255,107,107,0.3); }
            50% { box-shadow: 0 0 20px rgba(255,107,107,0.6), 0 0 40px rgba(255,107,107,0.3); }
        }
        @keyframes typing {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
        }
        @keyframes gradientMove {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* ===== 页面整体 ===== */
        .stApp {
            animation: fadeIn 0.8s ease-out;
        }

        /* ===== 侧边栏按钮 ===== */
        div[data-testid="stVerticalBlock"] > div:has(> div > button:contains("💰")) {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-radius: 16px;
            padding: 18px;
            margin: 12px 0;
            border: 2px solid #ff9800;
            transition: all 0.3s ease;
            animation: slideInLeft 0.6s ease-out;
        }
        div[data-testid="stVerticalBlock"] > div:has(> div > button:contains("💰")):hover {
            transform: translateX(8px) scale(1.02);
            box-shadow: 0 8px 25px rgba(255,152,0,0.4);
        }
        div[data-testid="stVerticalBlock"] > div:has(> div > button:contains("💝")) {
            background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%);
            border-radius: 16px;
            padding: 18px;
            margin: 12px 0;
            border: 2px solid #e91e63;
            transition: all 0.3s ease;
            animation: slideInLeft 0.6s ease-out 0.15s both;
        }
        div[data-testid="stVerticalBlock"] > div:has(> div > button:contains("💝")):hover {
            transform: translateX(8px) scale(1.02);
            box-shadow: 0 8px 25px rgba(233,30,99,0.4);
        }
        div[data-testid="stVerticalBlock"] > div:has(> div > button:contains("")) {
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border-radius: 16px;
            padding: 18px;
            margin: 12px 0;
            border: 2px solid #9c27b0;
            transition: all 0.3s ease;
            animation: slideInLeft 0.6s ease-out 0.3s both;
        }
        div[data-testid="stVerticalBlock"] > div:has(> div > button:contains("📚")):hover {
            transform: translateX(8px) scale(1.02);
            box-shadow: 0 8px 25px rgba(156,39,176,0.4);
        }
        div[data-testid="stVerticalBlock"] button {
            width: 100% !important;
            font-size: 18px !important;
            font-weight: bold !important;
            padding: 18px 20px !important;
            border-radius: 14px !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stVerticalBlock"] button:hover {
            animation: pulse 0.5s ease;
        }

        /* ===== 聊天消息动画 ===== */
        .stChatMessage {
            animation: slideInUp 0.5s ease-out;
        }
        .stChatMessage:nth-child(even) {
            animation: slideInRight 0.5s ease-out;
        }
        .stChatMessage:nth-child(odd) {
            animation: slideInLeft 0.5s ease-out;
        }

        /* ===== 聊天输入框 ===== */
        .stChatInput {
            animation: fadeIn 0.6s ease-out 0.4s both;
        }

        /* ===== 模块标题卡片 ===== */
        div[style*="background-color"] {
            animation: fadeIn 0.6s ease-out;
        }

        /* ===== 侧边栏标题 ===== */
        h1 {
            font-size: 22px !important;
            margin-bottom: 5px !important;
        }

        /* ===== 小贴士卡片 ===== */
        div[data-testid="stAlert"] {
            animation: fadeIn 0.8s ease-out 0.5s both;
        }

        /* ===== 按钮点击波纹效果 ===== */
        button:hover {
            position: relative;
            overflow: hidden;
        }
        button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        button:active::after {
            width: 300px;
            height: 300px;
        }

        /* ===== 滚动条美化 ===== */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #ff6b6b, #ee5a24);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #ee5a24, #ff6b6b);
        }

        /* ===== 加载动画 ===== */
        .stSpinner > div {
            animation: bounce 1s ease-in-out infinite;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title(" 智能助手")
    
    st.markdown("---")
    st.markdown("### 🎮 选一个模块来玩吧！✨")
    
    current_module = st.session_state.get('current_module', 'expense')
    
    if st.button("💰 小金库", key="btn_expense", use_container_width=True):
        st.session_state['current_module'] = 'expense'
        st.rerun()
    
    if st.button("💝 心灵知己", key="btn_emotion", use_container_width=True):
        st.session_state['current_module'] = 'emotion'
        st.rerun()
    
    if st.button("📚 学霸姐姐", key="btn_study", use_container_width=True):
        st.session_state['current_module'] = 'study'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 小贴士")
    st.info("点击上方卡片切换模块，每个AI都有独特性格哦～！")

# 获取AI API实例
deepseek_api = get_deepseek_api()
use_ai_mode = deepseek_api.is_configured()

# CSS: 用户消息头像移到右边
st.markdown("""
<style>
    /* 用户消息：头像在右，内容在左 */
    .stChatMessage[data-testid="stChatMessage"]:has([data-testid="stChatAvatarUser"]) {
        flex-direction: row-reverse !important;
    }
    .stChatMessage[data-testid="stChatMessage"]:has([data-testid="stChatAvatarUser"]) [data-testid="stChatMessageContent"] {
        margin-right: 0 !important;
        margin-left: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

def format_history_for_api(chat_history):
    """将聊天历史格式化为API消息列表"""
    messages = []
    for msg in chat_history[-10:]:  # 最近10条
        role = "user" if msg['role'] == 'user' else "assistant"
        messages.append({"role": role, "content": msg['content']})
    return messages

# ========== 模块渲染区域 ==========
current_module = st.session_state.get('current_module', 'expense')

# ========== 模块1：对话记账 ==========
if current_module == 'expense':
    st.markdown("""
    <div style='background-color: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='color: #ff9800; margin: 0;'>🌟 小金库 - 活泼可爱的记账小助手</h4>
        <p style='color: #666; margin: 5px 0;'>嗨～我是小金库！我会帮你记录每一笔消费，还会鼓励你省钱哦！✨</p>
        <p style='color: #999; margin: 0; font-size: 12px;'>示例：今天晚饭22元、昨天买了本书45元、查看本月开销</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'chat_history_expense' not in st.session_state:
        st.session_state['chat_history_expense'] = []
    
    for msg in st.session_state['chat_history_expense']:
        if msg['role'] == 'user':
            _, user_col = st.columns([2, 1])
            with user_col:
                st.markdown(f"""
                <div style='display:flex;justify-content:flex-end;align-items:flex-start;gap:8px;margin-bottom:4px;'>
                    <div style='background:#e3f2fd;padding:10px 14px;border-radius:12px;max-width:100%;'>
                        {msg['content']}
                    </div>
                    <div style='width:36px;height:36px;border-radius:50%;background:#ff6b6b;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;'>
                        😊
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.chat_message('assistant').write(msg['content'])
    
    if not st.session_state['chat_history_expense']:
        welcome_msg = "嗨～我是小金库！🌟\n\n我会帮你记录每一笔消费，还会鼓励你省钱哦！\n\n你可以告诉我今天花了多少钱，比如「今天晚饭22元」，或者问我「查看本月开销」～\n\n来吧，让我们一起管理好钱包吧！💪"
        st.session_state['chat_history_expense'].append({'role': 'assistant', 'content': welcome_msg})
        st.chat_message('assistant').write(welcome_msg)
    
    user_input = st.chat_input("和小金库聊聊消费...", key="expense_input")
    
    if user_input:
        st.session_state['chat_history_expense'].append({'role': 'user', 'content': user_input})
        
        if use_ai_mode:
            monthly_stats = {
                'total': get_monthly_total(),
                'categories': get_monthly_by_category()
            }
            
            history = format_history_for_api(st.session_state['chat_history_expense'])
            messages = build_expense_prompt(user_input, history, monthly_stats)
            
            with st.spinner("🤔 小金库思考中..."):
                ai_response = deepseek_api.chat(messages, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS)
            
            try:
                if ai_response and '{' in ai_response:
                    start = ai_response.find('{')
                    end = ai_response.rfind('}') + 1
                    if end > start:
                        data = json.loads(ai_response[start:end])
                        
                        if data.get('save'):
                            expense_data = {
                                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                                'category': data.get('category', '其他'),
                                'amount': float(data.get('amount', 0)),
                                'description': data.get('description', ''),
                                'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if expense_data['amount'] > 0:
                                save_expense(expense_data)
                                friendly_response = ai_response[:start].strip()
                                if not friendly_response:
                                    friendly_response = f"✅ 好的！我已帮你记下来了哦～\n\n📅 日期：{expense_data['date']}\n🏷️ 分类：{expense_data['category']}\n💰 金额：{expense_data['amount']:.2f}元\n\n记得要合理消费呀！💪"
                                st.session_state['chat_history_expense'].append({'role': 'assistant', 'content': friendly_response})
                                st.rerun()
                        elif data.get('action') == 'query_monthly':
                            st.session_state['chat_history_expense'].append({'role': 'assistant', 'content': data.get('response', ai_response)})
                            st.rerun()
                        elif data.get('action') == 'general':
                            st.session_state['chat_history_expense'].append({'role': 'assistant', 'content': data.get('response', ai_response)})
                            st.rerun()
            except json.JSONDecodeError:
                pass
            
            st.session_state['chat_history_expense'].append({'role': 'assistant', 'content': ai_response})
            st.rerun()
        else:
            if user_input.lower() in ['查看本月开销', '本月消费', '消费统计']:
                total = get_monthly_total()
                category_data = get_monthly_by_category()
                
                response = f"💰 本月总消费：{total:.2f}元\n\n"
                for cat, amount in category_data.items():
                    response += f"• {cat}：{amount:.2f}元\n"
                
                st.session_state['chat_history_expense'].append({'role': 'assistant', 'content': response})
            else:
                expense_data = parse_expense(user_input)
                
                if expense_data['amount'] > 0:
                    save_expense(expense_data)
                    response = f"✅ 已记录消费：\n"
                    response += f"日期：{expense_data['date']}\n"
                    response += f"分类：{expense_data['category']}\n"
                    response += f"金额：{expense_data['amount']:.2f}元\n"
                    response += f"描述：{expense_data['description']}"
                else:
                    response = "❌ 未能识别消费金额，请重新输入（例如：今天晚饭22元）"
                
                st.session_state['chat_history_expense'].append({'role': 'assistant', 'content': response})
            st.rerun()

# ========== 模块2：情感陪伴 ==========
elif current_module == 'emotion':
    st.markdown("""
    <div style='background-color: #fce4ec; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='color: #e91e63; margin: 0;'>💝 心灵知己 - 温暖贴心的情感陪伴伙伴</h4>
        <p style='color: #666; margin: 5px 0;'>嗨～我是心灵知己！我会在这里陪伴你，开心时一起分享，难过时给你安慰 💕</p>
        <p style='color: #999; margin: 0; font-size: 12px;'>不管你有什么心情，都可以和我聊聊～</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'chat_history_emotion' not in st.session_state:
        st.session_state['chat_history_emotion'] = []
    
    for msg in st.session_state['chat_history_emotion']:
        if msg['role'] == 'user':
            _, user_col = st.columns([2, 1])
            with user_col:
                st.markdown(f"""
                <div style='display:flex;justify-content:flex-end;align-items:flex-start;gap:8px;margin-bottom:4px;'>
                    <div style='background:#fce4ec;padding:10px 14px;border-radius:12px;max-width:100%;'>
                        {msg['content']}
                    </div>
                    <div style='width:36px;height:36px;border-radius:50%;background:#e91e63;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;'>
                        😊
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.chat_message('assistant').write(msg['content'])
    
    if not st.session_state['chat_history_emotion']:
        welcome_msg = "嗨～我是心灵知己 💝\n\n不管你开心还是难过，我都在这里陪着你...\n\n开心的时候，我们可以一起分享喜悦 🎉\n难过的时刻，我会温柔地倾听和安慰 🤗\n\n有什么想说的吗？我准备好了倾听你的一切 💕"
        st.session_state['chat_history_emotion'].append({'role': 'assistant', 'content': welcome_msg})
        st.chat_message('assistant').write(welcome_msg)
    
    user_input = st.chat_input("和心灵知己说说心里话...", key="emotion_input")
    
    if user_input:
        st.session_state['chat_history_emotion'].append({'role': 'user', 'content': user_input})
        
        if use_ai_mode:
            history = format_history_for_api(st.session_state['chat_history_emotion'])
            messages = build_emotion_prompt(user_input, history)
            
            with st.spinner("💭 心灵知己在倾听..."):
                ai_response = deepseek_api.chat(messages, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS)
            
            st.session_state['chat_history_emotion'].append({'role': 'assistant', 'content': ai_response})
            st.rerun()
        else:
            response = "💝 我在这里听你说...\n\n"
            response += "有什么想说的吗？我准备好了倾听你的一切 💕"
            
            st.session_state['chat_history_emotion'].append({'role': 'assistant', 'content': response})
            st.rerun()

# ========== 模块3：期末备考 ==========
elif current_module == 'study':
    st.markdown("""
    <div style='background-color: #f3e5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='color: #9c27b0; margin: 0;'>📚 学霸姐姐 - 温柔耐心的学习伙伴</h4>
        <p style='color: #666; margin: 5px 0;'>嗨～我是学霸姐姐！我会帮你制定学习计划，陪你一起备考哦！</p>
        <p style='color: #999; margin: 0; font-size: 12px;'>告诉我考试日期和科目，我会给你一份轻松高效的学习计划～</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'chat_history_study' not in st.session_state:
        st.session_state['chat_history_study'] = []
    
    for msg in st.session_state['chat_history_study']:
        if msg['role'] == 'user':
            _, user_col = st.columns([2, 1])
            with user_col:
                st.markdown(f"""
                <div style='display:flex;justify-content:flex-end;align-items:flex-start;gap:8px;margin-bottom:4px;'>
                    <div style='background:#f3e5f5;padding:10px 14px;border-radius:12px;max-width:100%;'>
                        {msg['content']}
                    </div>
                    <div style='width:36px;height:36px;border-radius:50%;background:#9c27b0;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;'>
                        😊
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.chat_message('assistant').write(msg['content'])
    
    if not st.session_state['chat_history_study']:
        welcome_msg = "嗨～我是学霸姐姐！📚\n\n我会帮你制定学习计划，陪你一起备考哦！\n\n告诉我考试日期和科目，我会给你一份轻松高效的学习计划！\n\n别担心，相信自己，你一定可以的！💪"
        st.session_state['chat_history_study'].append({'role': 'assistant', 'content': welcome_msg})
        st.chat_message('assistant').write(welcome_msg)
    
    user_input = st.chat_input("和学霸姐姐聊聊学习...", key="study_input")
    
    if user_input:
        st.session_state['chat_history_study'].append({'role': 'user', 'content': user_input})
        
        if use_ai_mode:
            history = format_history_for_api(st.session_state['chat_history_study'])
            
            messages = build_study_prompt(
                user_input,
                history,
                st.session_state.get('study_data', {})
            )
            
            with st.spinner("🤔 学霸姐姐规划中..."):
                ai_response = deepseek_api.chat(messages, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS)
            
            if user_input.lower() == '导出':
                plan = st.session_state.get('study_plan', [])
                study_data = st.session_state.get('study_data', {})
                
                if plan and study_data:
                    filepath = export_plan_to_txt(plan, study_data)
                    export_msg = f"📥 学习计划已导出到：{filepath}\n\n✅ 导出成功！记得要劳逸结合哦～"
                    st.session_state['chat_history_study'].append({'role': 'assistant', 'content': export_msg})
                else:
                    st.session_state['chat_history_study'].append({'role': 'assistant', 'content': "❌ 暂无学习计划可导出，请先生成学习计划哦～"})
                st.rerun()
            else:
                    st.session_state['chat_history_study'].append({'role': 'assistant', 'content': ai_response})
                    
                    import re
                    
                    date_patterns = [
                        r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
                        r'(\d{1,2}[-/月]\d{1,2}[日]?)'
                    ]
                    
                    for pattern in date_patterns:
                        date_match = re.search(pattern, ai_response)
                        if date_match:
                            exam_date = parse_date(date_match.group(1))
                            if exam_date:
                                st.session_state.setdefault('study_data', {})['exam_date'] = exam_date
                                break
                    
                    subjects = re.findall(r'《?([^《,\n，]+)》?', ai_response)
                    if subjects:
                        valid_subjects = [s.strip() for s in subjects if len(s.strip()) > 1 and s.strip() not in ['科目', '考试', '复习']]
                        if valid_subjects:
                            st.session_state.setdefault('study_data', {})['subjects'] = [
                                {'name': s, 'difficulty': 3, 'importance': 2} for s in valid_subjects[:5]
                            ]
                    
                    study_data = st.session_state.get('study_data', {})
                    if study_data.get('exam_date') and study_data.get('subjects'):
                        plan = generate_study_plan(study_data, 3.0)
                        st.session_state['study_plan'] = plan
                        
                        if plan:
                            plan_preview = f"\n\n📅 学习计划已生成！距离考试还有 {len(plan)} 天\n\n"
                            plan_preview += "【前3天计划预览】\n"
                            for day_plan in plan[:3]:
                                plan_preview += f"\n第{day_plan['day']}天 - {day_plan['date']}\n"
                                for schedule in day_plan['schedule']:
                                    plan_preview += f"  • {schedule['time']}: {schedule['subject']} ({schedule['hours']}h)\n"
                            plan_preview += "\n💡 输入「导出」保存完整计划\n\n记住：学习重要，但健康更重要哦！💪"
                            
                            st.session_state['chat_history_study'].append({'role': 'assistant', 'content': plan_preview})
                    
                    st.rerun()
        else:
            step = st.session_state.get('study_step', 0)
            study_data = st.session_state.get('study_data', {})
            
            if step == 0:
                response = "📚 欢迎使用期末备考规划！\n\n"
                response += "请提供以下信息：\n"
                response += "1. 考试日期（格式：YYYY-MM-DD 或 MM-DD）"
                st.session_state['chat_history_study'].append({'role': 'assistant', 'content': response})
                st.session_state['study_step'] = 1
                st.rerun()
            
            elif step == 1:
                exam_date = parse_date(user_input)
                if exam_date:
                    study_data['exam_date'] = exam_date
                    response = "2. 请输入考试科目（多个科目用逗号分隔）"
                    st.session_state['chat_history_study'].append({'role': 'assistant', 'content': response})
                    st.session_state['study_step'] = 2
                else:
                    response = "❌ 日期格式不正确，请重新输入（例如：6-20 或 2024-06-20）"
                    st.session_state['chat_history_study'].append({'role': 'assistant', 'content': response})
                st.rerun()
            
            elif step == 2:
                subjects = [s.strip() for s in user_input.replace('，', ',').split(',') if s.strip()]
                if subjects:
                    study_data['subjects'] = [{'name': s, 'difficulty': 3, 'importance': 2} for s in subjects]
                    response = "3. 每日可用学习时长（小时），留空则使用默认空闲时长"
                    st.session_state['chat_history_study'].append({'role': 'assistant', 'content': response})
                    st.session_state['study_step'] = 3
                else:
                    response = "❌ 请至少输入一个科目"
                    st.session_state['chat_history_study'].append({'role': 'assistant', 'content': response})
                st.rerun()
            
            elif step == 3:
                try:
                    free_time = float(user_input)
                    study_data['free_time'] = free_time
                except ValueError:
                    study_data['free_time'] = 3.0
                
                st.session_state['study_data'] = study_data
                
                plan = generate_study_plan(study_data, 3.0)
                st.session_state['study_plan'] = plan
                
                if plan:
                    response = f"✅ 学习计划已生成！距离考试还有 {len(plan)} 天\n\n"
                    response += "📅 学习计划预览：\n"
                    response += "---\n"
                    
                    for day_plan in plan[:3]:
                        response += f"【第{day_plan['day']}天】{day_plan['date']}\n"
                        for schedule in day_plan['schedule']:
                            response += f"  • {schedule['time']}: {schedule['subject']} ({schedule['hours']}小时)\n"
                        response += "\n"
                    
                    if len(plan) > 3:
                        response += f"... 还有 {len(plan) - 3} 天的计划...\n\n"
                    
                    response += "💡 你可以输入调整指令（如：每天多1小时刷题），或输入「导出」保存计划"
                else:
                    response = "❌ 无法生成学习计划，请检查输入的考试日期"
                
                st.session_state['chat_history_study'].append({'role': 'assistant', 'content': response})
                st.session_state['study_step'] = 4
                st.rerun()
            
            elif step >= 4:
                if user_input.lower() == '导出':
                    plan = st.session_state.get('study_plan', [])
                    if plan:
                        filepath = export_plan_to_txt(plan, study_data)
                        response = f"📥 学习计划已导出到：{filepath}\n\n"
                        response += "✅ 导出成功！"
                    else:
                        response = "❌ 暂无学习计划可导出"
                else:
                    plan = st.session_state.get('study_plan', [])
                    if plan:
                        plan = adjust_plan(plan, user_input)
                        st.session_state['study_plan'] = plan
                        
                        response = f"🔄 已根据你的要求调整学习计划\n\n"
                        response += "📅 调整后的计划预览：\n"
                        response += "---\n"
                        
                        for day_plan in plan[:2]:
                            response += f"【第{day_plan['day']}天】{day_plan['date']}\n"
                            for schedule in day_plan['schedule']:
                                response += f"  • {schedule['time']}: {schedule['subject']} ({schedule['hours']}小时)\n"
                            response += "\n"
                        
                        response += "💡 输入「导出」保存计划，或继续调整"
                    else:
                        response = "❌ 暂无学习计划可调整"
                
                st.session_state['chat_history_study'].append({'role': 'assistant', 'content': response})
                st.rerun()