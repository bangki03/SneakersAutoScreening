from KreamManager import KreamManager
from StockXManager import StockXManager
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
        self.ReportManager = ReportManager()

        ### SETTING ###
        self.brand_list = ['Nike', 'Jordan', 'Adidas', 'New Balance']

    ### 기능 1) 상품 스크랩
    def scrap_product(self):
        self.scrap_stockx_product(delay_min=0.2, delay_max=0.5, brand_list=self.brand_list)
        self.scrap_kream_product(delay_min=0.2, delay_max=0.5)
        self.scrap_stockx_model_no(id_start=1, batch=50, delay_min=1.0, delay_max=1.2)        ## 얘가 웰케 403 걸리지
        self.export_common_product()
        self.scrap_stockx_size(id_start=1, batch=50, delay_min=0.8, delay_max=1.2)
        self.fill_size_estimated_mm(id_start=1, batch=200)
        self.match_kream_size(id_start=1, batch=200)
        self.match_id_kream()
        
    ### 기능 2) 가격 스크랩
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

    ### 기능 3) Report 발행
    def export_report_price(self):
        self.ReportManager.export_report_price()

    ##### 기능 1 관련 함수 #############################################################################################################################################################################
    def scrap_stockx_product(self, brand_list, delay_min=0.2, delay_max=0.5):
        print("[SneakersManager] : StockX 상품 스크랩 시작합니다.")
        page = 1
        tic = time.time()
        while(1) :
            sleep_random(delay_min, delay_max)
            state, data = self.StockXManager.scrap_productlist_page(page=page, brand_list=brand_list)
            if(state):
                for product in data:
                    self.DBManager._stockx_insert_productinfo(product=product)

                toc = time.time()
                print("[SneakersManager] : StockX 상품 스크랩 중 (%d page) [%.0fs]" %(page, toc-tic))    

                page = page + 1
            else:
                break

        toc = time.time()
        print("[SneakersManager] : StockX 상품 스크랩 완료되었습니다. [%.1fmin]"%((toc-tic)/60))

    def scrap_kream_product(self, delay_min=0.2, delay_max=0.5):
        print("[SneakersManager] : kream 상품 스크랩 시작합니다.")
        page = 1
        tic = time.time()
        while(1) :
            sleep_random(delay_min, delay_max)
            state, data = self.KreamManager.scrap_productlist_page(page=page, brand_list=self.brand_list)
            if(state):
                for product in data:
                    self.DBManager._kream_insert_productinfo(product=product)
                
                toc = time.time()
                print("[SneakersManager] : kream 상품 스크랩 중 (%d page) [%.0fs]" %(page, toc-tic))
                
                page = page + 1
            else:
                break
        
        toc = time.time()
        print("[SneakersManager] : Kream 상품 스크랩 완료되었습니다. %.1fmin"%((toc-tic)/60))

    def scrap_stockx_model_no(self, id_start=1, batch=50, delay_min=0.2, delay_max=0.5):
        print("[SneakersManager] : stockx 모델명 스크랩 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='stockx')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._stockx_select_urlkey(id_start=id_start, id_end=id_end)

            for (id, urlkey) in data:
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
        self.ReportManager.export_report_proudct()  # sneakers DB는 여기서 임시 레포트만 뽑지, DB 축적은 아래에서 한다.

        data = self.DBManager._fetch_sneakers_product(option_pandas=False)
        for (brand, model_no, product_name, urlkey) in data:
            self.DBManager._sneakers_insert_productinfo(brand=brand, model_no=model_no, product_name=product_name, urlkey=urlkey)

    def scrap_stockx_size(self, id_start=1, batch=50, delay_min=0.5, delay_max=0.8):
        print("[SneakersManager] : StockX 사이즈 스크랩 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='sneakers')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._sneakers_select_all(id_start=id_start, id_end=id_end)

            for (id, brand, model_no, product_name, urlkey) in data:
                sleep_random(delay_min, delay_max)
                state, data = self.StockXManager.scrap_size(urlkey=urlkey)
                if(state):
                    for item in data:
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

    def fill_size_estimated_mm(self, id_start=1, batch=500):
        print("[SneakersManager] : StockX 사이즈(US) -> 예상 사이즈(mm) 변환 시작합니다.")
        cnt_total = self.DBManager._table_count_total(table='sneakers_price')

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self.DBManager._sneakers_price_select_size_stockx(id_start=id_start, id_end=id_end)

            ## 처리
            for (id, brand, model_no, size_stockx, urlkey) in data:
                size_estimated_mm = self._convert_size_US2mm(brand=brand, size_US=size_stockx)
                self.DBManager._sneakers_price_update_size_estimated_mm(brand=brand, model_no=model_no, size_stockx=size_stockx, size_estimated_mm=size_estimated_mm)
            
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
        if(brand == 'Nike' or brand == 'Jordan'):
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
                    print(size_US)
                return ''
        elif(brand == 'adidas' or brand == 'New Balance'):
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
                    print(size_US)
                return ''
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

    def match_id_kream(self):
        print("[SneakersManager] : id_kream 매칭 시작합니다.")
        data = self.DBManager._kream_select_distict_id_kream_model_no()

        tic = time.time()
        for (id_kream, model_no) in data:
            self.DBManager._sneakers_price_update_id_kream(model_no=model_no, id_kream=id_kream)

        toc = time.time()
        print("[SneakersManager] : id_kream 매칭 완료하였습니다. [%.1fmin]"%((toc-tic)/60))




    ##### 기능 1 관련 함수 #############################################################################################################################################################################



if __name__ == '__main__':
    SneakersManager = SneakersManager()
    
    # SneakersManager.scrap_product()

    # SneakersManager.scrap_price(id_start=159, delay_min=0.9, delay_max=1.0)

    # SneakersManager.export_report_price()