from datetime import datetime
import time

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

def stock_have_shares(name):
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


#           need to  buy 
# ------------------------------
#           need to  sell
def find_triger_price(peak_price, rate_init_raise = 1, rate_peak_drop = 1, init_pirce = 0):
    a = init_pirce * (1 + (1.0*rate_init_raise/100))
    b = peak_price * (1 - (1.0*rate_peak_drop/100)) 
    stop_price = max( a, b)
    return round(stop_price, 2)


def ipo_order(order_sequence, name, share, peak_price, rate_init_raise , rate_peak_drop, init_pirce):
    stop_price = find_triger_price(peak_price, rate_init_raise, rate_peak_drop, init_pirce)
    valid_stock_have_shares, shares = stock_have_shares(name)

    #buy
    if order_sequence[0] == "buy" and valid_stock_have_shares == False: 
        stock_buy_stop(name, share, stop_price)
        print("bought", name, share, stop_price)
        order_sequence.reverse()
    #sell
    if order_sequence[0] == "sell" and valid_stock_have_shares == True: 
        stock_sell_stop(name, share, stop_price)
        print("sold", name, share, stop_price)
        order_sequence.reverse()

    print(order_sequence)

# ipo_buy("QQQ", 1, 20, 1000) # triger by $990

if __name__ == "__main__":

    order_sequence = ["buy" , "sell"]

    name = "QQQ"
    share = 1
    peak_price = 500
    rate_init_raise, rate_peak_drop = 1, 1
    init_pirce = 20
    # order_sequence.reverse()
    ipo_order(order_sequence, name, share, peak_price, rate_init_raise , rate_peak_drop, init_pirce) 