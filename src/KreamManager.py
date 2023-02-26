import requests
import pymysql
from Lib_else import sleep_random
import time

class KreamManager:
    def __init__(self):
        self.delay_min = 0.2
        self.delay_max = 0.3
        self.brand_list = ['Nike', 'Jordan', 'Adidas', 'New Balance', 'Vans', 'Converse']
        # self.time_last_request = time.time()
        pass

    def __setManagers__(self, SneakersManager, StockXManager, MusinsaManager, DBManager, ReportManager):
        self.SneakersManager = SneakersManager
        self.StockXManager = StockXManager
        self.MusinsaManager = MusinsaManager
        self.DBManager = DBManager
        self.ReportManager = ReportManager
    
    
    ### 동작 1. 상품 업데이트
    def update_product(self, table):
        if(table=='kream'):
            print("[KreamManager] : 상품 스크랩 시작합니다.")
            data_filtered = self.scrap_product_list()    # kream은 필터링 해서 준다.

            print("[KreamManager] : 신규 상품 %d개 등록합니다."%(len(data_filtered)))
            for item in data_filtered:
                self.DBManager.kream_update_product(item)

            print("[KreamManager] : 상품 등록 (to kream) 완료하였습니다.")

        elif(table=='sneakers_price'):
            # kream에서 registred False 인 (model_no, id_kream) 불러와서,
            # for
            # 1) INSERT 이면, kream에서 상품 가져와서, size_estimated_us 만들고, INSERT
            # 2) UPDATE 이면, sneakers_price에서 stockx 상품 가져와서, 맞는 kream 사이즈 찾아서 UPDATE
            # 3) PASS 이면, 이미 등록되었으니까 아무것도 안한다.

            tic = time.time()
            data = self.DBManager.kream_fetch_product()
            print("[KreamManager] : 신규 상품 %d개 sneakers_price 등록 검토합니다."%(len(data)))
            for index, item in enumerate(data):

                if(self.DBManager.sneakers_price_check_product_need_update(market='kream', product=item) == 'UPDATE'):
                    data_sneakers_price = self.DBManager.sneakers_price_fetch_product(product=item)
                    for item_sneakers_price in data_sneakers_price:
                        data_kream = self.DBManager.kream_fetch_product_size(product=item_sneakers_price)
                        if(len(data_kream) >0):
                            item_sneakers_price.update([('size_kream_mm', data_kream[0]['size_kream_mm']), ('size_kream_us', data_kream[0]['size_kream_us'])])
                            # item_sneakers_price.update(data_kream[0])
                            self.DBManager.sneakers_price_update_product(market='kream', query_type='UPDATE', product=item_sneakers_price)
                    self.DBManager.sneakers_price_update_product_id_kream(product=item)
                    self.DBManager.kream_update_registered(product=item)
                    toc = time.time()
                    print("[KreamManager] : (%d/%d) [%.1fmin] - [model_no: %s, id_kream: %s] - 업데이트 완료"%(index+1, len(data), (toc-tic)/60, item['model_no'], item['id_kream']))                

                elif(self.DBManager.sneakers_price_check_product_need_update(market='kream', product=item) == 'INSERT'):
                    data_kream = self.DBManager.kream_fetch_product_id_kream(id_kream=item['id_kream'])
                    for item_kream in data_kream:
                        self.DBManager.sneakers_price_update_product(market='kream', query_type='INSERT', product=item_kream)
                    self.DBManager.kream_update_registered(product=item)
                    toc = time.time()
                    print("[KreamManager] : (%d/%d) [%.1fmin] - [model_no: %s, id_kream: %s] - 신규등록 완료"%(index+1, len(data), (toc-tic)/60, item['model_no'], item['id_kream']))                

                else:
                    print("[KreamManager] : (%d/%d) [model_no: %s, id_kream: %s] - pass"%(index+1, len(data), item['model_no'], item['id_kream']))                
            print("[KreamManager] : 상품 등록 (to sneakers_price) 완료하였습니다.")                

    ### 동작 2. 가격 업데이트
    def update_price(self, id_start=1):
        print("[KreamManager] : 가격 스크랩 시작합니다.")

        list_id_kream = self.DBManager.sneakers_price_fetch_id_kream()
        cnt_total = len(list_id_kream)

        tic=time.time()
        for index, item_id_kream in enumerate(list_id_kream):
            if(index<id_start-1):
                continue

            data = self.DBManager.sneakers_price_fetch_product_id_kream(id_kream=item_id_kream['id_kream'])
            if(data[0]['id_musinsa'] == None):
                continue

            for item in data:
                state = self.scrap_price(item)
                if(state):
                    self.DBManager.sneakers_price_update_price(market='kream', product=item)
            
            toc=time.time()
            print("[KreamManager] : (%s)가격 스크랩 완료(%d/%d) [%.1fmin]"%(item['urlkey'], index+1, cnt_total, (toc-tic)/60))
        
        print("[KreamManager] : 가격 등록 완료하였습니다.")



    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 1. 상품 업데이트
    #######################################################################################################################################
    #######################################################################################################################################
    
    ### Lv1) 상품 스크랩 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_product_list(self):
        data_output = []

        page = 1
        tic = time.time()
        while(1) :
            sleep_random(self.delay_min, self.delay_max)
            state, data_page = self.scrap_productlist_page(page=page, brand_list=self.brand_list)
            if(state):
                data_output.extend(data_page)
                
                toc = time.time()
                print("[KreamManager] : kream 상품 스크랩 중 (%d page) [%.1fmin]" %(page, (toc-tic)/60))
                
                page = page + 1
            else:
                return data_output
                

    ### Lv2) 페이지 별 상품 스크랩 ###
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
    
    ### Lv3) 페이지 별 상품 Request ###
    # input : page
    # output : response
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

    ### Lv3) 상품 정보 Parsing ###
    # input : response, filter_brand_list
    # output : state, list[dict{'brand','id_kream','product_name','model_no', 'size_mm', 'size_us'}]
    def _parse_productinfo(self, response, brand_list):
        output_productlist = []

        data = response.json()
        if(data['next_cursor'] == None):
            print("[Kream_Manager] : 마지막 페이지 입니다.")
        
        else:
            for item in data['items']:
                if(self._filter_brand(item, brand_list)):
                    product = self.new_product()
                    product['brand'] = item['brand']['name'].lower()                 ## 브랜드
                    # product['size'] = item['options']                       ## 사이즈
                    product['id_kream'] = item['release']['id']                 ## Kream id
                    product['product_name'] = item['release']['name']               ## 이름
                    # product['product_name_kor'] = item['release']['translated_name']    ## 이름
                    product['model_no'] = item['release']['style_code']         ## 모델명
                    # product['color'] = item['release']['colorway']           ## color
                    # product['gender'] = item['release']['gender']             ## men
                    # product['original_price'] = item['release']['original_price']     ## 발매가
                    # product['has_immediate_delivery_item'] = item['market']['has_immediate_delivery_item']  ## 있는지

                    if(product['model_no']== '-'):
                        product['model_no'] = None

                    ### 여기서 DB 등록 여부 판단하자.
                    if(self.DBManager.kream_check_product_exist(product)):
                        continue

                    ## Size 처리 한 후, For문으로 상품 만들자.
                    if(type(item['options']) == list):
                        for size_raw in item['options']:
                            # 0. 초기화
                            product_copy = product.copy()
                            product_copy['size_kream_mm'] = ''
                            product_copy['size_kream_us'] = ''

                            # 1. '(' 기준 split
                            size_raw = size_raw.replace(')', '')
                            size_raw_list = size_raw.split('(')

                            # 2. 각 단위에 맞게 저장
                            for sizes in size_raw_list:
                                if(sizes.isnumeric()):
                                    product_copy['size_kream_mm'] = sizes
                                elif('US' in sizes):
                                    # sizes = sizes.replace('US', '').strip()
                                    sizes = sizes.strip()
                                    product_copy['size_kream_us'] = sizes
                                # 일단은 US 없어도, US에 넣자.
                                else:
                                    sizes = sizes.strip()
                                    product_copy['size_kream_us'] = sizes

                            ## 저장해야함.
                            output_productlist.append(product_copy)
                            del product_copy
                            
                    del product

        return output_productlist

    ### Lv4) sneakers 브랜드 Filtering ###
    # input : product, fiter_list
    # output : state
    def _filter_brand(self, item, filter):
        if(type(filter) == list):
            for item_filter in filter:
                if(item['brand']['name'].lower() == item_filter.lower()):
                    return True

        elif(type(filter) == str):
            if(item['brand']['name'].lower() == filter.lower()):
                    return True

        else:
            print("[KreamManager] : '_filter_brand' cannot filter type %s"%(type(filter)))

        return False

    ### Lv4) Product Template 생성 ###
    # input : 
    # output : dict{'brand','id_kream','product_name','model_no', 'size_mm', 'size_us'}
    def new_product(self):
        product = {}
        product['id_kream'] = ''
        product['brand'] = ''
        product['model_no'] = ''
        product['product_name'] = ''
        # product['product_name_kor'] = ''
        product['size_kream_mm'] = []
        product['size_kream_us'] = []
        # product['size_uk'] = []
        # product['gender'] = ''
        # product['color'] = ''
        # product['original_price'] = ''
        # product['has_immediate_delivery_item'] = False

        return product





    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 2. 가격 업데이트 (sneakers 에서 요청)
    #######################################################################################################################################
    #######################################################################################################################################

    ### 2. 가격 긁기 ###
    # input : dict{'size_kream_mm','size_kream_us','product_name','model_no', 'size_mm', 'size_us'}
    # output : state, dict{price_buy, price_sell, price_recent}
    def scrap_price(self, product):
        sleep_random(self.delay_min, self.delay_max)
        if(product['size_kream_mm'] == None or product['size_kream_mm'] ==''):
            return False
        
        size_kream = self._parse_kream_size(product['size_kream_mm'], product['size_kream_us'])
        response = self._request_price(id_kream=product['id_kream'], size=size_kream)
        if(response.status_code == 200):
            data = self._parse_priceinfo(response=response)
            product.update(data)
            state = True
        elif(response.status_code != 200):
            print("[KreamManager] : Error Code(%s) at '_request_price' with [id_kream=%s, size_mm=%s, size_us=%s]) "%(response.status_code, product['id_kream'], product['size_kream_mm'], product['size_kream_us']))
            state = False

        return state
    


    def _parse_kream_size(self, size_kream_mm, size_kream_us):
        if(size_kream_us == ""):
            size_kream = size_kream_mm
        else:
            size_kream = "%s(%s)"%(size_kream_mm, size_kream_us)

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
            'price_buy_kream' : 0,
            'price_sell_kream' : 0,
            'price_recent_kream': 0
        }

        data = response.json()
        output['price_buy_kream'] = data['market']['lowest_ask']
        output['price_sell_kream'] = data['market']['highest_bid']
        output['price_recent_kream'] = data['market']['last_sale_price']

        if(output['price_buy_kream'] == '' or output['price_buy_kream'] == None):
            output['price_buy_kream'] = 0
        if(output['price_sell_kream'] == '' or output['price_sell_kream'] == None):
            output['price_sell_kream'] = 0
        if(output['price_recent_kream'] == '' or output['price_recent_kream'] == None):
            output['price_recent_kream'] = 0

        return output



if __name__ == '__main__':
    KreamManager = KreamManager()
