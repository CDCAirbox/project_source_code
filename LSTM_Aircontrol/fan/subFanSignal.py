#!/usr/bin/python
#encoding:utf-8

import RPi.GPIO
import time
import paho.mqtt.client as mqtt
# coding: utf-8
import sys, os, time, signal
import test

time_out=5
RELAY=21
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(RELAY,RPi.GPIO.OUT)
# RPi.GPIO.output(RELAY,RPi.GPIO.LOW)
def main():
        
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        
        client.subscribe("plan/fan" , qos = 0)
    def on_log(client, userdata, level, buf):
        print("log: ",buf)


    def on_message(client, userdata, msg):
        print(msg.topic+" "+ msg.payload.decode('utf-8'))

        

        if( msg.payload.decode('utf-8') == "on" ) :
            RPi.GPIO.output(RELAY,RPi.GPIO.LOW)
            # time.sleep(1)

        elif (msg.payload.decode('utf-8') == "off" ) :
            
            RPi.GPIO.output(RELAY,RPi.GPIO.HIGH)
            # time.sleep(1)

    client = mqtt.Client()
        
    client.on_connect = on_connect

    client.on_log=on_log
    client.on_message = on_message

    client.connect("***.***.***.***", 8883)

    client.loop_forever()


if __name__ == '__main__':
	try:
	  	main()
	except KeyboardInterrupt:
		RPi.GPIO.cleanup()
