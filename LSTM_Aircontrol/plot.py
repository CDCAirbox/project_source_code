from time import time
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from getDataFromLass import getLassData
import requests
from requests.structures import CaseInsensitiveDict
import json
import numpy as np
from datetime import datetime
import pandas as pd
# datas = getLassData()
url = "https://pm25.lass-net.org/API-1.0.0/device/B827EB4AE378/history/"

headers = CaseInsensitiveDict()
headers["accept"] = "application/json"


resp = requests.get(url , headers = headers)
text = resp.text
text = json.loads(text)


feeds = text["feeds"]
MAPS = feeds[0]["MAPS"]

T10value = [] 
#27 42
for i in reversed(range((63-14),(63-1))):
    values = list(MAPS[-(i+1)].values())[0]
    tmp = values["s_t0"]
    rh = values["s_h0"]

    co2 = values["s_g8"]
    timestamp = values["timestamp"]
    thetime = timestamp.split("T")[1].split("Z")[0].split(":")
    #thetime = timestamp
    print(thetime)
    thetime = thetime[0] +":"+ thetime[1]
    td = ((rh/100)**(1/8))**(1/8)*(112+0.9*tmp)+0.1*(tmp)-112
    thi = tmp-(0.55*(1-(np.exp((17.269*td)/(td+237.3))/np.exp((17.269*tmp)/tmp+237.3))))
    T10value.append([thetime,co2,thi])
day = []
thetime = []
thi = []
co2 = []
timestamp = []

for data in T10value:
    thetime.append(data[0])
    co2.append(data[1])
    thi.append(data[2])
print(thetime)
x = [datetime.strptime(date, "%H:%M") for date in thetime]
print(x)
x = pd.to_datetime(x, format="%H:%M")
print(x)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.plot(x,co2)
plt.title("original Co2") # title
plt.ylabel("Concentration of Co2 (ppm)") # y label
plt.xlabel("Time (hour:min)") # x label
plt.savefig("Original_co2.png")
plt.clf()

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.plot(x,thi)
plt.title("original THI") # title
plt.ylabel("Temperature Humidity Index") # y label
plt.xlabel("Time (hour:min)") # x label
plt.savefig("Original_thi.png")
plt.show()