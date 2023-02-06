import pymysql
import pandas
from Lib_else import get_date
import time

class Analyzer:
    def __init__(self):
        self.con = self.connect_db()
        self.cursor = self.con.cursor()
        self.date = get_date()

    def connect_db(self):
        con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8')

        return con

    ##### 기능 1. (일회성) kream / stockx 공통된 상품 추출 #####
    def select_common_brand_model_no(self):
        self._query_fetch_kream_product()
        self._query_fetch_stockx_product()
        data = self._query_fetch_sneakers_product()
        
        for (brand, model_no, product_name, urlkey) in data:
            self._query_insert_sneakers_product(brand=brand, model_no=model_no, product_name=product_name, urlkey=urlkey)

    ##### 기능 2. (일회성) US 사이즈 -> 예상 mm 사이즈 #####
    def fill_size_estimated_mm(self, batch=500, id_start=1):
        print("[Analyzer] : 예상 Size 변환 시작합니다.")
        cnt_total = self._query_count_total(table="sneakers_price")

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self._query_fetch_size_stockx(table="sneakers_price", id_start=id_start, id_end=id_end)

            ## 처리
            for (id, brand, model_no, size_stockx, urlkey) in data:
                
                size_estimated_mm = self._convert_size_US2mm(brand=brand, size_US=size_stockx)
                self._query_update_size_estimated_mm(brand=brand, model_no=model_no, size_stockx=size_stockx, size_estimated_mm=size_estimated_mm)
            
            toc = time.time()
            print("[Analyzer_Manager] : 처리중(%4d/%4d) - %.0fs"%(id_end, cnt_total, toc-tic))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

    ##### 기능 3. 예상 mm 사이즈 = Kream 사이즈 가져오기 #####
    def update_kream_size(self, batch=500, id_start=1):
        print("[Analyzer] : Kream 사이즈 가져옵니다.")
        cnt_total = self._query_count_total(table="sneakers_price")

        tic = time.time()
        while(1):
            id_end = min(id_start + batch -1, cnt_total)
            data = self._query_fetch_size_estimated(table="sneakers_price", id_start=id_start, id_end=id_end)

            ## 처리
            for (id, brand, model_no, size_stockx, size_estimated) in data:
                
                size_mm, size_us = self._get_kream_size(brand=brand, model_no=model_no, size_stockx=size_stockx, size_estimated=size_estimated)
                self._query_update_size_kream(brand=brand, model_no=model_no, size_stockx=size_stockx, size_estimated_mm=size_estimated, size_mm=size_mm, size_us=size_us)
            
            toc = time.time()
            print("[Analyzer] : 처리중(%4d/%4d) - %.0fmin"%(id_end, cnt_total, (toc-tic)/60))
            # 처리 끝났으면 while 조건 체크
            if(id_end == cnt_total):
                break
            else:
                id_start = id_start + batch

    ##### 기능 3. id_kream 가져오기 #####
    def update_id_kream(self):
        print("[Analyzer] : id_kream 가져옵니다.")
        data = self._query_select_distict_id_kream_model_no_()

        tic = time.time()
        for (id_kream, model_no) in data:
            self._query_update_id_kream(model_no=model_no, id_kream=id_kream)

        toc = time.time()
        print("[Analyzer] : id_kream 완료하였습니다. - %.1fmin"%((toc-tic)/60))


    ##### 기능 4. sneakers_price table 추출 #####
    def export_report(self):
        query = "SELECT brand, model_no, product_name, size_stockx, size_estimated_mm, size_kream_mm, size_kream_us, price_buy_kream, price_sell_kream, price_recent_kream, price_buy_stockx, price_sell_stockx, price_recent_stockx, updated_at FROM sneakers_price"
        result = pandas.read_sql_query(query,self.con)
        filename = 'report\[%s][SASS_Price].csv'%(self.date)
        result.to_csv(filename, index=False)

        print("[Analyzer] : Export Complete(%s)"%(filename))

    ################################################################################################
    ##### 기능 1 관련 함수 #####
    def _query_fetch_kream_product(self):
        query = "SELECT DISTINCT brand, model_no, product_name FROM kream"
        result = pandas.read_sql_query(query,self.con)
        filename = 'report\[%s][Item_List][kream].csv'%(self.date)
        result.to_csv(filename, index=False)

        print("[Analyzer] : Export Complete(%s)"%(filename))

    def _query_fetch_stockx_product(self):
        query = "SELECT DISTINCT brand, model_no, urlkey, product_name FROM stockx"
        result = pandas.read_sql_query(query,self.con)
        filename = 'report\[%s][Item_List][stockx].csv'%(self.date)
        result.to_csv(filename, index=False)

        print("[Analyzer] : Export Complete(%s)"%(filename))

    def _query_fetch_sneakers_product(self):
        query = "SELECT brand, model_no, product_name, urlkey FROM stockx WHERE model_no in (select model_no from kream)"
        result = pandas.read_sql_query(query,self.con)
        filename = 'report\[%s][Item_List][sneakers].csv'%(self.date)
        result.to_csv(filename, index=False)

        print("[Analyzer] : Export Complete(%s)"%(filename))

        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def _query_insert_sneakers_product(self, brand, model_no, product_name, urlkey):
        query = "INSERT INTO sneakers (brand, model_no, product_name, urlkey) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (brand, model_no, product_name, urlkey))
        self.con.commit()

    ################################################################################################
    ##### 기능 2 관련 함수 #####
    def _query_count_total(self, table):
        query = "SELECT COUNT(*) FROM %s"%(table)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        return result[0]
    
    def _query_fetch_size_stockx(self, table, id_start, id_end):
        query = "SELECT id, brand, model_no, size_stockx, urlkey FROM %s WHERE id>%d AND id <%d"%(table, id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data
    
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
        
    def _query_update_size_estimated_mm(self, brand, model_no, size_stockx, size_estimated_mm):
        query = "UPDATE sneakers_price SET size_estimated_mm=%s WHERE brand=%s AND model_no=%s AND size_stockx=%s"
        self.cursor.execute(query, (size_estimated_mm, brand, model_no, size_stockx))

        self.con.commit()

    ################################################################################################
    ##### 기능 3 관련 함수 #####
    def _query_fetch_size_estimated(self, table, id_start, id_end):
        query = "SELECT id, brand, model_no, size_stockx, size_estimated_mm FROM %s WHERE id>%d AND id <%d"%(table, id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
            
        return data

    def _get_kream_size(self, brand, model_no, size_stockx, size_estimated):
        data = self._query_select_size_estimated(brand, model_no, size_estimated)

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

    def _query_select_size_estimated(self, brand, model_no, size_estimated):
        query = "SELECT size_mm, size_us FROM kream WHERE brand=%s AND model_no=%s AND size_mm=%s"
        self.cursor.execute(query, (brand, model_no, size_estimated))

        data = self.cursor.fetchall()
        return data

    def _query_update_size_kream(self, brand, model_no, size_stockx, size_estimated_mm, size_mm, size_us):
        query = "UPDATE sneakers_price SET size_kream_mm=%s, size_kream_us=%s WHERE brand=%s AND model_no=%s AND size_stockx=%s AND size_estimated_mm=%s"
        self.cursor.execute(query, (size_mm, size_us, brand, model_no, size_stockx, size_estimated_mm))

        self.con.commit()

    def _query_select_id_kream(self, model_no):
        query="SELECT id_kream FROM kream WHERE model_no=%s"
        self.cursor.execute(query, (model_no))

        data = self.cursor.fetchall()
        return data[0][0]
    def _query_update_id_kream(self, model_no, id_kream):
        query = "UPDATE sneakers_price SET id_kream=%s WHERE model_no=%s"
        self.cursor.execute(query, (id_kream, model_no))

        self.con.commit()


    ################################################################################################
    ##### 기능 4 관련 함수 #####
    def _query_select_distict_id_kream_model_no_(self):
        query = "SELECT DISTINCT id_kream, model_no FROM kream"
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data





if __name__ == '__main__':
    Analyzer = Analyzer()
    # Analyzer.select_brand_model_no()
    # Analyzer.fill_size_estimated_mm()
    # Analyzer.update_kream_size(id_start=1)
    # Analyzer.update_id_kream()
    Analyzer.export_report()