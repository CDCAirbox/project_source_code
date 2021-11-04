# server end

Requirements: paho.mqtt.client, commands, sys, os, keras, sklearn, numpy, pandas, matplotlib, math

## server/getDataFromLass.py
```python
# Change your airbox mac for get your surrounding's data 
url = "https://pm25.lass-net.org/API-1.0.0/device/B827EB4AE378/history/"
```
## server/control.py's hostname & port
```python
#hostname & port can reset
client.connect(hostname = "***.***.***.***", port = ****)
```

## server/control.py
```sh
#run for taking control of air quality
python3 control.py
```

# edge end

Requirements: io, sys, os, subprocess, paho.mqtt.client, RPi.GPIO

## ac/subAcSignal.py and fan/subFanSignal.py's hostname & port
```python
#hostname & port can reset
client.connect(hostname = "***.***.***.***", port = ****)
```

## AC_ir_record.py
```sh
#run for recording ac's signal
python3 AC_ir_record.py
```
