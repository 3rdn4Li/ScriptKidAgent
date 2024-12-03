import requests
import time
import hashlib
class Proxy:
    def __init__(self, ip, port):
        self.nps_host = "http://149.28.91.18:8080"
        self.ip = ip
        self.proxy_port = port
        self.auth_key = "ScriptKidTest"
        self.vkey = ""
        
    def get_key(self):
        timestamp = str(int(time.time()))
        auth_key = hashlib.md5((self.auth_key+timestamp).encode()).hexdigest()
        return auth_key, timestamp
    
    def add_client(self):
        auth_key, timestamp = self.get_key()
        uri = "/client/add"
        data = {
            "auth_key": auth_key,
            "timestamp": timestamp,
            "remark": self.ip,
            "config_conn_allow": 1,
            "compress": 0,
            "crypt": 0
        }
        response = requests.post(f"{self.nps_host}{uri}", data=data)
        print(response.text)
    
    def get_client(self):
        auth_key, timestamp = self.get_key()
        uri = "/client/list"
        data = {
            "auth_key": auth_key,
            "timestamp": timestamp,
            "search": self.ip,
            "start": 0,
            "limit": 200
        }
        response = requests.post(f"{self.nps_host}{uri}", data=data)
        return response.json()

    def add_socks5(self):
        auth_key, timestamp = self.get_key()
        uri = "/proxy/add"
        data = {
            "auth_key": auth_key,
            "timestamp": timestamp,
            "remark": self.ip,
            "type": "socks5",
            "client_id": self.id,
            "port" : self.proxy_port
        }
        response = requests.post(f"{self.nps_host}{uri}", data=data)
        

    def get_proxy(self):
        auth_key, timestamp = self.get_key()
        uri = "/index/gettunnel"
        data = {
            "auth_key": auth_key,
            "timestamp": timestamp,
            "type": "socks5",
            "offset": 0,
            "limit": 100
        }
        response = requests.post(f"{self.nps_host}{uri}", data=data)
        return response.json()
        
    def setup(self):
        self.add_client()
        client = self.get_client()
        self.vkey = client.get('rows')[0].get('VerifyKey')
        self.id = client.get('rows')[0].get('Id')
        self.add_socks5()
