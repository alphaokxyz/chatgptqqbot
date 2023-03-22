from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from EdgeGPT import Chatbot, ConversationStyle

chatgpt = on_message(rule=to_me(), priority=5)

@chatgpt.handle()
async def chatgpt_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.message)
    sender_info = f'{event.get_user_id()}'
    bot = Chatbot(cookiePath='/file/cookies.json')
    a = await bot.ask(prompt=msg, conversation_style=ConversationStyle.creative)
    b = a['item']['messages'][1]['text']
    await bot.close()
    await chatgpt.finish(MessageSegment.at(sender_info) + b)
