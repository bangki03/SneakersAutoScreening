import requests
import time
from Lib_else import sleep_random
from bs4 import BeautifulSoup

class MusinsaManager:
    def __init__(self):
        self.brand_list = ['adidas', 'vans', 'converse']
        self.delay_min = 0.2
        self.delay_max = 0.4
        pass

    def __setManagers__(self, SneakersManager, StockXManager, KreamManager, DBManager, ReportManager):
        self.SneakersManager = SneakersManager
        self.StockXManager = StockXManager
        self.MusinsaManager = KreamManager
        self.DBManager = DBManager
        self.ReportManager = ReportManager




    ### 동작 1. 상품 업데이트
    def update_product(self, table):
        if(table=='musinsa'):
            print("[MusinsaManager] : 상품 스크랩 시작합니다.")

            data = self.scrap_product_list()

            data_filtered = [item for item in data if not self.DBManager.musinsa_check_product_exist(item)]
            print("[MusinsaManager] : 신규 상품 %d개 상품 정보 스크랩 시작합니다."%(len(data_filtered)))

            self.scrap_productinfo(product_list=data_filtered)
            print("[MusinsaManager] : 상품 등록 (to musinsa) 완료하였습니다.")

        elif(table=='sneakers_price'):
            # 1. 등록 여부 False 인 애들 다 불러와.
            # 2. sneakers_price에 model_no 등록된 애들 찾자.
            # 3. 걔네들만 업데이트
            data = self.DBManager.musinsa_fetch_product()

            data_filtered = [item for item in data if self.DBManager.sneakers_price_check_product_need_update(market='musinsa', product=item)]
            print("[MusinsaManager] : 신규 상품 %d개 등록합니다."%(len(data_filtered)))

            for item in data_filtered:
                self.DBManager.sneakers_price_update_product(market='musinsa', product=item)

            print("[MusinsaManager] : 상품 등록 (to sneakers_price) 완료하였습니다.")
        else:
            print("[MusinsaManager] : 테이블 명(%s) 는 존재하지 않습니다."%(table))

    ### 동작 2. 가격 업데이트
    def update_price(self, id_start=1):
        print("[MusinsaManager] : 가격 스크랩 시작합니다.")

        data = self.DBManager.sneakers_price_fetch_id_musinsa()
        cnt_total = len(data)

        tic=time.time()
        for index, item in enumerate(data):
            if(index<id_start-1):
                continue

            state, data_price = self.scrap_price(id_musinsa=item['id_musinsa'])
            if(state):
                data_price.update(item)
                self.DBManager.sneakers_price_update_price(market='musinsa', product=data_price)
            
            toc=time.time()
            print("[MusinsaManager] : (%s)가격 스크랩 완료(%d/%d) [%.1fmin]"%(item['id_musinsa'], index+1, cnt_total, (toc-tic)/60))
            sleep_random(self.delay_min, self.delay_max)
        
        print("[MusinsaManager] : 가격 등록 완료하였습니다.")



    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 1. 상품 업데이트
    #######################################################################################################################################
    #######################################################################################################################################

    ### Lv1) 상품 스크랩 ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_product_list(self):
        data_output = []

        page = 1
        tic = time.time()
        while(1) :
            sleep_random(self.delay_min, self.delay_max)
            state, data_page = self.scrap_id_musinsa_page(page=page, brand_list=self.brand_list)
            if(state):
                data_output.extend(data_page)
                
                toc = time.time()
                print("[MusinsaManager] : 상품 스크랩 중 (%d page) [%.1fmin]" %(page, (toc-tic)/60))
                
                page = page + 1
            else:
                return data_output

    ### Lv2) 페이지 별 상품 스크랩 ###
    # input : page, brand_list
    # output : state, list[dict{id_musinsa}]
    def scrap_id_musinsa_page(self, page, brand_list):
        data = []
        response = self._get_productlist_page(page=page, brand_list=brand_list)
        if(response.status_code == 200):
            data = self._parse_id_musinsa(response=response)
            if( len(data) >0 ):
                state = True
            else:
                state = False
        elif(response.status_code != 200):
            print("[MusinsaManager] : Error Code(%s) at 'scrap_id_musinsa_page' with [page=%s]) "%(response.status_code, page))
            state = False
        
        return state, data
    
    ### Lv3) 페이지 별 상품 Request ###
    # input : page
    # output : response
    def _get_productlist_page(self, page, brand_list):
        brandlist_str = "%2C".join(brand_list)
        url = "https://www.musinsa.com/categories/item/018?d_cat_cd=018&brand=%s&list_kind=small&sort=pop_category&page=%s&display_cnt=90"%(brandlist_str, page)

        response = requests.request("GET", url)

        return response

    ### Lv3) 상품 정보 Parsing ###
    # input : response
    # output : state, list[dict{'id_musinsa'}]
    def _parse_id_musinsa(self, response):
        output_productlist = []

        bs = BeautifulSoup(response.text, features="html.parser")

        item_box_list= bs.select('#searchList > li.li_box')
        for item_box in item_box_list:
            product = {}
            try:
                url = item_box.find('a', attrs={'name': 'goods_link'})['href']
                product['id_musinsa'] = url.split('/')[-1]

                output_productlist.append(product)
            except Exception as err:
                pass
        
        return output_productlist
    


    ### Lv1) 상품정보 스크랩 (리스트) ###
    # input : page, brand_list
    # output : state, list[dict{brand, id_stockx, product_name, urlkey}]
    def scrap_productinfo(self, product_list):
        tic = time.time()
        for index, item in enumerate(product_list):
            sleep_random(self.delay_min, self.delay_max)
            state = self.scrap_productinfo_product(item)
            
            if(state):
                self.DBManager.musinsa_update_product(item)

                toc = time.time()
                print("[MusinsaManager] : 상품정보 스크랩 중 (%d/%d) [%.1fmin]" %(index+1, len(product_list), (toc-tic)/60))



    ### Lv2) 상품정보 스크랩 (상품별) ###
    # input : page, brand_list
    # output : state, list[dict{'brand','model_no','product_name','price_sale', 'price_discount'}]
    def scrap_productinfo_product(self, product):
        response = self._get_price(id_musinsa=product['id_musinsa'])
        if(response.status_code == 200):
            data = self._parse_productinfo(response=response)
            product.update(data)
            state = True
        elif(response.status_code != 200):
            print("[MusinsaManager] : Error Code(%s) at 'scrap_productinfo_product' with [id_musinsa=%s]) "%(response.status_code, product['id_musinsa']))
            state = False

        return state


    ### Lv3) 상품 정보(가격) Request ###
    # input : page
    # output : response
    def _get_price(self, id_musinsa):
        url = "https://www.musinsa.com/app/goods/%s"%(id_musinsa)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        response = requests.request("GET", url, headers=headers)

        return response

    ### Lv3) 상품 정보 Parsing ###
    # input : response
    # output : state, list[dict{'brand','model_no','product_name','price_sale', 'price_discount'}]
    def _parse_productinfo(self, response):
        output = {
            'brand' : '',
            'model_no' : '',
            'product_name': '',
            # 'price_sale_musinsa' : 0,
            # 'price_discount_musinsa': 0,
            'registred': False
        }

        bs = BeautifulSoup(response.text, features="html.parser")

        str1 = bs.select_one('#product_order_info > div.explan_product.product_info_section > ul > li:nth-child(1) > p.product_article_contents > strong').get_text()
        str1 = str1.split('/')
        output['brand'] = str1[0].strip().lower()
        output['model_no'] = str1[1].strip()
        output['product_name'] = bs.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > span > em').get_text()
        # output['price_sale_musinsa'] = bs.select_one('#normal_price').get_text().replace('원','').replace(',', '')
        # try:
        #     output['price_discount_musinsa'] = bs.select_one('#sPrice > ul > li > span.txt_price_member.m_list_price').get_text().replace('원','').replace(',', '')
        # except:
        #     output['price_discount_musinsa'] = output['price_sale_musinsa']

        return output
    

    #######################################################################################################################################
    #######################################################################################################################################
    ### 동작 2. 가격 업데이트 (sneakers 에서 요청)
    #######################################################################################################################################
    #######################################################################################################################################


    ### Lv2) 가격정보 스크랩 (상품별) ###
    # input : page, brand_list
    # output : state, list[dict{'brand','model_no','product_name','price_sale', 'price_discount'}]
    def scrap_price(self, id_musinsa):
        sleep_random(self.delay_min, self.delay_max)
        data = {}
        response = self._get_price(id_musinsa=id_musinsa)
        if(response.status_code == 200):
            data = self._parse_priceinfo(response=response)
            data['id_musinsa'] = id_musinsa
            state = True
        elif(response.status_code != 200):
            print("[MusinsaManager] : Error Code(%s) at 'scrap_price' with [id_musinsa=%s]) "%(response.status_code, id_musinsa))
            state = False

        return state, data




    ### Lv3) 가격 정보 Parsing ###
    # input : response
    # output : state, list[dict{'brand','model_no','product_name','price_sale', 'price_discount'}]
    def _parse_priceinfo(self, response):
        output = {
            # 'brand' : '',
            # 'model_no' : '',
            # 'product_name': '',
            'price_sale_musinsa' : 0,
            'price_discount_musinsa': 0,
            # 'registred': False
        }

        bs = BeautifulSoup(response.text, features="html.parser")

        str1 = bs.select_one('#product_order_info > div.explan_product.product_info_section > ul > li:nth-child(1) > p.product_article_contents > strong').get_text()
        str1 = str1.split('/')
        # output['brand'] = str1[0].strip().lower()
        # output['model_no'] = str1[1].strip()
        # output['product_name'] = bs.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > span > em').get_text()
        output['price_sale_musinsa'] = bs.select_one('#normal_price').get_text().replace('원','').replace(',', '')
        try:
            output['price_discount_musinsa'] = bs.select_one('#sPrice > ul > li > span.txt_price_member.m_list_price').get_text().replace('원','').replace(',', '')
        except:
            output['price_discount_musinsa'] = output['price_sale_musinsa']

        return output

