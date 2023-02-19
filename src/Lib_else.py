import time
import random
import requests
from datetime import datetime

def sleep_random(t_min, t_max):
    time.sleep(random.uniform(t_min,t_max))


def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def get_date():
    return datetime.now().strftime('%y%m%d')

def get_user_agent():
    user_agent_list = [
        # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        # "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        # "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        # "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        # "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        # "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        # "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        # "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        "PostmanRuntime/7.30.1"
    ]
    
    return random.choice(user_agent_list)

def set_proxies():
    # proxy_url = "free-proxy-list.net/"
    # response = requests.get(proxy_url)
    # sel = Selector(resp)
    # tr_list = sel.xpath('//*[@id="proxylisttable"]/tbody/tr')

    # proxy_server_list = []

    # for tr in tr_list:
    #     ip = tr.xpath("td[1]/text()").extract_first()
    #     port = tr.xpath("td[2]/text()").extract_first()
    #     https = tr.xpath("td[7]/text()").extract_first()

    #     if https == "yes":
    #         server = f"{ip}:{port}"
    #         proxy_server_list.append(server)

    proxy_server_list = [
        "167.235.35.185:3128",

        
        
        # "212.108.144.67:8080",
        # "91.207.173.99:443",
        # "",
        # "",
    ]

    # proxy_server = random.choice(proxy_server_list)
    proxy_server = proxy_server_list[-1]
    # proxies = {"http": "http://"+proxy_server, 'https': "https://"+proxy_server}
    proxies = {"http": proxy_server, 'https': proxy_server}

    return proxies
