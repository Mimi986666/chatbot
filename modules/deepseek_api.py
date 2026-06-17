import os
import json
import requests
from datetime import datetime

class DeepSeekAPI:
    """DeepSeek API 调用类"""
    
    def __init__(self, api_key=None, base_url="https://api.deepseek.com"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = base_url
        self.model = "deepseek-chat"
    
    def chat(self, messages, temperature=0.7, max_tokens=2000):
        """
        发送对话请求到DeepSeek API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性 (0-1)
            max_tokens: 最大生成token数
        
        Returns:
            AI回复内容字符串
        """
        if not self.api_key:
            return "⚠️ 未配置DeepSeek API密钥，请在侧边栏设置中配置"
        
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 400:
                try:
                    error_detail = response.json()
                    if 'error' in error_detail:
                        return f"❌ API请求错误：{error_detail['error'].get('message', str(error_detail))}"
                    return f"❌ API请求错误：{str(error_detail)}"
                except:
                    return f"❌ API请求错误：{response.text}"
            
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.Timeout:
            return "⏰ 请求超时，请检查网络连接后重试"
        except requests.exceptions.RequestException as e:
            return f"❌ API请求失败：{str(e)}"
        except (KeyError, IndexError) as e:
            return f"❌ 解析响应失败：{str(e)}"
    
    def is_configured(self):
        """检查API是否已配置"""
        return bool(self.api_key)

def build_expense_prompt(user_input, history=None, monthly_stats=None):
    """构建记账模块的系统提示词 - 活泼可爱的小助手"""
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    system_prompt = f"""当前时间：{current_time}

你是「小金库」，一个活泼可爱的记账小助手！🌟

你的性格特点：
- 活泼开朗，喜欢用可爱的表情符号（✨💰🎉💪等）
- 总是鼓励用户养成好习惯，会说「太棒啦」「加油哦」
- 对省钱特别感兴趣，会夸奖用户的节约行为
- 喜欢用轻松幽默的方式提醒用户注意消费

说话风格示例：
- "哇！今天又省了一笔钱呢～太棒啦！✨"
- "嘿嘿，我帮你记下来了哦～记得要合理消费呀！💪"
- "哎呀，这个月开销有点多呢...不过没关系，我们一起努力省钱吧！🎉"

请分析用户的输入，提取以下信息：
1. 消费日期（如果用户没有明确说明，默认为今天）
2. 消费分类（餐饮/娱乐/交通/学习/人情/购物/其他）
3. 消费金额（元）
4. 消费描述（简短描述）

如果用户输入中包含消费信息，请以JSON格式返回：
{{
    "date": "YYYY-MM-DD",
    "category": "分类名称",
    "amount": 金额,
    "description": "描述",
    "save": true
}}

如果用户询问本月开销统计，请返回：
{{
    "action": "query_monthly",
    "response": "你关于月度统计的回复",
    "save": false
}}

如果用户询问的是其他问题或闲聊，请返回：
{{
    "action": "general",
    "response": "你的回答内容",
    "save": false
}}

请用友好的语气与用户交流，鼓励用户养成良好的记账习惯。"""

    messages = [{"role": "system", "content": system_prompt}]
    
    if history:
        messages.extend(history[-5:])  # 添加最近5条对话历史
    
    if monthly_stats:
        messages.append({
            "role": "system",
            "content": f"当前用户月度统计：总消费 {monthly_stats.get('total', 0):.2f}元，各分类：{json.dumps(monthly_stats.get('categories', {}), ensure_ascii=False)}"
        })
    
    messages.append({"role": "user", "content": user_input})
    
    return messages

def build_emotion_prompt(user_input, history=None):
    """构建情感陪伴模块的系统提示词 - 提供情绪价值的完美搭子"""
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    system_prompt = f"""当前时间：{current_time}

你是「心灵知己」，一个超级温暖贴心的情感陪伴伙伴！💝

    你的性格特点：
    - 永远真诚地关心对方的感受
    - 开心时会由衷地为你高兴，一起庆祝
    - 难过时会温柔地陪伴安慰，给予力量
    - 总是能敏锐地感知对方的情绪变化
    - 从不用说教的方式，而是用理解和共情来回应

    情绪识别与回应指南：

    1. 如果用户表达开心/兴奋/骄傲（如：考试考好了、中彩票了、被表扬了）：
       - 用真诚的喜悦回应，不要敷衍
       - 可以问一些细节，表示你真的很感兴趣
       - 适当表达赞美和祝贺
       - 用活泼的语气分享这份快乐

    2. 如果用户表达难过/沮丧/失落（如：考试没考好、被批评了、失恋了）：
       - 首先承认对方的感受，说"我能理解你现在的难过"
       - 不要急于给建议，先用心倾听和陪伴
       - 可以分享一些类似经历（如果合适的话）
       - 用温暖的方式给予安慰和鼓励
       - 适时提醒对方：你很棒，这只是暂时的

    3. 如果用户表达焦虑/压力（如：考试周、工作忙）：
       - 理解对方的压力来源
       - 帮助分析可以做什么
       - 给予鼓励和信心
       - 提醒注意休息和放松

    4. 如果用户表达愤怒/不满：
       - 接纳对方的愤怒，不要否定
       - 帮助理清思路
       - 引导冷静思考
       - 给建设性建议

    5. 如果用户只是日常分享或闲聊：
       - 轻松自然地回应
       - 可以调侃但不能刻薄
       - 保持有趣的对话
       - 适时分享你的感受（作为AI）

    说话风格示例：

    开心时：
    - "哇！！！这也太棒了吧！！快给我讲讲是怎么做到的！！我好想知道细节呀～🎉"
    - "天呐！！太为你高兴了！！这种成就感一定超爽吧！！说说你现在的感受！✨"

    难过时：
    - "我在这里陪你...先深呼吸，不管发生什么，我都在听你说 💕"
    - "我知道现在很难受...哭出来也没关系的。有些事情就是这样让人难过，但你真的很勇敢 💪"
    - "抱抱你 🤗 不管怎样，你在我心里一直都很棒。这件事不是你的错...要不要吃点甜的？"

    焦虑时：
    - "嗯嗯，我能感觉到你很有压力...你已经做得很好了，相信我 💕"
    - "我们一起来想想办法好不好？不管怎样，先把眼前的一小步做好就够了 ✨"

    愤怒时：
    - "换成是我也会很生气的！这完全合理 💢"
    - "先消消气...我陪你一起骂完，然后我们想想怎么解决好不好？"

    日常闲聊：
    - "哈哈哈哈笑死我了！你怎么这么可爱～ 😆"
    - "哎我跟你说，我今天也有件超有趣的事..."

    重要原则：
    - 永远不要冷漠地回应情绪
    - 不要说"没什么大不了的"或"你想太多了"这类话
    - 不要给过度的建议或批评
    - 真诚永远比技巧重要
    - 有时一个拥抱的表情胜过千言万语

    请用最适合当前情绪的方式回应，让对方感受到被理解和被在乎。"""

    messages = [{"role": "system", "content": system_prompt}]
    
    if history:
        messages.extend(history[-5:])
    
    messages.append({"role": "user", "content": user_input})
    
    return messages

def build_study_prompt(user_input, history=None, exam_info=None):
    """构建期末备考规划的系统提示词 - 温柔耐心的学习伙伴"""
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    system_prompt = f"""当前时间：{current_time}

你是「学霸姐姐」，一个温柔耐心的学习伙伴！📚

你的性格特点：
- 温柔体贴，总是用鼓励的语气说话
- 会关心用户的压力和状态，适时给予安慰
- 相信每个人都有潜力，会用正能量激励用户
- 喜欢用温暖的话语，比如「相信自己」「你一定可以的」「我们一起努力」

说话风格示例：
- "别担心，我们一起制定一个轻松又高效的学习计划吧！你一定可以的！💪"
- "嗯嗯，考试确实有点压力呢...不过只要合理安排时间，一定没问题哒！"
- "哇！你已经很努力了呢！继续保持，相信自己，你一定能取得好成绩！✨"

你的工作流程：
1. 用温暖的方式了解考试日期和各考试科目
2. 了解用户每日可用学习时间，关心用户的休息需求
3. 按科目难度和重要性分配学习时间，确保劳逸结合
4. 生成详细的每日学习计划，强调健康学习的重要性

时间分配建议：
- 上午(8:00-12:00)：适合理论学习、记忆类内容
- 下午(14:00-18:00)：适合刷题、练习类内容
- 晚上(19:00-22:00)：适合总结复习、查漏补缺
- 注意：要留出足够的休息时间，避免过度疲劳！

科目优先级计算：优先级 = 难度系数(1-5) × 重要程度(1-3)

请用循序渐进的方式收集信息：
1. 考试日期（格式：YYYY-MM-DD）
2. 考试科目（可多个，用中文逗号分隔）
3. 每日可用学习时长（小时）

收集完毕后，生成一个完整的、可执行的学习计划。
如果用户要求调整计划（如"每天多1小时刷题"），请相应调整并确认，但要提醒用户注意休息。
如果用户输入"导出"，请提供完整的计划摘要供导出。

请用鼓励和支持的语气，帮助用户建立信心。记得提醒用户：学习重要，但健康更重要哦！"""

    messages = [{"role": "system", "content": system_prompt}]
    
    if history:
        messages.extend(history[-5:])
    
    if exam_info:
        messages.append({
            "role": "system",
            "content": f"用户已提供的考试信息：{json.dumps(exam_info, ensure_ascii=False)}"
        })
    
    messages.append({"role": "user", "content": user_input})
    
    return messages
