import requests
import pymysql
import json
from Lib_else import sleep_random, get_user_agent, set_proxies
import time
import brotli

class StockXManager:
    def __init__(self):
        self.con = self.connect_db()
        self.cursor = self.con.cursor()

    ##### 기능 1. (일회성) 상품 스크랩 #####
    def scrap_product(self, delay_min=0.2, delay_max=0.5):
        print("[StockX_Manager] : 상품 Srap 시작합니다.")
        page = 1
        
        tic = time.time()
        while(1) :
            sleep_random(delay_min, delay_max)
            response = self._request_post_productlist_page_N(page)
            if(response.status_code != 200):
                print(response.status_code)
                continue

            state = self._parse_productinfo(response)

            toc = time.time()
            print("[StockX_Manager] : %d page - %.0fs" %(page, toc-tic))

            if(state):
                page = page + 1
            else:
                break
        toc = time.time()
        print("[StockX_Manager] : 상품 Srap 완료되었습니다. %.0fmin"%((toc-tic)/60))

    ##### 기능 2. (일회성) 모델명 스크랩 #####
    def scrap_model_no(self, batch=50, delay_min=0.2, delay_max=0.5, id_start=1):
        print("[StockX_Manager] : 모델명 Scrap 시작합니다.")
        cnt_total = self._query_count_total(table="stockx")

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self._query_fetch_urlkey(table="stockx", id_start=id_start, id_end=id_end)

            ## 처리
            for (id, urlkey) in data:
                # Model No.
                sleep_random(delay_min, delay_max)
                response = self._request_get_model_no(urlkey=urlkey)
                if(response.status_code == 403):
                    # print(response.headers)
                    print("status_code: %s (urlkey: %s)"%(response.status_code, urlkey))
                elif(response.status_code != 200):
                    print(response.status_code)
                    continue
                else:
                    model_no = self._parse_model_no(response)
                    self._query_update_model_no(model_no=model_no, urlkey=urlkey)
            
            toc = time.time()
            print("[StockX_Manager] :%4d/%4d - %.0f"%(id_end, cnt_total, toc-tic))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

    ##### 기능 3. (일회성) 사이즈 스크랩 #####
    def scrap_size(self, batch=50, delay_min=0.2, delay_max=0.5, id_start=1):
        print("[StockX_Manager] : 사이즈 Scrap 시작합니다.")
        cnt_total = self._query_count_total(table="sneakers")

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self._query_fetch_all(table="sneakers", id_start=id_start, id_end=id_end)

            ## 처리
            for (id, brand, model_no, product_name, urlkey) in data:
                sleep_random(delay_min, delay_max)
                state = self._insert_data_with_size_scraping(brand=brand, model_no=model_no, product_name=product_name, urlkey=urlkey)

                if(not state):
                    continue
            
            toc = time.time()
            print("처리중(%4d/%4d) - %.0fs"%(id_end, cnt_total, toc-tic))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

    ##### 기능 4. (주기성) 가격 스크랩 #####
    def scrap_price(self, batch=20, delay_min=0.5, delay_max=0.8, id_start=0):
        print("[StockX_Manager] :가격 Scrap 시작합니다.")
        tic = time.time()
        data = self._query_select_distinct_urlkey(table="sneakers_price")
        cnt_total = len(data)
        while(1):
            id_end = min(id_start + batch, cnt_total)
            data_batch = data[id_start: id_end]
            for urlkey in data_batch:
                sleep_random(delay_min, delay_max)

                state = self._update_price(urlkey=urlkey[0])

                # price recent
                data_id = self._query_select_id_stockx_in_urlkey(urlkey=urlkey[0])
                for id_stockx in data_id:
                    sleep_random(delay_min, delay_max)

                    state_price_recent = self._update_price_recent(urlkey=urlkey[0], id_stockx=id_stockx[0])

                # if(~state):
                #     continue
            
            toc = time.time()
            print("[StockX_Manager] : 처리중(%d/%d) - %.1fmin"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch





    ########################################################################################################################################################################
    ##### 기능 1 관련 함수 #####
    def _request_post_productlist_page_N(self, page):
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
    def _parse_productinfo(self, response):
        data = response.json()
        if(data['data']['browse']['results']['pageInfo']['total']==0):
            return False
        else:
            for item in data['data']['browse']['results']['edges']:
                if(self._filter_brand(item, ['Nike', 'Jordan', 'adidas', 'New Balance'])):
                    product = self.new_product()
                    product['id_stockx'] = item['node']['id']
                    product['brand'] = item['node']['brand']
                    product['product_name'] = item['node']['title']
                    product['urlkey'] = item['node']['urlKey']

                    self._query_insert_productinfo(product)
                    del product
            return True
    def _query_insert_productinfo(self, product):
        try:
            query = "INSERT INTO stockx (brand, product_name, id_stockx, urlkey) VALUES (%s, %s, %s, %s)" 
            self.cursor.execute(query, (product['brand'], product['product_name'], product['id_stockx'], product['urlkey']))

            self.con.commit()
        except Exception as e:
            print(product)
            print(e)

    def _filter_brand(self, item, filter):
        if(type(filter) == list):
            for item_filter in filter:
                if(item['node']['brand'] == item_filter):
                    return True

        elif(type(filter) == str):
            if(item['node']['brand'] == filter):
                    return True


        else:
            print("_filter_brand cannot filter type %s"%(type(filter)))

        return False
    def new_product(self):
        product = {}
        product['id_stockx'] = ''
        product['brand'] = ''
        product['model_no'] = ''
        product['product_name'] = ''
        product['urlkey'] = ''

        return product
    ########################################################################################################################################################################
    ##### 기능 2 관련 함수 #####
    def _query_count_total(self, table):
        query = "SELECT COUNT(*) FROM %s"%(table)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        return result[0]
    def _query_fetch_urlkey(self, table, id_start, id_end):
        query = "SELECT id, urlkey FROM %s WHERE id>%d AND id <%d"%(table, id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data

    def _request_get_model_no(self, urlkey):
        url = "https://stockx.com/"+urlkey
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            # 'Host' : 'https://stockx.com/ko-kr',
            'Referer': 'https://stockx.com/ko-kr/sneakers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
            # 'User-Agent' : get_user_agent(),
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'docs',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'Cookie': '__cf_bm=fw4jjjUy5taEN6zR11CIdWxhBPfEzGB0MIISUbxijvU-1675090134-0-AW/Zip/nfts0u1BxLUXaMb3sTWTu8Gw/Qxqzz+NV+fRpxPvXR2ykkNaledaIAUgPAs/5foilWlpbMeaD6tQCVz8=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=4d1108b7-bdc0-47f6-b220-2c67b639c993'
        }
        
        # response = requests.get(url, headers=headers)
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
        except Exception as e:
            print (e)
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

    ########################################################################################################################################################################
    ##### 기능 3 관련 함수 #####
    # size랑 price 받아오는 리소스가 동일하다.
    #### 옛날 버전 (~23.02.03)
    # def _request_post_size(self, urlkey):
    #     url = "https://stockx.com/api/p/e"
    #     headers = {
    #         # 'Accept': '*/*',
    #         # 'Accept-Encoding': 'gzip, deflate, br',
    #         'Accept-language': 'ko-KR',   ## 이거 안넣으면 404
    #         'apollographql-client-name': 'Iron',    ## 필수
    #         'Content-Type': 'application/json',
    #         # 'origin': 'https://stockx.com',
    #         'Referer': 'https://stockx.com/ko-kr/'+urlkey,
    #         'selected-country': 'KR',
    #         # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
    #         'User-Agent' : get_user_agent(),
    #         # 'Authorization' : 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuc3RvY2t4LmNvbS8iLCJzdWIiOiJhdXRoMHw2M2QwN2Y1MTc4ZDEwYmU5ZGYzNTk4YWQiLCJhdWQiOlsiZ2F0ZXdheS5zdG9ja3guY29tIiwiaHR0cHM6Ly9zdG9ja3gtcHJvZC5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjc1NDA0NjQ2LCJleHAiOjE2NzU0NDc4NDYsImF6cCI6Ik9WeHJ0NFZKcVR4N0xJVUtkNjYxVzBEdVZNcGNGQnlEIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSJ9.PheLqoED2YCgg2vYLTyq6TRkLiECRRyc8EduIf74EF5sbSeuhJevuKP11IQVj2a2lSDcTtz3L6aYRwqWbIoqziqIeOk1dbJrXDemrebBk1IalJ9XPr3wvM2UdFNdMwpIPd9HlpNdpCxm21cbu9sYq1V4-uUDgXEc5qRdnt1GFZL0WmaGcewyFxGkIxW6PM8LZvOzt7pMO0lJKHJr0H8Pba6GNCTRXjUdv2-5u1wD9Uh2Ce_VBvA-w3fG22qViwE37PCSpyfxcx_W5U4KWdg33I8oMqJnKo_22G_38WbyEwcIPux_S8QFU0dIn8Del9zlkRIDRld1kGsvODO2XtVSjQ',
    #         # 'sec-ch-ua-mobile' : '?0',
    #         # 'sec-ch-ua-platform' : '"Windows"',
    #         # 'sec-fetch-dest' : 'empty',
    #         # 'sec-fetch-mode': 'cors',
    #         # 'sec-fetch-site': 'same-origin',
    #         'x-operation-name': 'GetMarketData', ##  
    #         'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a', ## 
    #         # 'X-Remote-IP': '10.10.10.10,'
    #     }
    #     body = {
    #         "query": "query GetMarketData($id: String!, $currencyCode: CurrencyCode, $countryCode: String!, $marketName: String) {\n  product(id: $id) {\n    id\n    urlKey\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n    variants {\n      id\n      market(currencyCode: $currencyCode) {\n        bidAskData(country: $countryCode, market: $marketName) {\n          highestBid\n          highestBidSize\n          lowestAsk\n          lowestAskSize\n        }\n      }\n    }\n    ...BidButtonFragment\n    ...BidButtonContentFragment\n    ...BuySellFragment\n    ...BuySellContentFragment\n    ...XpressAskPDPFragment\n  }\n}\n\nfragment BidButtonFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BidButtonContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  minimumBid(currencyCode: $currencyCode)\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n      numberOfAsks\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n        numberOfAsks\n      }\n    }\n  }\n}\n\nfragment BuySellFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BuySellContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment XpressAskPDPFragment on Product {\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode) {\n      numberOfCustodialAsks\n    }\n  }\n  variants {\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode) {\n        numberOfCustodialAsks\n      }\n    }\n  }\n}\n",
    #         "variables": {
    #             "id": urlkey,
    #             "currencyCode": "KRW",
    #             "countryCode": "KR",
    #             "marketName": None
    #         },
    #         "operationName": "GetMarketData"
    #     }
    #     data = json.dumps(body)
    #     response = requests.post(url, headers=headers, data=data)
    #     # proxies = set_proxies()
    #     # response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=3)
    #     return response
    #### 지금 버전 (23.02.03~)
    def _request_post_size(self, urlkey):
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
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuc3RvY2t4LmNvbS8iLCJzdWIiOiJhdXRoMHw2M2QwN2Y1MTc4ZDEwYmU5ZGYzNTk4YWQiLCJhdWQiOiJnYXRld2F5LnN0b2NreC5jb20iLCJpYXQiOjE2NzU2Nzg0MDQsImV4cCI6MTY3NTcyMTYwNCwiYXpwIjoiT1Z4cnQ0VkpxVHg3TElVS2Q2NjFXMER1Vk1wY0ZCeUQiLCJzY29wZSI6Im9mZmxpbmVfYWNjZXNzIn0.j8l4GwvwMEm-hp5vPKexLQK7AFTlNSF3cIwfSUedK1B6jKJ0AqKSgM1XxQp9RoD6lwyy4iMAwlrEC2GA4FUTx7ROSEn45IgWSUq2fTaT4pR7xO5GfmOqgdMZpW346bnBvDANloHSE3NlUy5C7UWPD2993erkc1j1kqbOV8JyCPk06aWZAxes1n-JeptnBWVuZRcXfVZiVqsHVkaOekLtq4ybo_RbcT2_Hst3qmdpewuf2RdvHzXHAAWyoVdiG-SXJ3xuCo3BEpBXfiLITxozLbihJO5EeIOkAsQHXrIXeKSJkn0HwDPF72-j_r0TraOJy2wvStthdftsyAjuQ_WCiw',
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


    def _query_fetch_all(self, table, id_start, id_end):
        query = "SELECT id, brand, model_no, product_name, urlkey FROM %s WHERE id>%d AND id <%d"%(table, id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data
    def _insert_data_with_size_scraping(self, brand, model_no, product_name, urlkey):
        response = self._request_post_size(urlkey=urlkey)
        if(response.status_code != 200):
            print("status_code: %d request_post_size(url_key:%s)"%(response.status_code, urlkey))
            return False
        else:
            data = response.json()
            # data = brotli.decompress(response.content).json()
            for item in data['data']['product']['variants']:
                id_stockx = item['id']
                size = item['market']['bidAskData']['highestBidSize']

                self._query_insert_data_with_size(brand=brand, model_no=model_no, product_name=product_name, size=size, urlkey=urlkey, id_stockx=id_stockx)

            return True
    def _query_insert_data_with_size(self, brand, model_no, product_name, size, urlkey, id_stockx):
        try:
            ## 임시로 id_stockx만 업데이트
            # query = "UPDATE sneakers_price SET id_stockx=%s WHERE model_no=%s AND size_stockx=%s"
            # self.cursor.execute(query, (id_stockx, model_no, size))

            query = "INSERT INTO sneakers_price (brand, model_no, product_name, size_stockx, urlkey, id_stockx) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query, (brand, model_no, product_name, size, urlkey, id_stockx))

            self.con.commit()
        except Exception as e:
            print(size, urlkey)
            print(e)

    ########################################################################################################################################################################
    ##### 기능 4 관련 함수 #####
    def _query_select_distinct_urlkey(self, table):
        query = "SELECT DISTINCT urlkey FROM %s"%(table)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data
    def _query_select_id_stockx_in_urlkey(self, urlkey):
        query = "SELECT id_stockx FROM sneakers_price WHERE urlkey=%s"
        self.cursor.execute(query, (urlkey))

        data = self.cursor.fetchall()
            
        return data


    # size랑 price 받아오는 리소스가 동일하다.
    def _request_post_price(self, urlkey):
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
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuc3RvY2t4LmNvbS8iLCJzdWIiOiJhdXRoMHw2M2QwN2Y1MTc4ZDEwYmU5ZGYzNTk4YWQiLCJhdWQiOiJnYXRld2F5LnN0b2NreC5jb20iLCJpYXQiOjE2NzU2Nzg0MDQsImV4cCI6MTY3NTcyMTYwNCwiYXpwIjoiT1Z4cnQ0VkpxVHg3TElVS2Q2NjFXMER1Vk1wY0ZCeUQiLCJzY29wZSI6Im9mZmxpbmVfYWNjZXNzIn0.j8l4GwvwMEm-hp5vPKexLQK7AFTlNSF3cIwfSUedK1B6jKJ0AqKSgM1XxQp9RoD6lwyy4iMAwlrEC2GA4FUTx7ROSEn45IgWSUq2fTaT4pR7xO5GfmOqgdMZpW346bnBvDANloHSE3NlUy5C7UWPD2993erkc1j1kqbOV8JyCPk06aWZAxes1n-JeptnBWVuZRcXfVZiVqsHVkaOekLtq4ybo_RbcT2_Hst3qmdpewuf2RdvHzXHAAWyoVdiG-SXJ3xuCo3BEpBXfiLITxozLbihJO5EeIOkAsQHXrIXeKSJkn0HwDPF72-j_r0TraOJy2wvStthdftsyAjuQ_WCiw',
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
    def _request_get_price_recent(self, urlkey, id_stockx):
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
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuc3RvY2t4LmNvbS8iLCJzdWIiOiJhdXRoMHw2M2QwN2Y1MTc4ZDEwYmU5ZGYzNTk4YWQiLCJhdWQiOiJnYXRld2F5LnN0b2NreC5jb20iLCJpYXQiOjE2NzU2Nzg0MDQsImV4cCI6MTY3NTcyMTYwNCwiYXpwIjoiT1Z4cnQ0VkpxVHg3TElVS2Q2NjFXMER1Vk1wY0ZCeUQiLCJzY29wZSI6Im9mZmxpbmVfYWNjZXNzIn0.j8l4GwvwMEm-hp5vPKexLQK7AFTlNSF3cIwfSUedK1B6jKJ0AqKSgM1XxQp9RoD6lwyy4iMAwlrEC2GA4FUTx7ROSEn45IgWSUq2fTaT4pR7xO5GfmOqgdMZpW346bnBvDANloHSE3NlUy5C7UWPD2993erkc1j1kqbOV8JyCPk06aWZAxes1n-JeptnBWVuZRcXfVZiVqsHVkaOekLtq4ybo_RbcT2_Hst3qmdpewuf2RdvHzXHAAWyoVdiG-SXJ3xuCo3BEpBXfiLITxozLbihJO5EeIOkAsQHXrIXeKSJkn0HwDPF72-j_r0TraOJy2wvStthdftsyAjuQ_WCiw',
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
    
    def _update_price(self, urlkey):
        try:
            response = self._request_post_price(urlkey=urlkey)
        except Exception as e:
            print("[StockXManager] : Error(%s) at (urlkey:%s)"%(e, urlkey))
        if(response.status_code == 403):
            print("status_code: %d request_post_price(url_key:%s)"%(response.status_code, urlkey))
            ### db 쌓자!
            return False
        elif(response.status_code != 200):
            print("status_code: %d request_post_price(url_key:%s)"%(response.status_code, urlkey))
            return False
        else:
            try:
                data = response.json()
                # data = brotli.decompress(response.content).json()

                if(data['data']['product'] == None):
                    print("Prodcut doesn't exist. (urlkey: %s)"%(urlkey))
                    return False

                for item in data['data']['product']['variants']:
                    # id_stockx = item['id']
                    size = item['market']['bidAskData']['highestBidSize']
                    price_buy = item['market']['bidAskData']['lowestAsk']
                    price_sell = item['market']['bidAskData']['highestBid']

                    self._query_update_price(size=size, price_buy=price_buy, price_sell=price_sell, urlkey=urlkey)
            except Exception as e:
                print("[StockX_Manager] : Error(price Parsing 과정) at (urlkey: %s)"%(urlkey))

            return True
    def _update_price_recent(self, urlkey, id_stockx):
        try:
            response = self._request_get_price_recent(urlkey=urlkey, id_stockx=id_stockx)
        except Exception as e:
            print("[StockXManager] : _request_get_price_recent Error(%s) at (urlkey:%s)"%(e, urlkey))
        if(response.status_code == 403):
            ###### DB 쌓자 ######
            print("status_code: %d _update_price_recent(url_key:%s / id_stockx:%s)"%(response.status_code, urlkey, id_stockx))
            return False
        elif(response.status_code != 200):
            print("status_code: %d _update_price_recent(url_key:%s / id_stockx:%s)"%(response.status_code, urlkey, id_stockx))
            return False
        else:
            try:
                data = response.json()
                if(len(data['data']['variant']['market']['sales']['edges']) != 0):
                    price_recent = data['data']['variant']['market']['sales']['edges'][0]['node']['amount']
                    self._query_update_price_recent(id_stockx=id_stockx, price_recent=price_recent)
            except Exception as e:
                print("[StockX_Manager] : Error(price_recent Parsing 과정) at (urlkey: %s / id_stockx:%s)"%(urlkey, id_stockx))

            return True


    def _query_update_price(self, size, price_buy, price_sell, urlkey):
        try:
            # query = "INSERT INTO sneakers_price (size_stockx, price_buy_stockx, price_sell_stockx, urlkey) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE price_buy_stockx=%s, price_sell_stockx=%s"
            query = "UPDATE sneakers_price SET price_buy_stockx=NULLIF(%s, ''), price_sell_stockx=NULLIF(%s, '') WHERE urlkey=%s AND size_stockx=%s"
            self.cursor.execute(query, (price_buy, price_sell, urlkey, size))

            self.con.commit()
        except Exception as e:
            print(size, price_buy, price_sell, urlkey, price_buy, price_sell)
            print(e)
    def _query_update_price_recent(self, id_stockx, price_recent):
        try:
            query = "UPDATE sneakers_price SET price_recent_stockx=NULLIF(%s, '') WHERE id_stockx=%s"
            self.cursor.execute(query, (price_recent, id_stockx))

            self.con.commit()
        except Exception as e:
            print("_query_update_price_recent error(%s) at id_stockx : %s"%(e, id_stockx))
            



    

    ########################################################################################################################################################################
    def connect_db(self):
        con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8')

        return con




if __name__ == '__main__':
    StockXManager = StockXManager()
    # StockXManager.scrap_product()
    # StockXManager.scrap_model_no(batch=50, delay_min=1, delay_max=1, id_start=423)
    # StockXManager.scrap_size(batch=50, delay_min=1, delay_max=1, id_start=1)
    StockXManager.scrap_price(batch=20, delay_min=0.5, delay_max=0.8, id_start=162)