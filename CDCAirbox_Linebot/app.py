# -*- coding: utf-8 -*-
from function import *
import random

load_dotenv()
app = Flask(__name__)

myclient = pymongo.MongoClient("localhost",27017)

mydb = myclient["CDC"]
token_col = [d for d in mydb["token"].find().sort('id',1)]
device_col = [d for d in mydb["device"].find()]
subscribe_col = [d for d in mydb["subscribe"].find()]
changing = False

place , place_name = [], []
[place.append(i['loc']) for i in token_col]
[place_name.append(i['name']) for i in token_col]

helptxt = 'Hello! Wellcome to Airbox status check bot\n'\
            '歡迎來到空氣盒子的聊天機器人\n'\
            'To use this bot, there are some steps to do first:\n'\
            '這裡有數個功能可以使用\n'\
            'You have to get your token from the supervisor.\n'\
            '你必須要跟管理者取得授權碼\n'\
            'You only need to input the token once, and you can use other function.\n'\
            '授權碼只需輸入一次就可以永久使用\n'\
            'Richmenu:圖形介面\n'\
            'Status: \nTo see the information about the device in your organization.\n'\
            '可以看到你的機構裡機器的資料\n'\
            'Location: \nShare your location, and find the nearest organization.\n'\
            '可以查詢目前離你最近的機構是哪間\n'\
            'Subscribe: \nTo subscribe the device/ organization you want to focus on, or set alerm.\n'\
            '訂閱後每天會收到一個機構的存活訊息\n'\
            'Website: \nGo to our website.\n'\
            '可以來觀看我們的網站\n'\
            'Lass: \nGo to Lass website.\n'\
            '這是Lass的網頁\n'\
            'help: \nshow this help.\n'\
            '尋求幫忙,以及更改機器放置地點\n'\
            'You can input "profile" to see your profile and some info in this bot.\n'\
            '可以輸入 profile 來檢查你的個人狀態.'
changtxt = 'now enter the device id and the location you want to move,\n'\
            '輸入機器的id以及想放置的地點\n'\
            'id location(middle have a space),\n'\
            '機器id 地點(中間空一格)\n'\
            'For example:\n'\
            'B00000000000 房間101\n'\
            '就能將機器status的機器位置替換了.'

# Channel Access Token
line_bot_api=LineBotApi('')
# Channel Secret
handler = WebhookHandler('')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global changing
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    msg = event.message.text
    token = mydb['token'].find_one({'token':msg})
    place , place_name = [], []
    [place.append(i['loc']) for i in token_col]
    [place_name.append(i['name']) for i in token_col]
    change = mydb["change"].find_one()
    checking = msg.split(' ')
    checkdevice = mydb['device'].find_one({'id':checking[0]})

    if checkdevice !=None:
        if changing == True:
            if checking[1]!='':
                nam = checking[1]
                query = {'id':checking[0]}
                new = {'$set':{'name':nam}}
                mydb['device'].update_one(query,new)
                changing = False
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text='change success!please check the status.\n機器位置更改成功！請去status查看.'))

    if msg == 'reiwqjfsdanovijjqewirji': # get change place token
        tem = change['token']
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=tem)
            )
        
    if msg =='web':
        m = 'https://hallsoultions.com/cdc'
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=m)
            )
    
    if msg =='lass':
        m = 'https://pm25.lass-net.org'
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=m)
            )

    if msg == 'iqjrewiojsdnafjniuhqerwhjpow': # show all token
        gettoken = mydb['token'].find()
        tokenlist = ''
        for i in gettoken:
            tokenlist = tokenlist + i['name'] + ":\n" + i['token'] + "\n"
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=tokenlist)
            )

    if 'fortesting' in msg:
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='test success!')
            )

    if msg == change['token']:
        tok = ''
        for i in range(9):
            temp = random.randint(0,9)
            tok = tok + str(temp)
        query = {'_id':'x'}
        new = {'$set':{'token':tok}}
        mydb['change'].update_one(query,new)
        changing = True
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=changtxt)
            )

    if msg.lower() =='profile':
        t='名字 Display name: %s \n'\
            '使用者id user_id: %s \n'\
            '機構 Enrolled Organization: \n'%(profile.display_name, user_id)
        for i in range(np.size(place)):
            if mydb[place[i]].find_one({'user_id':user_id})!=None:
                t+='%s \n'%(place_name[i])
        line_bot_api.reply_message(event.reply_token, 
                    TextSendMessage(text=t)
                )
    if token !=None:
        if mydb[token['loc']].find_one({'user_id':user_id})==None:
            tf={'user_id':user_id,'user_name':profile.display_name}
            mydb[token['loc']].insert_one(tf) #add to status check db
            tf.update({token['loc']:False}) #default set subscribe as False
            if mydb['subscribe'].find_one({'user_id':user_id}):
                query = {'user_id':user_id}
                sub_query = {'$set':{token['loc']:False}}
                mydb['subscribe'].update_one(query,sub_query)
            else:
                mydb['subscribe'].insert_one(tf) #add to subscribe db
            t='Hi. '+profile.display_name+'\nAdd to '+token['name']+' succeed!'
        else:
            t='You have already a member.'
        if mydb['authority'].find_one({'user_id':user_id}): #add to authority db
            query = {'user_id':user_id}
            auth_query = {'$set':{token['loc']:True}}
            mydb['authority'].update_one(query,auth_query)
        else:
            tf = {'user_id':user_id,'user_name':profile.display_name,token['loc']:True}
            mydb['authority'].insert_one(tf)
        line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text=t)
                        )
    if msg == 'qowerninfdsvuiureqpwejrpwjqpi': #get admin 
        tf={'user_id':user_id,'user_name':profile.display_name}
        for i in place:
            if mydb[i].find_one({'user_id':user_id})==None:
                mydb[i].insert_one(tf)
        [tf.update({i:False}) for i in place]
        if mydb['subscribe'].find_one({'user_id':user_id})==None:
            mydb['subscribe'].insert_one(tf)
        [tf.update({i:True}) for i in place]
        if mydb['authority'].find_one({'user_id':user_id})==None:
            mydb['authority'].insert_one(tf)
        line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text='Hi admin,\nYou are added to all database.')
                    )
    if msg == 'help':
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(
                text='Select an option!',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="說明", data="hel")
                            ),
                        QuickReplyButton(
                            action=PostbackAction(label="換機器位置", data="changespace")
                            ),
                    ])))

    if msg == 'subscribe':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Select an option!',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="show Subscribed", data="sub_show")
                        ),
                        QuickReplyButton(
                            # action=PostbackAction(label="Subscribe", data="add_depart")
                            action=PostbackAction(label="Subscribe", data="not_yet")
                        ),
                        # QuickReplyButton(
                        #     action=PostbackAction(label="Set alert threshold", data="TODO")
                        # ),
                        # QuickReplyButton(
                        #     action=PostbackAction(label="Set alarm", data="TODO")
                        # ),
                        QuickReplyButton(
                            action=PostbackAction(label="Unsubscribe", data="Unsub")
                        ),
                    ])))

    if msg == 'location':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Please share your location!\n請分享你的位址',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=LocationAction(label="ShareLocation")
                        ),
                    ])))

    if msg == 'status':
        act=[]
        auth = mydb['authority'].find_one({'user_id':user_id})
        for i in range(np.size(place)):
            #if mydb[place[i]].find_one({'user_id':user_id})!=None:
            try:
                if auth[place[i]]:
                    act.append(ButtonComponent(
                                style='link',
                                height='sm',
                                action=PostbackAction(label=place_name[i], data=place[i])
                            ))
                    print(place[i])
            except:
                pass
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
        if act:
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(msg),flex_message])
        else:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='Your info is not in the DataBase.\n你沒有任何機構\nPlease input the token first.\n請先輸入授權碼'))
    
    else:
        m = '輸入web,可查看網頁\n'\
            '輸入status,可查看機器狀態\n'\
            '本機器人id:\n'\
            '@777swkhp' # your linebot id
        message =ImageSendMessage(
            original_content_url='https://qr-official.line.me/sid/L/777swkhp.png', # your linebot qrcode
            preview_image_url='https://qr-official.line.me/sid/L/777swkhp.png'
        )
        line_bot_api.reply_message(event.reply_token,
            [message,TextSendMessage(text=m)]
            )


@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    msg = event.postback.data
    subscribe_col = mydb["subscribe"].find_one({'user_id':user_id})
    

    if msg == 'hel':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=helptxt))

    elif msg == 'changespace':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Contact supervisor to get the change token\n聯絡管理員取得更換授權碼\nenter it then you can change one device's location\n輸入後即可更換機器位置一次"))

    elif msg == 'not_yet':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(
                text='In development,please wait.'))

    elif msg == 'add_depart':
        sub_txt, check = add_department(subscribe_col, user_id,'sub:')
        if check:
            line_bot_api.reply_message(event.reply_token,[TextSendMessage('Subscribe Department\n訂閱機構'),sub_txt])
        elif subscribe_col:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(
                text='You are already subscribed all.'))
        else:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(
                text='Your info is not in the DataBase.\nPlease input the token first.'))

    elif msg == 'sub_show':
        sub_txt = subscribed_show(user_id)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=sub_txt))

    elif msg == 'Unsub':
        sub_txt, check = add_department(subscribe_col, user_id,'sub!')
        if check:
            line_bot_api.reply_message(event.reply_token,[TextSendMessage('Unsbscribe Department\n取消訂閱'),sub_txt])
        elif subscribe_col:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(
                text='You subscribed nothing.'))
        else:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(
                text='Your info is not in the DataBase.\nPlease input the token first.'))

    elif 'sub:'in msg:
        depart = msg.split(':')[1]
        if mydb[depart].find_one({'user_id':user_id}):
            query={'user_id':user_id}
            value={'$set':{depart:True}}
            mydb['subscribe'].update_one(query,value)
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(
                text='Subscribe Succeed\n訂閱成功'))

    elif 'sub!'in msg:
        depart = msg.split('!')[1]
        if mydb[depart].find_one({'user_id':user_id}):
            query={'user_id':user_id}
            value={'$set':{depart:False}}
            mydb['subscribe'].update_one(query,value)
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(
                text='Unsubscribe Succeed\n取消訂閱了'))

    elif msg == 'TODO':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='TODO'))

    elif msg in place:
        print(msg)
        flex_message = flex(msg)
        line_bot_api.reply_message(event.reply_token,flex_message)

    else:
        try:
            t = Airbox(msg)
        except:
            t='Error!!!\nUse help to see command\nIf your input is device_id, please contact Supervisor!\n請聯絡管理員'
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(msg),TextSendMessage(text=t)])


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    user_id = event.source.user_id
    location_get = [d for d in mydb['token'].find()]
    lat = event.message.latitude
    lon = event.message.longitude
    la = []
    lo = []
    where = []
    for i in location_get:
        la.append(i['lat'])
        lo.append(i['lon'])
        where.append(i['name'])

    locatmin = 10000
    dis = []
    for i in range(len(la)):
        temla = (la[i]-lat)*(la[i]-lat)
        temlo = (lo[i]-lon)*(lo[i]-lon)
        temdis = (temla+temlo)**0.5
        dis.append(temdis)

    posi = 0
    for i in range(len(dis)):
        if locatmin>dis[i]:
            locatmin=dis[i]
            posi=i

    print(location_get[posi]['loc'])
    plc = location_get[posi]['loc']
    idauth = mydb['authority'].find_one({'user_id':user_id})
    # print(idauth[plc])
    try:
        if idauth[plc]==True:
            flex_message = flex(plc)
            line_bot_api.reply_message(event.reply_token,[
                LocationSendMessage(
                title='Location', address=location_get[posi]['name'],
                latitude=location_get[posi]['lat'], longitude = location_get[posi]['lon']
                ),
                TextSendMessage(text='the closest institution is\n距離最近的機構為:\n  %s  '%(location_get[posi]['name'])),
                flex_message
            ])
    
    except:
        line_bot_api.reply_message(
        event.reply_token,[
        LocationSendMessage(
            title='Location', address=location_get[posi]['name'],
            latitude=location_get[posi]['lat'], longitude = location_get[posi]['lon']
        ),
        TextSendMessage(text='the closest institution is\n距離最近的機構為:\n  %s  \nplease contact Supervisor to get the token,thank you!\n請聯絡管理員取得存取碼'%(location_get[posi]['name'])),
        ]
        )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)  
