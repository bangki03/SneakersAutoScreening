from DBManager import DBManager
from Lib_else import get_date

class ReportManager:
    def __init__(self):
        self.date = get_date()

        
    def __setManagers__(self, SneakersManager, StockXManager, KreamManager, MusinsaManager, DBManager):
        self.SneakersManager = SneakersManager
        self.StockXManager = StockXManager
        self.KreamManager = KreamManager
        self.MusinsaManager = MusinsaManager
        self.DBManager = DBManager
        




    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 1. 로그
    #######################################################################################################################################
    #######################################################################################################################################
    def log_text(self):
        pass


    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 2. 레포트
    #######################################################################################################################################
    #######################################################################################################################################
    def Export_table(self, table):
        if(table == 'sneakers_price'):
            pandas_price = self.DBManager.table_fetch(table=table, option_pandas=True)
            filename = 'report\[%s][sneakers_price].csv'%(self.date)
            pandas_price.to_csv(filename, index=False)
        elif(table == 'stockx'):
            pandas_price = self.DBManager.table_fetch(table=table, option_pandas=True)
            filename = 'report\[%s][stockx].csv'%(self.date)
            pandas_price.to_csv(filename, index=False)
        elif(table == 'kream'):
            pandas_price = self.DBManager.table_fetch(table=table, option_pandas=True)
            filename = 'report\[%s][kream].csv'%(self.date)
            pandas_price.to_csv(filename, index=False)
        elif(table == 'musinsa'):
            pandas_price = self.DBManager.table_fetch(table=table, option_pandas=True)
            filename = 'report\[%s][musinsa].csv'%(self.date)
            pandas_price.to_csv(filename, index=False)
        else:
            print("No Table named(%s)"%(table))
            
            
        
if __name__ == '__main__':
    ReportManager = ReportManager()
    ReportManager




    