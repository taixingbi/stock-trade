import schedule
import time
from module import TradeIpo

def schedule_trade_ipo():
    tradeIpo = TradeIpo("QQQ")
    # schedule.every(59).minutes.do(Trade.job)
    schedule.every(59).seconds.do(tradeIpo.process)

    tradeIpo.process()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    schedule_trade_ipo()

