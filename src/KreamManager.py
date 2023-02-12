import requests
import pymysql
from Lib_else import sleep_random
import time

class KreamManager:
    def __init__(self):
        # self.time_last_request = time.time()
        pass

    def __del__(self):
        pass
    
    ### 1. 페이지 돌며 전체 상품 긁기 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_kream, product_name, model_no, size_mm, size_us}]
    def scrap_productlist_page(self, page, brand_list=['Nike', 'Jordan', 'Adidas', 'New Balance']):
        data = []
        response = self._get_productlist_page(page=page)
        if(response.status_code == 200):
            data = self._parse_productinfo(response=response, brand_list=brand_list)
            state = True
        elif(response.status_code != 200):
            print("[KreamManager] : Error Code(%s) at '_get_productlist_page' with [page=%s]) "%(response.status_code, page))
            state = False
        
        return state, data

    ### 2. 가격 긁기 ###
    # input : id_kream, size_mm, size_us
    # output : state, dict{price_buy, price_sell, price_recent}
    def scrap_price(self, id_kream, size_mm, size_us):
        data = {}
        if(size_mm == '' and size_us ==''):
            return False, data
        
        size_kream = self._parse_keram_size(size_mm, size_us)
        response = self._request_price(id_kream=id_kream, size=size_kream)
        if(response.status_code == 200):
            data = self._parse_priceinfo(response=response)
            state = True
        elif(response.status_code != 200):
            print("[KreamManager] : Error Code(%s) at '_request_price' with [id_kream=%s, size_mm=%s, size_us=%s]) "%(response.status_code, id_kream, size_mm, size_us))
            state = False

        return state, data
        

    
    ##### 기능 1 관련 함수 #############################################################################################################################################################################
    def _get_productlist_page(self, page):
        url = "https://kream.co.kr/api/p/products?category_id=34&per_page=40&cursor="+str(page)+"&request_key=b9958edc-cea2-478c-87a2-f5f9920020d6"
        headers = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## ****필수****
            'x-kream-api-version': '14',
            'x-kream-client-datetime': '20230127114050+0900', ##  datetime 옛날걸로 해도 data 변화 없음.
            'x-kream-device-id': 'web;0f018fc8-60aa-4a21-bf18-57713010be19', ##  device-id 옛날걸로 해도 data 변화 없음.
        }
        ## Body에 암만 넣어봐도 소용없다. URL에 넣어줘야 변한다.
        # body = {
        #     'category_id': 34,
        #     'per_page': 40,
        #     'cursor': 1,
        #     'request_key': 'd39de13b-fa7e-40bf-99a9-d81654d0cbf0',  ## 필요없음
        # }
        # response = requests.get(url, headers=headers, params=body)
        response = requests.get(url, headers=headers)
        return response

    def _parse_productinfo(self, response, brand_list):
        output_productlist = []

        data = response.json()
        if(data['next_cursor'] == None):
            print("[Kream_Manager] : 마지막 페이지 입니다.")
        
        else:
            for item in data['items']:
                #### PreProcessing (Nike, Jordan, Adidas, New Balance, Vans, Converse)
                if(self._filter_brand(item, brand_list)):
                    product = self.new_product()
                    product['brand'] = item['brand']['name']                 ## 브랜드
                    # product['size'] = item['options']                       ## 사이즈
                    product['id_kream'] = item['release']['id']                 ## Kream id
                    product['product_name'] = item['release']['name']               ## 이름
                    # product['product_name_kor'] = item['release']['translated_name']    ## 이름
                    product['model_no'] = item['release']['style_code']         ## 모델명
                    # product['color'] = item['release']['colorway']           ## color
                    # product['gender'] = item['release']['gender']             ## men
                    # product['original_price'] = item['release']['original_price']     ## 발매가
                    # product['has_immediate_delivery_item'] = item['market']['has_immediate_delivery_item']  ## 있는지

                    ## Size 처리 한 후, For문으로 상품 만들자.
                    if(type(item['options']) == list):
                        for size_raw in item['options']:
                            # 0. 초기화
                            product['size_mm'] = ''
                            product['size_us'] = ''

                            # 1. '(' 기준 split
                            size_raw = size_raw.replace(')', '')
                            size_raw_list = size_raw.split('(')

                            # 2. 각 단위에 맞게 저장
                            for sizes in size_raw_list:
                                if(sizes.isnumeric()):
                                    product['size_mm'] = sizes
                                elif('US' in sizes):
                                    # sizes = sizes.replace('US', '').strip()
                                    sizes = sizes.strip()
                                    product['size_us'] = sizes
                                # 일단은 US 없어도, US에 넣자.
                                else:
                                    sizes = sizes.strip()
                                    product['size_us'] = sizes

                            ## 저장해야함.
                            output_productlist.append(product)
                            
                    del product

        return output_productlist

    def _filter_brand(self, item, filter):
        if(type(filter) == list):
            for item_filter in filter:
                if(item['brand']['name'] == item_filter):
                    return True

        elif(type(filter) == str):
            if(item['brand']['name'] == filter):
                    return True

        else:
            print("[KreamManager] : '_filter_brand' cannot filter type %s"%(type(filter)))

        return False

    def new_product(self):
        product = {}
        product['id_kream'] = ''
        product['brand'] = ''
        product['model_no'] = ''
        product['product_name'] = ''
        # product['product_name_kor'] = ''
        product['size_mm'] = []
        product['size_us'] = []
        # product['size_uk'] = []
        # product['gender'] = ''
        # product['color'] = ''
        # product['original_price'] = ''
        # product['has_immediate_delivery_item'] = False

        return product


    ##### 기능 2 관련 함수 #############################################################################################################################################################################
    def _parse_keram_size(self, size_mm, size_us):
        if(size_us == ""):
            size_kream = size_mm
        else:
            size_kream = "%s(%s)"%(size_mm, size_us)

        return size_kream

    def _request_price(self, id_kream, size):
        url = "https://kream.co.kr/api/p/products/"+str(id_kream)+"/"+str(size)
        headers = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',    ## ****필수****
            'x-kream-api-version': '14',
            'x-kream-client-datetime': '20230127114050+0900', ##  datetime 옛날걸로 해도 data 변화 없음.
            'x-kream-device-id': 'web;0f018fc8-60aa-4a21-bf18-57713010be19', ##  device-id 옛날걸로 해도 data 변화 없음.
        }

        response = requests.get(url, headers=headers)
        return response

    def _parse_priceinfo(self, response):
        output = {
            'price_buy' : 0,
            'price_sell' : 0,
            'price_recent': 0
        }

        data = response.json()
        output['price_buy'] = data['market']['lowest_ask']
        output['price_sell'] = data['market']['highest_bid']
        output['price_recent'] = data['market']['last_sale_price']

        return output


if __name__ == '__main__':
    KreamManager = KreamManager()
