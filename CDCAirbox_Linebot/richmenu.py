import os
import datetime
import json

from dotenv import load_dotenv

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

load_dotenv()
# Channel Access Token
line_bot_api=LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

rich_menu_to_create = RichMenu(
size=RichMenuSize(width=2500, height=1686),
selected=False,
name="Nice richmenu",
chat_bar_text="Tap here",
areas=[RichMenuArea(
    bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
    action=PostbackAction(label='status', data='status'))
    ,
    RichMenuArea(
    bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
    action=PostbackAction(label='location', data='location'))
    ,
    RichMenuArea(
    bounds=RichMenuBounds(x=1666, y=0, width=833, height=843),
    action=PostbackAction(label='subscribe', data='subscribe'))
    ,
    RichMenuArea(
    bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
    action=URIAction(label='Go to web', uri='https://nslab.csie.ntnu.edu.tw/cdc'))
    ,
    RichMenuArea(
    bounds=RichMenuBounds(x=833, y=843, width=833, height=843),
    action=URIAction(label='Go to lass', uri='https://pm25.lass-net.org'))
    ,
    RichMenuArea(
    bounds=RichMenuBounds(x=1666, y=843, width=833, height=843),
    action=PostbackAction(label='help', data='help'))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
with open('richmenu_1578026862882.jpg', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/jpeg', f)
line_bot_api.set_default_rich_menu(rich_menu_id)
