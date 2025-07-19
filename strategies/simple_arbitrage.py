# %%
from client import load_bingx
import talib
import numpy as np
import pprint
import pandas
# %%
def simple_arbitrage_usdc_usdt()-> None:
    amount = 2
    bingx = load_bingx()
    balanse_usdc= bingx.fetch_balance()["USDC"]
    balanse_usdt= bingx.fetch_balance()["USDT"] 
    data = bingx.fetch_ohlcv("USDC/USDT","5m")
    price = np.array(data)[:,3]
    upper, middle, lower = talib.BBANDS(price,timeperiod=20, nbdevup=2, nbdevdn=2, matype= 1)
    #print(upper[-1], middle[-1], lower[-1])
    if balanse_usdt['free']>amount:
        if price[-1] < lower[-1]:
            print("Buy USDC")
            bingx.create_order(
                symbol='USDC/USDT',
                type='limit',
                side='buy',
                amount=amount,
                price=lower[-1])
            
    if balanse_usdc['free']>amount:
        if price[-1] > upper[-1]:
            print("Buy USDC")
            bingx.create_order(
                symbol='USDC/USDT',
                type='limit',
                side='sell',
                amount=amount,
                price=upper[-1])
