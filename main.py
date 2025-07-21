import time
from client import load_bingx
from strategies.simple_arbitrage import simple_arbitrage_usdc_usdt_pivots
import pandas as pd
def main():
    bingx = load_bingx()
   # print(bingx.fetch_balance())
    q = True
    while q:
        simple_arbitrage_usdc_usdt_pivots()
        time.sleep(60)
if __name__ == "__main__":
    main()