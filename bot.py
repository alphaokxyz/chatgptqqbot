from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from revChatGPT.V1 import Chatbot as RevChatbot
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from EdgeGPT.ImageGen import ImageGen
import argparse
import json
import re
import random
import os
import asyncio

chatbot1_enabled = True  
chatbot2_enabled = False  
chatbot3_enabled = False  

accounts = [
    # {"email": "","password": ""},

    {"access_token": ""}
]

chatbots = [RevChatbot(config=account) for account in accounts]

cur_chatbot_index = 0

cookie_file = "/file/bing_cookies_2.json"
output_dir = "/file/picture"


switch_chatbot = on_command('switch_chatbot', aliases={'切换机器人'})

@switch_chatbot.handle()
async def switch_chatbot_handle(bot: Bot, event: Event, state: T_State):
    global chatbot1_enabled, chatbot2_enabled, chatbot3_enabled
    sender_info = f'{event.get_user_id()}'

    if chatbot1_enabled:
        chatbot1_enabled = False
        chatbot2_enabled = True
        await switch_chatbot.finish(MessageSegment.at(sender_info) + '已切换到new Bing')
    elif chatbot2_enabled:
        chatbot2_enabled = False
        chatbot3_enabled = True
        await switch_chatbot.finish(MessageSegment.at(sender_info) + '已切换到Bing画图')
    else:
        chatbot3_enabled = False
        chatbot1_enabled = True
        await switch_chatbot.finish(MessageSegment.at(sender_info) + '已切换到ChatGPT')

chat = on_message(rule=to_me(), priority=5)


@chat.handle()
async def chat_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.message)
    sender_info = f'{event.get_user_id()}'
    global cur_chatbot_index
    response = ""

    if chatbot1_enabled:
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
            await chat.finish(MessageSegment.at(sender_info) + 'Sorry, something went wrong')

    elif chatbot2_enabled:
        cookies1 = json.loads(open("/file/bing_cookies_1.json", encoding="utf-8").read())
        bot = await Chatbot.create(cookies=cookies1)
        try:
            a = await bot.ask(prompt=msg, conversation_style=ConversationStyle.creative, simplify_response=True)
            b = json.dumps(a, indent=2)
            c = json.loads(b)

            d = c["text"]

        except Exception as e:
            d = f"Sorry, something went wrong"
        finally:
            await bot.close()
            await chat.finish(MessageSegment.at(sender_info) + d)
    elif chatbot3_enabled:
        prompt = msg.strip()
        if not re.match(r'^[a-zA-Z0-9\s\W]+$', prompt):
            error_msg = 'We only support English now'
            await chat.finish(MessageSegment.at(sender_info) + error_msg)
            return
        output_dir = "/file/picture"
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        with open(cookie_file, encoding="utf-8") as file:
            cookie_json = json.load(file)
            for cookie in cookie_json:
                if cookie.get("name") == "_U":
                    U = cookie.get("value")
                    break
        image_generator = ImageGen(U)
        try:
            image_generator.save_images(
                image_generator.get_images(prompt),
                output_dir=output_dir,
            )
        except Exception as e:
            await chat.finish(MessageSegment.at(sender_info) + 'Sorry, something went wrong')
            return

        file_list = os.listdir(output_dir)
        file_count = len(file_list)
        if file_count != 0:
            if file_count == 1:
                aa = Message(f'[CQ:image,file=file:/file/picture/0.jpeg]')
                await chat.finish(MessageSegment.at(sender_info) + aa)
            elif file_count == 2:
                aa = Message(f'[CQ:image,file=file:/file/picture/0.jpeg][CQ:image,file=file:/file/picture/1.jpeg]')
                await chat.finish(MessageSegment.at(sender_info) + aa)
            elif file_count == 3:
                aa = Message(f'[CQ:image,file=file:/file/picture/0.jpeg][CQ:image,file=file:/file/picture/1.jpeg][CQ:image,file=file:/file/picture/2.jpeg]')
                await chat.finish(MessageSegment.at(sender_info) + aa)
            elif file_count == 4:
                aa = Message(f'[CQ:image,file=file:/file/picture/0.jpeg][CQ:image,file=file:/file/picture/1.jpeg][CQ:image,file=file:/file/picture/2.jpeg][CQ:image,file=file:/file/picture/3.jpeg]')
                await chat.finish(MessageSegment.at(sender_info) + aa)
            else:
                await chat.finish(MessageSegment.at(sender_info) + 'Sorry, something went wrong')
        else:
            await chat.finish(MessageSegment.at(sender_info) + 'Sorry, something went wrong')