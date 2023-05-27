from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import on_message
from nonebot import on_regex
from nonebot.adapters.ntchat import MessageSegment,TextMessageEvent
import json
import re
import random
import os
import asyncio
import argparse
from base64 import b64encode
from io import BytesIO
from pathlib import Path

from EdgeGPT import Chatbot, ConversationStyle
from ImageGen import ImageGen
from revChatGPT.V1 import Chatbot as RevChatbot
chatbot1_enabled = True  
chatbot2_enabled = False  
chatbot3_enabled = False  

accounts = [
    {"access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJhbHBoYW9rdGVzdDAyQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS9hdXRoIjp7InVzZXJfaWQiOiJ1c2VyLXpJVTdFaHVaTEJ3UWxtSGJGaU5DRjVSQSJ9LCJpc3MiOiJodHRwczovL2F1dGgwLm9wZW5haS5jb20vIiwic3ViIjoiYXV0aDB8NjQxNmYxYzhlMmQ0NjdiNTg2ZWU1MjNhIiwiYXVkIjpbImh0dHBzOi8vYXBpLm9wZW5haS5jb20vdjEiLCJodHRwczovL29wZW5haS5vcGVuYWkuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY4NDQwMTIyMiwiZXhwIjoxNjg1NjEwODIyLCJhenAiOiJUZEpJY2JlMTZXb1RIdE45NW55eXdoNUU0eU9vNkl0RyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgbW9kZWwucmVhZCBtb2RlbC5yZXF1ZXN0IG9yZ2FuaXphdGlvbi5yZWFkIG9yZ2FuaXphdGlvbi53cml0ZSJ9.UXcxm4EzmZ7CZV3sEsItDbIueF9e-lD9j6LjLqTLoWXWhXTPV19KbURENXF2Bmq0yQx_YNtasp8SJQSN2cnMEzBYyU3yH9kONvFr1eiOGz-LZjTwXsoQVDXZhheFwV22b-OqnW3pQ6EbttRuSQPhC10RF2BO0hbFK79tlh3uBqgfdQQi513VsWqq0WWLi_ebRbeQW1oWF8VzDnLeyw1xMIrPgUqBjUIP0TsDhRydS6Q_vlwZPWYOopwFqRJ_-qDmqmweqHRTk2nbxWVAZKWiR32Eu0N7CVk9m0-dOTiCGOHG8PEFn2TyH0vyPDHiScTWYhCdeHYiDtxP0IQOL2na4A"},
    {"access_token": "<access_token>"}
]

chatbots = [RevChatbot(config=account) for account in accounts]

cur_chatbot_index = 0

cookie_file = "C:\File\cookies2.json"
output_dir = "C:\File\picture"

switch_chatbot = on_message(rule=to_me(), priority=5)

@switch_chatbot.handle()
async def switch_chatbot_handle(bot: Bot, event: Event, state: T_State):
    global chatbot1_enabled, chatbot2_enabled, chatbot3_enabled
    msg = str(event.message)
    msg2 = msg[len("@本群最浪 "):]
    if msg2 == "切换机器人":
        if chatbot1_enabled:
            chatbot1_enabled = False
            chatbot2_enabled = True
            await switch_chatbot.finish('已切换到new Bing')
        elif chatbot2_enabled:
            chatbot2_enabled = False
            chatbot3_enabled = True
            await switch_chatbot.finish('已切换到Bing画图')
        else:
            chatbot3_enabled = False
            chatbot1_enabled = True
            await switch_chatbot.finish('已切换到ChatGPT')
    


chat = on_message(rule=to_me(), priority=5)
cookies = json.loads(open("C:\File\cookies.json", encoding="utf-8").read())
bot2 = None


@chat.handle()
async def chat_handle(bot: Bot, event: TextMessageEvent, state: T_State):
    msg = str(event.message)
    msg2 = msg[len("@本群最浪 "):]
    global cur_chatbot_index
    response = ""

    if chatbot1_enabled:
        while True:
            try:
                chatbot = chatbots[cur_chatbot_index]
                for data in chatbot.ask(msg2):
                    response = data["message"]
                break
            except Exception as e:
                cur_chatbot_index = (cur_chatbot_index + 1) % len(accounts)
                if cur_chatbot_index == 0:
                    break

        if response:
            await chat.finish(response)
        else:
            await chat.finish('Sorry, something went wrong')

    elif chatbot2_enabled:
        global bot2
        if not bot2:
            bot2 =await Chatbot.create(cookies=cookies)
        response = await bot2.ask(prompt=msg2, conversation_style=ConversationStyle.creative)
        reply = response['item']['messages'][1]['text']
        if reply:
            await chat.finish(reply)
        else:
            await chat.finish('Sorry, something went wrong')
    
    elif chatbot3_enabled:
        prompt = msg2.strip()
        if not re.match(r'^[a-zA-Z0-9\s\W]+$', prompt):
            error_msg = 'We only support English now'
            await chat.finish(error_msg)
            return
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
        image_generator = ImageGen(U, True)
        try:
            image_generator.save_images(
                image_generator.get_images(prompt),
                output_dir=output_dir,
            )
        except Exception as e:
            await chat.finish('Sorry, something went wrong')
            return

        file_list = os.listdir(output_dir)
        file_count = len(file_list)
        if file_count != 0:
            if file_count == 1:
                url1 = "http://127.0.0.1/picture/0.jpeg"
                image1 = MessageSegment.image(url1)
                await chat.finish(image1)
            elif file_count == 2:
                url1 = "http://127.0.0.1/picture/0.jpeg"
                url2 = "http://127.0.0.1/picture/1.jpeg"
                image1 = MessageSegment.image(url1)
                image2 = MessageSegment.image(url2)
                await chat.send(image1)
                await chat.finish(image2)
            elif file_count == 3:
                url1 = "http://127.0.0.1/picture/0.jpeg"
                url2 = "http://127.0.0.1/picture/1.jpeg"
                url3 = "http://127.0.0.1/picture/2.jpeg"
                image1 = MessageSegment.image(url1)
                image2 = MessageSegment.image(url2)
                image3 = MessageSegment.image(url3)
                await chat.send(image1)
                await chat.send(image2)
                await chat.finish(image3)
            elif file_count == 4:
                url1 = "http://127.0.0.1/picture/0.jpeg"
                url2 = "http://127.0.0.1/picture/1.jpeg"
                url3 = "http://127.0.0.1/picture/2.jpeg"
                url4 = "http://127.0.0.1/picture/3.jpeg"
                image1 = MessageSegment.image(url1)
                image2 = MessageSegment.image(url2)
                image3 = MessageSegment.image(url3)
                image4 = MessageSegment.image(url4)
                
                await chat.send(image1)
                await chat.send(image2)
                await chat.send(image3)
                await chat.finish(image4)
            else:
                await chat.finish('Sorry, something went wrong')
        else:
            await chat.finish('Sorry, something went wrong')