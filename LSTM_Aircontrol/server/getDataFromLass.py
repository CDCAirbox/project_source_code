import requests
from requests.structures import CaseInsensitiveDict
import numpy as np
import json
def getLassData():
        
    url = "https://pm25.lass-net.org/API-1.0.0/device/B827EB4AE378/history/"

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"


    resp = requests.get(url , headers = headers)
    text = resp.text
    text = json.loads(text)


    feeds = text["feeds"]
    MAPS = feeds[0]["MAPS"]

    T10value = []
    for i in reversed(range(11)):
        values = list(MAPS[-(i+1)].values())[0]
        tmp = values["s_t0"]
        rh = values["s_h0"]
        pm25 = values["s_d0"]
        co2 = values["s_g8"]
        tovc = values["s_gg"]
        td = ((rh/100)**(1/8))**(1/8)*(112+0.9*tmp)+0.1*(tmp)-112
        thi = tmp-(0.55*(1-(np.exp((17.269*td)/(td+237.3))/np.exp((17.269*tmp)/tmp+237.3))))
        fan = 0
        ac = 0
        T10value.append([co2,pm25,tovc,rh,tmp,thi,fan,ac])
    return T10value
        




