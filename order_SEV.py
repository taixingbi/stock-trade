import schedule
import time
from module import *

NAME = "QQQ"
NAME = "SEV"

PERCENGTAGE_SELL_TRAILING_STOP = 1 

def tradeIpo():
    print("\n" + getTimeNow() + " " + NAME )
    is_stock_have_share, share_hold = stock_have_share(NAME)
    print(is_stock_have_share, share_hold)
    if is_stock_have_share:
        stockSelltrailingStop(NAME, share_hold, PERCENGTAGE_SELL_TRAILING_STOP)
        
tradeIpo()
schedule.every(5).seconds.do(tradeIpo)
while True:
    schedule.run_pending()
    time.sleep(1)


