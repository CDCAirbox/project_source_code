FROM ubuntu:latest

RUN apt-get update && apt-get upgrade && apt-get install -y \
    python3-pip \
    mongodb 
    
RUN mkdir /home/linebot

WORKDIR /home/linebot

COPY . /home/linebot

RUN pip3 install -r requirements.txt

CMD sh ./start.sh
