import requests
import json
import os
import datetime
import pymongo
import numpy as np
from dotenv import load_dotenv

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import *


load_dotenv()

myclient = pymongo.MongoClient(os.getenv('Mongo_url'))
admin_user = os.getenv('admin_user')
line_bot_api=LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
mydb = myclient["CDC"]

token_col = [d for d in mydb["token"].find()]
subscribe_col = [d for d in mydb["subscribe"].find()]
device_col = [d for d in mydb["device"].find()]

def push_txt(name,loc,num):
    if num>0:
        alive=0
        for i in device_col:
            if i['loc']==loc and i['status']=='online':
                alive+=1
        alive=int((alive/num)*100)
        return '%s:\n%s%s\n\n'%(name,alive,'%')
    else:
        return ''

for a in subscribe_col:
    msg=''
    #print(a['user_name'])
    for i in token_col:
        try:
            if a[i['loc']]:
                msg+=push_txt(i['name'],i['loc'],i['num'])
        except:
            pass

   #print(msg)
    if msg:
        print('ff')
        line_bot_api.push_message(a['user_id'],TextSendMessage(text=msg))
