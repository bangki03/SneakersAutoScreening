from KreamManager import KreamManager
from StockXManager import StockXManager
from Analyzer import Analyzer
import time
import math
from Lib_else import sleep_random

if __name__ == '__main__':
    ### 상품 관리 ###
    # KreamManager = KreamManager()
    # StockXManager = StockXManager()
    # Analyzer = Analyzer()

    # StockXManager.scrap_product(delay_min=0.2, delay_max=0.5)
    # KreamManager.scrap_product()
    # StockXManager.scrap_model_no(batch=50, delay_min=1, delay_max=1, id_start=423)
    # Analyzer.select_common_brand_model_no()
    # StockXManager.scrap_size(batch=50, delay_min=1, delay_max=1, id_start=1)
    # Analyzer.fill_size_estimated_mm(batch=500, id_start=1)
    # Analyzer.update_kream_size(batch=500, id_start=1)
    # Analyzer.update_id_kream()


    ### 가격 Scrap ###
    # KreamManager = KreamManager()
    # KreamManager.scrap_price(batch=20, delay_min=0.9, delay_max=1.5, id_start=1)

    
    # StockXManager = StockXManager()
    # StockXManager.scrap_price(batch=20, delay_min=0.5, delay_max=0.8, id_start=0)

    ### Report ###
    Analyzer = Analyzer()
    Analyzer.export_report()




    #################### (임시) 가격 Scrap 번갈아 ####################
    # KreamManager = KreamManager()
    # StockXManager = StockXManager()
    # batch = 1
    # delay_min = 0.5
    # delay_max = 0.8
    # id_start_kream = 0 + 1
    # id_start_stockx = 0

    # state_loop_kream = True
    # state_loop_stockx = True

    # # kream scrap 준비
    # cnt_total_kream = KreamManager._query_count_total(table="sneakers_price")

    # data_stockx = StockXManager._query_select_distinct_urlkey(table="sneakers_price")
    # cnt_total_stockx = len(data_stockx)

    # ratio_int = math.floor(cnt_total_kream/cnt_total_stockx)
    # tic = time.time()


    
    # while(1):
    #     ### kream ###
    #     if(state_loop_kream):
    #         id_end_kream = min(id_start_kream + batch*ratio_int -1, cnt_total_kream)
    #         data_kream = KreamManager._query_fetch_size(table="sneakers_price", id_start=id_start_kream, id_end=id_end_kream)

    #         for (id, id_kream, size_kream_mm, size_kream_us) in data_kream:
    #             if(size_kream_mm == "" and size_kream_us == ""):
    #                 continue

    #             size_kream = KreamManager._parse_keram_size(size_kream_mm, size_kream_us)
                
    #             try:
    #                 sleep_random(delay_min, delay_max)
    #                 response = KreamManager._request_price(id_kream=id_kream, size=size_kream)
    #                 state, price_buy, price_sell, price_recent = KreamManager._parse_priceinfo(response)

    #                 if(state):
    #                     KreamManager._query_update_priceinfo(id, id_kream=id_kream, size_kream_mm=size_kream_mm, size_kream_us=size_kream_us, price_buy=price_buy, price_sell=price_sell, price_recent=price_recent)
    #             except Exception as e:
    #                 print("[KreamManager]: Error(%s) at (id_kream:%s, size:%s)"%(e, id_kream, size_kream))
            
    #         toc = time.time()
    #         print("[Kream_Manager] : 처리중(%6d/%d) - %.1fmin"%(id_end_kream, cnt_total_kream, (toc-tic)/60))

    #         # 처리 끝났으면 while 조건 체크
    #         if(id_end_kream == cnt_total_kream):
    #             state_loop_kream = False
    #         else:
    #             id_start_kream = id_start_kream + batch*ratio_int



    #     ### stockx ###
    #     if(state_loop_stockx):
    #         id_end_stockx = min(id_start_stockx + batch, cnt_total_stockx)
    #         data_batch_stockx = data_stockx[id_start_stockx: id_end_stockx]

    #         for urlkey in data_batch_stockx:
    #             # Model No.
    #             if(not state_loop_kream):
    #                 sleep_random(delay_min, delay_max)
    #             state = StockXManager._update_price(urlkey=urlkey[0])

    #             # price recent
    #             data_id = StockXManager._query_select_id_stockx_in_urlkey(urlkey=urlkey[0])
    #             for id_stockx in data_id:
    #                 sleep_random(delay_min, delay_max)

    #                 state_price_recent = StockXManager._update_price_recent(urlkey=urlkey[0], id_stockx=id_stockx[0])

    #             # if(~state):
    #             #     continue
            

    #         toc = time.time()
    #         print("[StockX_Manager] : 처리중(%d/%d) - %.1fmin"%(id_end_stockx, cnt_total_stockx, (toc-tic)/60))

    #         # 처리 끝났으면 while 조건 체크
    #         if(id_end_stockx == cnt_total_stockx):
    #             state_loop_stockx = False
    #         else:
    #             id_start_stockx = id_start_stockx + batch

        
    #     if( not state_loop_kream and not state_loop_stockx):
    #         print("가격 Srap 완료되었습니다. %.0fmin"%((toc-tic)/60))
    #         break
