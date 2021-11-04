# CDC linebot
## Docker build
```sh
1. docker build -t name .

2. docker run -itd -p 5000:5000 --name name imageID
```

## To deploy this bot, please follow the steps below

Requirements: line-bot-sdk, flask, pymongo, requests, python-dotenv.

Install [Flask](https://flask.palletsprojects.com/en/1.1.x/) and [Mongo](https://www.tutorialspoint.com/mongodb/index.htm)
```sh
pip install Flask pymongo
```
## Mongodb Collections
- [Token](#token)
- [Device](#device)
- [Authority](#authority) (Need integrate)
- [Subscribe](#subscribe)
## Linebot Functions
- [Status](#status)
- [Location](#location)
- [Subscribe](#subscribe)

## Mongodb Collections
### Basic pymongo code
```python
#data type: dict
#Insert
db[collection].insert(data) #insert all
db[collection].insert_one(data) #insert one
#Find
db[collection].find(data) #find all
db[collection].find_one(data) #find first one
#Delete
db[collection].delete(data) #delete all
db[collection].delete_one(data) #delete first one
#Update
query = {key1:value1}
newvalues = {'$set':{key2:value2}}
db[collection].update_one(query,newvalues)
```

### Token
| column name | Data |
| :------ | ------ |
| id_ | department's serial number |
| loc | department's location code |
| token | department's token |
| num | number of devices |
| name | department's chinese name |
| lat | latitude |
| lon | longitude |
| image | image url (todo) |

#### Add new Department
```python
drpartment ={'id_':int,'loc':str,'token':str,'num':int,'name':str,'lat':float,'lon':float}
db['token'].insert_one(department)
```
### Device
| col_name | Data |
| :------ | ------ |
| name | device's room |
| id | device's id |
| loc | department's location code |
| status | online/offline |
#### Add new devices
```python
device = {'name':str,'id':str,'loc':str,'status':str}
db['device'].insert_one(device)
```
#### Update device's status
```python
id_ = device_id
status = device_status
query = {'id':id_}
newvalue = {'$set':{'status':status}}
db['device'].update_one(myquery,newvalue)
```

### Authority
#### Old db (one department one collection)
too much collections
| col_name | Data |
| :------ | ------ |
| name | device's room |
| id | device's id |
#### User add new department (Old)
```python
loc = department_name
if db[loc].find_one({'user_id':user_id})==None:
    tf={'user_id':user_id,'user_name':profile.display_name}
    db[loc].insert_one(tf)
```

#### New db (all department one collection)
merge to one collection
| col_name | Data |
| :------ | ------ |
| name | device's room |
| id | device's id |
| department's location code<br><center>$\vdots$</center> | True/False |
#### User add new department (New)
```python
if db['authority'].find_one({'user_id':user_id}): #Check db
    #update
    query = {'user_id':user_id}
    auth_query = {'$set':{token['loc']:True}}
    db['authority'].update_one(query,auth_query)
else:
    #insert
    tf = {'user_id':user_id,'user_name':profile.display_name,token['loc']:True}
    db['authority'].insert_one(tf)
```
#### Has been merged and needs improvement

### Subscribe
| col_name | Data |
| :------ | ------ |
| name | device's room |
| id | device's id |
| loc | department's location code |
| status | online/offline |
#### User add new department (Default : False)
```python
if db['subscribe'].find_one({'user_id':user_id}): #Check db
    #update
    query = {'user_id':user_id}
    auth_query = {'$set':{token['loc']:False}}
    db['subscribe'].update_one(query,auth_query)
else:
    #insert
    tf = {'user_id':user_id,'user_name':profile.display_name,token['loc']:False}
    db['subscribe'].insert_one(tf)
```


## Status
### Step
1. [Check Authentication](#checkauthentication)
2. [Choose Device](#choosedevice)
3. [Get Device info](#getdeviceinfo)
### Check Authentication
```python
auth = db['authority'].find_one({'user_id':user_id})
place,place_name=[d['loc'] for d in db['token'].find()],[d['name'] for d in db['token'].find()]
#Check
for i in range(np.size(place)):
    if auth[place[i]]:
        #Add Action if yes
        act.append(ButtonComponent(
                    style='link',
                    height='sm',
                    action=PostbackAction(label=place_name[i], data=place[i])
                    ))
#Add to Flex_message
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
```
### Choose Device
See function.py flex(msg)
### Get device info
See function.py Airbox(msg)

## Location
see app.py handle_location_message(event)

## Subscribe
### Select an option
- [show subscribed](#showsubscribed)
- [subscribe department](#subscribedepartment)
- [set alert threshold](#setalertthreshold)
- [set alarm](#setalarm)
- [unsubscribe](#unsubscribe)
### show subscribed
See function.py subscribed_show(user_id)
### subscribe department
#### Check Authentication
See function.py add_department(subscribe_col,user_id,sub_act='sub:')
#### Choose department to subscribe (Need to integrate with new Authority)
```python
if mydb[depart].find_one({'user_id':user_id}):
    query={'user_id':user_id}
    value={'$set':{depart:True}}
    mydb['subscribe'].update_one(query,value)
    line_bot_api.reply_message(
    event.reply_token, TextSendMessage(
        text='Subscribe Succeed'))
```

### unsubscribe
#### Check Authentication
See function.py add_department(subscribe_col,user_id,sub_act='sub!')
#### Choose department to unsubscribe (Need to integrate with new Authority)
```python
if mydb[depart].find_one({'user_id':user_id}):
    query={'user_id':user_id}
    value={'$set':{depart:False}}
    mydb['subscribe'].update_one(query,value)
    line_bot_api.reply_message(
    event.reply_token, TextSendMessage(
        text='Unsubscribe Succeed'))
```