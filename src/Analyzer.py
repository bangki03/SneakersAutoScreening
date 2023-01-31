import pymysql
import pandas

class Analyzer:
    def __init__(self):
        self.con = self.connect_db()
        self.cursor = self.con.cursor()

    def connect_db(self):
        con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8', cursorclass=pymysql.cursors.D)

        return con

    ############## 브랜드/모델넘버 조합 뽑기 기능(분석용) ##############
    def select_brand_model_no(self, batch=100):
        print("Kream 상품들을 가져옵니다.")
        self._query_fetch_kream_data1()
        print("Stockx 상품들을 가져옵니다.")
        self._query_fetch_stockx_data1()
                
    
    ################################################################################################
    def _query_fetch_kream_data1(self):
        query = "SELECT DISTINCT brand, model_no, id, product_name FROM kream_model"
        result = pandas.read_sql_query(query,self.con)
        result.to_csv(r'kream_상품정보.csv',index=True)

    def _query_fetch_stockx_data1(self):
        query = "SELECT DISTINCT brand, model_no, urlkey, product_name"
        result = pandas.read_sql_query(query,self.con)
        result.to_csv(r'stockx_상품정보.csv',index=True)
    ################################################################################################


if __name__ == '__main__':
    Analyzer = Analyzer()
    Analyzer.select_brand_model_no()
