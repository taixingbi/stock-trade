import schedule
import time
from module import TradeIpo

def schedule_trade_ipo(NAME):
    # NAME = "QQQ"
    # SHARE = 1
    # INIT_PRICE = 393.80 # $20
    # INIT_PERCENGTAGE_HIGHER = 0 # 1%
    # SIDE = "BUY" # BUY / SELL
    SIDE = "BUY" # BUY / SELL
    SHARE = 10
    LOWEST_PRICE_TRIGER = 0
    PERCENGTAGE_BUY_TRAILING_STOP = 2
    PERCENGTAGE_SELL_TRAILING_STOP = 2 

    tradeIpo = TradeIpo(NAME, SIDE, SHARE, LOWEST_PRICE_TRIGER, PERCENGTAGE_BUY_TRAILING_STOP, PERCENGTAGE_SELL_TRAILING_STOP)
    # schedule.every(59).minutes.do(Trade.job)
    schedule.every(15).seconds.do(tradeIpo.process)

    tradeIpo.process()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    name = "BLZE"
    name = "VAXX"
    # name = "EXFY"

    try:
        schedule_trade_ipo(name)    
    except KeyboardInterrupt:
        print('Interrupted')
