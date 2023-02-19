import requests
import pymysql
import json
from Lib_else import sleep_random, get_user_agent, set_proxies
import time
import brotli

class StockXManager:
    def __init__(self):
        self.auth_token = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImh0dHBzOi8vc3RvY2t4LmNvbS9lbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5zdG9ja3guY29tLyIsInN1YiI6ImF1dGgwfDYzZDA3ZjUxNzhkMTBiZTlkZjM1OThhZCIsImF1ZCI6ImdhdGV3YXkuc3RvY2t4LmNvbSIsImlhdCI6MTY3NjY4OTkwOCwiZXhwIjoxNjc2NzMzMTA4LCJhenAiOiJPVnhydDRWSnFUeDdMSVVLZDY2MVcwRHVWTXBjRkJ5RCIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3MifQ.rKle6VN5gH9y4kHnpINrTqzECyNhYbaWdVqhgec_tYwrKfZLu40YxAqdsMtcpMnDKpQvwP9xMbjAAzszCTwiyPY9PuEvKjWI5IwwIiSB2NWTuQgPR0ursBfNfmjN_w7EZ6b8dxrrj8la7AcPw1LpIiZSZRdXzzmXuZEFTYk-S-qt8kSE3K5Iw8imT27v152-DC8V-YAyCUwZSlq2wJrCOGi9DubWuQGgOTMAZ0civRBpqlS3ECi-VSn7Ak0HmnPGxGNe61XJxA3qVVGgnrCPD8waA0BeMstTrpeq1BvIxFVaYlJGtYWnGdMYD0p06WxLjQX6uVzXDhzMlzAAF1vXUA'
        pass


    ### 1. 페이지 돌며 전체 상품 긁기 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_productlist_page(self, page, brand_list=['Nike', 'Jordan', 'Adidas', 'New Balance']):
        data = []
        response = self._post_productlist_page(page=page)
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
    
    ### 1. 반스 페이지 상품 긁기 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_productlist_page_brand(self, brand, page):
        data = []
        response = self._post_productlist_page_brand(brand=brand, page=page)
        if(response.status_code == 200):
            state, data = self._parse_productinfo(response=response, brand_list=brand)
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
        # response = self._get_model_no(urlkey)
        response = self._get_model_no_option(urlkey, browser='whale', language=0)    ## language 1: Korean / 2: French   ## browser
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
    
    def _post_productlist_page_brand(self, brand, page):
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
                "category":"sneakers",
                "filters":[{"id":"_tags","selectedValues":["{}".format(brand)]},{"id":"browseVerticals","selectedValues":["sneakers"]}],
                "filtersVersion":4,
                "sort":{"id":"featured_loc","order":"DESC"},
                "page":{"index":page,"limit":40},
                "currency":"USD",
                "country":"KR",
                "marketName":None,
                "staticRanking":{"enabled":False},"skipFollowed":True},
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
                    product['brand'] = item['node']['brand'].lower()
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
                if(item['node']['brand'].lower() == item_filter.lower()):
                    return True

        elif(type(filter) == str):
            if(item['node']['brand'].lower() == filter.lower()):
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
    def _get_model_no_option(self, urlkey, browser, language=0):
        if(language==1 or language=='Korean'):
            url = "https://stockx.com/ko-kr/"+urlkey
            referer = "https://stockx.com/ko-kr/sneakers"
        elif(language==2 or language=='French'):
            url = "https://stockx.com/fr-fr/"+urlkey
            referer = "https://stockx.com/fr-fr/sneakers"
        else:
            url = "https://stockx.com/"+urlkey
            referer = "https://stockx.com/sneakers"
        
        ### Chrome ###
        if (browser=='chrome'):
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                # 'Host' : 'https://stockx.com/',
                # 'Referer': referer,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
                # 'User-Agent' : get_user_agent(),
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                # 'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
            }
        elif(browser=='edge'):
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                # 'Host' : 'https://stockx.com/',
                'Referer': referer,
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41',    ## 이거 안넣으면 403 뜸
                #  'User-Agent': 'PostmanRuntime/7.30.1',
                # 'User-Agent' : get_user_agent(),
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                # 'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
            }
        elif(browser=='whale'):
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                # 'Host' : 'https://stockx.com/',
                'Referer': referer,
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Whale/3.19.166.16 Safari/537.36',
                #  'User-Agent':get_user_agent(),
                'sec-ch-ua': '"Whale";v="3", "Not-A.Brand";v="8", "Chromium";v="110"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                # 'Cookie': '_pxvid=9271baee-ac77-11ed-928a-737365484843; __pxvid=9297c1db-ac77-11ed-8141-0242ac120002; stockx_device_id=a39fc46c-a558-4975-bfa4-19c72ed6642c; language_code=ko; _ga=GA1.2.987222420.1676386634; _gid=GA1.2.1555855740.1676386634; ajs_anonymous_id=8043c869-cc48-412a-91a2-32e2429ecc4e; _ga=GA1.2.987222420.1676386634; _gcl_au=1.1.2146146535.1676386635; rbuid=rbos-f3830f87-314e-4daf-b251-c5fc26007c6f; _pin_unauth=dWlkPVpEbGlOamd3TnpndFpHUm1PUzAwWldRMUxXSTJaVFl0T0RKa01qWTRPREprWkdaaQ; _rdt_uuid=1676386638500.92a659e8-56e9-461f-b46a-441fb9a6881f; __pdst=80da1543827a4c36b2cde24bb1846bae; __ssid=2766985977c05a40673fc1f50c051f5; rskxRunCookie=0; rCookie=is37jx4vs24mdw57yhqifle4dc4bl; stockx_homepage=sneakers; QuantumMetricUserID=2bd3cc24cef169eb343ed7d1f080a117; OptanonAlertBoxClosed=2023-02-14T14:57:59.270Z; lastRskxRun=1676619768006; stockx_session=3de65993-7d61-418e-96e1-a3a47b4d8919; stockx_selected_region=KR; __cf_bm=9XROC5yvqBmzSlu3CX9bbRN2_7j.l0RZaKOQyBnLjMQ-1676700855-0-ARrPP+ye+IwnNDd1nCwLJsoW7ao3VnkknA7/5HeSaib9BVZOBqPXL01dFO0m1cP3HhmnyFz6q3P5nQ7Ew5gMhNE=; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; pxcts=786c7f01-af53-11ed-95dd-73755056584b; _pxff_idp_c=1,s; _pxff_fed=5000; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Feb+18+2023+15%3A14%3A15+GMT%2B0900+(%ED%95%9C%EA%B5%AD+%ED%91%9C%EC%A4%80%EC%8B%9C)&version=202211.2.0&isIABGlobal=false&hosts=&consentId=1528961d-8c0a-4238-a7b0-bc5d7dc91f87&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1&geolocation=KR%3B11&AwaitingReconsent=false; _gat=1; ftr_blst_1h=1676700856355; _px3=c831f7f650a2b9562a5c03c1ee9466d267c738df5e5d7fb3f285201e746c664b:oyzWqjNATwMlzOzJyqwQ4JdbfOXMUuP2mA8bearA+TOdaxpeozkCfI3fLRPuDEhuFzX3w7S/ACJxvAYm0YbBNw==:1000:Dhb4jR3hnzgmUrfPLnGR4kS83ta/a6xh8F6yNSUZG17cIPQAZurTlyREo9jzu/s5X3UoTk4uMEJaxGl9AGdO2l4Ro6NxLgkEmKjf30OJfkP4kZdxySDnYrF8VoUW7sAdazrHjn8d/L/7nQcmroZwZvlJmrPo4vy8TteVxQDO3Lqa0t19hNKKP9WCPRLXENfG20vfGiQJiEujbghp2xh3rw==; IR_gbd=stockx.com; stockx_preferred_market_activity=sales; IR_9060=1676700860726%7C0%7C1676700860726%7C%7C; IR_PI=c8c767f3-ae0e-11ed-b1d2-0fb0e47f7daa%7C1676787260726; _pxde=9ecc4f9f302d634f791f5ccd3e2752d697001641d4eb1cc81627b63405f5e40a:eyJ0aW1lc3RhbXAiOjE2NzY3MDA4NjA5MjYsImZfa2IiOjB9; stockx_product_visits=1; _uetsid=de23c290ac7711ed87d52d07f9048c28; _uetvid=de23ed70ac7711ed9c13510cbe7ba93d; forterToken=ed90dabe99ff4e3da3b073ba0d1522ff_1676700855808__UDF43-m4_13ck; _dd_s=rum=0&expire=1676701760525'
            }

        elif(browser=='postman'):
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                # 'Host' : 'https://stockx.com/',
                # 'Referer': referer,
                 'User-Agent': 'PostmanRuntime/7.30.1',
                # 'User-Agent' : get_user_agent(),
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                # 'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
            }
        else:
            headers = {}

        
        # headers = {
        #     'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
        # }
        # payload = {}
        # response = requests.get(url, headers=headers)
        # response = requests.request("GET", url)
        # response = requests.request("GET", url, headers=headers, data=payload)

        # proxies = set_proxies()
        # response = requests.request("GET", url, headers=headers, proxies=proxies)

        response = requests.request("GET", url, headers=headers)

        return response
    
    def _get_model_no(self, urlkey):
        url = "https://stockx.com/ko-kr/"+urlkey
        
        ### Chrome ###
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            # 'Host' : 'https://stockx.com/',
            # 'Referer': 'https://stockx.com/ko-kr/sneakers',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
            #  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Whale/3.19.166.16 Safari/537.36',
            #  'User-Agent': 'Chrome/110.0.0.0',
            #  'User-Agent': 'Whale/3.19.166.16',
            #  'User-Agent': 'PostmanRuntime/7.30.1',
            #  'User-Agent': 'Edg/110.0.1587.41',
            # 'User-Agent' : get_user_agent(),
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            # 'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
        }

        ### Whale ###
        # headers = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        #     'Cache-Control': 'max-age=0',
        #     # 'Host' : 'https://stockx.com/',
        #     'Referer': 'https://stockx.com/ko-kr/sneakers',
        #     #  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
        #      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Whale/3.19.166.16 Safari/537.36',
        #     #  'User-Agent': 'Chrome/110.0.0.0',
        #     #  'User-Agent': 'Whale/3.19.166.16',
        #     #  'User-Agent': 'PostmanRuntime/7.30.1',
        #     #  'User-Agent': 'Edg/110.0.1587.41',
        #     # 'User-Agent' : get_user_agent(),
        #     'sec-ch-ua': '"Whale";v="3", "Not-A.Brand";v="8", "Chromium";v="110"',
        #     'sec-ch-ua-mobile': '?0',
        #     'sec-ch-ua-platform': '"Windows"',
        #     'sec-fetch-dest': 'document',
        #     'sec-fetch-mode': 'navigate',
        #     'sec-fetch-site': 'same-origin',
        #     'sec-fetch-user': '?1',
        #     'upgrade-insecure-requests': '1',
        #     # 'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
        # }

        ### Edge ###
        # headers = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        #     'Cache-Control': 'max-age=0',
        #     # 'Host' : 'https://stockx.com/',
        #     # 'Referer': 'https://stockx.com/ko-kr/sneakers',
        #      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41',    ## 이거 안넣으면 403 뜸
        #     #  'User-Agent': 'PostmanRuntime/7.30.1',
        #     # 'User-Agent' : get_user_agent(),
        #     'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        #     'sec-ch-ua-mobile': '?0',
        #     'sec-ch-ua-platform': '"Windows"',
        #     'sec-fetch-dest': 'document',
        #     'sec-fetch-mode': 'navigate',
        #     'sec-fetch-site': 'same-origin',
        #     'sec-fetch-user': '?1',
        #     'upgrade-insecure-requests': '1',
        #     # 'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
        # }

        ### Postman ###
        # headers = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        #     'Cache-Control': 'max-age=0',
        #     # 'Host' : 'https://stockx.com/',
        #     # 'Referer': 'https://stockx.com/ko-kr/sneakers',
        #     #  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41',    ## 이거 안넣으면 403 뜸
        #      'User-Agent': 'PostmanRuntime/7.30.1',
        #     # 'User-Agent' : get_user_agent(),
        #     # 'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        #     'sec-ch-ua-mobile': '?0',
        #     'sec-ch-ua-platform': '"Windows"',
        #     'sec-fetch-dest': 'document',
        #     'sec-fetch-mode': 'navigate',
        #     'sec-fetch-site': 'same-origin',
        #     'sec-fetch-user': '?1',
        #     'upgrade-insecure-requests': '1',
        #     # 'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
        # }


        
        # headers = {
        #     'Cookie': '__cf_bm=l53SqH28OmKuqJID416v7yJELRnale0hKrqxJOKHWJw-1676295258-0-AdYc6fA8mU8njgz2dyii6tBoH5xiCbyMmp1pp8szts5PIQQ14sH2dJ/9VUD7+DLrP3rUGgc5TACtoVOyKV70E7g=; language_code=en; stockx_device_id=b5bf17d1-f317-40ac-abf3-172da3629943; stockx_selected_region=KR; stockx_session=2079917c-0b4b-475a-b3a1-d1f01fe36d3d'
        # }
        # payload = {}
        # response = requests.get(url, headers=headers)
        # response = requests.request("GET", url)
        # response = requests.request("GET", url, headers=headers, data=payload)

        # proxies = set_proxies()
        # response = requests.request("GET", url, headers=headers, proxies=proxies)

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
            product['price_buy'] = item['market']['bidAskData']['lowestAsk']
            product['price_sell'] = item['market']['bidAskData']['highestBid']

            if(item['market']['bidAskData']['highestBidSize'] == None):
                product['size'] = item['market']['bidAskData']['lowestAskSize']
            else:
                product['size'] = item['market']['bidAskData']['highestBidSize']
            
            if(product['price_buy'] == None):
                product['price_buy'] = 0
            if(product['price_sell'] == None):
                product['price_sell'] = 0

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
