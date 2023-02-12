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
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
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
        ## South Korea
        ## http
        "14.46.231.57:8000",    ## [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다
        "14.46.231.171:8001",   ## [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다
        "125.141.151.83:80",    ## SSL: WRONG_VERSION_NUMBER]
        "175.45.195.18:80",     ## The handshake operation timed out
        "1.224.3.122:3888",     ## SSL: WRONG_VERSION_NUMBER]
        "112.217.162.5:3128",   ## Connection to 112.217.162.5 timed out.
        ## https
        "115.144.101.200:10000",    ## SSL: WRONG_VERSION_NUMBER]
        "124.243.11.41:8000",       ## SSL: WRONG_VERSION_NUMBER]
        "118.45.255.236:8000",      ## [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다
        "112.165.14.107:8000",      ## [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다


        "20.121.184.238:443",   ## US   ## 
        "128.14.27.141:80",   ## US
        "128.22.123.175:80",  ## Japan  The handshake operation timed out
        "20.110.99.169:80",   ## US     SSL: WRONG_VERSION_NUMBER
        "128.14.27.143:80"   ## US
    ]

    # proxy_server = random.choice(proxy_server_list)
    proxy_server = proxy_server_list[14]
    proxies = {"http": "http://"+proxy_server, 'https': "https://"+proxy_server}

    return proxies
