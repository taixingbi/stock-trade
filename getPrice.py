from yahoo_fin import stock_info as si
import robin_stocks.robinhood as rs

from module import *

import pandas as pd
import numpy as np
import yfinance
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def getDf(name, start, end, interval):
    ticker = yfinance.Ticker(name)
    df = ticker.history(interval=interval, start= start, end= end)
    return df

name = "TQQQ"
start="2021-11-09"
# end="2021-11-11"
end=None
getDf(name, start, end, '1m')






