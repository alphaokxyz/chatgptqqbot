from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from revChatGPT.V1 import Chatbot
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment

# 定义两个聊天机器人账号
accounts = [
    {"email": "", "password": ""},
    {"email": "", "password": ""}
]

# 使用账号信息创建 chatbot 对象
chatbots = [Chatbot(config=account) for account in accounts]

# 当前使用的聊天机器人在 chatbots 列表中的索引
cur_chatbot_index = 0

# 定义一个事件处理器，用于处理机器人的聊天请求
chatgpt = on_message(rule=to_me(), priority=5)

# 使用装饰器将 chatgpt_handle 函数注册到 chatgpt 事件处理器中
@chatgpt.handle()
async def chatgpt_handle(bot: Bot, event: Event, state: T_State):
    global cur_chatbot_index  # 声明全局变量 cur_chatbot_index，用于指定当前使用的聊天机器人

    msg = str(event.message)  # 获取用户发送的消息
    response = ""  # 定义回复内容的初始值为空字符串
    sender_info = f'{event.get_user_id()}'  # 获取用户 ID，用于在回复消息前 @ 用户

    while True:
        try:
            # 使用当前的聊天机器人回复用户消息
            chatbot = chatbots[cur_chatbot_index]
            for data in chatbot.ask(msg):
                response = data["message"]
            break
        except Exception as e:
            # 如果当前聊天机器人出现异常，则切换到下一个聊天机器人
            cur_chatbot_index = (cur_chatbot_index + 1) % len(accounts)
            if cur_chatbot_index == 0:
                break

    if response:
        # 如果回复内容不为空，则 @ 用户并发送回复消息
        await chatgpt.finish(MessageSegment.at(sender_info) + response)
    else:
        # 如果回复内容为空，则提示用户请求超过次数限制
        await chatgpt.finish('两个chatgpt账号一小时内请求都超过60次,请联系开发者提供更多账号。')
