import requests
from bs4 import BeautifulSoup

class MusinsaManager:
    def __init__(self):
        pass

    ### 1. 페이지 돌며 전체 상품(id_musinsa) 긁기 ###
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

    ### 2. 가격 및 상품정보 긁기 ###
    # input : id_musinsa
    # output : state, dict{price_buy, price_sell, price_recent}
    def scrap_price(self, id_musinsa):
        data = {}
        response = self._get_price(id_musinsa=id_musinsa)
        if(response.status_code == 200):
            data = self._parse_priceinfo(response=response)
            state = True
        elif(response.status_code != 200):
            print("[MusinsaManager] : Error Code(%s) at 'scrap_price' with [id_musinsa=%s]) "%(response.status_code, id_musinsa))
            state = False

        return state, data


    ##### 기능 1 관련 함수 #############################################################################################################################################################################  
    def _get_productlist_page(self, page, brand_list):
        brandlist_str = "%2C".join(brand_list)
        url = "https://www.musinsa.com/categories/item/018?d_cat_cd=018&brand=%s&list_kind=small&sort=pop_category&page=%s&display_cnt=90"%(brandlist_str, page)

        response = requests.request("GET", url)

        return response

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
    

    ##### 기능 2 관련 함수 #############################################################################################################################################################################  
    def _get_price(self, id_musinsa):
        url = "https://www.musinsa.com/app/goods/%s"%(id_musinsa)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            # '': '',
            # '': '',
            # '': '',
            # '': '',
        }

        response = requests.request("GET", url, headers=headers)

        return response

    def _parse_priceinfo(self, response):
        output = {
            'price_buy' : '',
            'model_no' : '',
            'product_name': '',
            'price_sale' : 0,
            'price_discount': 0
        }

        bs = BeautifulSoup(response.text, features="html.parser")

        str1 = bs.select_one('#product_order_info > div.explan_product.product_info_section > ul > li:nth-child(1) > p.product_article_contents > strong').get_text()
        str1 = str1.split('/')
        output['brand'] = str1[0].strip().lower()
        output['model_no'] = str1[1].strip()
        output['product_name'] = bs.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > span > em').get_text()
        output['price_sale'] = bs.select_one('#normal_price').get_text().replace('원','').replace(',', '')
        try:
            output['price_discount'] = bs.select_one('#sPrice > ul > li > span.txt_price_member.m_list_price').get_text().replace('원','').replace(',', '')
        except:
            output['price_discount'] = output['price_sale']

        return output




