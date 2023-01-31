from KreamManager import KreamManager
from StockXManager import StockXManager

if __name__ == '__main__':
    KreamManager = KreamManager()
    KreamManager.update_price(batch=40, delay_min=0.2, delay_max=0.5, id_start=1908)
