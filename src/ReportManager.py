from DBManager import DBManager
from Lib_else import get_date

class ReportManager:
    def __init__(self):
        self.DBManager = DBManager()
        self.date = get_date()
        

    def export_report_proudct(self, table):
        if(table == 'kream'):
            pandas_kream = self.DBManager._fetch_kream_product(option_pandas=True)
            filename_kream = 'report\[%s][Item_List][kream].csv'%(self.date)
            pandas_kream.to_csv(filename_kream, index=False)

        elif(table == 'stockx'):
            pandas_stockx = self.DBManager._fetch_stockx_product(option_pandas=True)
            filename_stockx = 'report\[%s][Item_List][stockx].csv'%(self.date)
            pandas_stockx.to_csv(filename_stockx, index=False)

        elif(table == 'musinsa'):
            # pandas_sneakers = self.DBManager._fetch_sneakers_product(option_pandas=True)
            # filename_sneakers = 'report\[%s][Item_List][sneakers].csv'%(self.date)
            # pandas_sneakers.to_csv(filename_sneakers, index=False)
            pass

        elif(table == 'sneakers'):
            pandas_sneakers = self.DBManager._fetch_sneakers_product(option_pandas=True)
            filename_sneakers = 'report\[%s][Item_List][sneakers].csv'%(self.date)
            pandas_sneakers.to_csv(filename_sneakers, index=False)

        
    

        print("[ReportManager] : 상품정보 레포트 발행 완료되었습니다.")

    def export_report_price(self):
        pandas_price = self.DBManager._fetch_sneakers_price(option_pandas=True)
        filename = 'report\[%s][SASS_Price].csv'%(self.date)
        pandas_price.to_csv(filename, index=False)