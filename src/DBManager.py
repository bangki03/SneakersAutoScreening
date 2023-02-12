import pymysql
import pandas

class DBManager:
    def __init__(self):
        self.con = pymysql.connect(host='localhost', user='bangki', password='Bangki12!@', db='sneakers', charset='utf8')
        self.cursor = self.con.cursor()

    def __del__(self):
        self.con.close()

    
    ########### Table kream ###########
    def _kream_insert_productinfo(self, product):
        try:
            query = "INSERT INTO kream (brand, model_no, product_name, id_kream, size_mm, size_us) VALUES (%s, %s, %s, %s, %s, %s)" 
            self.cursor.execute(query, (product['brand'], product['model_no'], product['product_name'], product['id_kream'], product['size_mm'], product['size_us']))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_kream_insert_productinfo' with [미정...]) "%(err))
    def _kream_select_size(self, id_start, id_end):
        query = "SELECT id, id_kream, size_kream_mm, size_kream_us FROM kream WHERE id>%d AND id <%d"%(id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    def _kream_select_size_which_price_is_none(self, id_start, id_end):
        query = "SELECT id, id_kream, size_kream_mm, size_kream_us FROM kream WHERE id>%d AND id <%d AND ((price_buy_kream IS NULL) AND (price_sell_kream IS NULL))"%(id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    def _kream_select_size_estimated(self, brand, model_no, size_estimated):
        query = "SELECT size_mm, size_us FROM kream WHERE brand=%s AND model_no=%s AND size_mm=%s"
        self.cursor.execute(query, (brand, model_no, size_estimated))

        data = self.cursor.fetchall()
        return data
    def _kream_select_id_kream(self, model_no):
        query="SELECT id_kream FROM kream WHERE model_no=%s"
        self.cursor.execute(query, (model_no))

        data = self.cursor.fetchall()
        return data[0][0]
    def _kream_select_distict_id_kream_model_no(self):
        query = "SELECT DISTINCT id_kream, model_no FROM kream"
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data

    ########### Table stockx ###########
    def _stockx_insert_productinfo(self, product):
        try:
            query = "INSERT INTO stockx (brand, product_name, id_stockx, urlkey) VALUES (%s, %s, %s, %s)" 
            self.cursor.execute(query, (product['brand'], product['product_name'], product['id_stockx'], product['urlkey']))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_stockx_insert_productinfo' with [미정...]) "%(err))
    def _stockx_select_urlkey(self, id_start, id_end):
        # query = "SELECT id, urlkey FROM stockx WHERE id>%d AND id <%d"%(id_start-1, id_end+1)
        query = "SELECT id, urlkey FROM stockx WHERE id>%d AND id <%d AND model_no is NULL"%(id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    def _stockx_update_model_no(self, model_no, urlkey):
        try:
            query = "UPDATE stockx SET model_no=%s WHERE urlkey=%s"
            self.cursor.execute(query, (model_no, urlkey))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_stockx_update_model_no' with [model_no=%s WHERE urlkey=%s]) "%(err, model_no, urlkey))
    
    
    ## 이거 쓰는건지 체크
    def _stockx_select_size(self, table, id_start, id_end):
        query = "SELECT id, brand, model_no, size_stockx, urlkey FROM %s WHERE id>%d AND id <%d"%(table, id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    

    ########### Table sneakers ###########
    def _sneakers_select_all(self, id_start, id_end):
        query = "SELECT id, brand, model_no, product_name, urlkey FROM sneakers WHERE id>%d AND id <%d"%(id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    
    def _sneakers_insert_productinfo(self, brand, model_no, product_name, urlkey):
        try:
            query = "INSERT INTO sneakers (brand, model_no, product_name, urlkey) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (brand, model_no, product_name, urlkey))
            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_insert_productinfo' with [미정...]) "%(err))    



    ########### Table sneakers_price ###########
    def _sneakers_price_update_price_kream(self, id_kream, size_kream_mm, size_kream_us, price_buy, price_sell, price_recent):
        try:
            # query = "INSERT INTO sneakers_price (id, id_kream, size_kream_mm, size_kream_us, price_buy_kream, price_sell_kream) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE price_buy_kream=%s, price_sell_kream=%s"
            # query = "UPDATE sneakers_price SET price_buy_kream='%s', price_sell_kream='%s' WHERE id_kream=%s AND size_kream_mm=%s AND size_kream_us=%s"
            query = "UPDATE sneakers_price SET price_buy_kream=NULLIF(%s, 0), price_sell_kream=NULLIF(%s, 0), price_recent_kream=NULLIF(%s, 0) WHERE id_kream=%s AND size_kream_mm=%s AND size_kream_us=%s"
            self.cursor.execute(query, (price_buy, price_sell, price_recent, id_kream, size_kream_mm, size_kream_us))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_update_priceinfo' with [id_kream=%s AND size_kream_mm=%s AND size_kream_us=%s]"%(err, id_kream, size_kream_mm, size_kream_us))
    def _sneakers_price_insert_data_with_size(self, brand, model_no, product_name, size, urlkey, id_stockx):
        try:
            ## 임시로 id_stockx만 업데이트
            # query = "UPDATE sneakers_price SET id_stockx=%s WHERE model_no=%s AND size_stockx=%s"
            # self.cursor.execute(query, (id_stockx, model_no, size))

            query = "INSERT INTO sneakers_price (brand, model_no, product_name, size_stockx, urlkey, id_stockx) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query, (brand, model_no, product_name, size, urlkey, id_stockx))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_insert_data_with_size' with [brand=%s, model_no=%s, product_name=%s, size=%s, urlkey=%s, id_stockx=%s]"%(err, brand, model_no, product_name, size, urlkey, id_stockx))
    def _sneakers_price_select_distinct_urlkey(self):
        query = "SELECT DISTINCT urlkey FROM sneakers_price"
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    def _sneakers_price_select_distinct_model_no(self):
        query = "SELECT DISTINCT model_no FROM sneakers_price"
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    def _sneakers_price_select_id_stockx_in_urlkey(self, urlkey):
        query = "SELECT id_stockx FROM sneakers_price WHERE urlkey=%s"
        self.cursor.execute(query, (urlkey))

        data = self.cursor.fetchall()
        return data
    def _sneakers_price_update_price_stockx(self, size, price_buy, price_sell, urlkey):
        try:
            # query = "INSERT INTO sneakers_price (size_stockx, price_buy_stockx, price_sell_stockx, urlkey) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE price_buy_stockx=%s, price_sell_stockx=%s"
            query = "UPDATE sneakers_price SET price_buy_stockx=NULLIF(%s, 0), price_sell_stockx=NULLIF(%s, 0) WHERE urlkey=%s AND size_stockx=%s"
            self.cursor.execute(query, (price_buy, price_sell, urlkey, size))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_update_price_stockx' with [urlkey=%s AND size_stockx=%s]"%(err, urlkey, size))
    def _sneakers_price_update_price_recent_stockx(self, id_stockx, price_recent):
        try:
            query = "UPDATE sneakers_price SET price_recent_stockx=NULLIF(%s, 0) WHERE id_stockx=%s"
            self.cursor.execute(query, (price_recent, id_stockx))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_update_price_recent_stockx' with [id_stockx=%s]"%(err, id_stockx))
    def _sneakers_price_update_price_kream_and_price_recent_stockx(self, price_buy_kream, price_sell_kream, price_recent_kream, price_recent_stockx, id_stockx):
        try:
            query = "UPDATE sneakers_price SET price_buy_kream=NULLIF(%s, 0), price_sell_kream=NULLIF(%s, 0), price_recent_kream=NULLIF(%s, 0), price_recent_stockx=NULLIF(%s, 0) WHERE id_stockx=%s"
            self.cursor.execute(query, (price_buy_kream, price_sell_kream, price_recent_kream, price_recent_stockx, id_stockx))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_update_price_kream_and_price_recent_stockx' with [id_stockx=%s]"%(err, id_stockx))

    def _sneakers_price_select_size_stockx(self, id_start, id_end):
        query = "SELECT id, brand, model_no, size_stockx, urlkey FROM sneakers_price WHERE id>%d AND id <%d"%(id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    def _sneakers_price_update_size_estimated_mm(self, brand, model_no, size_stockx, size_estimated_mm):
        try:
            query = "UPDATE sneakers_price SET size_estimated_mm=%s WHERE brand=%s AND model_no=%s AND size_stockx=%s"
            self.cursor.execute(query, (size_estimated_mm, brand, model_no, size_stockx))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_update_size_estimated_mm' with [brand=%s, model_no=%s, size_stockx=%s]"%(err, brand, model_no, size_stockx))
    def _sneakers_price_select_size_estimated(self, id_start, id_end):
        query = "SELECT id, brand, model_no, size_stockx, size_estimated_mm FROM sneakers_price WHERE id>%d AND id <%d"%(id_start-1, id_end+1)
        self.cursor.execute(query)

        data = self.cursor.fetchall()
        return data
    def _sneakers_price_update_size_kream(self, brand, model_no, size_stockx, size_estimated_mm, size_mm, size_us):
        try:
            query = "UPDATE sneakers_price SET size_kream_mm=%s, size_kream_us=%s WHERE brand=%s AND model_no=%s AND size_stockx=%s AND size_estimated_mm=%s"
            self.cursor.execute(query, (size_mm, size_us, brand, model_no, size_stockx, size_estimated_mm))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_update_size_kream' with [brand=%s AND model_no=%s AND size_stockx=%s AND size_estimated_mm=%s]"%(err, brand, model_no, size_stockx, size_estimated_mm))
    def _sneakers_price_update_id_kream(self, model_no, id_kream):
        try:
            query = "UPDATE sneakers_price SET id_kream=%s WHERE model_no=%s"
            self.cursor.execute(query, (id_kream, model_no))

            self.con.commit()
        except Exception as err:
            print("[DBManager] : Error(%s) at '_sneakers_price_update_id_kream' with [id_kream=%s WHERE model_no=%s]"%(err, id_kream, model_no))

    def _sneakers_price_select_all_in_urlkey(self, urlkey):
        self.cursor = self.con.cursor(pymysql.cursors.DictCursor)   ## Dictionary로 데이터 가져오기 위함
        query = "SELECT * FROM sneakers_price WHERE urlkey=%s"
        self.cursor.execute(query, (urlkey))

        data = self.cursor.fetchall()
        self.cursor = self.con.cursor() ## 다시 커서 원복해놓자.
        return data


    ########### Common ###########
    def _table_count_total(self, table):
        query = "SELECT COUNT(*) FROM %s"%(table)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        return result[0]
    def _common_select_product(self):
        query = "SELECT brand, model_no, product_name, urlkey FROM stockx WHERE model_no in (select model_no from kream)"

        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data


    ########### return Pandas ###########
    def _fetch_kream_product(self, option_pandas=False):
        query = "SELECT DISTINCT brand, model_no, product_name FROM kream"
        if(option_pandas):
            data = pandas.read_sql_query(query,self.con)
        else:
            self.cursor.execute(query)
            data = self.cursor.fetchall()

        return data
        
    def _fetch_stockx_product(self, option_pandas=False):
        query = "SELECT DISTINCT brand, model_no, urlkey, product_name FROM stockx"
        if(option_pandas):
            data = pandas.read_sql_query(query,self.con)
        else:
            self.cursor.execute(query)
            data = self.cursor.fetchall()

        return data
    def _fetch_sneakers_product(self, option_pandas=False):
        query = "SELECT brand, model_no, product_name, urlkey FROM stockx WHERE model_no in (select model_no from kream) AND model_no != ''"
        if(option_pandas):
            data = pandas.read_sql_query(query,self.con)
        else:
            self.cursor.execute(query)
            data = self.cursor.fetchall()

        return data
    
    def _fetch_sneakers_price(self, option_pandas=False):
        query = "SELECT brand, model_no, product_name, size_stockx, size_estimated_mm, size_kream_mm, size_kream_us, price_buy_kream, price_sell_kream, price_buy_stockx, price_sell_stockx, updated_at FROM sneakers_price"
        if(option_pandas):
            data = pandas.read_sql_query(query,self.con)
        else:
            self.cursor.execute(query)
            data = self.cursor.fetchall()

        return data


    ## 함수 1)
    ## 함수 2)
    ## 함수 3)
    ## 함수 4)
    ## 함수 5)
    ## 함수 6)
    ## 함수 7)
