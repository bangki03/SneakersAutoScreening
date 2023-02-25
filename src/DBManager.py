import pymysql
import pymysql.cursors
import pandas

class DBManager:
    def __init__(self):
        self.con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8')
        self.cursor = self.con.cursor(pymysql.cursors.DictCursor)

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
        self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['id_kream'], product['size_mm'], product['size_us']))

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

    ### 2) sneakers_price 상품 등록 여부 확인
    def sneakers_price_check_product_need_update(self, market, product):
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


    ### 1) stockx 상품 업데이트 ###
    def sneakers_price_update_product(self, market, product):
        if(market=='stockx'):
            query = "INSERT INTO sneakers_price (brand, model_no, product_name, size_stockx, size_estimated_mm, id_stockx, urlkey) VALUES (%s, %s, %s, %s, %s, %s, %s)" 
            self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['size_stockx'], product['size_estimated_mm'], product['id_stockx'], product['urlkey']))
            
            self.con.commit()

        elif(market=='kream'):
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

    ### 2) Distinct urlkey (stockx 가격 업데이트 필요한 상품군 불러오기 위함) ###
    def sneakers_price_fetch_urlkey(self):
        query = "SELECT DISTINCT urlkey FROM sneakers_price"
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
    def sneakers_price_fetch_id_muisnsa(self):
        query = "SELECT DISTINCT id_musinsa from sneakers_price WHERE id_musinsa IS NOT NULL"
        self.cursor.execute(query)
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
    
    
    
    