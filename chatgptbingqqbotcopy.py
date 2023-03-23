from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from revChatGPT.V1 import Chatbot as RevChatbot
from EdgeGPT import Chatbot, ConversationStyle


chatbot1_enabled = True  # 标记第一个聊天机器人是否启用
chatbot2_enabled = False  # 标记第二个聊天机器人是否启用

accounts = [
    {"email": "@gmail.com", "password": ""},
    {"email": "@gmail.com", "password": ""}
]

chatbots = [RevChatbot(config=account) for account in accounts]

cur_chatbot_index = 0


switch_chatbot = on_command('switch_chatbot', aliases={'切换机器人'})

@switch_chatbot.handle()
async def switch_chatbot_handle(bot: Bot, event: Event, state: T_State):
    global chatbot1_enabled, chatbot2_enabled
    sender_info = f'{event.get_user_id()}'

    if chatbot1_enabled:
        chatbot1_enabled = False
        chatbot2_enabled = True
        await switch_chatbot.finish(MessageSegment.at(sender_info) + '已切换到new Bing')
    else:
        chatbot1_enabled = True
        chatbot2_enabled = False
        await switch_chatbot.finish(MessageSegment.at(sender_info) + '已切换到ChatGPT')

# 根据当前聊天机器人的启用情况选择使用哪个聊天机器人进行回复
chat = on_message(rule=to_me(), priority=5)


@chat.handle()
async def chat_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.message)
    sender_info = f'{event.get_user_id()}'
    global cur_chatbot_index
    response = ""

    if chatbot1_enabled:
        # 使用第一个聊天机器人进行回复
        # ...
        while True:
            try:
                chatbot = chatbots[cur_chatbot_index]
                for data in chatbot.ask(msg):
                    response = data["message"]
                break
            except Exception as e:
                cur_chatbot_index = (cur_chatbot_index + 1) % len(accounts)
                if cur_chatbot_index == 0:
                    break

        if response:
            await chat.finish(MessageSegment.at(sender_info) + response)
        else:
            await chat.finish(MessageSegment.at(sender_info) + 'error')

    elif chatbot2_enabled:
        # 使用第二个聊天机器人进行回复
        # ...
        bot = Chatbot(cookiePath='/file/cookies.json')
        a = await bot.ask(prompt=msg, conversation_style=ConversationStyle.creative)
        b = a['item']['messages'][1]['text']
        await bot.close()
        await chat.finish(MessageSegment.at(sender_info) + b)
