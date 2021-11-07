from datetime import datetime
from pytz import timezone

from yahoo_fin import stock_info as si
import cryptocompare

import os
import robin_stocks.robinhood as rs

CRYPTO= ["BTC", "DOGE", "ETH"]

# ----------------------- login  -----------------------
def login():
    print("login successfully")
    robin_user = os.environ.get("robinhood_username")
    robin_pass = os.environ.get("robinhood_password")
    res= rs.login(username=robin_user,
            password=robin_pass,
            expiresIn=86400,
            by_sms=True)
    # print(res)
    return rs

rs = login()

# ----------------------- check real time price  -----------------------
def livePrice(ticker):
    # print("livePrice")
    if ticker in CRYPTO: 
        response= cryptocompare.get_price(ticker, currency='USD') 
        live_price= response[ticker]['USD']
    else:
        live_price= si.get_live_price(ticker) 
        live_price= live_price.item() # numpy to float

    # timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # timestamp = time.time()
    return live_price

# ----------------------- check my stock -----------------------
def check_my_stocks(name):
    my_stocks = rs.build_holdings()
    for key, stock in my_stocks.items():
        if key == name : return stock

    return None

def stock_have_share(name):
    stock = check_my_stocks(name)
    if stock: 
        shares_float = float(stock['quantity']) 
        return shares_float > 1, int(shares_float) 
    return False, 0

# ----------------------- order -----------------------
# triger a market sell order if stock falls to
def stock_sell_stop(name, share, price):
    res = rs.orders.order_sell_stop_loss(name,
                                share,
                                price,
                                timeInForce='gtc',
                                extendedHours=False)
    print(res)
# stock_sell_limit("TQQQ", 1, 150)

# triger a market buy order if stock rises to
def stock_buy_stop(name, share, price):
    res= rs.orders.order(   name, 
                            share, 
                            "buy", 
                            limitPrice=None, 
                            stopPrice= price, 
                            timeInForce='gtc', 
                            extendedHours=False, 
                            jsonify=True)
    print(res)
# stock_buy_stop("QQQ", 1, 500)

def cancel_stock_order(order_id):
    if order_id:
        rs.orders.cancel_stock_order(order_id)

# ----------------------- triger -----------------------
def find_triger_price(peak_price, rate_init_raise = 1, rate_peak_drop = 1, init_pirce = 0):
    a = init_pirce * (1 + (1.0*rate_init_raise/100))
    b = peak_price * (1 - (1.0*rate_peak_drop/100)) 
    stop_price = max( a, b)
    return round(stop_price, 2)

#           need to  buy 
# ------------------------------
#           need to  sell
class TradeIpo:
    def __init__(self, name):
        self.name = name
        self.init_pirce = 20 # $20
        self.rate_init_raise = 1 # 1%
        self.rate_peak_drop = 1  # 1%
        self.live_price = 0
        self.peak_price = 0
        self.share = 1
        self.order_sequence = ["buy", "sell"]
        self.stoploss_order_id = None

    def peakPrice(self):
        peak_price = livePrice(self.name)
        if self.peak_price < peak_price : 
            self.peak_price = peak_price
            return True, self.peak_price # isChange, $30
        return False, self.peak_price # isChange, $30

    def stockSellStop(self):
        cancel_stock_order(self.stoploss_order_id)
        res = stock_sell_stop(self.name, self.share, self.stop_price)
        self.stoploss_order_id = res['id']

    def process(self):
        timenow = datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
        # Logger.critical(timenow)
        print("\n"+timenow)
        isPeakChange, peak_price = self.peakPrice() 

        stop_price = find_triger_price( peak_price, self.rate_init_raise, self.rate_peak_drop, self.init_pirce)
        is_stock_have_share, share_hold = stock_have_share(self.name)

        # share = max(share, share_hold)
        # buy
        if is_stock_have_share == False and self.order_sequence[0] == "buy" : 
            stock_buy_stop(self.name, self.share, stop_price)
            
            print(self.order_sequence[0], self.name, self.share, stop_price)
            self.order_sequence.reverse() # ["sell", "buy"]
            self.stoploss_order_id = None

        # multi sell
        if is_stock_have_share == True and (self.stoploss_order_id == None or isPeakChange):
            self.stockSellStop()
            print(self.order_sequence[0], self.name, self.share, stop_price)
            if self.order_sequence[0] == "sell":
                self.order_sequence.reverse() # buy

        print(self.order_sequence)

if __name__ == "__main__":
    TradeIpo = TradeIpo()
    TradeIpo.process()
