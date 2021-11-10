import schedule
import time
from module import TradeIpo

def schedule_trade_ipo():
    # NAME = "QQQ"
    # SHARE = 1
    # INIT_PRICE = 393.80 # $20
    # INIT_PERCENGTAGE_HIGHER = 0 # 1%

    NAME = "EXFY"
    SHARE = 1
    LOWEST_PRICE_TRIGER = 39
    PERCENGTAGE_BUY_TRAILING_STOP = 1 
    PERCENGTAGE_SELL_TRAILING_STOP = 1 

    tradeIpo = TradeIpo(NAME, SHARE, LOWEST_PRICE_TRIGER, PERCENGTAGE_BUY_TRAILING_STOP, PERCENGTAGE_SELL_TRAILING_STOP)
    # schedule.every(59).minutes.do(Trade.job)
    schedule.every(5).seconds.do(tradeIpo.process)

    tradeIpo.process()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    try:
        schedule_trade_ipo()    
    except KeyboardInterrupt:
        print('Interrupted')
