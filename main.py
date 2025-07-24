import time
from client import load_bingx
from strategies.simple_arbitrage import simple_arbitrage_usdc_usdt_pivots
import pandas as pd
import ccxt
def main():
    try: 
        bingx = load_bingx()
        bingx.fetch_time()
    except ccxt.NetworkError as e:
        print(bingx.id, 'fetch_order_book failed due to a network error:', str(e))
    except ccxt.ExchangeError as e:
        print(bingx.id, 'fetch_order_book failed due to exchange error:', str(e))
    except Exception as e:
        print(bingx.id, 'fetch_order_book failed with:', str(e))
           
    simple_arbitrage_usdc_usdt_pivots(bingx)
    
if __name__ == "__main__":
    main()