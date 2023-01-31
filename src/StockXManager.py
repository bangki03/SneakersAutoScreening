import requests
import pymysql
import json
from Lib_else import sleep_random

class StockXManager:
    def __init__(self):
        self.con = self.connect_db()
        self.cursor = self.con.cursor()

    def insert_product(self):
        print("전체 상품 Srap 시작합니다.")
        page = 1
        while(1) :
            print("%d page" %(page))

            sleep_random(0.3, 0.5)
            response = self._request_post_productlist_page_N(page)
            if(response.status_code != 200):
                print(response.status_code)
                continue

            state = self._parse_productinfo(response)
            if(state):
                page = page + 1
            else:
                break

    def update_price(self, batch=50, delay_min=0.2, delay_max=0.5, id_start=1):
        print("모델 넘버들을 가져옵니다.")
        cnt_total = self._query_count_total()

        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self._query_fetch_data(id_start=id_start, id_end=id_end)

            ## 처리
            for (id, urlkey) in data:
                # Model No.
                sleep_random(delay_min, delay_max)
                response = self._request_get_model_no(urlkey=urlkey)
                if(response.status_code != 200):
                    print(response.status_code)
                    continue

                model_no = self._parse_model_no(response)
                self._query_update_model_no(model_no=model_no, urlkey=urlkey)
                
                # Size별 가격
                state = self._update_post_size_price(urlkey=urlkey, model_no=model_no)

                if(~state):
                    continue
                
            print("처리중(%7d/%7d)"%(id_end, cnt_total))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

    ########################################################################################################################################################################
    ########################################################################################################################################################################
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
            query = "INSERT INTO stockx_model (id_stockx, brand, product_name, urlkey) VALUES (%s, %s, %s, %s)" 
            self.cursor.execute(query, (product['id_stockx'], product['brand'], product['product_name'], product['urlkey']))

            self.con.commit()
        except Exception as e:
            print(product)
            print(e)
        try:
            query = "UPDATE stockx_model (id_stockx, brand, product_name, urlkey) VALUES (%s, %s, %s, %s)" 
            self.cursor.execute(query, (product['id_stockx'], product['brand'], product['product_name'], product['urlkey']))

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
        product['size_mm'] = []
        product['size_us'] = []

        return product
    ########################################################################################################################################################################
    ########################################################################################################################################################################
    def _query_count_total(self):
        query = "SELECT COUNT(*) FROM stockx_model"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        return result[0]
    def _query_fetch_data(self, id_start, id_end):
        query = "SELECT id, urlkey FROM stockx_model WHERE id>%d AND id <%d"%(id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data
    
    ########################################################################################################################################################################
    ########################################################################################################################################################################
    def _request_get_model_no(self, urlkey):
        url = "https://stockx.com/"+urlkey
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://stockx.com/ko-kr/sneakers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
            # 'User-Agent' : 'PostmanRuntime/7.30.0'
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
            query = "UPDATE stockx_model SET model_no=%s WHERE urlkey=%s"
            self.cursor.execute(query, (model_no, urlkey))

            self.con.commit()
        except Exception as e:
            print(model_no, urlkey)
            print(e)

    def _update_post_size_price(self, urlkey, model_no):
        response = self._request_post_size_price(urlkey=urlkey)
        if(response.status_code != 200):
            print("status_code: %d request_post_size_price(url_key:%s)"%(response.status_code, urlkey))
            return False
        else:
            data = response.json()
            for item in data['data']['product']['variants']:
                id_stockx = item['id']
                size = item['market']['bidAskData']['highestBidSize']
                price_buy = item['market']['bidAskData']['lowestAsk']
                price_sell = item['market']['bidAskData']['highestBid']

                self._query_update_priceinfo(id_stockx=id_stockx, model_no=model_no, size=size, price_buy=price_buy, price_sell=price_sell, urlkey=urlkey)

            return True

    def _query_update_priceinfo(self, id_stockx, model_no, size, price_buy, price_sell, urlkey):
        try:
            query = "INSERT INTO stockx_price (id_stockx, model_no, size, price_buy, price_sell, urlkey) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE price_buy=%s, price_sell=%s"
            # query = "UPDATE stockx_price SET price_buy='%s', price_sell='%s' WHERE id=%s"
            self.cursor.execute(query, (id_stockx, model_no, size, price_buy, price_sell, urlkey, price_buy, price_sell))

            self.con.commit()
        except Exception as e:
            print(id_stockx, model_no, size, price_buy, price_sell, urlkey, price_buy, price_sell)
            print(e)



    def _request_post_size_price(self, urlkey):
        url = "https://stockx.com/api/p/e"
        headers = {
            'accept-language': 'ko-KR',   ## 이거 안넣으면 404
            'apollographql-client-name': 'Iron',    ## 필수
            'Content-Type': 'application/json',
            'origin': 'https://stockx.com',
            'Referer': 'https://stockx.com/ko-kr/'+urlkey,
            # 'selected-country': 'KR',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## 이거 안넣으면 403 뜸
            'x-operation-name': 'GetMarketData', ##  
            'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a', ## 
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
        return response

                

    ########################################################################################################################################################################
    def connect_db(self):
        con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8')

        return con




if __name__ == '__main__':
    StockXManager = StockXManager()
    StockXManager.update_price()