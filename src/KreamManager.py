import requests
import pymysql
from Lib_else import sleep_random
import time

class KreamManager:
    def __init__(self):
        self.con = self.connect_db()
        self.cursor = self.con.cursor()

    def __del__(self):
        self.con.close()

    ##### 기능 1. (일회성) 상품 스크랩 #####
    def scrap_product(self):
        print("[Kream_Manager] : 상품 Srap 시작합니다.")
        tic = time.time()
        page = 1
        while(1) :
            sleep_random(0.3, 0.5)
            response = self._request_get_productlist_page_N(page)
            state = self._parse_productinfo(response)

            toc = time.time()
            print("[Kream_Manager] : %d page - %.0f" %(page, toc-tic))
            
            if(state):
                page = page + 1
            else:
                break
        
        toc = time.time()
        print("[Kream_Manager] : 상품 Srap 완료되었습니다. %.0fmin"%((toc-tic)/60))

    ##### 기능 2. (주기성) 가격 스크랩 ##### (Kream은 3600 per 1hour)
    def scrap_price(self, batch=40, delay_min=0.2, delay_max=0.5, id_start=1):
        tic = time.time()
        print("[Kream_Manager] : 가격 Scrap 시작합니다.")
        cnt_total = self._query_count_total(table="sneakers_price")

        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self._query_fetch_size(table="sneakers_price", id_start=id_start, id_end=id_end)

            ## 처리
            for (id, id_kream, size_kream_mm, size_kream_us) in data:
                if(size_kream_mm == "" and size_kream_us == ""):
                    continue

                # URL용 size 재조합
                size_kream = self._parse_keram_size(size_kream_mm, size_kream_us)
                
                sleep_random(delay_min, delay_max)
                response = self._request_price(id_kream=id_kream, size=size_kream)
                state, price_buy, price_sell = self._parse_priceinfo(response)

                if(state):
                    self._query_update_priceinfo(id, id_kream=id_kream, size_kream_mm=size_kream_mm, size_kream_us=size_kream_us, price_buy=price_buy, price_sell=price_sell)
            
            toc = time.time()
            print("[Kream_Manager] : 처리중(%6d/%d) - %.1fmin"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

    ##### 기능 3. (일회성 - 임시) 가격 없는애들만 뽑아서 스크랩 ##### 
    def scrap_price_which_is_none(self, batch=1000, delay_min=0.2, delay_max=0.5, id_start=1):
        tic = time.time()
        print("[Kream_Manager] : 가격 Scrap 시작합니다.")
        cnt_total = self._query_count_total(table="sneakers_price")

        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self._query_fetch_size_which_price_is_none(table="sneakers_price", id_start=id_start, id_end=id_end)## 임시

            ## 처리
            for (id, id_kream, size_kream_mm, size_kream_us) in data:
                if(size_kream_mm == "" and size_kream_us == ""):
                    continue

                # URL용 size 재조합
                size_kream = self._parse_keram_size(size_kream_mm, size_kream_us)
                
                sleep_random(delay_min, delay_max)
                response = self._request_price(id_kream=id_kream, size=size_kream)
                state, price_buy, price_sell = self._parse_priceinfo(response)

                if(state):
                    self._query_update_priceinfo(id, id_kream=id_kream, size_kream_mm=size_kream_mm, size_kream_us=size_kream_us, price_buy=price_buy, price_sell=price_sell)
            
            toc = time.time()
            print("[Kream_Manager] : 처리중(%6d/%d) - %.1fmin"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch



    ########################################################################################################################################################################
    ##### 기능 1 관련 함수 #####
    def _request_get_productlist_page_N(self, page):
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

    def _parse_productinfo(self, response):
        if(response.status_code != 200):
            print(response.status_code)
            return False
        else:
            data = response.json()
            for item in data['items']:
                #### PreProcessing (Nike, Jordan, Adidas, New Balance, Vans, Converse)
                if(self._filter_brand(item, ['Nike', 'Jordan', 'Adidas', 'New Balance'])):
                # if(self._filter_brand(item, 'Nike')):
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

                            self._query_insert_productinfo(product)
                    del product

            if(data['next_cursor'] == None):
                print("[Kream_Manager] : 마지막 페이지 입니다.")
                return False
            else:
                return True

    def _query_insert_productinfo(self, product):
        try:
            query = "INSERT INTO kream (brand, model_no, product_name, id_kream, size_mm, size_us) VALUES (%s, %s, %s, %s, %s, %s)" 
            self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['id_kream'], product['size_mm'], product['size_us']))

            self.con.commit()
        except Exception as e:
            print(product)
            print(e)

    def _filter_brand(self, item, filter):
        if(type(filter) == list):
            for item_filter in filter:
                if(item['brand']['name'] == item_filter):
                    return True

        elif(type(filter) == str):
            if(item['brand']['name'] == filter):
                    return True


        else:
            print("_filter_brand cannot filter type %s"%(type(filter)))

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


    ########################################################################################################################################################################
    ##### 기능 2 관련 함수 #####
    def _query_count_total(self, table):
        query = "SELECT COUNT(*) FROM %s"%(table)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        return result[0]

    def _query_fetch_size(self, table, id_start, id_end):
        query = "SELECT id, id_kream, size_kream_mm, size_kream_us FROM %s WHERE id>%d AND id <%d"%(table, id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data

    def _query_fetch_size_which_price_is_none(self, table, id_start, id_end):
        query = "SELECT id, id_kream, size_kream_mm, size_kream_us FROM %s WHERE id>%d AND id <%d AND ((price_buy_kream IS NULL) AND (price_sell_kream IS NULL))"%(table, id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data

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
        price_buy = ""
        price_sell = ""

        if(response.status_code == 429):
            print(response.headers)
        elif(response.status_code != 200):
            print(response.status_code)
            return False, price_buy, price_sell
        else:
            data = response.json()
            price_buy = data['market']['lowest_ask']
            price_sell = data['market']['highest_bid']

            return True, price_buy, price_sell

    def _query_update_priceinfo(self, id, id_kream, size_kream_mm, size_kream_us, price_buy, price_sell):
        try:
            # query = "INSERT INTO sneakers_price (id, id_kream, size_kream_mm, size_kream_us, price_buy_kream, price_sell_kream) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE price_buy_kream=%s, price_sell_kream=%s"
            # query = "UPDATE sneakers_price SET price_buy_kream='%s', price_sell_kream='%s' WHERE id_kream=%s AND size_kream_mm=%s AND size_kream_us=%s"
            query = "UPDATE sneakers_price SET price_buy_kream=NULLIF(%s, ''), price_sell_kream=NULLIF(%s, '') WHERE id_kream=%s AND size_kream_mm=%s AND size_kream_us=%s"
            self.cursor.execute(query, (price_buy, price_sell, id_kream, size_kream_mm, size_kream_us))

            self.con.commit()
        except Exception as e:
            print(e)
    

    ########################################################################################################################################################################
    def connect_db(self):
        con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8')

        return con


if __name__ == '__main__':
    KreamManager = KreamManager()

    ## 기능 1.
    # KreamManager.scrap_product()

    ## 기능 2.
    # KreamManager.scrap_price(batch=20, delay_min=0.2, delay_max=0.5, id_start=1321)

    KreamManager.scrap_price_which_is_none(batch=500, delay_min=0.2, delay_max=0.5, id_start=6501)


