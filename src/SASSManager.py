from SneakersManager import SneakersManager
from KreamManager import KreamManager
from StockXManager import StockXManager
from MusinsaManager import MusinsaManager
from ReportManager import ReportManager
from DBManager import DBManager

class SASSManager:
    def __init__(self):
        print("[SASSManager]: Welcome! This is Sneakers Auto Screening Systme Manager.")
        print("[SASSManager]: Manager들 세팅 중입니다.")
        
        # Manager들 설정
        self.SneakersManager = SneakersManager()
        self.StockXManager = StockXManager()
        self.DBManager = DBManager()
        self.KreamManager = KreamManager()
        self.StockXManager = StockXManager()
        self.MusinsaManager = MusinsaManager()
        self.ReportManager = ReportManager()

        # 서로에게 co-worker들 알려주는 Sequence
        self.SneakersManager.__setManagers__(StockXManager=self.StockXManager, KreamManager=self.KreamManager, MusinsaManager=self.MusinsaManager, DBManager=self.DBManager, ReportManager=self.ReportManager)
        self.StockXManager.__setManagers__(SneakersManager=self.SneakersManager, KreamManager=self.KreamManager, MusinsaManager=self.MusinsaManager, DBManager=self.DBManager, ReportManager=self.ReportManager)
        self.KreamManager.__setManagers__(SneakersManager=self.SneakersManager, StockXManager=self.StockXManager, MusinsaManager=self.MusinsaManager, DBManager=self.DBManager, ReportManager=self.ReportManager)
        self.MusinsaManager.__setManagers__(SneakersManager=self.SneakersManager, StockXManager=self.StockXManager, KreamManager=self.KreamManager, DBManager=self.DBManager, ReportManager=self.ReportManager)
        self.DBManager.__setManagers__(SneakersManager=self.SneakersManager, StockXManager=self.StockXManager, KreamManager=self.KreamManager, MusinsaManager=self.MusinsaManager, ReportManager=self.ReportManager)
        self.ReportManager.__setManagers__(SneakersManager=self.SneakersManager, StockXManager=self.StockXManager, KreamManager=self.KreamManager, MusinsaManager=self.MusinsaManager, DBManager=self.DBManager)
        
        print("[SASSManager]: 준비 완료되었습니다.")

    def __run__(self):
        ## [To Do] : Console Input Mode 개발
        print("[SASSManager]: 무엇을 도와드릴까요?")




    # 동작1. 상품 업데이트 (전체)
    def _update_product_all(self):
        # self._update_product_stockx()
        # self._update_product_musinsa()
        # self._update_product_kream()
        pass
        

    # 동작1-1. 상품 업데이트 (sneakers)
    def _update_product_sneakers(self):
        self.SneakersManager.update_product()

    # 동작1-2. 상품 업데이트 (stockx)
    def _update_product_stockx(self):
        # self.StockXManager.update_product(table='stockx')
        self.StockXManager.update_product(table='sneakers_price')
        
    # 동작1-3. 상품 업데이트 (kream)
    def _update_product_kream(self):
        self.KreamManager.update_product(table='kream')
        self.KreamManager.update_product(table='sneakers_price')
        
    # 동작1-4. 상품 업데이트 (musinsa)
    def _update_product_musinsa(self):
        self.MusinsaManager.update_product(table='musinsa')
        self.MusinsaManager.update_product(table='sneakers_price')


    # 동작2. 가격 업데이트 (전체)
    def _update_price_all(self, id_start):
        self.SneakersManager.update_price(id_start=id_start)

    # 동작2-1. 가격 업데이트 (stockx)
    def _update_price_stockx(self, id_start=1):
        self.StockXManager.update_price(id_start=id_start)

    # 동작2-2. 가격 업데이트 (kream)
    def _update_price_kream(self, id_start=1):
        self.KreamManager.update_price(id_start=id_start)
        

    # 동작2-3. 가격 업데이트 (musinsa)
    def _update_price_musinsa(self, id_start=1):
        self.MusinsaManager.update_price(id_start=id_start)
        


    # 동작 10. Report 출력
    def _report_sneakers_price(self):
        self.ReportManager.Export_table(table='sneakers_price')

    
if __name__ == '__main__':
    SASSManager = SASSManager()

    ### 상품 업데이트 ###
    # SASSManager._update_product_sneakers()      # 검증 완료
    # SASSManager._update_product_musinsa()       # to_musinsa / musinsa to sneakers_price 둘 다 검증 완료.
    # SASSManager._update_product_kream()
    # SASSManager._update_product_stockx()     

    
    ### 가격 업데이트 ###
    
    # SASSManager._update_price_all(id_start=711)  
    # SASSManager._update_price_stockx(id_start=1155)
    # SASSManager._update_price_kream(id_start=2412)
    # SASSManager._update_price_musinsa(id_start=55)


    ### 레포트 ###
    SASSManager._report_sneakers_price()



