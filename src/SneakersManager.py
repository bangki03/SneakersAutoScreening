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
    def update_product(self):
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
                    self.DBManager.sneakers_price_update_product(market='stockx', query_type='INSERT', product=item)
                    toc=time.time()
                print("[SneakersManager] : 사이즈 스크랩 및 상품 등록 중 (%d/%d) [%.1fmin]" %(index+1, len(data_filtered), (toc-tic)/60))    


        print("[SneakersManager] : stockx 상품 등록 완료하였습니다.")

    ### 동작 2. 가격 업데이트
    def update_price(self, id_start=1):
        print("[SneakersManager] : 가격 scrap 시작합니다.")

        list_model_no = self.DBManager.sneakers_price_fetch_model_no()
        cnt_total = len(list_model_no)

        tic=time.time()
        for index, product in enumerate(list_model_no):
            if(index<id_start-1):
                continue

            data = self.DBManager.sneakers_price_fetch_product_model_no(model_no=product['model_no'])
            registered_at = self.check_market_registered(data)

            if(registered_at['stockx'] and registered_at['kream'] and registered_at['musinsa']):
                self.update_price_market(market='stockx', data=data)
                self.update_price_market(market='kream', data=data)
                self.update_price_market(market='musinsa', data=data)

                toc=time.time()
                print("[SneakersManager] : (%s-%s)가격 스크랩 완료(stockx, kream, musinsa) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))
            
            elif(registered_at['stockx'] and registered_at['kream']):
                self.update_price_market(market='stockx', data=data)
                self.update_price_market(market='kream', data=data)

                toc=time.time()
                print("[SneakersManager] : (%s-%s)가격 스크랩 완료(stockx, kream) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))
            
            elif(registered_at['kream'] and registered_at['musinsa']):
                self.update_price_market(market='kream', data=data)
                self.update_price_market(market='musinsa', data=data)

                toc=time.time()
                print("[SneakersManager] : (%s-%s)가격 스크랩 완료(kream, musinsa) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))

            elif(registered_at['stockx'] and registered_at['musinsa']):
                self.update_price_market(market='stockx', data=data)
                self.update_price_market(market='musinsa', data=data)

                toc=time.time()
                print("[SneakersManager] : (%s-%s)가격 스크랩 완료(stockx, musinsa) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))

            # elif(registered_at['stockx']):
            #     self.update_price_market(market='stockx', data=data)

            #     toc=time.time()
            #     print("[SneakersManager] : (%s-%s)가격 스크랩 완료(stockx) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))

            # elif(registered_at['kream']):
            #     self.update_price_market(market='kream', data=data)

            #     toc=time.time()
            #     print("[SneakersManager] : (%s-%s)가격 스크랩 완료(kream) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))

            # elif(registered_at['musinsa']):
            #     self.update_price_market(market='musinsa', data=data)

            #     toc=time.time()
            #     print("[SneakersManager] : (%s-%s)가격 스크랩 완료(musinsa) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))

            else:
                toc=time.time()
                print("[SneakersManager] : (%s-%s)가격 스크랩 패스(No Market) (%d/%d) [%.1fmin]"%(product['brand'], product['model_no'], index+1, cnt_total, (toc-tic)/60))
        
        print("[SneakersManager] : 가격 등록 완료하였습니다.")


    def update_price_market(self, market, data):
        if(market=='stockx'):
            state, data_stockx = self.StockXManager.scrap_price(urlkey=data[0]['urlkey'])
            if(state):
                for item_stockx in data_stockx:
                    item_stockx['urlkey'] = data[0]['urlkey']
                    self.DBManager.sneakers_price_update_price(market='stockx', product=item_stockx)
        elif(market=='kream'):
            for item in data:
                state = self.KreamManager.scrap_price(item)
                if(state):
                    self.DBManager.sneakers_price_update_price(market='kream', product=item)
        elif(market=='musinsa'):
            id_musinsa = data[0]['id_musinsa']
            state, data_musinsa = self.MusinsaManager.scrap_price(id_musinsa=id_musinsa)
            if(state):
                self.DBManager.sneakers_price_update_price(market='musinsa', product=data_musinsa)



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
        if(data[0]['urlkey'] != None):
            registered_at['stockx'] = True

        

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


size_LUT = [
    {'brand': 'nike',
     'LUT': [
        {'mm': '170', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'10.5C'},
        {'mm': '175', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'11C'},
        {'mm': '180', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'11.5C'},
        {'mm': '185', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'12C'},
        {'mm': '190', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'12.5C'},
        {'mm': '195', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'13C'},
        {'mm': '195', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'13.5C'},
        {'mm': '200', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'1Y',    'US_K' :'', 'US_C' :''},
        {'mm': '205', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'1.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '210', 'US': '',     'US_M': '',     'US_W': '4W',   'US_Y':'2Y',    'US_K' :'', 'US_C' :''},
        {'mm': '215', 'US': '2.5',  'US_M': '2.5M', 'US_W': '4.5W', 'US_Y':'2.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '220', 'US': '3',    'US_M': '3M',   'US_W': '5W',   'US_Y':'3Y',    'US_K' :'', 'US_C' :''},
        {'mm': '225', 'US': '3.5',  'US_M': '3.5M', 'US_W': '5.5W', 'US_Y':'3.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '230', 'US': '4',    'US_M': '4M',   'US_W': '6W',   'US_Y':'4Y',    'US_K' :'', 'US_C' :''},
        {'mm': '235', 'US': '4.5',  'US_M': '4.5M', 'US_W': '6.5W', 'US_Y':'4.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '235', 'US': '5',    'US_M': '5M',   'US_W': '6.5W', 'US_Y':'5Y',    'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '5.5',  'US_M': '5.5M', 'US_W': '7W',   'US_Y':'5.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '6',    'US_M': '6M',   'US_W': '7W',   'US_Y':'6Y',    'US_K' :'', 'US_C' :''},
        {'mm': '245', 'US': '6.5',  'US_M': '6.5M', 'US_W': '7.5W', 'US_Y':'6.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '250', 'US': '7',    'US_M': '7M',   'US_W': '8W',   'US_Y':'7Y',    'US_K' :'', 'US_C' :''},
        {'mm': '255', 'US': '7.5',  'US_M': '7.5M', 'US_W': '8.5W', 'US_Y':'7.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '260', 'US': '8',    'US_M': '8M',   'US_W': '9W',   'US_Y':'8Y',    'US_K' :'', 'US_C' :''},
        {'mm': '265', 'US': '8.5',  'US_M': '8.5M', 'US_W': '9.5W', 'US_Y':'8.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '270', 'US': '9',    'US_M': '9M',   'US_W': '10W',  'US_Y':'9Y',    'US_K' :'', 'US_C' :''},
        {'mm': '275', 'US': '9.5',  'US_M': '9.5M', 'US_W': '10.5W','US_Y':'9.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '280', 'US': '10',   'US_M': '10M',  'US_W': '11W',  'US_Y':'10Y',   'US_K' :'', 'US_C' :''},
        {'mm': '285', 'US': '10.5', 'US_M': '10.5M','US_W': '11.5W','US_Y':'10.5Y', 'US_K' :'', 'US_C' :''},
        {'mm': '290', 'US': '11',   'US_M': '11M',  'US_W': '12W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '295', 'US': '11.5', 'US_M': '11.5M','US_W': '12.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '300', 'US': '12',   'US_M': '12M',  'US_W': '13W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '305', 'US': '12.5', 'US_M': '12.5M','US_W': '13.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '310', 'US': '13',   'US_M': '13M',  'US_W': '14W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '315', 'US': '13.5', 'US_M': '13.5M','US_W': '14.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '320', 'US': '14',   'US_M': '14M',  'US_W': '15W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '325', 'US': '14.5', 'US_M': '14.5M','US_W': '15.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '330', 'US': '15',   'US_M': '15M',  'US_W': '16W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '335', 'US': '15.5', 'US_M': '15.5M','US_W': '16.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '340', 'US': '16',   'US_M': '16M',  'US_W': '17W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '345', 'US': '16.5', 'US_M': '16.5M','US_W': '17.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '350', 'US': '17',   'US_M': '17M',  'US_W': '18W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '355', 'US': '17.5', 'US_M': '17.5M','US_W': '18.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '360', 'US': '18',   'US_M': '18M',  'US_W': '19W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '365', 'US': '18.5', 'US_M': '18.5M','US_W': '19.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '370', 'US': '19',   'US_M': '19M',  'US_W': '20W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '375', 'US': '19.5', 'US_M': '19.5M','US_W': '20.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '380', 'US': '20',   'US_M': '20M',  'US_W': '21W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '385', 'US': '20.5', 'US_M': '20.5M','US_W': '21.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '390', 'US': '21',   'US_M': '21M',  'US_W': '22W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '395', 'US': '21.5', 'US_M': '21.5M','US_W': '22.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '400', 'US': '22',   'US_M': '22M',  'US_W': '23W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
     ]},
    {'brand': 'jordan',
     'LUT': [
        {'mm': '170', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'10.5C'},
        {'mm': '175', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'11C'},
        {'mm': '180', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'11.5C'},
        {'mm': '185', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'12C'},
        {'mm': '190', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'12.5C'},
        {'mm': '195', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'13C'},
        {'mm': '195', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'',      'US_K' :'', 'US_C' :'13.5C'},
        {'mm': '200', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'1Y',    'US_K' :'', 'US_C' :''},
        {'mm': '205', 'US': '',     'US_M': '',     'US_W': '',     'US_Y':'1.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '210', 'US': '',     'US_M': '',     'US_W': '4W',   'US_Y':'2Y',    'US_K' :'', 'US_C' :''},
        {'mm': '215', 'US': '2.5',  'US_M': '2.5M', 'US_W': '4.5W', 'US_Y':'2.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '220', 'US': '3',    'US_M': '3M',   'US_W': '5W',   'US_Y':'3Y',    'US_K' :'', 'US_C' :''},
        {'mm': '225', 'US': '3.5',  'US_M': '3.5M', 'US_W': '5.5W', 'US_Y':'3.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '230', 'US': '4',    'US_M': '4M',   'US_W': '6W',   'US_Y':'4Y',    'US_K' :'', 'US_C' :''},
        {'mm': '235', 'US': '4.5',  'US_M': '4.5M', 'US_W': '6.5W', 'US_Y':'4.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '235', 'US': '5',    'US_M': '5M',   'US_W': '6.5W', 'US_Y':'5Y',    'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '5.5',  'US_M': '5.5M', 'US_W': '7W',   'US_Y':'5.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '6',    'US_M': '6M',   'US_W': '7W',   'US_Y':'6Y',    'US_K' :'', 'US_C' :''},
        {'mm': '245', 'US': '6.5',  'US_M': '6.5M', 'US_W': '7.5W', 'US_Y':'6.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '250', 'US': '7',    'US_M': '7M',   'US_W': '8W',   'US_Y':'7Y',    'US_K' :'', 'US_C' :''},
        {'mm': '255', 'US': '7.5',  'US_M': '7.5M', 'US_W': '8.5W', 'US_Y':'7.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '260', 'US': '8',    'US_M': '8M',   'US_W': '9W',   'US_Y':'8Y',    'US_K' :'', 'US_C' :''},
        {'mm': '265', 'US': '8.5',  'US_M': '8.5M', 'US_W': '9.5W', 'US_Y':'8.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '270', 'US': '9',    'US_M': '9M',   'US_W': '10W',  'US_Y':'9Y',    'US_K' :'', 'US_C' :''},
        {'mm': '275', 'US': '9.5',  'US_M': '9.5M', 'US_W': '10.5W','US_Y':'9.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '280', 'US': '10',   'US_M': '10M',  'US_W': '11W',  'US_Y':'10Y',   'US_K' :'', 'US_C' :''},
        {'mm': '285', 'US': '10.5', 'US_M': '10.5M','US_W': '11.5W','US_Y':'10.5Y', 'US_K' :'', 'US_C' :''},
        {'mm': '290', 'US': '11',   'US_M': '11M',  'US_W': '12W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '295', 'US': '11.5', 'US_M': '11.5M','US_W': '12.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '300', 'US': '12',   'US_M': '12M',  'US_W': '13W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '305', 'US': '12.5', 'US_M': '12.5M','US_W': '13.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '310', 'US': '13',   'US_M': '13M',  'US_W': '14W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '315', 'US': '13.5', 'US_M': '13.5M','US_W': '14.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '320', 'US': '14',   'US_M': '14M',  'US_W': '15W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '325', 'US': '14.5', 'US_M': '14.5M','US_W': '15.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '330', 'US': '15',   'US_M': '15M',  'US_W': '16W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '335', 'US': '15.5', 'US_M': '15.5M','US_W': '16.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '340', 'US': '16',   'US_M': '16M',  'US_W': '17W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '345', 'US': '16.5', 'US_M': '16.5M','US_W': '17.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '350', 'US': '17',   'US_M': '17M',  'US_W': '18W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '355', 'US': '17.5', 'US_M': '17.5M','US_W': '18.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '360', 'US': '18',   'US_M': '18M',  'US_W': '19W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '365', 'US': '18.5', 'US_M': '18.5M','US_W': '19.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '370', 'US': '19',   'US_M': '19M',  'US_W': '20W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '375', 'US': '19.5', 'US_M': '19.5M','US_W': '20.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '380', 'US': '20',   'US_M': '20M',  'US_W': '21W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '385', 'US': '20.5', 'US_M': '20.5M','US_W': '21.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '390', 'US': '21',   'US_M': '21M',  'US_W': '22W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '395', 'US': '21.5', 'US_M': '21.5M','US_W': '22.5W','US_Y':'',      'US_K' :'', 'US_C' :''},
        {'mm': '400', 'US': '22',   'US_M': '22M',  'US_W': '23W',  'US_Y':'',      'US_K' :'', 'US_C' :''},
     ]},
    {'brand': 'adidas',
     'LUT': [
        {'mm': '205', 'US': '2.5',  'US_M': '2.5M', 'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '210', 'US': '3',    'US_M': '3M',   'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '215', 'US': '3.5',  'US_M': '3.5M', 'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '220', 'US': '4',    'US_M': '4M',   'US_W': '5W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '225', 'US': '4.5',  'US_M': '4.5M', 'US_W': '5.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '230', 'US': '5',    'US_M': '5M',   'US_W': '6W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '235', 'US': '5.5',  'US_M': '5.5M', 'US_W': '6.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '6',    'US_M': '6M',   'US_W': '7W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '6',    'US_M': '6M',   'US_W': '7.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '245', 'US': '6.5',  'US_M': '6.5M', 'US_W': '8W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '250', 'US': '7',    'US_M': '7M',   'US_W': '8.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '255', 'US': '7.5',  'US_M': '7.5M', 'US_W': '9W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '260', 'US': '8',    'US_M': '8M',   'US_W': '9.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '265', 'US': '8.5',  'US_M': '8.5M', 'US_W': '10W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '265', 'US': '8.5',  'US_M': '8.5M', 'US_W': '10.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '270', 'US': '9',    'US_M': '9M',   'US_W': '11W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '275', 'US': '9.5',  'US_M': '9.5M', 'US_W': '11.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '280', 'US': '10',   'US_M': '10M',  'US_W': '12W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '285', 'US': '10.5', 'US_M': '10.5M','US_W': '12.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '290', 'US': '11',   'US_M': '11M',  'US_W': '13W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '295', 'US': '11.5', 'US_M': '11.5M','US_W': '13.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '295', 'US': '11.5', 'US_M': '11.5M','US_W': '14W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '300', 'US': '12',   'US_M': '12M',  'US_W': '14.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '305', 'US': '12.5', 'US_M': '12.5M','US_W': '15W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '310', 'US': '13',   'US_M': '13M',  'US_W': '15.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '315', 'US': '13.5', 'US_M': '13.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '320', 'US': '14',   'US_M': '14M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '325', 'US': '14.5', 'US_M': '14.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '330', 'US': '15',   'US_M': '15M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '335', 'US': '15.5', 'US_M': '15.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '340', 'US': '16',   'US_M': '16M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '345', 'US': '16.5', 'US_M': '16.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '350', 'US': '17',   'US_M': '17M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '355', 'US': '17.5', 'US_M': '17.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '360', 'US': '18',   'US_M': '18M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
     ]},
    {'brand': 'new balance',
     'LUT': [
        {'mm': '205', 'US': '2.5',  'US_M': '2.5M', 'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '210', 'US': '3',    'US_M': '3M',   'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '215', 'US': '3.5',  'US_M': '3.5M', 'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '220', 'US': '4',    'US_M': '4M',   'US_W': '5W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '225', 'US': '4.5',  'US_M': '4.5M', 'US_W': '5.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '230', 'US': '5',    'US_M': '5M',   'US_W': '6W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '235', 'US': '5.5',  'US_M': '5.5M', 'US_W': '6.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '6',    'US_M': '6M',   'US_W': '7W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '6',    'US_M': '6M',   'US_W': '7.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '245', 'US': '6.5',  'US_M': '6.5M', 'US_W': '8W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '250', 'US': '7',    'US_M': '7M',   'US_W': '8.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '255', 'US': '7.5',  'US_M': '7.5M', 'US_W': '9W',       'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '260', 'US': '8',    'US_M': '8M',   'US_W': '9.5W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '265', 'US': '8.5',  'US_M': '8.5M', 'US_W': '10W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '265', 'US': '8.5',  'US_M': '8.5M', 'US_W': '10.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '270', 'US': '9',    'US_M': '9M',   'US_W': '11W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '275', 'US': '9.5',  'US_M': '9.5M', 'US_W': '11.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '280', 'US': '10',   'US_M': '10M',  'US_W': '12W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '285', 'US': '10.5', 'US_M': '10.5M','US_W': '12.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '290', 'US': '11',   'US_M': '11M',  'US_W': '13W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '295', 'US': '11.5', 'US_M': '11.5M','US_W': '13.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '295', 'US': '11.5', 'US_M': '11.5M','US_W': '14W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '300', 'US': '12',   'US_M': '12M',  'US_W': '14.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '305', 'US': '12.5', 'US_M': '12.5M','US_W': '15W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '310', 'US': '13',   'US_M': '13M',  'US_W': '15.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '315', 'US': '13.5', 'US_M': '13.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '320', 'US': '14',   'US_M': '14M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '325', 'US': '14.5', 'US_M': '14.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '330', 'US': '15',   'US_M': '15M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '335', 'US': '15.5', 'US_M': '15.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '340', 'US': '16',   'US_M': '16M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '345', 'US': '16.5', 'US_M': '16.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '350', 'US': '17',   'US_M': '17M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '355', 'US': '17.5', 'US_M': '17.5M','US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '360', 'US': '18',   'US_M': '18M',  'US_W': '',         'US_Y':'',  'US_K' :'', 'US_C' :''},
     ]},
    {'brand': 'vans',
     'LUT': [
        {'mm': '215', 'US': '3.5', 'US_M': '3.5M',  'US_W': '5W',      'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '220', 'US': '4',   'US_M': '4M',    'US_W': '5.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '225', 'US': '4.5', 'US_M': '4.5M',  'US_W': '6W',      'US_Y':'3.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '230', 'US': '5',   'US_M': '5M',    'US_W': '6.5W',    'US_Y':'4Y',  'US_K' :'', 'US_C' :''},
        {'mm': '235', 'US': '5.5', 'US_M': '5.5M',  'US_W': '7W',      'US_Y':'4.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '240', 'US': '6',   'US_M': '6M',    'US_W': '7.5W',    'US_Y':'5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '245', 'US': '6.5', 'US_M': '6.5M',  'US_W': '8W',      'US_Y':'5.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '245', 'US': '6.5', 'US_M': '6.5M',  'US_W': '8W',      'US_Y':'6Y',  'US_K' :'', 'US_C' :''},
        {'mm': '250', 'US': '7',   'US_M': '7M',    'US_W': '8.5W',    'US_Y':'6.5Y',  'US_K' :'', 'US_C' :''},
        {'mm': '255', 'US': '7.5', 'US_M': '7.5M',  'US_W': '9W',      'US_Y':'7Y',  'US_K' :'', 'US_C' :''},
        {'mm': '260', 'US': '8',   'US_M': '8M',    'US_W': '9.5W',    'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '265', 'US': '8.5', 'US_M': '8.5M',  'US_W': '10W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '270', 'US': '9',   'US_M': '9M',    'US_W': '10.5W',   'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '275', 'US': '9.5', 'US_M': '9.5M',  'US_W': '11W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '280', 'US': '10',  'US_M': '10M',   'US_W': '11.5W',   'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '285', 'US': '10.5','US_M': '10.5M', 'US_W': '12W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '290', 'US': '11',  'US_M': '11M',   'US_W': '12.5W',   'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '295', 'US': '11.5','US_M': '11.5M', 'US_W': '13W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '300', 'US': '12',  'US_M': '12M',   'US_W': '13.5W',   'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '305', 'US': '12.5','US_M': '12.5M', 'US_W': '',        'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '310', 'US': '13',  'US_M': '13M',   'US_W': '14W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '315', 'US': '13.5','US_M': '13.5M', 'US_W': '',        'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '320', 'US': '14',  'US_M': '14M',   'US_W': '14.5W',   'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '325', 'US': '14.5','US_M': '14.5M', 'US_W': '',        'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '330', 'US': '15',  'US_M': '15M',   'US_W': '15W',     'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '335', 'US': '15.5','US_M': '15.5M', 'US_W': '',        'US_Y':'',  'US_K' :'', 'US_C' :''},
        {'mm': '340', 'US': '16',  'US_M': '16M',   'US_W': '15.5W',         'US_Y':'',  'US_K' :'', 'US_C' :''},


     ]},

]
