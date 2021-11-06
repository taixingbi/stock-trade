from datetime import datetime
import schedule
import time
from pytz import timezone
from logger import logger
Logger = logger("test.log")

from module import ipo_order, livePrice


order_sequence = ["buy" , "sell"]
# order_sequence.reverse()

def job():
    timenow = datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
    # Logger.critical(timenow)
    print("\n"+timenow)

    
    name = "QQQ"
    init_pirce, rate_init_raise = 20, 1 # $20, 1%
    peak_price, rate_peak_drop=  livePrice(name), 1 # $500 1%

    share = 1
    # order_sequence.reverse()
    ipo_order(order_sequence, name, share, peak_price, rate_init_raise , rate_peak_drop, init_pirce) 

# schedule.every(1).minutes.do(job)
schedule.every(30).seconds.do(job)

job()
while True:
    schedule.run_pending()
    time.sleep(1)

