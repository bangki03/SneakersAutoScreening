import requests
import pymysql
import json

class StockXManager:
    def __init__(self):
        self.con = self.connect_db()
        self.cursor = self.con.cursor()

    





    def _request_get_productlist_page_N(self, page):
        url = "https://stockx.com/api/p/e"
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            # 'accept-encoding': 'utf-8',
            # 'accept-language': 'ko-KR',   ## 이거넣으면 400 Bad Request 뜸
            'apollographql-client-name': 'Iron',
            'apollographql-client-version': '2023.01.15.05',
            'app-platform': 'Iron',
            'app-version':"2023.01.15.05",
            # 'content-length': '2813',
            'content-type': 'application/json',
            'origin': 'https://stockx.com',
            'Referer': 'https://stockx.com/ko-kr/sneakers?page=1',
            'sec-ch-ua':'"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile':"?0",
            'sec-ch-ua-platform':'"Windows"',
            'sec-fetch-dest':"empty",
            'sec-fetch-mode':"cors",
            'sec-fetch-site':"same-origin",
            'selected-country': 'KR',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## ****필수****
            'x-operation-name': 'Browse', ##  
            'x-stockx-device-id': '052ebc20-b6ba-48e5-b3a9-d94b8a64df2a', ## 
            # 'cookie': 'stockx_device_id=052ebc20-b6ba-48e5-b3a9-d94b8a64df2a; _pxvid=c4e2bbe4-9976-11ed-aab3-575552764d57; _ga=GA1.2.569109511.1674297091; ajs_anonymous_id=6593169f-2cec-4748-8a84-ab935ea5f813; __pxvid=c514f26d-9976-11ed-b321-0242ac120002; _gcl_au=1.1.1570150577.1674297091; rbuid=rbos-dc1e4acd-a291-490d-8242-4de37a93dd1c; __ssid=ac2c621ce974a5208576220bbae4656; rskxRunCookie=0; rCookie=03bentcw3fenxkvyo8zwuwld5t9dhl; QuantumMetricUserID=1c8a556b683048d6ddc5c111fbd718ef; _rdt_uuid=1674297095164.6a485bc7-e5a6-4d1a-8558-b7530720ed13; __pdst=40f158377cfa4d989f101edd0779df41; _ga=GA1.2.569109511.1674297091; _pin_unauth=dWlkPVl6QTFaREptTkRVdE9EYzJOeTAwTkRjeExUaGpaVFF0TkRBeFpEWmxOVGhpTURCbA; language_code=ko; stockx_dismiss_modal=true; stockx_dismiss_modal_set=2023-01-24T11%3A38%3A45.532Z; stockx_dismiss_modal_expiration=2024-01-24T11%3A38%3A45.531Z; OptanonAlertBoxClosed=2023-01-24T11:38:50.156Z; tracker_device=10696ba6-010f-4b51-ae75-4a2982e6baf8; stockx_seen_ask_new_info=true; stockx_homepage=sneakers; _gid=GA1.2.350429630.1674902266; stockx_session=c6171df7-4e41-4c5c-a286-70517155c4a4; __cf_bm=ru6HiwrXHBQqMf3PH8uOdnhcU5pYwraQSKnv7r9OrDE-1674955974-0-AeXq8CeuhpsB136LckEI/zf/ZPiKnbYAgMbHbsLW49a+EklRpYJmwFf8UZZYqZaRmuZ8QYgg8WaJjVwuNWSHrBo=; stockx_selected_region=KR; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Jan+29+2023+10%3A32%3A55+GMT%2B0900+(%ED%95%9C%EA%B5%AD+%ED%91%9C%EC%A4%80%EC%8B%9C)&version=202211.2.0&geolocation=KR%3B11&isIABGlobal=false&hosts=&consentId=68357594-217d-4425-9343-9c5309623e84&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1&AwaitingReconsent=false; pxcts=dad69b4f-9f74-11ed-8d52-694c7a506679; _px3=e3b371f571fbadb22e9240c28ca45547f59a1a8a0ec63c2e1f2081702bbad43e:W6v7MQ03QVaAN0MBl06RFM1hEPEqiUNmMidWsOTae3gNXUxP+kpwhSC66ll5c8jTh3H98BX7rsJ6DWHRBjDx9w==:1000:uNAZCwmGvKOXOFRvx1mikmrgVXvhG+0ViZLTZZ9NrgPLhcydc63Tm4x9QvbmukSuVy29eVwLLyr/cVYg+S7AOpbCyPII/C/K9Lsugo9VmXbtMhm/a5+OXatL7sL1r0wq998YzUDbBsp0HeemzJUWRJGEfp8BKXHBp2CebuAQ6dt1sKmu5g30cdb3sTo0QTwz6jGhHrKq7UQc4Nhp9sVaMA==; forterToken=4880e3a1bc124c478eaa6ecf50b63162_1674955976295__UDF43_13ck; lastRskxRun=1674955978494; QuantumMetricSessionID=034dded78bed68c6ce1adadb9f59e8ea; IR_gbd=stockx.com; IR_9060=1674955980333%7C0%7C1674955980333%7C%7C; IR_PI=c7c35067-9976-11ed-b9f8-25af62750bf1%7C1675042380333; _pxde=0ee46d27e656eb0c78a91d112f40da8c70602c9a0a52bc70fdcd264c4183de76:eyJ0aW1lc3RhbXAiOjE2NzQ5NTU5OTQ4NzQsImZfa2IiOjB9; _dd_s=rum=0&expire=1674956937898; _gat=1; _uetsid=cd93f4d09ef711edaffe2bb988e92881; _uetvid=b24a09e09c4d11edae7967fe428be46d'
        }
        cookies = {'stockx_device_id':'052ebc20-b6ba-48e5-b3a9-d94b8a64df2a',
            '_pxvid':'c4e2bbe4-9976-11ed-aab3-575552764d57',
            '_ga':'GA1.2.569109511.1674297091',
            'ajs_anonymous_id':'6593169f-2cec-4748-8a84-ab935ea5f813',
            '__pxvid':'c514f26d-9976-11ed-b321-0242ac120002',
            '_gcl_au':'1.1.1570150577.1674297091',
            'rbuid':'rbos-dc1e4acd-a291-490d-8242-4de37a93dd1c',
            '__ssid':'ac2c621ce974a5208576220bbae4656',
            'rskxRunCookie':'0',
            'rCookie':'03bentcw3fenxkvyo8zwuwld5t9dhl',
            'QuantumMetricUserID':'1c8a556b683048d6ddc5c111fbd718ef',
            '_rdt_uuid':'1674297095164.6a485bc7-e5a6-4d1a-8558-b7530720ed13',
            '__pdst':'40f158377cfa4d989f101edd0779df41',
            '_ga':'GA1.2.569109511.1674297091',
            '_pin_unauth':'dWlkPVl6QTFaREptTkRVdE9EYzJOeTAwTkRjeExUaGpaVFF0TkRBeFpEWmxOVGhpTURCbA',
            'language_code':'ko',
            'stockx_dismiss_modal':'true',
            'stockx_dismiss_modal_set': '2023-01-24T11%3A38%3A45.532Z',
            'stockx_dismiss_modal_expiration':'2024-01-24T11%3A38%3A45.531Z',
            'OptanonAlertBoxClosed':'2023-01-24T11:38:50.156Z',
            'tracker_device':'10696ba6-010f-4b51-ae75-4a2982e6baf8',
            'stockx_seen_ask_new_info':'true',
            'stockx_homepage':'sneakers',
            '_gid':'GA1.2.350429630.1674902266',
            'stockx_session':'c6171df7-4e41-4c5c-a286-70517155c4a4',
            '__cf_bm':'ru6HiwrXHBQqMf3PH8uOdnhcU5pYwraQSKnv7r9OrDE-1674955974-0-AeXq8CeuhpsB136LckEI/zf/ZPiKnbYAgMbHbsLW49a+EklRpYJmwFf8UZZYqZaRmuZ8QYgg8WaJjVwuNWSHrBo=',
            'stockx_selected_region':'KR',
            'OptanonConsent':'isGpcEnabled=0&datestamp=Sun+Jan+29+2023+10%3A32%3A55+GMT%2B0900+(%ED%95%9C%EA%B5%AD+%ED%91%9C%EC%A4%80%EC%8B%9C)&version=202211.2.0&geolocation=KR%3B11&isIABGlobal=false&hosts=&consentId=68357594-217d-4425-9343-9c5309623e84&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1&AwaitingReconsent=false',
            'pxcts':'dad69b4f-9f74-11ed-8d52-694c7a506679',
            '_px3':'e3b371f571fbadb22e9240c28ca45547f59a1a8a0ec63c2e1f2081702bbad43e:W6v7MQ03QVaAN0MBl06RFM1hEPEqiUNmMidWsOTae3gNXUxP+kpwhSC66ll5c8jTh3H98BX7rsJ6DWHRBjDx9w==:1000:uNAZCwmGvKOXOFRvx1mikmrgVXvhG+0ViZLTZZ9NrgPLhcydc63Tm4x9QvbmukSuVy29eVwLLyr/cVYg+S7AOpbCyPII/C/K9Lsugo9VmXbtMhm/a5+OXatL7sL1r0wq998YzUDbBsp0HeemzJUWRJGEfp8BKXHBp2CebuAQ6dt1sKmu5g30cdb3sTo0QTwz6jGhHrKq7UQc4Nhp9sVaMA==',
            'forterToken':'4880e3a1bc124c478eaa6ecf50b63162_1674955976295__UDF43_13ck',
            'lastRskxRun':'1674955978494',
            'QuantumMetricSessionID':'034dded78bed68c6ce1adadb9f59e8ea',
            'IR_gbd':'stockx.com',
            'IR_9060':'1674955980333%7C0%7C1674955980333%7C%7C; IR_PI=c7c35067-9976-11ed-b9f8-25af62750bf1%7C1675042380333',
            '_pxde':'0ee46d27e656eb0c78a91d112f40da8c70602c9a0a52bc70fdcd264c4183de76:eyJ0aW1lc3RhbXAiOjE2NzQ5NTU5OTQ4NzQsImZfa2IiOjB9',
            '_dd_s':'rum=0&expire=1674956937898',
            '_gat':'1',
            '_uetsid':'cd93f4d09ef711edaffe2bb988e92881',
            '_uetvid':'b24a09e09c4d11edae7967fe428be46d'}
        body = {
            "query":"query Browse($category: String, $filters: [BrowseFilterInput], $filtersVersion: Int, $query: String, $sort: BrowseSortInput, $page: BrowsePageInput, $currency: CurrencyCode, $country: String!, $market: String, $staticRanking: BrowseExperimentStaticRankingInput, $skipFollowed: Boolean!) {\n  browse(\n    category: $category\n    filters: $filters\n    filtersVersion: $filtersVersion\n    query: $query\n    sort: $sort\n    page: $page\n    experiments: {staticRanking: $staticRanking}\n  ) {\n    suggestions {\n      isCuratedPage\n      relatedPages {\n        title\n        url\n      }\n    }\n    results {\n      edges {\n        objectId\n        node {\n          ... on Product {\n            ...BrowseProductDetailsFragment\n            ...FollowedFragment @skip(if: $skipFollowed)\n            ...ProductTraitsFragment\n            market(currencyCode: $currency) {\n              ...MarketFragment\n            }\n          }\n          ... on Variant {\n            id\n            followed @skip(if: $skipFollowed)\n            product {\n              ...BrowseProductDetailsFragment\n              traits(filterTypes: [RELEASE_DATE, RETAIL_PRICE]) {\n                name\n                value\n              }\n            }\n            market(currencyCode: $currency) {\n              ...MarketFragment\n            }\n            traits {\n              size\n            }\n          }\n        }\n      }\n      pageInfo {\n        limit\n        page\n        pageCount\n        queryId\n        queryIndex\n        total\n      }\n    }\n    query\n  }\n}\n\nfragment FollowedFragment on Product {\n  followed\n}\n\nfragment ProductTraitsFragment on Product {\n  productTraits: traits(filterTypes: [RELEASE_DATE, RETAIL_PRICE]) {\n    name\n    value\n  }\n}\n\nfragment MarketFragment on Market {\n  currencyCode\n  bidAskData(market: $market, country: $country) {\n    lowestAsk\n    highestBid\n    lastHighestBidTime\n    lastLowestAskTime\n  }\n  state(country: $country) {\n    numberOfCustodialAsks\n  }\n  salesInformation {\n    lastSale\n    lastSaleDate\n    salesThisPeriod\n    salesLastPeriod\n    changeValue\n    changePercentage\n    volatility\n    pricePremium\n  }\n  deadStock {\n    sold\n    averagePrice\n  }\n}\n\nfragment BrowseProductDetailsFragment on Product {\n  id\n  name\n  urlKey\n  title\n  brand\n  description\n  model\n  condition\n  productCategory\n  listingType\n  media {\n    thumbUrl\n    smallImageUrl\n  }\n}\n",
            "variables":{
                "query":"",
                "category":"",
                "filters":[{"id":"currency","selectedValues":["KRW"]}],
                "filtersVersion":4,
                "sort":{"id":"featured_loc","order":"DESC"},
                "page":{"index":1,"limit":40},
                "currency":"KRW",
                "country":"KR",
                "marketName":None,
                "staticRanking":{"enabled":False},
                "skipFollowed":True},
            "operationName":"Browse"
            }
        data = json.dumps(body)
        # response = requests.post(url, headers=headers, json=body)
        # response = requests.post(url, headers=headers, data=body)
        response = requests.post(url, headers=headers, data=data)
        # response = requests.post(url, headers=headers, data=body, cookies=cookies)

        print(response.status_code)
        # print(response.json())
        return response
    # def _parse_productinfo_from_request(self, response):
    #     if(response.status_code != 200):
    #         print(response.status_code)
    #         return False
    #     else:

    

    ########################################################################################################################################################################
    def connect_db(self):
        con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8')

        return con




if __name__ == '__main__':
    StockXManager = StockXManager()
    StockXManager._request_get_productlist_page_N(page=1)