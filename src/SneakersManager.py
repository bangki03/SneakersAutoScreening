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
        pass

    def __setManagers__(self, StockXManager, KreamManager, MusinsaManager, DBManager, ReportManager):
        self.StockXManager = StockXManager
        self.KreamManager = KreamManager
        self.MusinsaManager = MusinsaManager
        self.DBManager = DBManager
        self.ReportManager = ReportManager


    ### 동작 1. 상품 업데이트
    def update_product(self, batch=200):
        print("[SneakersManager] : stockx 상품 등록 시작합니다.")
        data = self.DBManager.stockx_fetch_product()
        
        data_filtered = [item for item in data if self.DBManager.sneakers_price_check_product_need_update(market='stockx', product=item)]

        print("[SneakersManager] : 신규 상품 %d개 등록합니다."%(len(data_filtered)))
        
        tic = time.time()
        for index, item in enumerate(data_filtered):
            sleep_random(0.2, 0.5)
            state, data_size = self.StockXManager.scrap_size(urlkey=item['urlkey'])

            if(state):
                for item_size in data_size:
                    item.update(item_size)
                    self._convert_size_US2mm(item)
                    self.DBManager.sneakers_price_update_product(market='stockx', product=item)
                    toc=time.time()
                print("[SneakersManager] : 사이즈 스크랩 및 상품 등록 중 (%d/%d) [%.1fmin]" %(index+1, len(data_filtered), (toc-tic)/60))    


        print("[SneakersManager] : stockx 상품 등록 완료하였습니다.")

    ### 동작 2. 가격 업데이트
    def update_price(self, id_start=1, batch=200):
        print("[SneakersManager] : 가격 scrap 시작합니다.")

        list_urlkey = self.DBManager.sneakers_price_fetch_urlkey()
        cnt_total = len(list_urlkey)

        tic=time.time()
        for index, product in enumerate(list_urlkey):
            if(index<id_start-1):
                continue

            data = self.DBManager.sneakers_price_fetch_product_urlkey(urlkey=product['urlkey'])
            registered_at = self.check_market_registered(data)

            if(registered_at['kream']):
                for item in data:
                    state = self.KreamManager.scrap_price(item)
                    if(state):
                        self.DBManager.sneakers_price_update_price(market='kream', product=item)

            if(registered_at['musinsa']):
                id_musinsa = data[0]['id_musinsa']
                state, data_musinsa = self.MusinsaManager.scrap_price(id_musinsa=id_musinsa)
                if(state):
                    self.DBManager.sneakers_price_update_price(market='musinsa', product=data_musinsa)

            if(registered_at['stockx']):
                state, data_stockx = self.StockXManager.scrap_price(urlkey=product['urlkey'])
                if(state):
                    for item_stockx in data_stockx:
                        item_stockx['urlkey'] = product['urlkey']
                        self.DBManager.sneakers_price_update_price(market='stockx', product=item_stockx)
                    
            toc=time.time()
            print("[SneakersManager] : (%s)가격 스크랩 완료(%d/%d) [%.1fmin]"%(item['urlkey'], index+1, cnt_total, (toc-tic)/60))
        
        print("[SneakersManager] : 가격 등록 완료하였습니다.")


    def check_market_registered(self, data):
        registered_at = {
            'stockx' : False,
            'kream' : False,
            'musinsa' : False,
        }
        if(data[0]['id_kream'] != None):
            registered_at['kream'] = True
        if(data[0]['id_musinsa'] != None):
            registered_at['musinsa'] = True
        registered_at['stockx'] = registered_at['kream'] or registered_at['musinsa']

        return registered_at
        

        


    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 1. 상품 업데이트
    #######################################################################################################################################
    #######################################################################################################################################
    





    #######################################################################################################################################
    #######################################################################################################################################
    ### 기타 2. 사이즈 변환 (US → mm)
    #######################################################################################################################################
    #######################################################################################################################################
    
    ### Lv1) 사이즈 변환 ###
    # input : product
    # output : product
    def _convert_size_US2mm(self, product):
        if(product['brand'] == 'nike' or product['brand'] == 'jordan'):
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
                size_tmp = product['size_stockx'].split('/')[0].strip().upper()
                product['size_estimated_mm'] = LUT[size_tmp]
            except:
                if(product['size_stockx'] != None):
                    print("%s : %s"%(product['brand'], product['size_stockx']))
                product['size_estimated_mm'] = ''
        elif(product['brand'] == 'adidas' or product['brand'] == 'new balance'):
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
                product['size_estimated_mm'] = LUT[product['size_stockx']]
            except:
                if(product['size_stockx'] != None):
                    print("%s : %s"%(product['brand'], product['size_stockx']))
                product['size_estimated_mm'] = ''
        elif(product['brand'] == 'vans'):
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
                product['size_estimated_mm'] = LUT[product['size_stockx']]
            except:
                if(product['size_stockx'] != None):
                    print("%s : %s"%(product['brand'], product['size_stockx']))
                product['size_estimated_mm'] = ''
        elif(product['brand'] == 'converse'):
            product['size_estimated_mm'] = None
        else:
            print("No Size LUT for brand %s"%(product['brand']))
            product['size_estimated_mm'] = ''