import pymysql
import pymysql.cursors
import pandas

class DBManager:
    def __init__(self):
        while(True):
            self.username = input("[DBManager]ID를 입력하세요: ")
            self.password= input("[DBManager]Password를 입력하세요: ")
            try:
                self.con = pymysql.connect(host='58.143.128.86', port=33060, user=self.username, password=self.password, db='sneakers', charset='utf8')
                self.cursor = self.con.cursor(pymysql.cursors.DictCursor)
                print("[DBManager]### LOGIN SUCCESS ###")
                break
            except Exception as e:
                print("[DBManager]### LOGIN FAIL ###")
        

    def __setManagers__(self, SneakersManager, StockXManager, KreamManager, MusinsaManager, ReportManager):
        self.SneakersManager = SneakersManager
        self.StockXManager = StockXManager
        self.KreamManager = KreamManager
        self.MusinsaManager = MusinsaManager
        self.ReportManager = ReportManager



    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 1-1. market별 상품 존재 여부 확인
    #######################################################################################################################################
    #######################################################################################################################################
    
    ### 1) stockx 등록 상품인지 확인 ###
    # input : urlkey
    # output : state
    def stockx_check_product_exist(self, product):
        query = "SELECT * from stockx WHERE urlkey=%s"
        self.cursor.execute(query, (product['urlkey']))

        data = self.cursor.fetchall()
        if(len(data)>0):
            return True
        else:
            return False
        

    ### 2) kream 등록 상품인지 확인 ### 
    # input : id_kream, model_no
    # output : state
    def kream_check_product_exist(self, product):
        ### id_kream / model_no 다른 상품 
        query = "SELECT * from kream WHERE id_kream=%s or model_no=%s"
        self.cursor.execute(query, (product['id_kream'], product['model_no']))
        data_both = self.cursor.fetchall()

        ### 본 편 ###
        query = "SELECT * from kream WHERE id_kream=%s and model_no=%s"
        self.cursor.execute(query, (product['id_kream'], product['model_no']))
        data = self.cursor.fetchall()

        if(len(data_both) != len(data)):
            print("[DBManager] : kream 상품 이상 감지(id_kream: %s, model_no: %s)"%(product['id_kream'], product['model_no']))


        if(len(data)>0):
            return True
        else:
            return False

    ### 3) musinsa 등록 상품인지 확인 ###
    # input : id_musinsa
    # output : state
    def musinsa_check_product_exist(self, product):
        ### 본 편 ###
        query = "SELECT * from musinsa WHERE id_musinsa=%s"
        self.cursor.execute(query, (product['id_musinsa']))
        data = self.cursor.fetchall()

        if(len(data)>0):
            return True
        else:
            return False
        


    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 1-2. 각 market 상품 업데이트
    #######################################################################################################################################
    #######################################################################################################################################

    ### 1) stockx 상품 업데이트 ###
    def stockx_update_product(self, product):
        query = "INSERT INTO stockx (brand, product_name, id_stockx, urlkey) VALUES (%s, %s, %s, %s)" 
        self.cursor.execute(query, (product['brand'], product['product_name'], product['id_stockx'], product['urlkey']))

        self.con.commit()
    
    ### 2) kream 상품 업데이트 ###
    def kream_update_product(self, product):
        query = "INSERT INTO kream (brand, model_no, product_name, id_kream, size_mm, size_us) VALUES (%s, %s, %s, %s, %s, %s)" 
        self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['id_kream'], product['size_kream_mm'], product['size_kream_us']))

        self.con.commit()
    
    ### 3) musinsa 상품 업데이트 ###
    def musinsa_update_product(self, product):
        query = "INSERT INTO musinsa (brand, model_no, product_name, id_musinsa, registered) VALUES (%s, %s, %s, %s, False)" 
        self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['id_musinsa']))

        self.con.commit()
    


    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 2-2. sneakers_price 상품 업데이트
    #######################################################################################################################################
    #######################################################################################################################################

    ### 1) 전체 상품 수 읽어오기 ###
    def table_count_total(self, table):
        query = "SELECT COUNT(*) FROM %s"%(table)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        return result[0]

    ### 1) stockx 상품 읽어오기 ###
    def stockx_fetch_product(self):
        query = "SELECT * from stockx WHERE model_no IS NOT NULL"
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    
    ### 2) kream 상품 읽어오기 ###
    def kream_fetch_product(self):        
        query = "SELECT DISTINCT model_no, id_kream from kream WHERE registered IS False AND model_no IS NOT NULL"
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
        
    
    ### 3) musinsa 상품 읽어오기 ###
    def musinsa_fetch_product(self):
        query = "SELECT * from musinsa WHERE registered IS False"
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    
    ### 3) sneakers_price 상품 읽어오기 (kream 업데이트 필요 데이터) ###
    def sneakers_price_fetch_product(self, product):
        query = "SELECT * from sneakers_price WHERE model_no=%s AND id_kream IS NULL"
        self.cursor.execute(query, (product['model_no']))
        data = self.cursor.fetchall()

        return data
    

    ### 4) size_estimated_mm 와 같은 사이즈의 kream 상품 읽어오기 ###
    def kream_fetch_product_size(self, product):
        query = "SELECT * from kream WHERE model_no=%s AND size_kream_mm=%s"
        self.cursor.execute(query, (product['model_no'], product['size_estimated_mm']))
        data = self.cursor.fetchall()

        return data

    ### 2) sneakers_price 상품 등록 여부 확인 (Ver.B : stockx에 있는 모델만 등록.)
    def sneakers_price_check_product_need_update_verB(self, market, product):
        if(market=='stockx'):
            query = "SELECT * from sneakers_price WHERE urlkey=%s"
            self.cursor.execute(query, (product['urlkey']))
            data = self.cursor.fetchall()

            if(len(data)==0):
                return True
            else:
                return False

        elif(market=='kream'):
            query = "SELECT * from sneakers_price WHERE model_no=%s AND id_kream IS NULL"
            self.cursor.execute(query, (product['model_no']))
            data = self.cursor.fetchall()

            if(len(data)>0):
                return True
            else:
                return False

        elif(market=='musinsa'):
            query = "SELECT * from sneakers_price WHERE model_no=%s AND id_musinsa IS NULL"
            self.cursor.execute(query, (product['model_no']))
            data = self.cursor.fetchall()

            if(len(data)>0):
                return True
            else:
                return False
            
        else:
            print("[DBManager] : 존재하지 않는 Market(%s) 입니다."%(market))
            pass


    ### 2) sneakers_price 상품 등록 여부 확인 (Ver.C : kream도 주체 가능. senakers_price에 모델명 없으면 등록..)
    def sneakers_price_check_product_need_update(self, market, product):
        if(market=='stockx'):
            query = "SELECT * from sneakers_price WHERE model_no=%s"
            self.cursor.execute(query, (product['model_no']))
            data = self.cursor.fetchall()

            if(len(data)==0):
                return 'INSERT'
            else:
                query = "SELECT * from sneakers_price WHERE model_no=%s AND urlkey IS NULL"
                self.cursor.execute(query, (product['model_no']))
                data = self.cursor.fetchall()

                if(len(data)>0):
                    return 'UPDATE'
                else:
                    return 'PASS'

        elif(market=='kream'):
            query = "SELECT * from sneakers_price WHERE model_no=%s"
            self.cursor.execute(query, (product['model_no']))
            data = self.cursor.fetchall()

            if(len(data)==0):
                return 'INSERT'
            else:
                query = "SELECT * from sneakers_price WHERE model_no=%s AND id_kream IS NULL"
                self.cursor.execute(query, (product['model_no']))
                data = self.cursor.fetchall()

                if(len(data)>0):
                    return 'UPDATE'
                else:
                    return 'PASS'

        elif(market=='musinsa'):
            query = "SELECT * from sneakers_price WHERE model_no=%s AND id_musinsa IS NULL"
            self.cursor.execute(query, (product['model_no']))
            data = self.cursor.fetchall()

            if(len(data)>0):
                return True
            else:
                return False
            
        else:
            print("[DBManager] : 존재하지 않는 Market(%s) 입니다."%(market))
            pass


    ### 1) stockx 상품 업데이트 ###
    def sneakers_price_update_product(self, market, query_type, product):
        if(market=='stockx'):
            if(query_type=='INSERT'):
                query = "INSERT INTO sneakers_price (brand, model_no, product_name, size_stockx, size_estimated_mm, id_stockx, urlkey) VALUES (%s, %s, %s, %s, %s, %s, %s)" 
                self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['size_stockx'], product['size_estimated_mm'], product['id_stockx'], product['urlkey']))
                
                self.con.commit()
            if(query_type=='UPDATE'):
                query = "UPDATE sneakers_price SET size_stockx=%s, urlkey=%s, id_stockx=%s WHERE model_no=%s AND size_kream_mm=%s AND size_kream_us=%s"
                self.cursor.execute(query, (product['size_stockx'], product['urlkey'], product['id_stockx'], product['model_no'], product['size_kream_mm'], product['size_kream_us']))
                pass

        elif(market=='kream'):
            if(query_type=='INSERT'):
                query = "INSERT INTO sneakers_price (brand, model_no, product_name, size_kream_mm, size_kream_us, id_kream) VALUES (%s, %s, %s, %s, %s, %s)" 
                self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['size_kream_mm'], product['size_kream_us'], product['id_kream']))
                
                self.con.commit()

            if(query_type=='UPDATE'):
                query = "UPDATE sneakers_price SET id_kream=%s, size_kream_mm=%s, size_kream_us=%s  WHERE model_no=%s AND size_estimated_mm=%s" 
                self.cursor.execute(query, (product['id_kream'], product['size_kream_mm'], product['size_kream_us'], product['model_no'], product['size_kream_mm']))
                self.con.commit()

        elif(market=='musinsa'):
            query = "UPDATE sneakers_price SET id_musinsa=%s WHERE model_no=%s" 
            self.cursor.execute(query, (product['id_musinsa'], product['model_no']))
            
            self.con.commit()

            self.musinsa_update_registered(product)

        else:
            print("[DBManager] : 존재하지 않는 Market(%s) 입니다."%(market))
            pass

    ### 2) musinsa 상품 price_sneakers에 등록 시, 업데이트
    def musinsa_update_registered(self, product):
        query = "UPDATE musinsa SET registered=True WHERE model_no=%s"
        self.cursor.execute(query, (product['model_no']))
        self.con.commit()

    def sneakers_price_update_product_id_kream(self, product):
        query = "UPDATE sneakers_price SET id_kream=%s WHERE model_no=%s"
        self.cursor.execute(query, (product['id_kream'], product['model_no']))
        self.con.commit()

    def kream_update_registered(self, product):
        query = "UPDATE kream SET registered=True WHERE model_no=%s"
        self.cursor.execute(query, (product['model_no']))
        self.con.commit()


    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 3. sneakers_price 가격 업데이트
    #######################################################################################################################################
    #######################################################################################################################################

    ### 1) sneakers_price 가격 업데이트
    def sneakers_price_update_price(self, market, product):
        if(market=='stockx'):
            query = "UPDATE sneakers_price SET price_buy_stockx=%s, price_sell_stockx=%s WHERE urlkey=%s AND size_stockx=%s" 
            self.cursor.execute(query, (product['price_buy_stockx'], product['price_sell_stockx'], product['urlkey'], product['size_stockx']))
            
            self.con.commit()
        elif(market=='kream'):
            query = "UPDATE sneakers_price SET price_buy_kream=%s, price_sell_kream=%s, price_recent_kream=%s WHERE id_kream=%s AND size_kream_mm=%s AND size_kream_us=%s" 
            self.cursor.execute(query, (product['price_buy_kream'], product['price_sell_kream'], product['price_recent_kream'], product['id_kream'], product['size_kream_mm'], product['size_kream_us']))
            
            self.con.commit()
        elif(market=='musinsa'):
            query = "UPDATE sneakers_price SET price_sale_musinsa=%s, price_discount_musinsa=%s WHERE id_musinsa=%s" 
            self.cursor.execute(query, (product['price_sale_musinsa'], product['price_discount_musinsa'], product['id_musinsa']))
            
            self.con.commit()
        else:
            print("[DBManager] : 존재하지 않는 Market(%s) 입니다."%(market))
            pass

    ### 2) Distinct model_no (sneakers_price 가격 업데이트 할 때, 모델 단위로 불러오기 위함) ###
    def sneakers_price_fetch_model_no(self):
        query = "SELECT DISTINCT brand, model_no FROM sneakers_price"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        
        return data

    ### 2) Distinct urlkey (stockx 가격 업데이트 필요한 상품군 불러오기 위함) ###
    def sneakers_price_fetch_urlkey(self):
        query = "SELECT DISTINCT urlkey, model_no FROM sneakers_price"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        
        return data
    
    ### 3) Distinct id_kream (kream 가격 업데이트 필요한 상품군 불러오기 위함) ###
    def sneakers_price_fetch_id_kream(self):
        query = "SELECT DISTINCT id_kream from sneakers_price WHERE id_kream IS NOT NULL"
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        return data

    ### 4) Distinct id_musinsa (musinsa 가격 업데이트 필요한 상품군 불러오기 위함) ###
    def sneakers_price_fetch_id_musinsa(self):
        query = "SELECT DISTINCT id_musinsa from sneakers_price WHERE id_musinsa IS NOT NULL"
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        return data
    
    ### 5) 특정 model_no 상품 불러오기 (model_no 단위 상품 가격 업데이트 위함) ###
    def sneakers_price_fetch_product_model_no(self, model_no):
        query = "SELECT * FROM sneakers_price WHERE model_no=%s"
        self.cursor.execute(query, (model_no))
        data = self.cursor.fetchall()

        return data
    
    ### 5) 특정 urlkey 상품 불러오기 (urlkey 단위 상품 가격 업데이트 위함) ###
    def sneakers_price_fetch_product_urlkey(self, urlkey):
        query = "SELECT * FROM sneakers_price WHERE urlkey=%s"
        self.cursor.execute(query, (urlkey))
        data = self.cursor.fetchall()

        return data
    
    ### 6) 특정 id_kream 상품 불러오기 (id_kream 단위 상품 가격 업데이트 위함) ###
    def sneakers_price_fetch_product_id_kream(self, id_kream):
        query = "SELECT * FROM sneakers_price WHERE id_kream=%s"
        self.cursor.execute(query, (id_kream))
        data = self.cursor.fetchall()

        return data
    
    ### 6) 특정 id_kream 상품 불러오기 (id_kream 단위 상품 가격 업데이트 위함) ###
    def kream_fetch_product_id_kream(self, id_kream):
        query = "SELECT * FROM kream WHERE id_kream=%s"
        self.cursor.execute(query, (id_kream))
        data = self.cursor.fetchall()

        return data
    


    def table_fetch(self, table, option_pandas):
        query = "SELECT * FROM %s"%(table)
        if(option_pandas):
            data = pandas.read_sql_query(query, self.con)
            return data
        
    def sneakers_price_fetch_product_report(self, option_pandas):
        query = "SELECT * FROM sneakers_price WHERE NOT(price_buy_kream IS NULL AND price_sell_kream IS NULL AND price_sale_musinsa IS NULL AND price_discount_musinsa IS NULL AND price_buy_stockx IS NULL AND price_sell_stockx IS NULL)"
        if(option_pandas):
            data = pandas.read_sql_query(query, self.con)
            return data




    #######################################################################################################################################
    #######################################################################################################################################
    ### 기타 - 사용자 관리용 기능
    #######################################################################################################################################
    #######################################################################################################################################
    ### 기타) urlkey 의 index 출력 ###
    def _sneakers_price_fetch_index(self, market, key):
        if(market == 'stockx'):
            data = self.sneakers_price_fetch_urlkey()
            return [index for index, item in enumerate(data) if item['urlkey'] == key][0] + 1
        
        elif(market == 'kream'):
            data = self.sneakers_price_fetch_id_kream()
            return [index for index, item in enumerate(data) if item['id_kream'] == key][0] + 1
        
        elif(market == 'musinsa'):
            data = self.sneakers_price_fetch_id_musinsa()
            return [index for index, item in enumerate(data) if item['id_musinsa'] == key][0] + 1
        
        elif(market == 'sneakers'):
            data = self.sneakers_price_fetch_model_no()
            return [index for index, item in enumerate(data) if item['model_no'] == key][0] + 1
        
        elif(market == 'type1'):
            data = self.sneakers_price_fetch_urlkey()
            return [index for index, item in enumerate(data) if item['model_no'] == key][0] + 1


    def _stockx_update_registered(self):
        query = "UPDATE stockx INNER JOIN sneakers_price ON stockx.urlkey = sneakers_price.urlkey SET registered=True"
        query = "SELECT DISTINCT stockx.id FROM stockx INNER JOIN sneakers_price ON stockx.urlkey=sneakers_price.urlkey WHERE sneakers_price.urlkey IS NOT NULL"
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        return data




if __name__ == '__main__':
    DBManager = DBManager()

    ###### 상품 index 찾기 ######
    # print(DBManager._sneakers_price_fetch_index('kream', 12831))
    # print(DBManager._sneakers_price_fetch_index('musinsa', '2267726'))
    # print(DBManager._sneakers_price_fetch_index('stockx', 'new-balance-993-aime-leon-dore-brown'))

    # print(DBManager._sneakers_price_fetch_index('sneakers', '172896C'))