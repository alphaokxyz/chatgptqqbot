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
from ImageGen import ImageGen
import json
import re
import random
import mysql.connector
from datetime import datetime
import datetime as dt
import os
from os import path
from wordcloud import WordCloud
import jieba
import numpy as np

chatbot1_enabled = True  
chatbot2_enabled = False  
chatbot3_enabled = False  

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "testdb"
}

dbmessagein = ''
selfqqnumber = ''

accounts = [
    {"email": "", "password": ""},
    {"email": "", "password": ""}
]

chatbots = [RevChatbot(config=account) for account in accounts]

cur_chatbot_index = 0

cookie_file = "/file/cookies2.json"
output_dir = "/file/picture"


switch_chatbot = on_command('switch_chatbot', aliases={'切换机器人'})

@switch_chatbot.handle()
async def switch_chatbot_handle(bot: Bot, event: Event, state: T_State):
    global chatbot1_enabled, chatbot2_enabled, chatbot3_enabled
    sender_info = f'{event.get_user_id()}'
    if chatbot1_enabled:
        chatbot1_enabled = False
        chatbot2_enabled = True
        dbmessagein = '已切换到new Bing'
        try:
            # 连接数据库
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            # 执行插入操作
            add_msg = ("INSERT INTO message "
                    "(msgid, date, senderinfo, msg) "
                    "VALUES (NULL, %s, %s, %s)")
            data_msg = (datetime.now(), selfqqnumber, dbmessagein)
            cursor.execute(add_msg, data_msg)
            cnx.commit()  # 提交操作
        except mysql.connector.Error as err:
            print("MySQL Error: {}".format(err))
        cursor.close()
        cnx.close()
        await switch_chatbot.finish(MessageSegment.at(sender_info) + dbmessagein)
    elif chatbot2_enabled:
        chatbot2_enabled = False
        chatbot3_enabled = True
        dbmessagein = '已切换到Bing画图'
        try:
            # 连接数据库
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            # 执行插入操作
            add_msg = ("INSERT INTO message "
                    "(msgid, date, senderinfo, msg) "
                    "VALUES (NULL, %s, %s, %s)")
            data_msg = (datetime.now(), selfqqnumber, dbmessagein)
            cursor.execute(add_msg, data_msg)
            cnx.commit()  # 提交操作
        except mysql.connector.Error as err:
            print("MySQL Error: {}".format(err))
        cursor.close()
        cnx.close()
        await switch_chatbot.finish(MessageSegment.at(sender_info) + dbmessagein)
    else:
        chatbot3_enabled = False
        chatbot1_enabled = True
        dbmessagein = '已切换到ChatGPT'
        try:
            # 连接数据库
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            # 执行插入操作
            add_msg = ("INSERT INTO message "
                    "(msgid, date, senderinfo, msg) "
                    "VALUES (NULL, %s, %s, %s)")
            data_msg = (datetime.now(), selfqqnumber, dbmessagein)
            cursor.execute(add_msg, data_msg)
            cnx.commit()  # 提交操作
        except mysql.connector.Error as err:
            print("MySQL Error: {}".format(err))
        cursor.close()
        cnx.close()
        await switch_chatbot.finish(MessageSegment.at(sender_info) + dbmessagein)

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
            dbmessagein = response
            try:
                # 连接数据库
                cnx = mysql.connector.connect(**db_config)
                cursor = cnx.cursor()
                # 执行插入操作
                add_msg = ("INSERT INTO message "
                        "(msgid, date, senderinfo, msg) "
                        "VALUES (NULL, %s, %s, %s)")
                data_msg = (datetime.now(), selfqqnumber, dbmessagein)
                cursor.execute(add_msg, data_msg)
                cnx.commit()  # 提交操作
            except mysql.connector.Error as err:
                print("MySQL Error: {}".format(err))
            cursor.close()
            cnx.close()
            await chat.finish(MessageSegment.at(sender_info) + dbmessagein)
        else:
            dbmessagein = 'Sorry, something went wrong'
            try:
                # 连接数据库
                cnx = mysql.connector.connect(**db_config)
                cursor = cnx.cursor()
                # 执行插入操作
                add_msg = ("INSERT INTO message "
                        "(msgid, date, senderinfo, msg) "
                        "VALUES (NULL, %s, %s, %s)")
                data_msg = (datetime.now(), selfqqnumber, dbmessagein)
                cursor.execute(add_msg, data_msg)
                cnx.commit()  # 提交操作
            except mysql.connector.Error as err:
                print("MySQL Error: {}".format(err))
            cursor.close()
            cnx.close()
            await chat.finish(MessageSegment.at(sender_info) + dbmessagein)

    elif chatbot2_enabled:
        bot = Chatbot(cookiePath='/file/cookies.json')
        try:
            a = await bot.ask(prompt=msg, conversation_style=ConversationStyle.creative)
            b = a['item']['messages'][1]['text']
        except Exception as e:
            b = f"Sorry, something went wrong"
        dbmessagein = b
        try:
            # 连接数据库
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            # 执行插入操作
            add_msg = ("INSERT INTO message "
                    "(msgid, date, senderinfo, msg) "
                    "VALUES (NULL, %s, %s, %s)")
            data_msg = (datetime.now(), selfqqnumber, dbmessagein)
            cursor.execute(add_msg, data_msg)
            cnx.commit()  # 提交操作
        except mysql.connector.Error as err:
            print("MySQL Error: {}".format(err))
        cursor.close()
        cnx.close()
        await bot.close()
        await chat.finish(MessageSegment.at(sender_info) + dbmessagein)
    elif chatbot3_enabled:
        prompt = msg.strip()
        if not re.match(r'^[a-zA-Z0-9\s]+$', prompt):
            error_msg = 'We only support English now'
            dbmessagein = error_msg
            try:
                # 连接数据库
                cnx = mysql.connector.connect(**db_config)
                cursor = cnx.cursor()
                # 执行插入操作
                add_msg = ("INSERT INTO message "
                        "(msgid, date, senderinfo, msg) "
                        "VALUES (NULL, %s, %s, %s)")
                data_msg = (datetime.now(), selfqqnumber, dbmessagein)
                cursor.execute(add_msg, data_msg)
                cnx.commit()  # 提交操作
            except mysql.connector.Error as err:
                print("MySQL Error: {}".format(err))
            cursor.close()
            cnx.close()
            await chat.finish(MessageSegment.at(sender_info) + dbmessagein)
            return
        output_dir = "/file/picture"
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
            dbmessagein = 'Sorry, something went wrong'
            try:
                # 连接数据库
                cnx = mysql.connector.connect(**db_config)
                cursor = cnx.cursor()
                # 执行插入操作
                add_msg = ("INSERT INTO message "
                        "(msgid, date, senderinfo, msg) "
                        "VALUES (NULL, %s, %s, %s)")
                data_msg = (datetime.now(), selfqqnumber, dbmessagein)
                cursor.execute(add_msg, data_msg)
                cnx.commit()  # 提交操作
            except mysql.connector.Error as err:
                print("MySQL Error: {}".format(err))
            cursor.close()
            cnx.close()
            await chat.finish(MessageSegment.at(sender_info) + dbmessagein)
            return

        num = random.randint(0, 3)
        aa = Message(f'[CQ:image,file=file:/file/picture/{num}.jpeg]')
        await chat.finish(MessageSegment.at(sender_info) + aa)
    
msgstore = on_message(priority=5)

@msgstore.handle()
async def msgstore_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.message)
    sender_info = f'{event.get_user_id()}'
    try:
        # 连接数据库
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        # 执行插入操作
        add_msg = ("INSERT INTO message "
                "(msgid, date, senderinfo, msg) "
                "VALUES (NULL, %s, %s, %s)")
        data_msg = (datetime.now(), sender_info, msg)
        cursor.execute(add_msg, data_msg)
        cnx.commit()  # 提交操作
    except mysql.connector.Error as err:
        print("MySQL Error: {}".format(err))
    cursor.close()
    cnx.close()


ciyun = on_command('ciyun', aliases={'词云'})

@ciyun.handle()
async def ciyun_handle(bot: Bot, event: Event, state: T_State):
    sender_info = f'{event.get_user_id()}'
    cnx = mysql.connector.connect(**db_config)
    # 创建游标对象
    cursor = cnx.cursor()

    # 执行SQL查询语句
    today = dt.date.today()
    query = f"SELECT msg FROM message WHERE date >= '{today}'"
    cursor.execute(query)

    # 将查询结果转化为一个字符串
    results = cursor.fetchall()

    # 拼接所有消息
    msgs = [result[0] for result in results]
    joined_msgs = ' '.join(msgs)
    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()


    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()


    word_list = jieba.cut(joined_msgs, cut_all=False)
    result2 = " ".join(word_list)

    wordcloud = WordCloud().generate(result2)

    font_path = "/file/msyh.ttc"
    wordcloud = WordCloud(font_path=font_path, max_font_size=300,width= 1500,height=1500).generate(result2)

    import matplotlib.pyplot as plt
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    picture_dir = '/file/picture'
    plt.savefig(picture_dir + "/ciyun.png")
    bb = Message(f'[CQ:image,file=file:/file/picture/ciyun.png]')
    await ciyun.finish(MessageSegment.at(sender_info) + bb)


water = on_command('water', aliases={'统计'})

@water.handle()
async def water_handle(bot: Bot, event: Event, state: T_State):
    sender_info = f'{event.get_user_id()}'
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # SQL 查询语句
    query = """
    SELECT senderinfo, COUNT(*) AS count
    FROM message
    WHERE date >= CURDATE()
    GROUP BY senderinfo
    ORDER BY count DESC
    LIMIT 10;
    """
    cursor.execute(query)

    # 获取查询结果
    results = cursor.fetchall()

    # 拼接输出消息
    output = 'Senderinfo\tCount\n'
    for row in results:
        output += f"{row[0]}\t{row[1]}\n"

    
    # 关闭连接
    cursor.close()
    cnx.close()
    await water.finish(MessageSegment.at(sender_info) + output)
