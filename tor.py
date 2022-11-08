#!/usr/bin/python3
import os
from timeit import default_timer
from shutil import which
from stem.control import Controller
from stem import Signal
from controller.headers import headers
import requests

class Tor(): 
    """
    Tor controlling class
    """
    def __init__(self,cport : int,hport : int,timeout = 20):
        self.cport = cport
        self.hport = hport
        self.timeout = timeout
        if which("tor") == None:
            return 0

    def change_ip(self):
        with Controller.from_port(port=self.cport) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)

    def start(self):
        self.stop()
        self.mktemp_config()
        os.system("{} -f torrc > /tmp/stdout &".format(which("tor")))
        start_time = default_timer()
        while True:
            with open("/tmp/stdout","r") as file:
                lines = file.read().split("\n")
                if len(lines) > 3 and "Bootstrapped 100%" in lines[-2]:
                        return "Started"
                else:
                    if abs(start_time-default_timer()) > self.timeout:
                        self.stop()
                        return "Timeout"
                    else:
                        continue
                file.close()

    def mktemp_config(self):
        file = open("torrc","w")
        file.write("ControlPort {}\nHTTPTunnelPort {}".format(self.cport,self.hport))
        file.close()

    def stop(self):
        return os.system("pkill {} > /dev/null 2>&1 ".format(os.path.basename(which("tor"))))

    def proxy(self):
        return {"http": "http://localhost:{}".format(self.hport), "https": "http://localhost:{}".format(self.hport)}


class Instagram():
    """
    Instagram controller
    """
    def __init__(self,username,Tor : Tor):
        self.username = username
        self.session = requests.session()
        line = self.session.get("https://instagram.com/"+username).text.split("\n")[13]
        if self.username not in line:
            self.userexists  = False
            self.name = None
        else:
            self.userexists = True
            self.name = line.split("(")[0].split(">")[-1][:-1]
        self.tor = Tor
        self.session.proxies = self.tor.proxy()

    def ipaddr(self) -> str:
        return self.session.get("https://httpbin.org/ip").json()["origin"]

    def login(self,username,password) -> bool:
        pass

tor = Tor(9876,4949)
tor.start()
ig = Instagram("tdynamos.linux",tor)
print(ig.name)
print(ig.ipaddr())
