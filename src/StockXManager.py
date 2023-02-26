import requests
import json
from Lib_else import sleep_random, get_user_agent, set_proxies
import time
import brotli

class StockXManager:
    def __init__(self, delay_min=0.1, delay_max=0.2):
        self.brand_list = ['Nike', 'Jordan', 'Adidas', 'New Balance', 'Vans', 'Converse',]
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.last_page = 25
        self.auth_token = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImh0dHBzOi8vc3RvY2t4LmNvbS9lbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5zdG9ja3guY29tLyIsInN1YiI6ImF1dGgwfDYzZDA3ZjUxNzhkMTBiZTlkZjM1OThhZCIsImF1ZCI6ImdhdGV3YXkuc3RvY2t4LmNvbSIsImlhdCI6MTY3NzM3NTM2NywiZXhwIjoxNjc3NDE4NTY3LCJhenAiOiJPVnhydDRWSnFUeDdMSVVLZDY2MVcwRHVWTXBjRkJ5RCIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3MifQ.Wc-ULfqxC7TsxFYdfaUYbFUBhsjiUE8m-SXlEsEMaXCqly6n4j4RFMdY30pNc5-F8gAD2Zlh629tbbtgWuXANJhyy5nrzQyZnRWcB2edMDNwfw5vQvXTJsqIe5V3r2bYztyrpEjLz9AsKr2jIWTdok0d9psmZ6YU-Nco7Z2M8YQE7PI5zWySHR2Mb7eQlxovF9D0nnxqLXy5RhQFyK1YtWS2G3uIcErXgB5BeO4sRoHKSY4NrjA8bnaVKRe9IfKtB0oiWfiT-j9o1EgtQSAUAkLDjQKygIzg29zknJzoIgcLAQHom4tgfgypFNGXtdnEca8QCBVarsVpsj2UHunKEg'
        pass

    def __setManagers__(self, SneakersManager, KreamManager, MusinsaManager, DBManager, ReportManager):
        self.SneakersManager = SneakersManager
        self.KreamManager = KreamManager
        self.MusinsaManager = MusinsaManager
        self.DBManager = DBManager
        self.ReportManager = ReportManager

    ### 동작 1. 상품 업데이트
    def update_product(self, table):
        if(table == 'stockx'):
            print("[StockXManager] : 상품 스크랩 시작합니다.")
            data = self.scrap_product_list()

            data_filtered = [item for item in data if not self.DBManager.stockx_check_product_exist(item)]
            
            print("[StockXManager] : 신규 상품 %d개 등록합니다."%(len(data_filtered)))
            for item in data_filtered:
                self.DBManager.stockx_update_product(item)

            print("[StockXManager] : 상품 등록 완료하였습니다.")
        elif(table == 'sneakers_price'):
            data = self.DBManager.stockx_fetch_product()
            print("[StockXManager] : 상품 %d개 sneakers_price 등록 검토합니다."%(len(data)))

            tic = time.time()
            for index, item in enumerate(data):
                if(self.DBManager.sneakers_price_check_product_need_update(market='stockx', product=item) == 'INSERT'):
                    sleep_random(0.2, 0.5)
                    state, data_size = self.scrap_size(urlkey=item['urlkey'])

                    if(state):
                        for item_size in data_size:
                            item.update(item_size)
                            self.SneakersManager._convert_size_US2mm(item)
                            self.DBManager.sneakers_price_update_product(market='stockx', query_type='INSERT', product=item)
                            toc=time.time()
                        print("[SneakersManager] : 사이즈 스크랩 및 상품 등록 중 (%d/%d) [%.1fmin]" %(index+1, len(data), (toc-tic)/60))  

                elif(self.DBManager.sneakers_price_check_product_need_update(market='stockx', product=item) == 'UPDATE'):
                    sleep_random(0.2, 0.5)
                    state, data_size = self.scrap_size(urlkey=item['urlkey'])

                    if(state):
                        for item_size in data_size:
                            ## 여기서 사이즈 매칭시키자.
                            self.SneakersManager._convert_size_US2mm(item_size)
                            item_size.update(item)
                            self.DBManager.sneakers_price_update_product(market='stockx', query_type='UPDATE', product=item_size)
                            toc=time.time()
                        print("[SneakersManager] : 사이즈 스크랩 및 상품 등록 중 (%d/%d) [%.1fmin]" %(index+1, len(data), (toc-tic)/60))  

            pass

    
    ### 동작 2. 가격 업데이트
    def update_price(self, id_start=1):
        print("[StockXManager] : 가격 스크랩 시작합니다.")

        data = self.DBManager.sneakers_price_fetch_urlkey()
        cnt_total = len(data)

        tic=time.time()
        for index, item in enumerate(data):
            if(index<id_start-1):
                continue

            state, data_price_list = self.scrap_price(urlkey=item['urlkey'])
            if(state):
                for data_price in data_price_list:
                    data_price.update(item)
                    self.DBManager.sneakers_price_update_price(market='stockx', product=data_price)
            
            toc=time.time()
            print("[StockXManager] : (%s)가격 스크랩 완료(%d/%d) [%.1fmin]"%(item['urlkey'], index+1, cnt_total, (toc-tic)/60))
        
        print("[StockXManager] : 가격 등록 완료하였습니다.")




    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 1. 상품 업데이트
    #######################################################################################################################################
    #######################################################################################################################################
    
    ### Lv1) 카테고리 별 상품 스크랩 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_product_list(self):
        data_output = []

        tic = time.time()
        for page in range(1, self.last_page + 1):
            sleep_random(self.delay_min, self.delay_max)
            state, data_page = self.scrap_productlist_page_sneakers(page=page)
            if(state):
                data_output.extend(data_page)
            toc = time.time()
            print("[StockXManager] : 상품 스크랩 중 (sneakers - %d page) [%.1fmin]" %(page, (toc-tic)/60))    

        for brand in self.brand_list:
            for page in range(1, self.last_page + 1):
                sleep_random(self.delay_min, self.delay_max)
                state, data_page = self.scrap_productlist_page_brand(brand=brand, page=page)
                if(state):
                    data_output.extend(data_page)
                toc = time.time()
                print("[StockXManager] : 상품 스크랩 중 (%s - %d page) [%.1fmin]" %(brand, page, (toc-tic)/60))

        return data_output

    ### Lv2-1) sneakers 카테고리 페이지 별 상품 스크랩 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_productlist_page_sneakers(self, page):
        data = []
        response = self._post_productlist_page(page=page)
        if(response.status_code == 200):
            state, data = self._parse_productinfo(response=response, brand_list=self.brand_list)
        elif(response.status_code != 401):
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page_sneakers' with [page=%s]) "%(response.status_code, page))
            state = False
        elif(response.status_code != 403):
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page_sneakers' with [page=%s]) "%(response.status_code, page))
            state = False
        else:
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page_sneakers' with [page=%s]) "%(response.status_code, page))
            state = False

        return state, data
    
    ### Lv2-2) 특정 브랜드 카테고리 페이지 별 상품 스크랩 ###
    # input : brand, page
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_productlist_page_brand(self, brand, page):
        data = []
        response = self._post_productlist_page_brand(brand=brand, page=page)
        if(response.status_code == 200):
            state, data = self._parse_productinfo(response=response, brand_list=brand)
        elif(response.status_code != 401):
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page_brand' with [page=%s]) "%(response.status_code, page))
            state = False
        elif(response.status_code != 403):
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page_brand' with [page=%s]) "%(response.status_code, page))
            state = False
        else:
            print("[StockXManager] : Error Code(%s) at 'scrap_productlist_page_brand' with [page=%s]) "%(response.status_code, page))
            state = False

        return state, data

    ### Lv3-1) sneakers 카테고리 페이지 별 상품 Request ###
    # input : page
    # output : response
    def _post_productlist_page(self, page):
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
    
    ### Lv3-2) sneakers 카테고리 페이지 별 상품 Request ###
    # input : brand, page
    # output : response
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
    
    ### Lv3) 상품 정보 Parsing ###
    # input : response, filter_brand_list
    # output : state, list[dict{'id_stockx','brand','product_name','urlkey'}]
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
    
    ### Lv4) sneakers 브랜드 Filtering ###
    # input : product, fiter_list
    # output : state
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
    
    ### Lv4) Product Template 생성 ###
    # input : 
    # output : dict{'id_stockx','brand','product_name','urlkey'}
    def new_product(self):
        product = {}
        product['id_stockx'] = ''
        product['brand'] = ''
        product['model_no'] = ''
        product['product_name'] = ''
        product['urlkey'] = ''

        return product




    #######################################################################################################################################
    #######################################################################################################################################
    ### 기타 1. SneakersManager 요청 사항 - 사이즈 정보 요청
    #######################################################################################################################################
    #######################################################################################################################################

    ### Lv1) Size 요청
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
    
    ### Lv2) 사이즈 Request ###
    # input : urlkey
    # output : response
    def _post_size(self, urlkey):
        url = "https://stockx.com/api/p/e"
        headers = {
            # 'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
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
    
    ### Lv2) 상품 정보 Parsing ###
    # input : response
    # output : state, list[dict{'id_stockx','size','price_buy','price_sell'}]
    def _parse_size(self, response):
        output_productlist = []

        data = response.json()
        # data = brotli.decompress(response.content).json() ## 데이터 깨져서, brotli encoding
        for item in data['data']['product']['variants']:
            product = {}
            product['id_stockx'] = item['id']
            product['price_buy_stockx'] = item['market']['bidAskData']['lowestAsk']
            product['price_sell_stockx'] = item['market']['bidAskData']['highestBid']

            if(item['market']['bidAskData']['highestBidSize'] == None):
                product['size_stockx'] = item['market']['bidAskData']['lowestAskSize']
            else:
                product['size_stockx'] = item['market']['bidAskData']['highestBidSize']
            
            if(product['price_buy_stockx'] == None):
                product['price_buy_stockx'] = 0
            if(product['price_sell_stockx'] == None):
                product['price_sell_stockx'] = 0

            output_productlist.append(product)
            del product

        return output_productlist



    
        





    #######################################################################################################################################
    #######################################################################################################################################
    ### 기타 2. SneakersManager 요청 사항 - 가격 정보 요청
    #######################################################################################################################################
    #######################################################################################################################################
    
    ### Lv1) 카테고리 별 상품 스크랩 ###
    # input : urlkey
    # output : state, list[dict{'size_stockx','price_buy_stockx','price_sell_stockx'}]
    def scrap_price(self, urlkey):
        data = []
        sleep_random(self.delay_min, self.delay_max)
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


    ### Lv2) 가격 Request ###
    # input : urlkey
    # output : response
    def _post_price(self, urlkey):
        url = "https://stockx.com/api/p/e"
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR',
            'apollographql-client-name': 'Iron',
            'apollographql-client-version': '2023.02.12.02',
            'app-platform': 'Iron',
            'app-version': '2023.02.12.02',
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
            # 'Cookie': 'stockx_device_id=052ebc20-b6ba-48e5-b3a9-d94b8a64df2a; _pxvid=c4e2bbe4-9976-11ed-aab3-575552764d57; _ga=GA1.2.569109511.1674297091; ajs_anonymous_id=6593169f-2cec-4748-8a84-ab935ea5f813; __pxvid=c514f26d-9976-11ed-b321-0242ac120002; _gcl_au=1.1.1570150577.1674297091; rbuid=rbos-dc1e4acd-a291-490d-8242-4de37a93dd1c; __ssid=ac2c621ce974a5208576220bbae4656; rskxRunCookie=0; rCookie=03bentcw3fenxkvyo8zwuwld5t9dhl; QuantumMetricUserID=1c8a556b683048d6ddc5c111fbd718ef; _rdt_uuid=1674297095164.6a485bc7-e5a6-4d1a-8558-b7530720ed13; __pdst=40f158377cfa4d989f101edd0779df41; _ga=GA1.2.569109511.1674297091; _pin_unauth=dWlkPVl6QTFaREptTkRVdE9EYzJOeTAwTkRjeExUaGpaVFF0TkRBeFpEWmxOVGhpTURCbA; stockx_dismiss_modal=true; stockx_dismiss_modal_set=2023-01-24T11%3A38%3A45.532Z; stockx_dismiss_modal_expiration=2024-01-24T11%3A38%3A45.531Z; OptanonAlertBoxClosed=2023-01-24T11:38:50.156Z; tracker_device=10696ba6-010f-4b51-ae75-4a2982e6baf8; stockx_seen_ask_new_info=true; ajs_user_id=bf8d3023-9c4b-11ed-9f0c-124738b50e12; mfaLogin=err; language_code=ko; ajs_user_id=bf8d3023-9c4b-11ed-9f0c-124738b50e12; ajs_anonymous_id=6593169f-2cec-4748-8a84-ab935ea5f813; stockx_homepage=sneakers; token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImh0dHBzOi8vc3RvY2t4LmNvbS9lbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5zdG9ja3guY29tLyIsInN1YiI6ImF1dGgwfDYzZDA3ZjUxNzhkMTBiZTlkZjM1OThhZCIsImF1ZCI6ImdhdGV3YXkuc3RvY2t4LmNvbSIsImlhdCI6MTY3NzI0ODQ5MywiZXhwIjoxNjc3MjkxNjkzLCJhenAiOiJPVnhydDRWSnFUeDdMSVVLZDY2MVcwRHVWTXBjRkJ5RCIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3MifQ.QRfvemvNitQh3bGdSpr7uXw_91uvXnjXxBrbl3p7GdyJnWaY4heyYU7C3MUmGZBMS5KJWO8lqUmS33waFsbCYAKc4k2nT17vaQa_MTIn_--V6WK4B57enOvDxJfeSy8TizfoPa4E4xQ5oIvW_BiTGE7jpIUnA07mp5BcCCItUapiRpJeR3mGytQUCOZDjbmRQMAmXf-__c19V_FSYbz_y_aX0_aMMAwFzyN-njYQfCHlJ_7bOucAVxy725jYK0dS_SPYwOT9cUT1H0pnOu5eatlzsSrlx9xjBnPdow-2OcSkcI22lA1p4L0Va2C3f_iaGxGJwf3-izaZ7EXI-EInXg; _gid=GA1.2.1218620974.1677248496; IR_PI=c7c35067-9976-11ed-b9f8-25af62750bf1%7C1677334902116; stockx_session=174d5550-0177-4286-bb83-d61a839e3467; __cf_bm=PxuwS3fXbM0oagMrDSPcvEaJbJvyvFVA5AwdmdA0.FQ-1677288797-0-AQ+WKZX4emFjSOtZ8LgRv/oyMhFkN7ZKx9hIZJyM6fR5d8wkVeZ7FVs9I6e272frNHthX9N1UGx0JpURwevhQwI=; stockx_selected_region=KR; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; pxcts=61e89360-b4ac-11ed-8d8b-5250544a696d; _pxff_idp_c=1,s; _pxff_fed=5000; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Feb+25+2023+10%3A33%3A19+GMT%2B0900+(%ED%95%9C%EA%B5%AD+%ED%91%9C%EC%A4%80%EC%8B%9C)&version=202211.2.0&geolocation=KR%3B11&isIABGlobal=false&hosts=&consentId=68357594-217d-4425-9343-9c5309623e84&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1&AwaitingReconsent=false; loggedIn=bf8d3023-9c4b-11ed-9f0c-124738b50e12; stockx_selected_currency=USD; _gat=1; _px3=5fce791844a99c39d44c87d854dea093d4029f514250a89e79397d2828559c52:sxZmMRnEOkjZtw3mK7N2AXVP2vCiZB0qRGmO7FkPQ3ar2OcZTYZ3AbQpYIqG7MwZALw9vtURc0B1vMl54PogmA==:1000:mSQcrIyJfPjCuo7y3JiB5U3xVsih7Q0ur0khKA0VLvgshjxCsLPdrsZw/tkXzjvnwli3mnUFVoXvNLrbAQ6kREu/vqjFjHZDhenWVOjUjohRe7CVWvo5YsU1DuvQvTuiNLyewuXITN1Rti9VYKm8/fGXEF9fpJEX1N6wRHbZFp6Y8xHzSs6495gWxzb2+R0tltISyzzEUtMrrlCP30RRWA==; forterToken=4880e3a1bc124c478eaa6ecf50b63162_1677288799808__UDF43_13ck; ftr_blst_1h=1677288800023; _pxde=a0ed2f3bc05c2cfcd4ad324895cba0dd8e633276036f2144c5f4165713ed8737:eyJ0aW1lc3RhbXAiOjE2NzcyODg4MDEzNjEsImZfa2IiOjB9; lastRskxRun=1677288803003; _uetsid=8bce61e0b44e11edb4b0cd03196d701d; _uetvid=b24a09e09c4d11edae7967fe428be46d; _dd_s=rum=0&expire=1677289703793',
            'Cookie' : 'stockx_device_id=052ebc20-b6ba-48e5-b3a9-d94b8a64df2a; _pxvid=c4e2bbe4-9976-11ed-aab3-575552764d57; _ga=GA1.2.569109511.1674297091; ajs_anonymous_id=6593169f-2cec-4748-8a84-ab935ea5f813; __pxvid=c514f26d-9976-11ed-b321-0242ac120002; _gcl_au=1.1.1570150577.1674297091; rbuid=rbos-dc1e4acd-a291-490d-8242-4de37a93dd1c; __ssid=ac2c621ce974a5208576220bbae4656; rskxRunCookie=0; rCookie=03bentcw3fenxkvyo8zwuwld5t9dhl; QuantumMetricUserID=1c8a556b683048d6ddc5c111fbd718ef; _rdt_uuid=1674297095164.6a485bc7-e5a6-4d1a-8558-b7530720ed13; __pdst=40f158377cfa4d989f101edd0779df41; _ga=GA1.2.569109511.1674297091; _pin_unauth=dWlkPVl6QTFaREptTkRVdE9EYzJOeTAwTkRjeExUaGpaVFF0TkRBeFpEWmxOVGhpTURCbA; stockx_dismiss_modal=true; stockx_dismiss_modal_set=2023-01-24T11%3A38%3A45.532Z; stockx_dismiss_modal_expiration=2024-01-24T11%3A38%3A45.531Z; OptanonAlertBoxClosed=2023-01-24T11:38:50.156Z; tracker_device=10696ba6-010f-4b51-ae75-4a2982e6baf8; stockx_seen_ask_new_info=true; ajs_user_id=bf8d3023-9c4b-11ed-9f0c-124738b50e12; mfaLogin=err; language_code=ko; ajs_user_id=bf8d3023-9c4b-11ed-9f0c-124738b50e12; ajs_anonymous_id=6593169f-2cec-4748-8a84-ab935ea5f813; stockx_homepage=sneakers; _gid=GA1.2.1218620974.1677248496; stockx_selected_region=KR; pxcts=61e89360-b4ac-11ed-8d8b-5250544a696d; loggedIn=bf8d3023-9c4b-11ed-9f0c-124738b50e12; stockx_selected_currency=USD; stockx_preferred_market_activity=sales; IR_gbd=stockx.com; token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImh0dHBzOi8vc3RvY2t4LmNvbS9lbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5zdG9ja3guY29tLyIsInN1YiI6ImF1dGgwfDYzZDA3ZjUxNzhkMTBiZTlkZjM1OThhZCIsImF1ZCI6ImdhdGV3YXkuc3RvY2t4LmNvbSIsImlhdCI6MTY3NzI5MjI2MiwiZXhwIjoxNjc3MzM1NDYyLCJhenAiOiJPVnhydDRWSnFUeDdMSVVLZDY2MVcwRHVWTXBjRkJ5RCIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3MifQ.WDP4J50jexco82770I6RFgEbGvxCiY2JJT1J8-LAJP7wmRf24KWUg7lARVUgE07RR_S-ZQ_xJXSNQkpLynFb8FjV4oNVRw-cQmuqN95ypOfPk8WPzByTNPlKJQLxBcVuRyyZik5dHcKInKVtTmTnnlZW7I_bwuvlwOdR9MdfbYYfxVOYZpSJiHUHG--laFZXYhgnJOmovfvKTX1VkIpUEslr9AZj1-kdhlkRnfHkI0R-gVRCqTcB4nsnhyPrYTdPS5DnWCBymqFXe41Q3nXlkTTKc8Di_zeKssQLgVJ5V6zi1vyO-Hg7WgKo-NkyATxOVSL5fqKpyVzVYDrCcX5y5w; QuantumMetricSessionID=57ea395e37230ebe5ae9933ad6ea6da1; stockx_session=809869ff-e581-44b2-9fcc-9ea7e74be788; ftr_blst_1h=1677298911823; lastRskxRun=1677299027425; IR_9060=1677299029362%7C0%7C1677299029362%7C%7C; IR_PI=c7c35067-9976-11ed-b9f8-25af62750bf1%7C1677385429362; forterToken=4880e3a1bc124c478eaa6ecf50b63162_1677299025566__UDF43-m4_13ck; _uetsid=8bce61e0b44e11edb4b0cd03196d701d; _uetvid=b24a09e09c4d11edae7967fe428be46d; __cf_bm=UFtvPVUGAxEeqVZavqvFu.M5vNEhGi_WAE5Dl8H.V2Q-1677299949-0-AawhYUKCcC2tC28et4ZOzMfL1UzJWBCYcQtGNtg9jjqKccoVZaKqrVDEWtXGY3hipn+3ylhMX79oN/g5tyimLlQ=; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; _pxff_idp_c=1,s; _pxff_rf=1; _pxff_fp=1; _pxff_fed=5000; _px3=98091d603942c2774ab9438daa3657ae6fc1c20cee26467578e0d3e0be1ced22:20m1ErfJK6uxonc5WaqJkDeAA7cWSrNfGOn456OtnS7Emqtv2k/HvFAJNXaANIdaGoy1t8tvWiZ0ZsJfsZoBCg==:1000:rp5RELUNTKP60nR1gzyE1DzsSol+4PO+6nIyRLihchusmFg/I01C0c/X3hf4/U2CN7bQF8qb1BCI7HzXKSi0FDFOMUOtwcF7/z/aj+bIszT/jOOCrOj9yO9i5GS2rPZP+kJhycx5WnLQpgqSMj1AAIBhjcgt83HWtns0KgOG1G8Ay8/phkmaMYzcRQdnhXhqRtcjVKb0dVDOJIc4NYokuQ==; _pxde=51d295e9b9769843110765967186e7642ff0698e526a0557411c93b5f8cf0d59:eyJ0aW1lc3RhbXAiOjE2NzcyOTk5NjE4ODYsImZfa2IiOjB9; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Feb+25+2023+13%3A39%3A22+GMT%2B0900+(%ED%95%9C%EA%B5%AD+%ED%91%9C%EC%A4%80%EC%8B%9C)&version=202211.2.0&geolocation=KR%3B11&isIABGlobal=false&hosts=&consentId=68357594-217d-4425-9343-9c5309623e84&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1&AwaitingReconsent=false; _dd_s=rum=0&expire=1677300862919; stockx_product_visits=7; _gat=1'
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

        # headers = {
        #     'Accept-Language': 'ko-KR',
        #     'apollographql-client-name': 'Iron',
        #     'apollographql-client-version': '2023.02.12.02',
        #     'app-platform': 'Iron',
        #     'app-version': '2023.02.12.02',
        #     'Origin': 'https://stockx.com',
        #     'Referer': 'https://stockx.com/ko-kr/adidas-gazelle-bold-pink-glow-w',
        #     'selected-country': 'KR',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        #     'x-operation-name': 'GetMarketData',
        #     'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a',
        #     'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        #     'sec-ch-ua-mobile': '?0',
        #     'sec-ch-ua-platform': '"Windows"',
        #     'sec-fetch-dest': 'empty',
        #     'sec-fetch-mode': 'cors',
        #     'sec-fetch-site': 'same-origin',
        #     'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImh0dHBzOi8vc3RvY2t4LmNvbS9lbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5zdG9ja3guY29tLyIsInN1YiI6ImF1dGgwfDYzZDA3ZjUxNzhkMTBiZTlkZjM1OThhZCIsImF1ZCI6ImdhdGV3YXkuc3RvY2t4LmNvbSIsImlhdCI6MTY3NzI0ODQ5MywiZXhwIjoxNjc3MjkxNjkzLCJhenAiOiJPVnhydDRWSnFUeDdMSVVLZDY2MVcwRHVWTXBjRkJ5RCIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3MifQ.QRfvemvNitQh3bGdSpr7uXw_91uvXnjXxBrbl3p7GdyJnWaY4heyYU7C3MUmGZBMS5KJWO8lqUmS33waFsbCYAKc4k2nT17vaQa_MTIn_--V6WK4B57enOvDxJfeSy8TizfoPa4E4xQ5oIvW_BiTGE7jpIUnA07mp5BcCCItUapiRpJeR3mGytQUCOZDjbmRQMAmXf-__c19V_FSYbz_y_aX0_aMMAwFzyN-njYQfCHlJ_7bOucAVxy725jYK0dS_SPYwOT9cUT1H0pnOu5eatlzsSrlx9xjBnPdow-2OcSkcI22lA1p4L0Va2C3f_iaGxGJwf3-izaZ7EXI-EInXg',
        #     'Content-Type': 'application/json',
        #     'Cookie': 'stockx_device_id=052ebc20-b6ba-48e5-b3a9-d94b8a64df2a; _pxvid=c4e2bbe4-9976-11ed-aab3-575552764d57; _ga=GA1.2.569109511.1674297091; ajs_anonymous_id=6593169f-2cec-4748-8a84-ab935ea5f813; __pxvid=c514f26d-9976-11ed-b321-0242ac120002; _gcl_au=1.1.1570150577.1674297091; rbuid=rbos-dc1e4acd-a291-490d-8242-4de37a93dd1c; __ssid=ac2c621ce974a5208576220bbae4656; rskxRunCookie=0; rCookie=03bentcw3fenxkvyo8zwuwld5t9dhl; QuantumMetricUserID=1c8a556b683048d6ddc5c111fbd718ef; _rdt_uuid=1674297095164.6a485bc7-e5a6-4d1a-8558-b7530720ed13; __pdst=40f158377cfa4d989f101edd0779df41; _ga=GA1.2.569109511.1674297091; _pin_unauth=dWlkPVl6QTFaREptTkRVdE9EYzJOeTAwTkRjeExUaGpaVFF0TkRBeFpEWmxOVGhpTURCbA; stockx_dismiss_modal=true; stockx_dismiss_modal_set=2023-01-24T11%3A38%3A45.532Z; stockx_dismiss_modal_expiration=2024-01-24T11%3A38%3A45.531Z; OptanonAlertBoxClosed=2023-01-24T11:38:50.156Z; tracker_device=10696ba6-010f-4b51-ae75-4a2982e6baf8; stockx_seen_ask_new_info=true; ajs_user_id=bf8d3023-9c4b-11ed-9f0c-124738b50e12; mfaLogin=err; language_code=ko; ajs_user_id=bf8d3023-9c4b-11ed-9f0c-124738b50e12; ajs_anonymous_id=6593169f-2cec-4748-8a84-ab935ea5f813; stockx_homepage=sneakers; token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImJmOGQzMDIzLTljNGItMTFlZC05ZjBjLTEyNDczOGI1MGUxMiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImh0dHBzOi8vc3RvY2t4LmNvbS9lbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5zdG9ja3guY29tLyIsInN1YiI6ImF1dGgwfDYzZDA3ZjUxNzhkMTBiZTlkZjM1OThhZCIsImF1ZCI6ImdhdGV3YXkuc3RvY2t4LmNvbSIsImlhdCI6MTY3NzI0ODQ5MywiZXhwIjoxNjc3MjkxNjkzLCJhenAiOiJPVnhydDRWSnFUeDdMSVVLZDY2MVcwRHVWTXBjRkJ5RCIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3MifQ.QRfvemvNitQh3bGdSpr7uXw_91uvXnjXxBrbl3p7GdyJnWaY4heyYU7C3MUmGZBMS5KJWO8lqUmS33waFsbCYAKc4k2nT17vaQa_MTIn_--V6WK4B57enOvDxJfeSy8TizfoPa4E4xQ5oIvW_BiTGE7jpIUnA07mp5BcCCItUapiRpJeR3mGytQUCOZDjbmRQMAmXf-__c19V_FSYbz_y_aX0_aMMAwFzyN-njYQfCHlJ_7bOucAVxy725jYK0dS_SPYwOT9cUT1H0pnOu5eatlzsSrlx9xjBnPdow-2OcSkcI22lA1p4L0Va2C3f_iaGxGJwf3-izaZ7EXI-EInXg; _gid=GA1.2.1218620974.1677248496; IR_PI=c7c35067-9976-11ed-b9f8-25af62750bf1%7C1677334902116; stockx_session=174d5550-0177-4286-bb83-d61a839e3467; __cf_bm=PxuwS3fXbM0oagMrDSPcvEaJbJvyvFVA5AwdmdA0.FQ-1677288797-0-AQ+WKZX4emFjSOtZ8LgRv/oyMhFkN7ZKx9hIZJyM6fR5d8wkVeZ7FVs9I6e272frNHthX9N1UGx0JpURwevhQwI=; stockx_selected_region=KR; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; pxcts=61e89360-b4ac-11ed-8d8b-5250544a696d; _pxff_idp_c=1,s; _pxff_fed=5000; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Feb+25+2023+10%3A33%3A19+GMT%2B0900+(%ED%95%9C%EA%B5%AD+%ED%91%9C%EC%A4%80%EC%8B%9C)&version=202211.2.0&geolocation=KR%3B11&isIABGlobal=false&hosts=&consentId=68357594-217d-4425-9343-9c5309623e84&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1&AwaitingReconsent=false; loggedIn=bf8d3023-9c4b-11ed-9f0c-124738b50e12; stockx_selected_currency=USD; _gat=1; _px3=5fce791844a99c39d44c87d854dea093d4029f514250a89e79397d2828559c52:sxZmMRnEOkjZtw3mK7N2AXVP2vCiZB0qRGmO7FkPQ3ar2OcZTYZ3AbQpYIqG7MwZALw9vtURc0B1vMl54PogmA==:1000:mSQcrIyJfPjCuo7y3JiB5U3xVsih7Q0ur0khKA0VLvgshjxCsLPdrsZw/tkXzjvnwli3mnUFVoXvNLrbAQ6kREu/vqjFjHZDhenWVOjUjohRe7CVWvo5YsU1DuvQvTuiNLyewuXITN1Rti9VYKm8/fGXEF9fpJEX1N6wRHbZFp6Y8xHzSs6495gWxzb2+R0tltISyzzEUtMrrlCP30RRWA==; forterToken=4880e3a1bc124c478eaa6ecf50b63162_1677288799808__UDF43_13ck; ftr_blst_1h=1677288800023; _pxde=a0ed2f3bc05c2cfcd4ad324895cba0dd8e633276036f2144c5f4165713ed8737:eyJ0aW1lc3RhbXAiOjE2NzcyODg4MDEzNjEsImZfa2IiOjB9; lastRskxRun=1677288803003; _uetsid=8bce61e0b44e11edb4b0cd03196d701d; _uetvid=b24a09e09c4d11edae7967fe428be46d; _dd_s=rum=0&expire=1677289703793'
        #     }
        # payload = json.dumps({
        #     "query": "query GetMarketData($id: String!, $currencyCode: CurrencyCode, $countryCode: String!, $marketName: String) {\n  product(id: $id) {\n    id\n    urlKey\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n    variants {\n      id\n      market(currencyCode: $currencyCode) {\n        bidAskData(country: $countryCode, market: $marketName) {\n          highestBid\n          highestBidSize\n          lowestAsk\n          lowestAskSize\n        }\n      }\n    }\n    ...BidButtonFragment\n    ...BidButtonContentFragment\n    ...BuySellFragment\n    ...BuySellContentFragment\n    ...XpressAskPDPFragment\n  }\n}\n\nfragment BidButtonFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BidButtonContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  minimumBid(currencyCode: $currencyCode)\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n      numberOfAsks\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n        numberOfAsks\n      }\n    }\n  }\n}\n\nfragment BuySellFragment on Product {\n  id\n  title\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  media {\n    imageUrl\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment BuySellContentFragment on Product {\n  id\n  urlKey\n  sizeDescriptor\n  productCategory\n  lockBuying\n  lockSelling\n  market(currencyCode: $currencyCode) {\n    bidAskData(country: $countryCode, market: $marketName) {\n      highestBid\n      highestBidSize\n      lowestAsk\n      lowestAskSize\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      bidAskData(country: $countryCode, market: $marketName) {\n        highestBid\n        highestBidSize\n        lowestAsk\n        lowestAskSize\n      }\n    }\n  }\n}\n\nfragment XpressAskPDPFragment on Product {\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode) {\n      numberOfCustodialAsks\n    }\n  }\n  variants {\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode) {\n        numberOfCustodialAsks\n      }\n    }\n  }\n}\n",
        #     "variables": {
        #         "id": "adidas-gazelle-bold-pink-glow-w",
        #         "currencyCode": "KRW",
        #         "countryCode": "KR",
        #         "marketName": None
        #     },
        #     "operationName": "GetMarketData"
        # })



        # response = requests.post(url, headers=headers, data=payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        # proxies = set_proxies()
        # response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=3)
        return response
    
    ### Lv2) 가격 Parsing ###
    # input : response
    # output : state, list[dict{'size_stockx','price_buy_stockx','price_sell_stockx'}]
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
            product['size_stockx'] = item['market']['bidAskData']['highestBidSize']
            product['price_buy_stockx'] = item['market']['bidAskData']['lowestAsk']
            product['price_sell_stockx'] = item['market']['bidAskData']['highestBid']

            output_productlist.append(product)

        return output_productlist


