import paho.mqtt.client as mqtt
# coding: utf-8
import sys, os, time, signal
reload(sys)


import commands
sys.setdefaultencoding('utf-8')
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    
    client.subscribe("ac" , qos = 0)
def on_log(client, userdata, level, buf):
    print("log: ",buf)


def on_message(client, userdata, msg):
    print(msg.topic+" "+ msg.payload.decode('utf-8'))
    data = "on"
    print(123)
    if msg.payload == data :
        t2 = time.time()
        commands.getoutput('irsend SEND_ONCE airc KEY_POWER')

client = mqtt.Client()
    
"""
client.tls_set(ca_certs = "myca/ca.crt")
client.tls_insecure_set(True)"""

client.on_connect = on_connect

client.on_log=on_log
client.on_message = on_message

client.connect("***.***.***.***", 8883)

print(1)
client.loop_forever()
