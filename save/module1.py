# https://readthedocs.org/projects/robin-stocks/downloads/pdf/latest/
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

# ----------------------- check real time price peak price -----------------------
class CheckPrice:
    def __init__(self, name):
        self.name = name
        self.peakPrice = 0

    def live(self):
        # print("livePrice")
        live_price = 0
        if self.name in CRYPTO: 
            response= cryptocompare.get_price(self.name, currency='USD') 
            live_price= response[self.name]['USD']
        else:
            # live_price= si.get_live_price(self.name) 
            # live_price= live_price.item() # numpy to float
            live_price = rs.stocks.get_latest_price(self.name, includeExtendedHours=True)
            if not live_price[0]:
                raise Exception(self.name + ' price does not exist in Robinhood yet\n')
            live_price = round( float(live_price[0]), 2)
        # timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # timestamp = time.time()
        return live_price

    def getShareDecimal(self, price):
        return round(1.0 * price/self.live(), 5)

    def getShare(self, price):
        return int(1.0 * price/self.live() )

    def peak(self):
        livePrice = self.live()
        print(self.peakPrice, livePrice)
        if self.peakPrice < livePrice : 
            self.peakPrice = livePrice
        return self.peakPrice # $30

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

# ----------------------- order stock -----------------------
# triger a market sell order if stock falls to
def stock_sell_stop(name, share, price):
    res = rs.orders.order_sell_stop_loss(name,
                                share,
                                price,
                                timeInForce='gtc',
                                extendedHours=True,
                                jsonify=True)
    print(res)
# stock_sell_limit("TQQQ", 1, 150)

def stock_sell(name, share):
    res = rs.orders.order_sell_market(name,
                                share,
                                timeInForce='gtc',
                                extendedHours=False,
                                jsonify=True)
    print(res)

def stockSelltrailingStop(name, share, percentage):
    res = rs.orders.order_sell_trailing_stop(   name, 
                                                share, 
                                                percentage,
                                                trailType= 'percentage',
                                                timeInForce= 'gtc', 
                                                extendedHours= False,
                                                jsonify=True)
    print(res)
    try:
        res['id']
        return True
    except:
        print("order_sell_trailing_stop failed")
        return False

# triger a market buy order if stock rises to
def stockBuyStop(name, share, price):
    res= rs.orders.order(   name, 
                            share, 
                            "buy", 
                            limitPrice=None, 
                            stopPrice= price, 
                            timeInForce='gtc', 
                            extendedHours=False, 
                            jsonify=True)
    print(res)

    try:
        res['id']
        return True
    except:
        print("stock_buy_stop failed")
        return False

    # {'detail': 'Only accepting immediate limit orders for this symbol since it has not traded yet.'}
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
    def __init__(self, NAME, SHARE, INIT_PRICE, INIT_PERCENGTAGE_HIGHER):
        self.NAME = NAME
        self.SHARE = SHARE
        
        # for buy
        self.INIT_PRICE = INIT_PRICE
        self.INIT_PERCENGTAGE_HIGHER = INIT_PERCENGTAGE_HIGHER 
        self.PEAK_PERCENGTAGE_LOWER = 1  
        # for sell
        self.PERCENGTAGE_TRAILING_STOP = 1

        self.order_sequence = ["buy", "sell"]
        # self.order_sequence = ["sell", "buy"]
        self.CheckPrice = CheckPrice(self.NAME)

    def process(self):
        timenow = datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
        # Logger.critical(timenow)
        print("\n"+timenow)
        stop_price = find_triger_price(self.CheckPrice.peak(), self.INIT_PERCENGTAGE_HIGHER, self.PEAK_PERCENGTAGE_LOWER, self.INIT_PRICE)
        is_stock_have_share, share_hold = stock_have_share(self.NAME)

        # share = max(share, share_hold)
        # buy
        if is_stock_have_share == False and self.order_sequence[0] == "buy" : 
            validOrder = stockBuyStop(self.NAME, self.SHARE, stop_price)
            if validOrder == False: return
            print(self.order_sequence[0], self.NAME, self.SHARE, stop_price)
            self.order_sequence.reverse() # ["sell", "buy"]

        # sell
        if is_stock_have_share == True and self.order_sequence[0] == "sell":
            validOrder = stockSelltrailingStop(self.NAME, self.SHARE, self.PERCENGTAGE_TRAILING_STOP)
            if validOrder == False: return
            print(self.order_sequence[0], self.NAME, self.SHARE, self.PERCENGTAGE_TRAILING_STOP)
            self.order_sequence.reverse() # buy

        print(self.order_sequence)

# ----------------------- order Crypto -----------------------
def cryptoBuyByPrice(name, price):
    res= rs.order_buy_crypto_by_price(name, price)
    print(res)

def cryptoSellByPrice(name, price):
    res= rs.order_sell_crypto_by_price(name, price)
    print(res)

def cryptoBuyByShare(name, quantity):
    res= rs.order_buy_crypto_by_quantity(name, quantity, timeInForce="gtc", jsonify=True)
    print(res)

def cryptoSellByShare(name, quantity):
    res= rs.order_sell_crypto_by_quantity(name, quantity, timeInForce="gtc", jsonify=True)
    print(res)


class TradeCrypto:
    def __init__(self, name):
        self.rs = rs
        self.name = name
        self.init_pirce = 20 # $20
        self.rate_init_raise = 1 # 1%
        self.rate_peak_drop = 1  # 1%
        self.price = 100
        self.CheckPrice = CheckPrice(self.name)
        self.share = self.CheckPrice.getShareDecimal(self.price)
        self.order_sequence = ["buy", "sell"]

    def process(self):
        livePrice = self.CheckPrice.live()
        isPeakChange, peakPrice = self.CheckPrice.peak()
        stopPrice = find_triger_price( peakPrice , self.rate_init_raise, self.rate_peak_drop, self.init_pirce)
        print(peakPrice, stopPrice, self.share)

        # buy
        if self.order_sequence[0] == "buy" and livePrice > stopPrice: 
            print("buy")
            cryptoBuyByShare(self.name, self.share)
            self.order_sequence.reverse() #  ["sell", "buy"]

        # sell
        if self.order_sequence[0] == "sell" and livePrice < stopPrice: 
            print("sell")
            cryptoSellByShare(self.name, self.share)
            self.order_sequence.reverse() #  ["sell", "buy"]

if __name__ == "__main__":
    # TradeIpo = TradeIpo("QQQ")
    # TradeIpo.process()

    # TradeCrypto = TradeCrypto("BTC")
    # TradeCrypto.process()

    # CheckPrice = CheckPrice("EXFY")
    # print( CheckPrice.live() )

    stockSelltrailingStop("QQQ", 1,  1)
    