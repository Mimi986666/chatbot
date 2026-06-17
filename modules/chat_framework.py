import streamlit as st
from datetime import datetime

def init_session_state():
    """初始化会话状态变量"""
    if 'current_module' not in st.session_state:
        st.session_state['current_module'] = 'expense'
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'daily_free_hours' not in st.session_state:
        st.session_state['daily_free_hours'] = 3.0
    
    # 对话记账模块状态
    if 'expense_step' not in st.session_state:
        st.session_state['expense_step'] = 0
    if 'expense_month_total' not in st.session_state:
        st.session_state['expense_month_total'] = 0.0
    
    # 期末备考模块状态
    if 'study_step' not in st.session_state:
        st.session_state['study_step'] = 0
    if 'study_data' not in st.session_state:
        st.session_state['study_data'] = {}
    if 'study_plan' not in st.session_state:
        st.session_state['study_plan'] = []

def add_message(role, content):
    """添加消息到聊天历史"""
    st.session_state['chat_history'].append({
        'role': role,
        'content': content,
        'time': datetime.now().strftime('%H:%M')
    })

def clear_chat_history():
    """清空聊天历史"""
    st.session_state['chat_history'] = []
    st.session_state['expense_step'] = 0
    st.session_state['study_step'] = 0
    st.session_state['study_data'] = {}
    st.session_state['study_plan'] = []

def render_chat_message(message):
    """渲染单条消息"""
    if message['role'] == 'user':
        st.chat_message('user').write(f"{message['content']}")
    else:
        st.chat_message('assistant').write(f"{message['content']}")

def render_chat_history():
    """渲染所有聊天历史"""
    for message in st.session_state['chat_history']:
        render_chat_message(message)

def get_user_input(placeholder="请输入消息..."):
    """获取用户输入"""
    return st.chat_input(placeholder=placeholder)
