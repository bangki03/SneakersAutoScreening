from KreamManager import KreamManager
from StockXManager import StockXManager
from MusinsaManager import MusinsaManager
from ReportManager import ReportManager
from DBManager import DBManager
import time
from math import floor
from Lib_else import sleep_random

class SneakersManager:
    def __init__(self):
        self.DBManager = DBManager()
        self.KreamManager = KreamManager()
        self.StockXManager = StockXManager()
        self.MusinsaManager = MusinsaManager()
        self.ReportManager = ReportManager()

        ### SETTING ###
        self.brand_list_kream = ['Nike', 'Jordan', 'Adidas', 'New Balance', 'Vans', 'Converse',]
        self.brand_list_stockx = ['Nike', 'Jordan', 'Adidas', 'New Balance', 'Vans', 'Converse',]
        self.brand_list_musinsa = ['adidas', 'vans', 'converse']

    ### 기능 1) (kream & stockx) 상품 스크랩
    def scrap_product(self):
        self.scrap_stockx_product(delay_min=0.2, delay_max=0.5, brand_list=self.brand_list_stockx)
        # self.DBManager._table_truncate(table="kream")
        self.scrap_kream_product(delay_min=0.2, delay_max=0.5, brand_list=self.brand_list_kream)
        self.scrap_stockx_model_no(id_start=1, batch=50, delay_min=5.0, delay_max=7.0)        ## 얘가 웰케 403 걸리지
        # self.DBManager._table_truncate(table="sneakers")
        self.export_common_product()
        # self.DBManager._table_truncate(table="sneakers_price")
        self.scrap_stockx_size(table='sneakers', id_start=1, batch=50, delay_min=0.8, delay_max=1.2)
        self.fill_size_estimated_mm(id_start=1)
        self.match_kream_size(id_start=1, batch=200)
        self.match_id_kream()
        
    ### 기능 2) (kream & stockx) 가격 스크랩
    def scrap_price(self, id_start=1, delay_min = 0.4, delay_max=0.5):
        # [To Do] 
        # 1. Kream 사이즈별로 가격 스크랩
        # 2. StockX 모델별로 가격 스크랩
        # 3. StockX 사이즈별로 체결가 스크랩
        # 특징) 
        # 1. 한 서버에 너무 빠르게 자주 요청하면, 403 Forbidden 혹인 429 Too Many Request 발생.
        #   └ 최대한 교대로 배치(Process 이용하면 좋겠지만, 일단은 수동 제어하자.)
        #
        # How)
        # 1. 모델별로 batch 생성
        # 2. StockX 가격 스크랩
        # 3. 사이즈별로
        #   1) Kream 가격 스크랩
        #   2) StockX 체결가스크랩
        # 4. DB에 update 요청
        data = self.DBManager._sneakers_price_select_distinct_urlkey()
        cnt_total = len(data)

        tic = time.time()
        for index, urlkey in enumerate(data):
            if(index<id_start-1):
                continue

            # 2.StockX 가격 스크랩
            state, price_stockx_list = self.StockXManager.scrap_price(urlkey=urlkey[0])
            if(state):
                for item in price_stockx_list:
                    self.DBManager._sneakers_price_update_price_stockx(size=item['size'], price_buy=item['price_buy'], price_sell=item['price_sell'], urlkey=urlkey[0])

            # 3. 사이즈 별로
            data_batch = self.DBManager._sneakers_price_select_all_in_urlkey(urlkey=urlkey[0])
            for item in data_batch:

                sleep_random(delay_min, delay_max)
                state_kream, data_kream = self.KreamManager.scrap_price(id_kream=item['id_kream'], size_mm=item['size_kream_mm'], size_us=item['size_kream_us'])
                if(state_kream):
                    self.DBManager._sneakers_price_update_price_kream(id_kream=item['id_kream'], size_kream_mm=item['size_kream_mm'], size_kream_us=item['size_kream_us'], price_buy=data_kream['price_buy'], price_sell=data_kream['price_sell'], price_recent=data_kream['price_recent'])

                # sleep_random(delay_min, delay_max)
                # state_stockx, data_stockx = self.StockXManager.scrap_price_recent(urlkey=urlkey, id_stockx=item['id_stockx'])
                # if(state_stockx):
                #     self.DBManager._sneakers_price_update_price_recent_stockx(id_stockx=item['id_stockx'], price_recent=data_stockx['price_recent'])


                # self.DBManager._sneakers_price_update_price_kream_and_price_recent_stockx(price_buy_kream=data_kream['price_buy'], price_sell_kream=data_kream['price_sell'], price_recent_kream=data_kream['price_recent'], price_recent_stockx=data_stockx['price_recent'], id_stockx=item['id_stockx'])

            
            toc = time.time()
            print("[SneakersManager] : (%s)가격 스크랩 완료(%d/%d) [%.1fmin]"%(urlkey[0], index+1, cnt_total, (toc-tic)/60))

        self.export_report_price()

    ### 기능 3) (kream & stockx) Report 발행
    def export_report_price(self):
        self.ReportManager.export_report_price()




    ### 기능 4) (Musinsa) 상품 스크랩
    def scrap_musinsa_product(self):
        # self.DBManager._table_truncate(table="musinsa")
        # self.scrap_musinsa_id_musinsa(brand_list=self.brand_list_musinsa, delay_min=0.5, delay_max=0.8)
        # self.scrap_musinsa_price(id_start=161, batch=20, delay_min=0.4, delay_max=0.5)

        self.update_musinsa_report(id_start=1, batch=40)
    


    ######### 정리하자 #########
    # 상품 스크랩 기존처럼
    # kream 그대로 (새걸로)
    # stockx 그대로 (업데이트)
    # musinsa 그대로 (새걸로)

    # sneakers_price는
    # stockx 업데이트 (가격, 사이즈)
    # kream 업데이트 (예상 사이즈, 가격)
    # musinsa 업데이트
    

    def tmp(self):
        #### 상품 스크랩 (stockx) ####
        # self.scrap_stockx_product(delay_min=0.2, delay_max=0.5, brand_list=self.brand_list_stockx)
        self.scrap_stockx_model_no(id_start=1, batch=50, delay_min=5.0, delay_max=7.0)        ## 얘가 웰케 403 걸리지

        #### 상품 스크랩 (musinsa) ####
        # self.DBManager._table_truncate(table="musinsa")
        # self.scrap_musinsa_id_musinsa(brand_list=self.brand_list_musinsa, delay_min=0.5, delay_max=0.8)
        # self.scrap_musinsa_price(id_start=1, batch=20, delay_min=0.4, delay_max=0.5)

        #### 상품 스크랩 (kream) ####
        # self.DBManager._table_truncate(table="kream")
        # self.scrap_kream_product(delay_min=0.2, delay_max=0.5, brand_list=self.brand_list_kream)


        #### sneakers_price 만들기 ####
        # self.update_sneakers_price_model_no(id_start=2950, batch=200) # ~1827 / 2700~3410 / 5053~
        # if(False):
        #     self.scrap_stockx_size(table='stockx', id_start=1, batch=20, delay_min=0.8, delay_max=1.0)  # 사이즈만
        # else:
        #     self.scrap_stockx_size_with_price(table='stockx', id_start=1, batch=20, delay_min=0.8, delay_max=1.0)   # 하는 김에 가격까지

        #### 가격 스크랩 (stockx) ####

        #### 가격 스크랩 (kream) ####
        # self.fill_size_estimated_mm_null(id_start=110310, batch=500)
        # self.match_kream_size(id_start=29401, batch=200)        ## 우선 33000까지만
        # self.match_id_kream()
        # self.scrap_kream_price(id_start=503, delay_min=0.5, delay_max=0.7)

        #### 가격 스크랩 (musinsa) ####
        # self.update_musinsa_report(id_start=1, batch=40)




    ##### 기능 1 관련 함수 #############################################################################################################################################################################
    def scrap_stockx_product(self, brand_list=[], delay_min=0.2, delay_max=0.5):
        print("[SneakersManager] : StockX 상품 스크랩 시작합니다.")
        tic = time.time()

        if(brand_list == []):
            page = 1
            while(1) :
                sleep_random(delay_min, delay_max)
                state, data = self.StockXManager.scrap_productlist_page(page=page, brand_list=brand_list)
                if(state):
                    for product in data:
                        data_db = self.DBManager._stockx_select_urlkey(product['urlkey'])
                        if(len(data_db) > 0):
                            self.DBManager._stockx_update_productinfo(product=product)
                        else:
                            self.DBManager._stockx_insert_productinfo(product=product)

                    toc = time.time()
                    print("[SneakersManager] : StockX 상품 스크랩 중 (%d page) [%.0fs]" %(page, toc-tic))    

                    page = page + 1
                else:
                    break

        for brand in brand_list:
            page = 1
            while(page<30) :        ## 언제까지 해야할지 못찾겠네.. 임시로 30페이지
                sleep_random(delay_min, delay_max)
                state, data = self.StockXManager.scrap_productlist_page_brand(brand=brand.lower(), page=page)
                if(state):
                    for product in data:
                        data_db = self.DBManager._stockx_select_urlkey(product['urlkey'])
                        if(len(data_db) > 0):
                            self.DBManager._stockx_update_productinfo(product=product)
                        else:
                            self.DBManager._stockx_insert_productinfo(product=product)

                    toc = time.time()
                    print("[SneakersManager] : StockX (%s)상품 스크랩 중 (%d page) [%.0fs]" %(brand, page, toc-tic))    

                    page = page + 1
                else:
                    break

        toc = time.time()
        print("[SneakersManager] : StockX 상품 스크랩 완료되었습니다. [%.1fmin]"%((toc-tic)/60))

    def scrap_kream_product(self, brand_list, delay_min=0.2, delay_max=0.5):
        print("[SneakersManager] : kream 상품 스크랩 시작합니다.")
        page = 1
        tic = time.time()
        while(1) :
            sleep_random(delay_min, delay_max)
            state, data = self.KreamManager.scrap_productlist_page(page=page, brand_list=brand_list)
            if(state):
                for product in data:
                    self.DBManager._kream_insert_productinfo(product=product)
                
                toc = time.time()
                print("[SneakersManager] : kream 상품 스크랩 중 (%d page) [%.1fs]" %(page, (toc-tic)/60))
                
                page = page + 1
            else:
                break
        
        toc = time.time()
        print("[SneakersManager] : Kream 상품 스크랩 완료되었습니다. %.1fmin"%((toc-tic)/60))

    def scrap_stockx_model_no(self, id_start=1, batch=50, delay_min=0.2, delay_max=0.5):
        print("[SneakersManager] : stockx 모델명 스크랩 시작합니다.")
        ## 비어있는 것만 찾아서 업데이트 하는 걸로 바꾸자.
        cnt_total = self.DBManager._table_count_total(table='stockx')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._stockx_select_urlkey_batch(id_start=id_start, id_end=id_end)

            for (id, urlkey, model_no) in data:
                sleep_random(delay_min, delay_max)
                state, data = self.StockXManager.scrap_model_no(urlkey=urlkey)
                if(state):
                    self.DBManager._stockx_update_model_no(model_no=data['model_no'], urlkey=urlkey)
            
            toc = time.time()
            print("[SneakersManager] : stockx 모델명 스크랩 중 (%4d/%4d) [%.0fs]"%(id_end, cnt_total, toc-tic))

            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch
        
        toc = time.time()
        print("[SneakersManager] : stockx 모델명 스크랩 완료되었습니다. %.1fmin"%((toc-tic)/60))

    def export_common_product(self):
        self.ReportManager.export_report_proudct(table='kream')  # sneakers DB는 여기서 임시 레포트만 뽑지, DB 축적은 아래에서 한다.
        self.ReportManager.export_report_proudct(table='stockx')
        self.ReportManager.export_report_proudct(table='sneakers')

        data = self.DBManager._fetch_sneakers_product(option_pandas=False)
        for (brand, model_no, product_name, urlkey) in data:
            self.DBManager._sneakers_insert_productinfo(brand=brand, model_no=model_no, product_name=product_name, urlkey=urlkey)

    def scrap_stockx_size(self, table, id_start=1, batch=50, delay_min=0.5, delay_max=0.8):
        print("[SneakersManager] : StockX 사이즈 스크랩 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table=table)

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data_batch = self.DBManager._sneakers_select_all(id_start=id_start, id_end=id_end)

            for (id, brand, model_no, product_name, urlkey) in data_batch:
                sleep_random(delay_min, delay_max)
                state, data = self.StockXManager.scrap_size(urlkey=urlkey)
                if(state):
                    for item in data:
                        data_exist = self.DBManager._sneakers_price_select_product(urlkey=urlkey, size_stockx=item['size'])
                        if(len(data_exist) >0 ):
                            self.DBManager._sneakers_price_insert_data_with_size(brand=brand, model_no=model_no, product_name=product_name, size=item['size'], urlkey=urlkey, id_stockx=item['id_stockx'])
            
            toc = time.time()
            print("[SneakersManager] : Stockx 사이즈 스크랩 중 (%4d/%4d) [%.1fmin]"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

        toc = time.time()
        print("[SneakersManager] : Stockx 사이즈 스크랩 완료되었습니다. [%.1fmin]"%((toc-tic)/60))

    def scrap_stockx_size_with_price(self, table, id_start=1, batch=50, delay_min=0.5, delay_max=0.8):
        print("[SneakersManager] : StockX 사이즈 스크랩 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table=table)

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data_batch = self.DBManager._stockx_select_all(id_start=id_start, id_end=id_end)

            for (id, brand, model_no, product_name, urlkey) in data_batch:
                # sleep 안기다리게 모델명으로만 사전 Filtering 하는 코드
                data_exist = self.DBManager._sneakers_price_select_product_from_only_urlkey(urlkey=urlkey)
                if(len(data_exist) > 0) :
                    continue

                sleep_random(delay_min, delay_max)
                state, data = self.StockXManager.scrap_size(urlkey=urlkey)
                if(state):
                    for item in data:
                        # 모델명&사이즈로 업데이트 여부 확인 코드
                        data_exist = self.DBManager._sneakers_price_select_product(urlkey=urlkey, size_stockx=item['size'])
                        if(len(data_exist) == 0 ):
                            self.DBManager._sneakers_price_insert_data_with_size_and_price(brand=brand, model_no=model_no, product_name=product_name, size=item['size'], urlkey=urlkey, id_stockx=item['id_stockx'], price_buy=item['price_buy'], price_sell=item['price_sell'])
            
            toc = time.time()
            print("[SneakersManager] : Stockx 사이즈 스크랩 중 (%4d/%4d) [%.1fmin]"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

        toc = time.time()
        print("[SneakersManager] : Stockx 사이즈 스크랩 완료되었습니다. [%.1fmin]"%((toc-tic)/60))

    def fill_size_estimated_mm(self, id_start=1):
        print("[SneakersManager] : StockX 사이즈(US) -> 예상 사이즈(mm) 변환 시작합니다.")
        data = self.DBManager._sneakers_price_select_distinct_urlkey()
        cnt_total = len(data)

        tic = time.time()
        for index, urlkey in enumerate(data):
            if(index<id_start-1):
                continue

            data = self.DBManager._sneakers_price_select_size_stockx(urlkey=urlkey[0])

            ## 처리
            for (id, brand, model_no, size_stockx, urlkey) in data:
                size_estimated_mm = self._convert_size_US2mm(brand=brand, size_US=size_stockx)
                self.DBManager._sneakers_price_update_size_estimated_mm(brand=brand, model_no=model_no, size_stockx=size_stockx, size_estimated_mm=size_estimated_mm)
            
            toc = time.time()
            print("[SneakersManager] : 예상 사이즈 계산중(%4d/%4d) [%.0fs]"%(index+1, cnt_total, toc-tic))

        toc = time.time()
        print("[SneakersManager] : 예상 사이즈(mm) 변환 완료되었습니다. [%.1fmin]"%((toc-tic)/60))
    def fill_size_estimated_mm_null(self, id_start=1, batch=500):
        print("[SneakersManager] : StockX 사이즈(US) -> 예상 사이즈(mm) 변환 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='sneakers_price')
        tic = time.time()

        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._sneakers_price_select_size_estimated_null(id_start=id_start, id_end=id_end)

        
            for (id, brand, size_stockx) in data:
                size_estimated_mm = self._convert_size_US2mm(brand=brand, size_US=size_stockx)
                self.DBManager._sneakers_price_update_size_estimated_mm_where_id(id=id, size_estimated_mm=size_estimated_mm)
                
            toc = time.time()
            print("[SneakersManager] : 예상 사이즈 계산중(%4d/%4d) [%.0fs]"%(id_end, cnt_total, toc-tic))

            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

        toc = time.time()
        print("[SneakersManager] : 예상 사이즈(mm) 변환 완료되었습니다. [%.1fmin]"%((toc-tic)/60))
    def _convert_size_US2mm(self, brand, size_US):
        if(brand == 'nike' or brand == 'jordan'):
            LUT = {
                '2.5':'215',
                '3':'220',
                '3.5':'225',
                '4':'230',
                '4.5':'235',
                '5':'235',
                '5.5':'240',
                '6':'240',
                '6.5':'245',
                '7':'250',
                '7.5':'255',
                '8':'260',
                '8.5':'265',
                '9':'270',
                '9.5':'275',
                '10':'280',
                '10.5':'285',
                '11':'290',
                '11.5':'295',
                '12':'300',
                '12.5':'305',
                '13':'310',
                '13.5':'315',
                '14':'320',
                '14.5':'325',
                '15':'330',
                '15.5':'335',
                '16':'340',
                '16.5':'345',
                '17':'350',
                '17.5':'355',
                '18':'360',
                '18.5':'365',
                '19':'370',
                '19.5':'375',
                '20':'380',
                '20.5':'385',
                '21':'390',
                '21.5':'395',
                '22':'400',
                '4W':'210',
                '4.5W':'215',
                '5W':'220',
                '5.5W':'225',
                '6W':'230',
                '6.5W':'235',
                '7W':'240',
                '7.5W':'245',
                '8W':'250',
                '8.5W':'255',
                '9W':'260',
                '9.5W':'265',
                '10W':'270',
                '10.5W':'275',
                '11W':'280',
                '11.5W':'285',
                '12W':'290',
                '12.5W':'295',
                '13W':'300',
                '13.5W':'305',
                '14W':'310',
                '14.5W':'315',
                '15W':'320',
                '15.5W':'325',
                '16W':'330',
                '16.5W':'335',
                '17W':'340',
                '17.5W':'345',
                '18W':'350',
                '18.5W':'355',
                '19W':'360',
                '19.5W':'365',
                '20W':'370',
                '20.5W':'375',
                '21W':'380',
                '21.5W':'385',
                '22W':'390',
                '22.5W':'395',
                '23W':'400',
                '3.5Y':'225',
                '4Y':'230',
                '4.5Y':'235',
                '5Y':'235',
                '5.5Y':'240',
                '6Y':'240',
                '6.5Y':'245',
                '7Y':'250',
                '7.5Y':'255',
                '8Y':'260',
                '8.5Y':'265',
                '9Y':'270',
                '9.5Y':'275',
                '10Y':'280',
                '10.5Y':'285',
                '10.5C':'170',
                '11C':'175',
                '11.5C':'180',
                '12C':'185',
                '12.5C':'190',
                '13C':'195',
                '13.5C':'195',
                '1Y':'200',
                '1.5Y':'205',
                '2Y':'210',
                '2.5Y':'215',
                '3Y':'220',
                }
            try:
                size_tmp = size_US.split('/')[0].strip().upper()
                return LUT[size_tmp]
            except:
                if(size_US != None):
                    print("%s : %s"%(brand, size_US))
                return ''
        elif(brand == 'adidas' or brand == 'new balance'):
            LUT = {
                '2.5':'205',
                '3':'210',
                '3.5':'215',
                '4':'220',
                '4.5':'225',
                '5':'230',
                '5.5':'235',
                '6':'240',
                '6.5':'245',
                '7':'250',
                '7.5':'255',
                '8':'260',
                '8.5':'265',
                '9':'270',
                '9.5':'275',
                '10':'280',
                '10.5':'285',
                '11':'290',
                '11.5':'295',
                '12':'300',
                '12.5':'305',
                '13':'310',
                '13.5':'315',
                '14':'320',
                '14.5':'325',
                '15':'330',
                '15.5':'335',
                '16':'340',
                '16.5':'345',
                '17':'350',
                '17.5':'355',
                '18':'360',
                '5W':'220',
                '5.5W':'225',
                '6W':'230',
                '6.5W':'235',
                '7W':'240',
                '7.5W':'240',
                '8W':'245',
                '8.5W':'250',
                '9W':'255',
                '9.5W':'260',
                '10W':'265',
                '10.5W':'265',
                '11W':'270',
                '11.5W':'275',
                '12W':'280',
                '12.5W':'285',
                '13W':'290',
                '13.5W':'295',
                '14W':'295',
                '14.5W':'300',
                '15W':'305',
                '15.5W':'310',

                }
            try:
                return LUT[size_US]
            except:
                if(size_US != None):
                    print("%s : %s"%(brand, size_US))
                return ''
        elif(brand == 'vans'):
            LUT = {
                '3.5': '215',
                '4': '220',
                '4.5': '225',
                '5': '230',
                '5.5': '235',
                '6':'240',
                '6.5':'245',
                '7':'250',
                '7.5':'255',
                '8':'260',
                '8.5':'265',
                '9':'270',
                '9.5':'275',
                '10':'280',
                '10.5':'285',
                '11':'290',
                '11.5':'295',
                '12':'300',
                '12.5':'305',
                '13':'310',
                '13.5':'315',
                '14':'320',
                '14.5':'325',
                '15':'330',
                '15.5':'335',
                '16':'340',
                '5W':'215',
                '5.5W':'220',
                '6W':'225',
                '6.5W':'230',
                '7W':'235',
                '7.5W':'240',
                '8W':'245',
                '8.5W':'250',
                '9W':'255',
                '9.5W':'260',
                '10W':'265',
                '10.5W':'270',
                '11W':'275',
                '11.5W':'280',
                '12W':'285',
                '12.5W':'290',
                '13W':'295',
                '13.5W':'300',
                '14W':'310',
                '14.5W':'320',
                '15W':'330',
                '15.5W':'340',
                '3.5Y': '225',
                '4Y': '230',
                '4.5Y': '235',
                '5Y': '240',
                '5.5Y': '245',
                '6Y': '245',
                '6.5Y': '250',
                '7Y': '255',
            }
            try:
                return LUT[size_US]
            except:
                if(size_US != None):
                    print("%s : %s"%(brand, size_US))
                return ''
        elif(brand == 'converse'):
            return None
        else:
            print("No Size LUT for brand %s"%(brand))
            return ''
        
    ##
    def match_kream_size(self, batch=500, id_start=1):
        print("[SneakersManager] : Kream 사이즈 매칭 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='sneakers_price')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._sneakers_price_select_size_estimated(id_start=id_start, id_end=id_end)

            for (id, brand, model_no, size_stockx, size_estimated) in data:
                                
                size_mm, size_us = self._get_kream_size(brand=brand, model_no=model_no, size_stockx=size_stockx, size_estimated=size_estimated)
                self.DBManager._sneakers_price_update_size_kream(brand=brand, model_no=model_no, size_stockx=size_stockx, size_estimated_mm=size_estimated, size_mm=size_mm, size_us=size_us)
            
            toc = time.time()
            print("[SneakersManager] : Kream 사이즈 매칭중(%4d/%4d) [%.1fmin]"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

        toc = time.time()
        print("[SneakersManager] : Kream 사이즈 매칭 완료되었습니다. [%.0fmin]"%((toc-tic)/60))

    def _get_kream_size(self, brand, model_no, size_stockx, size_estimated):
        data = self.DBManager._kream_select_size_estimated(brand, model_no, size_estimated)

        try:
            size_mm_set = data[0][0]
            size_us_set = data[0][1]
            for (size_mm, size_us) in data:
                if(size_stockx in size_us):
                    size_mm_set = size_mm
                    size_us_set = size_us
        except:
            size_mm_set = ''
            size_us_set = ''

        return size_mm_set, size_us_set

    # Kream에서 model_no, id_kream 뽑은다음에 무지성 업데이트
    def match_id_kream(self):
        print("[SneakersManager] : id_kream 매칭 시작합니다.")
        data = self.DBManager._kream_select_distict_id_kream_model_no()
        cnt_total = len(data)

        tic = time.time()
        index = 1
        for (id_kream, model_no) in data:
            self.DBManager._sneakers_price_update_id_kream(model_no=model_no, id_kream=id_kream)

            if(index % 100 == 0):
                toc = time.time()
                print("[SneakersManager] : id_kream 매칭중(%4d/%4d) [%.1fmin]"%(index, cnt_total, (toc-tic)/60))
            index = index+1

        toc = time.time()
        print("[SneakersManager] : id_kream 매칭 완료하였습니다. [%.1fmin]"%((toc-tic)/60))

    # 신규 상품에 대해, Kream에 상품 있는지 확인 후, 업데이트
    def match_id_kream(self):
            #1. sneakers_price > id_kream 이 없는 model_no 를 뽑는다.
            #2. 해당 model_no가 kream에 있는지 찾고, 있으면 id_kream을 가져온다.
            # 3. sneakers_price 에서 그 model_no에 해당하는 row들의 id_kream을 입력한다.
            print("[SneakersManager] : id_kream 매칭 시작합니다.")
            data = self.DBManager._sneakers_price_select_model_no_id_kream_null()
            cnt_total = len(data)

            tic = time.time()
            for (model_no) in data:
                data_id_kream = self.DBManager._kream_select_distict_id_kream_where_model_no()
                if(len(data_id_kream) >0):
                    self.DBManager._sneakers_price_update_id_kream(model_no=model_no, id_kream=data_id_kream)




    ##### Musinsa 관련 함수 #############################################################################################################################################################################
    def scrap_musinsa_id_musinsa(self, brand_list, delay_min=0.6, delay_max=0.8):
        print("[SneakersManager] : Musinsa 상품 스크랩 시작합니다.")

        page = 1
        tic = time.time()
        while(1) :
            sleep_random(delay_min, delay_max)
            state, data = self.MusinsaManager.scrap_id_musinsa_page(page=page, brand_list=brand_list)
            if(state):
                for product in data:
                    self.DBManager._musinsa_insert_id_musinsa(product=product)

                toc = time.time()
                print("[SneakersManager] : Musinsa id 스크랩 중 (%d page) [%.0fs]" %(page, toc-tic))    

                page = page + 1
            else:
                break

        toc = time.time()
        print("[SneakersManager] : Musinsa id 스크랩 완료되었습니다. [%.1fmin]"%((toc-tic)/60))
    
    def scrap_musinsa_price(self, id_start=1, batch=50, delay_min=0.6, delay_max=0.8):
        print("[SneakersManager] : musinsa 상품정보 및 가격 스크랩 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='musinsa')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._musinsa_select_id_musinsa(id_start=id_start, id_end=id_end)

            for (id, id_musinsa) in data:
                sleep_random(delay_min, delay_max)
                state, data = self.MusinsaManager.scrap_price(id_musinsa=id_musinsa)
                if(state):
                    self.DBManager._musinsa_update_product(product=data, id_musinsa=id_musinsa)
            
            toc = time.time()
            print("[SneakersManager] : musinsa 상품정보 및 가격 스크랩 중 (%4d/%4d) [%.0fs]"%(id_end, cnt_total, toc-tic))

            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch
        
        toc = time.time()
        print("[SneakersManager] : musinsa 스크랩 완료되었습니다. %.1fmin"%((toc-tic)/60))

    def update_musinsa_report(self, id_start=1, batch=40):
        print("[SneakersManager] : musinsa 가격 정보 레포트 업데이트 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='musinsa')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._musinsa_select_price(id_start=id_start, id_end=id_end)

            for (id, model_no, id_musinsa, price_sale, price_discount) in data:
                self.DBManager._sneakers_price_update_musinsa_price(model_no=model_no, price_sale_musinsa=price_sale, price_discount_musinsa=price_discount, id_musinsa=id_musinsa)
            
            toc = time.time()
            print("[SneakersManager] : musinsa 상품정보 및 가격 스크랩 중 (%4d/%4d) [%.0fs]"%(id_end, cnt_total, toc-tic))

            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch
        
        toc = time.time()
        print("[SneakersManager] : musinsa 스크랩 완료되었습니다. %.1fmin"%((toc-tic)/60))
        



    ##### 임시
    def export_common_product_musinsa_stockx(self):
        data = self.DBManager._fetch_musinsa_stockx_product(option_pandas=False)
        for (brand, model_no, product_name, urlkey) in data:
            self.DBManager._sneakers_insert_productinfo(brand=brand, model_no=model_no, product_name=product_name, urlkey=urlkey)

    def update_sneakers_price_model_no(self, id_start=1, batch=200):
        # 1. stockx에서 batch 단위로 urlkey, model_no 뽑는다.
        # 2. urlkey 매칭
        # 3. model_no 비어있으면 업데이트
        print("[SneakersManager] : model_no 업데이트 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='stockx')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._stockx_select_urlkey_NULL_batch(id_start=id_start, id_end=id_end)

            for (id, urlkey, model_no) in data:
                # 매칭 없이 걍 업데이트 해버릴까?
                self.DBManager._sneakers_price_update_model_no_from_urlkey(model_no=model_no, urlkey=urlkey)

            toc = time.time()
            print("[SneakersManager] : model_no 업데이트중(%4d/%4d) [%.1fmin]"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

        toc = time.time()
        print("[SneakersManager] : model_no 업데이트 완료되었습니다. [%.0fmin]"%((toc-tic)/60))


    def scrap_kream_price(self, id_start=1, delay_min = 0.4, delay_max=0.5):
        data = self.DBManager._sneakers_price_select_distinct_urlkey()
        cnt_total = len(data)

        tic = time.time()
        for index, urlkey in enumerate(data):
            if(index<id_start-1):
                continue

            # 3. 사이즈 별로
            data_batch = self.DBManager._sneakers_price_select_all_in_urlkey(urlkey=urlkey[0])
            for item in data_batch:

                if(item['size_kream_mm'] == '' or item['id_kream'] == None):
                    continue
                sleep_random(delay_min, delay_max)
                state_kream, data_kream = self.KreamManager.scrap_price(id_kream=item['id_kream'], size_mm=item['size_kream_mm'], size_us=item['size_kream_us'])
                if(state_kream):
                    self.DBManager._sneakers_price_update_price_kream(id_kream=item['id_kream'], size_kream_mm=item['size_kream_mm'], size_kream_us=item['size_kream_us'], price_buy=data_kream['price_buy'], price_sell=data_kream['price_sell'], price_recent=data_kream['price_recent'])

            toc = time.time()
            print("[SneakersManager] : Kream 가격 스크랩 완료(%s) (%d/%d) [%.1fmin]"%(urlkey[0], index+1, cnt_total, (toc-tic)/60))
    ## stockx 가격 scrap 만들자.


if __name__ == '__main__':
    SneakersManager = SneakersManager()
    
    # SneakersManager.scrap_product()
#
    # SneakersManager.scrap_price(id_start=317, delay_min=0.8, delay_max=1.0)

    # SneakersManager.export_report_price()


    # SneakersManager.scrap_musinsa_product()

    SneakersManager.tmp()

    # SneakersManager.export_report_price()