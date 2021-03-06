from kafka import KafkaConsumer
from kafka import KafkaProducer
import json 
from msgRec import on_message_come
import requests
import redis
import time
import os

class Message(object):
    def __init__(self,msg = None):
        if msg:
            try:
                msg = json.loads(msg)
                self.dataType = msg["dataType"]
                self.data = msg["data"]
                self.deviceName = msg["deviceName"]
                self.time = msg["time"]
            except Exception as e:
                print("wrong msg:"+str(msg))
        else:
            self.data = None
            self.dataType = None
            self.deviceName = None
            self.time = time.time()

class Client:
    def __init__(self):
        self.__scene = None
        self.__config = None
        self.__subTuple = None
        self.__pubJson = {}
        self.__producer = None
        self.__redis = None
        self.updateConfig()

    def updateConfig(self):
        configPath = "/app/config/custom.json"
        if os.path.exists(configPath):
            with open(configPath,'r') as load_f:
                configJson = json.load(load_f)
                self.__scene = configJson["scene"]
                self.__config = configJson["serviceConfig"]
                router = configJson["router"]["hign-temp-alarm"]
                if "pub" in router:
                    self.__pubJson = router["pub"]
                if "sub" in router:
                    self.__subTuple = tuple(router["sub"])
    
    def getConfig(self,service ="hign-temp-alarm"):
        return self.__config[service]

    def getScene(self):
        return self.__scene

    def getSubTuple(self):
        return self.__subTuple

    def initProducer(self):
        try:
            self.__producer = KafkaProducer(bootstrap_servers='edge-kafka:9092')
        except Exception as e:
            print("waiting kafka client start...")
            time.sleep(2)
            self.initProducer()

    def initRedis(self):
        try:
            self.__redis = redis.Redis(host='edge-cache', port=6379, decode_responses=True)   # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
        except:
            print("waiting redis client start...")
            time.sleep(2)
            self.initRedis()

    def publish(self, msg):
        if not self.__producer:
            self.initProducer()
        deviceName = msg.deviceName
        topic = ""
        if deviceName in self.__pubJson:
            topic = self.__pubJson[deviceName]
        elif "default" in self.__pubJson:
            topic = self.__pubJson["default"]
        else:
            print("lack default router")
            return
        print(msg.__dict__)
        print("topic:"+topic+" msg:"+str(msg))
        self.__producer.send(topic,bytes(json.dumps(msg.__dict__), encoding = "utf8"))

    def callDeviceService(self, deviceName,service,payload):
        if not self.__producer:
            self.initProducer()
        r = requests.get("http://edge-device-management/device/connector?deviceName="+deviceName)
        connector = r.json()["data"]
        topic = ""
        msg ={}
        msg["type"] = "callService"
        msg["deviceName"] = deviceName
        msg["service"] = service
        msg["payload"] = payload
        topic = "command_" + connector 
        print("topic:"+topic+" msg:"+str(msg))
        self.__producer.send(topic,bytes(json.dumps(msg), encoding = "utf8"))

    def setDeviceProperties(self, deviceName,payload):
        if not self.__producer:
            self.initProducer()
        r = requests.get("http://edge-device-management/device/connector?deviceName="+deviceName)
        connector = r.json()["data"]
        topic = ""
        msg ={}
        msg["type"] = "setValue"
        msg["deviceName"] = deviceName
        msg["payload"] = payload
        topic = "command_" + connector 
        print("topic:"+topic+" msg:"+str(msg))
        self.__producer.send(topic,bytes(json.dumps(msg), encoding = "utf8"))

    def read(self, deviceName,property,num = 1,freshness = 60):
        if(num<1):
            return None
        if not self.__redis:
            self.initRedis()
        #value = r.get(deviceName+":"+property)
        key = deviceName+":"+property
        length = self.__redis.llen(key)
        if length>=num:
            dataList = self.__redis.lrange(key, length-num, -1)
            valueList = []
            for data in dataList:
                data = json.loads(data)
                value = data["value"]
                if int(time.time())-int(data["time"])<freshness:
                    valueList.append(value)
                else:
                    print("Now time is " + str(int(time.time()))+" , "+str(data["time"])+" is too old")
            return valueList
        else:
            print("not enought")
            return None

    def updateCache(self, deviceName,property,value, uploadTime = 0):
        def handleList(name,length,value):
            if self.__redis.llen(name)==0:
                self.__redis.rpush(name, value)   # 这里"foo_list1"之前已经存在，往列表最右边添加一个元素，一次只能添加一个
            elif self.__redis.llen(name)==length:
                self.__redis.lpop(name)    # 删除列表最左边的元素，并且返回删除的元素
                self.__redis.rpushx(name, value)   # 这里"foo_list1"之前已经存在，往列表最右边添加一个元素，一次只能添加一个    
            else:
                self.__redis.rpushx(name, value)   # 这里"foo_list1"之前已经存在，往列表最右边添加一个元素，一次只能添加一个    s 
        if not self.__redis:
            self.initRedis()
        nowTime = uploadTime
        if uploadTime:
            nowTime = uploadTime
        else:
            nowTime = time.time()
        handleList(deviceName+":"+property,5,json.dumps({"value":value,"time":nowTime}))


        # if not self.__producer:
        #     self.initProducer()
        # topic = "cache_redis"
        # print("topic:"+topic+" msg:"+str(msg.__dict__))
        # self.__producer.send(topic,bytes(json.dumps(msg.__dict__), encoding = "utf8"))


    


class AppClient():
    def __init__(self):
        self.__consumer = None
        self.initConsumer()

    def initConsumer(self):
        try:
            self.__consumer = KafkaConsumer(bootstrap_servers=['edge-kafka:9092'],metadata_max_age_ms = 1000)
        except Exception as e:
            print("waiting kafka client start...")
            time.sleep(2)
            self.initConsumer()
    
    def startListen(self):   
        client = Client()
        subTuple = client.getSubTuple()
        self.__consumer.subscribe(topics = subTuple)
        print("start subscribe")
        for msg in self.__consumer:
            print("msg come")
            value = msg.value
            value = str(value,"utf-8")
            print(value)
            routeMsg = Message(value)
            on_message_come(client,routeMsg)

