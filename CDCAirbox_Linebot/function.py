# -*- coding: utf-8 -*-
import requests
import json
import os
import datetime
import pymongo
import time
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

myclient = pymongo.MongoClient("localhost",27017)
mydb = myclient["CDC"]
token_col = [d for d in mydb["token"].find()]

place , place_name = [], []
[place.append(i['loc']) for i in token_col]
[place_name.append(i['name']) for i in token_col]
#function_list = {'subscribed_show':subscribed_show,'add_department':add_department}
url_all = 'https://hallsoultions.com/cdc/plan_pic/'

d_type = {'s_g8':"NONE",
            's_t0':"NONE",
            's_h0':"NONE",
            's_d0':"NONE",
            's_d1':"NONE",
            's_d2':"NONE",
            's_gg':"NONE",
            'date':"NONE",
            'time':"NONE",
            'device_id':"NONE"}

def subscribed_show(user_id):
    subscribe_col = mydb["subscribe"].find_one({'user_id':user_id})
    msg='subscribed: \n'
    count=0
    if subscribe_col:
        for i in token_col:
            try:
                if subscribe_col[i['loc']]:
                    msg+=i['name']+'\n'
                    count+=1
            except :
                pass
    if not count:
        msg = "You didn't subscribe any department.\n"\
                "你還沒訂閱任何機構\n"\
                "Please subscribe first.\n"\
                "請先訂閱"
    return msg

def add_department(subscribe_col, user_id,sub_act):
    act=[]
    check=0
    sub_check = True if sub_act=='sub:' else False
    for i in range(np.size(place)):
        if mydb[place[i]].find_one({'user_id':user_id})!=None:
            if subscribe_col[place[i]]!=sub_check:
                call=sub_act+place[i]
                act.append(ButtonComponent(
                            style='link',
                            height='sm',
                            action=PostbackAction(label=place_name[i], data=call)
                        ))
    flex_message = FlexSendMessage(
            alt_text='Select Department',
            contents=BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='https://pm25.lass-net.org/LASS/assets/img/logos/LASS.jpg',
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    action=PostbackAction(label='TODO', data='TODO')
                ),
                footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=act
                )
            )
        )
    check=1 if act else 0
    return flex_message, check

def flex(msg):
    device_col = [d for d in mydb["device"].find()]
    tf, cf =[], []
    alive=0
    p=mydb['token'].find_one({'loc':msg})
    print(msg)
    #if msg=='ntnu_test' or msg=='ntnu_ho' or loc['loc']=='ntnu_s' or loc['loc']=='ntnu_e':
    #    print(p)
    if msg =='NTNU_linco':
        url_p= url_all + 'ntnulinkou/ntnulinkou.jpg'
    elif msg =='NTNU_study':
    	url_p= url_all + 'ntnusce/ntnusce1f.jpg'
    elif msg =='NTNU_csie':
        url_p= url_all + 'ntnucsie/ntnucsie.jpg'
    elif msg == 'NLJH':
        url_p= url_all + 'neili/neili.jpg'
    elif msg == 'KAO_godoc':
        url_p= url_all + 'jiayi/jiayi3F.jpg'
    elif msg == 'KAO_chiang':
        url_p= url_all + 'jiangqing/jiangqing2F.jpg'
    elif msg =='KAO_mincare':
        url_p= url_all + 'minsheng/minsheng.jpg'
    elif msg =='KAO_sinli':
        url_p= url_all + 'xinli/xinli.jpg'
    elif msg =='KAO_sangon':
        url_p= url_all + 'shenggonghuli/shenggonghuli3F.jpg'
    elif msg =='KAO_sangonh':
        url_p= url_all + 'shenggong/shenggong1.jpg'
    elif msg == 'CDC-1':
        url_p= url_all + 'chengkang_word.png'
    elif msg == 'CDC-2':
        url_p= url_all + 'cfad/cfad_1F_word.png'
    elif msg == 'CDC-3':
        url_p= url_all + 'hanh/hanh_3F.png'
    else:
        url_p= 'https://pm25.lass-net.org/LASS/assets/img/logos/LASS.jpg'

    #判斷要不要多補carousel
    size_=int(p['num']/5) if p['num']%5==0 else int(p['num']/5)+1
    for i in range (np.size(device_col)):
        if msg == device_col[i]['loc']:
            #print(msg)
            content={'type':'button',
                'style':'primary',
                'margin':'xs',
                'height':'sm',
                'action':{
                    'type':'postback',
                    'label':device_col[i]['name'],
                    'data':device_col[i]['id']
                    }
                }
            if device_col[i]['status']=='offline':
                content.update({'color':'#ff0000'})
            else:
                alive+=1
            tf.append(content)
        #else:
            #print(device_col[i]['loc'])
    #print(tf)
    alive = int(alive/p['num']*100)
    for i in range(size_):
        content={
                'type':'bubble',
                'header': {
                    'type':'box',
                    'layout':'vertical',
                    'contents':[{
                        'type': 'image',
                        'url': url_p,
                        'size': 'full',
                        'aspectRatio': '20:13',
                        'aspectMode': 'cover',
                        'gravity':'center',
                        'flex':1
                        },
                        {
                        'type':'text',
                        'text':'Alive percentage'+':'+str(alive)+'%',
                        'color':'#000000',
                        'align':'start',
                        'size':'xl',
                        'gravity':'center',
                        'margin':'lg'
                        },
                        {
                        'type':'box',
                        'layout':'vertical',
                        'contents':[{
                            'type':'box',
                            'layout':'vertical',
                            'contents':[{'type':'filler'}],
                            'width':str(alive)+'%',
                            'backgroundColor':'#DE5658',
                            'height':'6px',
                            }],
                        'backgroundColor':'#FAD2A76E',
                        'margin':'xl'
                        }
                        ],
                    'paddingAll':'0px'
                    },
                'footer':{
                    'type':'box',
                    'layout':'vertical',
                    'contents':tf[i*5:i*5+5]
                    }
                }
        #print(tf)
        cf.append(content)
        #print(cf)
    return FlexSendMessage(
        alt_text=p['name'],
        contents={
            'type': 'carousel',
            'direction': 'ltr',
            'contents':cf
            }
        )


def Airbox(msg):
    loc = mydb["device"].find_one({'id':msg})
    dashlink = ''
    if 'NTNU'in loc['loc'] or 'NLJH' in loc['loc'] or 'KAO' in loc['loc']:
        r = requests.get('https://pm25.lass-net.org/data/last.php?device_id='+msg)
        dashlink = 'https://pm25.lass-net.org/data/show.php?device_id='+msg
        print(msg)
    else:
        r = requests.get('https://pm25.lass-net.org/data/last-iaq.php?device_id='+msg)
        dashlink = 'https://pm25.lass-net.org/IAQ/show-iaq.php?device_id='+msg
    data = r.json()
    data_= {key: 0 for key in d_type}
    if data['feeds']:
        print('h')
        nowtime = time.strftime("%Y-%m-%d", time.localtime())
        clock = time.strftime("%H:%M:%S", time.localtime())
        if  'NTNU'in loc['loc'] or 'NLJH' in loc['loc'] or 'KAO' in loc['loc']:
            d = data['feeds'][0]['MAPS']
        else:
            d = data['feeds'][0]['IAQ_TW']
        for i in d:
            data_[i]=d[i] if d[i] else "NONE"
        return '時間 Time: '+nowtime+' '+clock+'\n'+\
                '機器id Device_id: '+data_['device_id']+'\n'+\
                '二氧化碳 CO2: '+str(data_['s_g8'])+'ppm'+'\n'+\
                '氣溫 Temperature: '+str(data_['s_t0'])+'°C'+'\n'+\
                '濕度 Humidity: '+str(data_['s_h0'])+'%'+'\n'+\
                '細懸浮微粒 PM2.5: '+str(data_['s_d0'])+'μg/m3'+'\n'+\
                '懸浮微粒 PM10: '+str(data_['s_d1'])+'μg/m3'+'\n'+\
                '顆粒物 PM1: '+str(data_['s_d2'])+'μg/m3'+'\n'+\
                '揮發性有機物 TVOC: '+str(data_['s_gg'])+'ppb'+'\n'+\
                '網頁連結 Dashboard: '+dashlink
    else:
        return 'Device '+msg+' is down, please contact Supervisor!'
