FROM arm32v7/python:3.8-slim

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
RUN pip config set global.index-url http://pypi.doubanio.com/simple/
RUN pip config set global.trusted-host pypi.doubanio.com

RUN apt-get update -y && apt-get install gcc -y

RUN apt-get install -y libffi-dev python3-dev libevent-dev

ADD whl_arm32v7/cryptography-3.4.6-cp38-cp38-linux_armv7l.whl . 
RUN pip3 install cryptography-3.4.6-cp38-cp38-linux_armv7l.whl

# ADD requirements.txt . 
# RUN pip3 install -r requirements.txt

RUN pip3 install HAP-python[QRCode]
RUN pip3 install python-miio
RUN pip3 install PyYAML

RUN apt-get install g++ -y
RUN pip3 install SQLAlchemy

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN pip3 install flask

ADD *.py /app/
ADD templates /app/templates

WORKDIR /app

CMD ["sh", "-c", "python3 -u main.py"]
