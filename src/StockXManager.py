import requests
import pymysql
import json
from Lib_else import sleep_random, get_user_agent, set_proxies
import time
import brotli

class StockXManager:
    def __init__(self):
        self.auth_token = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImh0dHBzOi8vc3RvY2t4LmNvbS9lbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5zdG9ja3guY29tLyIsInN1YiI6ImF1dGgwfDYzZDA3ZjUxNzhkMTBiZTlkZjM1OThhZCIsImF1ZCI6ImdhdGV3YXkuc3RvY2t4LmNvbSIsImlhdCI6MTY3NjE0ODY2NSwiZXhwIjoxNjc2MTkxODY1LCJhenAiOiJPVnhydDRWSnFUeDdMSVVLZDY2MVcwRHVWTXBjRkJ5RCIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3MifQ.SMdPe058efwXTVtiwSddYkkyw6QjK1xHozbFpAL-0fFmxTWa7GNKbNk3Xr6A5e3QWkK0IsEWb48pS5nenypeup3Qf7mrsvbvX4BlYc84ywzaAUvzIqiHirgf-hMkoxUUF_IWCrzllQNFqbdwCJb8d0ru3lm3EZzNm-1chUMPMEAEeW9iSXclz27zcLqhKFeZ4dSGz_lcpEluKubfKUWEIkxRkY1s-877CUGGE6ghVEONwIQ8-WEZorE2h5qTHk6vqo_TXOSqUESkSlhA10u_HeHIhTJb2lLgfj3ALc6bJSXE-yoy-kmecRXYuCn7N1mwX5F5KC3iOI4_uyIGMHb46A'
        pass


    ### 1. 페이지 돌며 전체 상품 긁기 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_productlist_page(self, page, brand_list=['Nike', 'Jordan', 'Adidas', 'New Balance']):
        data = []
        response = self._post_productlist_page(page)
        if(response.status_code == 200):
            state, data = self._parse_productinfo(response=response, brand_list=brand_list)
        elif(response.status_code != 401):
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page' with [page=%s]) "%(response.status_code, page))
            state = False
        elif(response.status_code != 403):
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page' with [page=%s]) "%(response.status_code, page))
            state = False
        else:
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page' with [page=%s]) "%(response.status_code, page))
            state = False

        return state, data

    ### 2. 상품별 모델명 긁기 ###
    # input : urlkey
    # output : state, dict['model_no']
    def scrap_model_no(self, urlkey):
        data = {}
        response = self._get_model_no(urlkey)
        if(response.status_code == 200):
            data['model_no'] = self._parse_model_no(response=response)
            state = True
        elif(response.status_code != 401):
            print("[StockXManager] : Error Code(%s) at 'scrap_model_no' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        elif(response.status_code != 403):
            print("[StockXManager] : Error Code(%s) at 'scrap_model_no' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        else:
            print("[StockXManager] : Error Code(%s) at 'scrap_model_no' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False

        return state, data

    ### 3. 상품별 사이즈 스크랩 ###
    # input : urlkey
    # output : state, list[dict{id_stockx, size}]
    def scrap_size(self, urlkey):
        data = []
        response = self._post_size(urlkey)
        if(response.status_code == 200):
            data = self._parse_size(response=response)
            state = True
        elif(response.status_code != 401):
            print("[StockXManager] : Error Code(%s) at 'scrap_size' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        elif(response.status_code != 403):
            print("[StockXManager] : Error Code(%s) at 'scrap_size' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        else:
            print("[StockXManager] : Error Code(%s) at 'scrap_size' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False

        return state, data

    ### 4. 가격 스크랩 ###
    # input : urlkey
    # output : state, list[dict{size, price_buy, price_sell}]
    def scrap_price(self, urlkey):
        data = []
        response = self._post_price(urlkey)
        if(response.status_code == 200):
            data = self._parse_price(response=response)
            state = True
        elif(response.status_code != 401):
            print("[StockXManager] : Error Code(%s) at 'scrap_price' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        elif(response.status_code != 403):
            print("[StockXManager] : Error Code(%s) at 'scrap_price' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        else:
            print("[StockXManager] : Error Code(%s) at 'scrap_price' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False

        return state, data
    
    ### 5. 최근체결가 스크랩 ###
    # input : urlkey
    # output : state, list[dict{price_recent}]
    def scrap_price_recent(self, urlkey, id_stockx):
        data = {}
        response = self._get_price_recent(urlkey=urlkey, id_stockx=id_stockx)
        if(response.status_code == 200):
            data = self._parse_price_recent(response=response)
            state = True
        elif(response.status_code != 401):
            print("[StockXManager] : Error Code(%s) at 'scrap_price' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        elif(response.status_code != 403):
            print("[StockXManager] : Error Code(%s) at 'scrap_price' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False
        else:
            print("[StockXManager] : Error Code(%s) at 'scrap_price' with [urlkey=%s]) "%(response.status_code, urlkey))
            state = False

        return state, data

    
    ##### 기능 1 관련 함수 #############################################################################################################################################################################
    def _post_productlist_page(self, page):
        ## 400 : 이해를 못했단겨. 정보를 잘못 넣어서, request 자체를 해석을 못하겠다는.
        ## 403 : 금지당한거
        ## 404 : Not Found(서버는 맞는데, 그 안에서 파일을 못찾았단거)
        
        url = "https://stockx.com/api/p/e"
        headers = {
            'accept-language': 'ko-KR',   ## 이거 안넣으면 404
            'apollographql-client-name': 'Iron',    ## 필수
            'Content-Type': 'application/json',
            'origin': 'https://stockx.com',
            'Referer': 'https://stockx.com/ko-kr/sneakers',
            'selected-country': 'KR',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
            'Authorization': self.auth_token,
            'x-operation-name': 'Browse', ##  
            'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a', ## 
        }
        body = {
            "query":"query Browse($category: String, $filters: [BrowseFilterInput], $filtersVersion: Int, $query: String, $sort: BrowseSortInput, $page: BrowsePageInput, $currency: CurrencyCode, $country: String!, $market: String, $staticRanking: BrowseExperimentStaticRankingInput, $skipFollowed: Boolean!) {\n  browse(\n    category: $category\n    filters: $filters\n    filtersVersion: $filtersVersion\n    query: $query\n    sort: $sort\n    page: $page\n    experiments: {staticRanking: $staticRanking}\n  ) {\n    suggestions {\n      isCuratedPage\n      relatedPages {\n        title\n        url\n      }\n    }\n    results {\n      edges {\n        objectId\n        node {\n          ... on Product {\n            ...BrowseProductDetailsFragment\n            ...FollowedFragment @skip(if: $skipFollowed)\n            ...ProductTraitsFragment\n            market(currencyCode: $currency) {\n              ...MarketFragment\n            }\n          }\n          ... on Variant {\n            id\n            followed @skip(if: $skipFollowed)\n            product {\n              ...BrowseProductDetailsFragment\n              traits(filterTypes: [RELEASE_DATE, RETAIL_PRICE]) {\n                name\n                value\n              }\n            }\n            market(currencyCode: $currency) {\n              ...MarketFragment\n            }\n            traits {\n              size\n            }\n          }\n        }\n      }\n      pageInfo {\n        limit\n        page\n        pageCount\n        queryId\n        queryIndex\n        total\n      }\n    }\n    query\n  }\n}\n\nfragment FollowedFragment on Product {\n  followed\n}\n\nfragment ProductTraitsFragment on Product {\n  productTraits: traits(filterTypes: [RELEASE_DATE, RETAIL_PRICE]) {\n    name\n    value\n  }\n}\n\nfragment MarketFragment on Market {\n  currencyCode\n  bidAskData(market: $market, country: $country) {\n    lowestAsk\n    highestBid\n    lastHighestBidTime\n    lastLowestAskTime\n  }\n  state(country: $country) {\n    numberOfCustodialAsks\n  }\n  salesInformation {\n    lastSale\n    lastSaleDate\n    salesThisPeriod\n    salesLastPeriod\n    changeValue\n    changePercentage\n    volatility\n    pricePremium\n  }\n  deadStock {\n    sold\n    averagePrice\n  }\n}\n\nfragment BrowseProductDetailsFragment on Product {\n  id\n  name\n  urlKey\n  title\n  brand\n  description\n  model\n  condition\n  productCategory\n  listingType\n  media {\n    thumbUrl\n    smallImageUrl\n  }\n}\n",
            "variables":{
                "query":"",
                "category":"",
                "filters":[{"id":"currency","selectedValues":["KRW"]}],
                "filtersVersion":4,
                "sort":{"id":"featured_loc","order":"DESC"},
                "page":{"index":page,"limit":40},
                "currency":"KRW",
                "country":"KR",
                "marketName":None,
                "staticRanking":{"enabled":False},
                "skipFollowed":True},
            "operationName":"Browse"
            }
        data = json.dumps(body)
        response = requests.post(url, headers=headers, data=data)

        return response
    def _parse_productinfo(self, response, brand_list):
        output_productlist = []
        # state = False

        data = response.json()
        if(data['data']['browse']['results']['pageInfo']['total']==0):
            # print("[StockXManager] : 마지막 페이지 입니다.")
            state = False
        else:
            for item in data['data']['browse']['results']['edges']:
                if(self._filter_brand(item, brand_list)):
                    product = self.new_product()
                    product['id_stockx'] = item['node']['id']
                    product['brand'] = item['node']['brand']
                    product['product_name'] = item['node']['title']
                    product['urlkey'] = item['node']['urlKey']

                    ## 저장해야함
                    output_productlist.append(product)
                    del product
                    state=True
        
        return state, output_productlist
    
    def _filter_brand(self, item, filter):
        if(type(filter) == list):
            for item_filter in filter:
                if(item['node']['brand'] == item_filter):
                    return True

        elif(type(filter) == str):
            if(item['node']['brand'] == filter):
                    return True

        else:
            print("[StockXManager] : '_filter_brand' cannot filter type %s"%(type(filter)))

        return False
    def new_product(self):
        product = {}
        product['id_stockx'] = ''
        product['brand'] = ''
        product['model_no'] = ''
        product['product_name'] = ''
        product['urlkey'] = ''

        return product
    
    ##### 기능 2 관련 함수 #############################################################################################################################################################################
    def _get_model_no(self, urlkey):
        url = "https://stockx.com/"+urlkey
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            # 'Host' : 'https://stockx.com/ko-kr',
            'Referer': 'https://stockx.com/ko-kr/sneakers',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
            # 'User-Agent' : get_user_agent(),
            # 'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            # 'Cookie': '__cf_bm=fw4jjjUy5taEN6zR11CIdWxhBPfEzGB0MIISUbxijvU-1675090134-0-AW/Zip/nfts0u1BxLUXaMb3sTWTu8Gw/Qxqzz+NV+fRpxPvXR2ykkNaledaIAUgPAs/5foilWlpbMeaD6tQCVz8=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=4d1108b7-bdc0-47f6-b220-2c67b639c993'
        }
        
        # headers = {
        #     'Cookie': '__cf_bm=UiZsDBYlVhKdmrNdgClLy2UgWdgZre97PEtGWUIGsL0-1676115937-0-AStwFPbEDLp6Kru9AMWMIRR9EW8PHHIU2kikpW0lqZsKn5UBDqDjVZxOR++NasLiafaZWn1XJ8/oj6d4PlXHTuU=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=79cb40a0-35ba-4e6a-8ba6-744f0ba4eb70'
        # }
        # response = requests.get(url, headers=headers)
        # response = requests.request("GET", url)
        response = requests.request("GET", url, headers=headers)

        return response
    def _parse_model_no(self,response):
        html_text = response.text

        try:
            title = self._parse_title(html_text)
            twittertitle = self._parse_twittertitle(html_text)

            str = title.replace(twittertitle, '')

            indexes = [index for index, char in enumerate(str) if char=='-']
            model_no = str[indexes[0]+1:indexes[-1]].strip()
            return model_no
        
        except Exception as err:
            print("[StockXManager] : Error(%s) at '_parse_model_no' with [미정...]) "%(err))
            return ''
    def _parse_title(self, html_text):
        ## tag 로 substring 찾자.
        idx1_1 = html_text.find('<title')
        idx1_2 = html_text.find('</title>')
        str1 = html_text[idx1_1:idx1_2+len('</title>')]
        
        ## tag지우고, text만 뽑자.
        idx2_1 = str1.find('>')
        idx2_2 = str1.find('</title>')
        str2 = str1[idx2_1+len('>'):idx2_2]
        
        return str2
    def _parse_twittertitle(self, html_text):
        substr1 = '<meta data-rh="true" property="twitter:title" content='
        idx1 = html_text.find(substr1)
        str1 = html_text[idx1+len(substr1):]

        substr2 = '/>'
        idx2 = str1.find(substr2)
        str2 = str1[:idx2]

        indexes = [index for index, char in enumerate(str2) if char=='"']
        str3 = str2[indexes[0]+1:indexes[1]].strip()

        return str3
    def _query_update_model_no(self, model_no, urlkey):
        try:
            query = "UPDATE stockx SET model_no=%s WHERE urlkey=%s"
            self.cursor.execute(query, (model_no, urlkey))

            self.con.commit()
        except Exception as e:
            print(model_no, urlkey)
            print(e)

    ##### 기능 3 관련 함수 #############################################################################################################################################################################
    """ 
    ## 옛날 버전 (~23.02.03)
    def _post_size(self, urlkey):
        url = "https://stockx.com/api/p/e"
        headers = {
            # 'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-language': 'ko-KR',   ## 이거 안넣으면 404
            'apollographql-client-name': 'Iron',    ## 필수
            'Content-Type': 'application/json',
            # 'origin': 'https://stockx.com',
            'Referer': 'https://stockx.com/ko-kr/'+urlkey,
            'selected-country': 'KR',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
            'User-Agent' : get_user_agent(),
            # 'Authorization' : 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuc3RvY2t4LmNvbS8iLCJzdWIiOiJhdXRoMHw2M2QwN2Y1MTc4ZDEwYmU5ZGYzNTk4YWQiLCJhdWQiOlsiZ2F0ZXdheS5zdG9ja3guY29tIiwiaHR0cHM6Ly9zdG9ja3gtcHJvZC5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjc1NDA0NjQ2LCJleHAiOjE2NzU0NDc4NDYsImF6cCI6Ik9WeHJ0NFZKcVR4N0xJVUtkNjYxVzBEdVZNcGNGQnlEIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSJ9.PheLqoED2YCgg2vYLTyq6TRkLiECRRyc8EduIf74EF5sbSeuhJevuKP11IQVj2a2lSDcTtz3L6aYRwqWbIoqziqIeOk1dbJrXDemrebBk1IalJ9XPr3wvM2UdFNdMwpIPd9HlpNdpCxm21cbu9sYq1V4-uUDgXEc5qRdnt1GFZL0WmaGcewyFxGkIxW6PM8LZvOzt7pMO0lJKHJr0H8Pba6GNCTRXjUdv2-5u1wD9Uh2Ce_VBvA-w3fG22qViwE37PCSpyfxcx_W5U4KWdg33I8oMqJnKo_22G_38WbyEwcIPux_S8QFU0dIn8Del9zlkRIDRld1kGsvODO2XtVSjQ',
            # 'sec-ch-ua-mobile' : '?0',
            # 'sec-ch-ua-platform' : '"Windows"',
            # 'sec-fetch-dest' : 'empty',
            # 'sec-fetch-mode': 'cors',
            # 'sec-fetch-site': 'same-origin',
            'x-operation-name': 'GetMarketData', ##  
            'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a', ## 
            # 'X-Remote-IP': '10.10.10.10,'
        }
        body = {
            "query": "query GetMarketData($id: String!, $currencyCode: CurrencyCode, $countryCode: String!, $marketName: String) {\n  product(id: $id) {\n    id\n    urlKey\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n    variants {\n      id\n      market(currencyCode: $currencyCode) {\n        bidAskData(country: $countryCode, market: $marketName) {\n          highestBid\n          highestBidSize\n          lowestAsk\n          lowestAskSize\n        }\n      }\n    }\n    ...BidButtonFragment\n    ...BidButtonContentFragment\n    ...BuySellFragment\n    ...BuySellContentFragment\n    ...XpressAskPDPFragment\n  }\n}\n\nfragment BidButtonFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BidButtonContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  minimumBid(currencyCode: $currencyCode)\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n      numberOfAsks\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n        numberOfAsks\n      }\n    }\n  }\n}\n\nfragment BuySellFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BuySellContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment XpressAskPDPFragment on Product {\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode) {\n      numberOfCustodialAsks\n    }\n  }\n  variants {\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode) {\n        numberOfCustodialAsks\n      }\n    }\n  }\n}\n",
            "variables": {
                "id": urlkey,
                "currencyCode": "KRW",
                "countryCode": "KR",
                "marketName": None
            },
            "operationName": "GetMarketData"
        }
        data = json.dumps(body)
        response = requests.post(url, headers=headers, data=data)
        # proxies = set_proxies()
        # response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=3)
        return response
     """

    ## 지금 버전 (23.02.03~)
    def _post_size(self, urlkey):
        url = "https://stockx.com/api/p/e"
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR',
            'apollographql-client-name': 'Iron',
            'apollographql-client-version': '2023.01.29.00',
            'app-platform': 'Iron',
            'app-version': '2023.01.29.00',
            'Origin': 'https://stockx.com',
            'Referer': 'https://stockx.com/ko-kr/'+urlkey,
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'selected-country': 'KR',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-operation-name': 'GetMarketData',
            'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a',
            'Authorization': self.auth_token,
            'Content-Type': 'application/json',
            # 'User-Agent': get_user_agent(),
        }
        payload = json.dumps({
            "query": "query GetMarketData($id: String!, $currencyCode: CurrencyCode, $countryCode: String!, $marketName: String) {\n  product(id: $id) {\n    id\n    urlKey\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n    variants {\n      id\n      market(currencyCode: $currencyCode) {\n        bidAskData(country: $countryCode, market: $marketName) {\n          highestBid\n          highestBidSize\n          lowestAsk\n          lowestAskSize\n        }\n      }\n    }\n    ...BidButtonFragment\n    ...BidButtonContentFragment\n    ...BuySellFragment\n    ...BuySellContentFragment\n    ...XpressAskPDPFragment\n  }\n}\n\nfragment BidButtonFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BidButtonContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  minimumBid(currencyCode: $currencyCode)\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n      numberOfAsks\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n        numberOfAsks\n      }\n    }\n  }\n}\n\nfragment BuySellFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BuySellContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment XpressAskPDPFragment on Product {\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode) {\n      numberOfCustodialAsks\n    }\n  }\n  variants {\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode) {\n        numberOfCustodialAsks\n      }\n    }\n  }\n}\n",
            "variables": {
                "id": urlkey,
                "currencyCode": "KRW",
                "countryCode": "KR",
                "marketName": None
            },
            "operationName": "GetMarketData"
        })
        # response = requests.post(url, headers=headers, data=payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        # proxies = set_proxies()
        # response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=3)
        return response
    def _parse_size(self, response):
        output_productlist = []

        data = response.json()
        # data = brotli.decompress(response.content).json() ## 데이터 깨져서, brotli encoding
        for item in data['data']['product']['variants']:
            product = {}
            product['id_stockx'] = item['id']
            if(item['market']['bidAskData']['highestBidSize'] == None):
                product['size'] = item['market']['bidAskData']['lowestAskSize']
            else:
                product['size'] = item['market']['bidAskData']['highestBidSize']
            
            output_productlist.append(product)
            del product

        return output_productlist

    ##### 기능 4 관련 함수 #############################################################################################################################################################################
    def _post_price(self, urlkey):
        url = "https://stockx.com/api/p/e"
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR',
            'apollographql-client-name': 'Iron',
            'apollographql-client-version': '2023.01.29.00',
            'app-platform': 'Iron',
            'app-version': '2023.01.29.00',
            'Origin': 'https://stockx.com',
            'Referer': 'https://stockx.com/ko-kr/'+urlkey,
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'selected-country': 'KR',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-operation-name': 'GetMarketData',
            'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a',
            'Authorization': self.auth_token,
            'Content-Type': 'application/json',
            'Cookie': 'stockx_selected_currency=USD;',
            # 'User-Agent': get_user_agent(),
        }
        payload = json.dumps({
            "query": "query GetMarketData($id: String!, $currencyCode: CurrencyCode, $countryCode: String!, $marketName: String) {\n  product(id: $id) {\n    id\n    urlKey\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n    variants {\n      id\n      market(currencyCode: $currencyCode) {\n        bidAskData(country: $countryCode, market: $marketName) {\n          highestBid\n          highestBidSize\n          lowestAsk\n          lowestAskSize\n        }\n      }\n    }\n    ...BidButtonFragment\n    ...BidButtonContentFragment\n    ...BuySellFragment\n    ...BuySellContentFragment\n    ...XpressAskPDPFragment\n  }\n}\n\nfragment BidButtonFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BidButtonContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  minimumBid(currencyCode: $currencyCode)\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n      numberOfAsks\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n        numberOfAsks\n      }\n    }\n  }\n}\n\nfragment BuySellFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BuySellContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment XpressAskPDPFragment on Product {\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode) {\n      numberOfCustodialAsks\n    }\n  }\n  variants {\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode) {\n        numberOfCustodialAsks\n      }\n    }\n  }\n}\n",
            "variables": {
                "id": urlkey,
                "currencyCode": "USD",
                "countryCode": "KR",
                "marketName": None
            },
            "operationName": "GetMarketData"
        })
        # response = requests.post(url, headers=headers, data=payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        # proxies = set_proxies()
        # response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=3)
        return response
    def _parse_price(self, response):
        output_productlist = []

        data = response.json()
        # data = brotli.decompress(response.content).json() ## 데이터 깨져서, brotli encoding

        if(data['data']['product'] == None):
            print("[StockXManager] : Product doesn't exist at [미정...]) ")
            return output_productlist

        for item in data['data']['product']['variants']:
            product = {}
            # id_stockx = item['id']
            product['size'] = item['market']['bidAskData']['highestBidSize']
            product['price_buy'] = item['market']['bidAskData']['lowestAsk']
            product['price_sell'] = item['market']['bidAskData']['highestBid']

            output_productlist.append(product)

        return output_productlist


    ##### 기능 5 관련 함수 #############################################################################################################################################################################
    def _get_price_recent(self, urlkey, id_stockx):
        url = "https://stockx.com/api/p/e"
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR',
            'apollographql-client-name': 'Iron',
            'apollographql-client-version': '2023.01.29.00',
            'app-platform': 'Iron',
            'app-version': '2023.01.29.00',
            'Origin': 'https://stockx.com',
            'Referer': 'https://stockx.com/ko-kr/'+urlkey,
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'selected-country': 'KR',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-operation-name': 'GetMarketData',
            'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a',
            'Authorization': self.auth_token,
            'Content-Type': 'application/json',
            # 'User-Agent': get_user_agent(),
        }
        payload = json.dumps({
        "query": "query GetProductMarketSales($productId: String!, $currencyCode: CurrencyCode, $first: Int, $isVariant: Boolean!) {\n  product(id: $productId) @skip(if: $isVariant) {\n    id\n    market(currencyCode: $currencyCode) {\n      ...MarketSalesFragment\n    }\n  }\n  variant(id: $productId) @include(if: $isVariant) {\n    id\n    market(currencyCode: $currencyCode) {\n      ...MarketSalesFragment\n    }\n  }\n}\n\nfragment MarketSalesFragment on Market {\n  sales(first: $first) {\n    edges {\n      cursor\n      node {\n        amount\n        associatedVariant {\n          id\n          traits {\n            size\n          }\n        }\n        createdAt\n      }\n    }\n  }\n}\n",
        "variables": {
            "productId": id_stockx,
            "currencyCode": "USD",
            "first": 50,
            "isVariant": True
        },
        "operationName": "GetProductMarketSales"
        })
        # response = requests.post(url, headers=headers, data=payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        # proxies = set_proxies()
        # response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=3)
        return response
    def _parse_price_recent(self, response):
        output = {}

        data = response.json()
        if(len(data['data']['variant']['market']['sales']['edges']) != 0):
            output['price_recent'] = data['data']['variant']['market']['sales']['edges'][0]['node']['amount']

        return output



if __name__ == '__main__':
    StockXManager = StockXManager()
