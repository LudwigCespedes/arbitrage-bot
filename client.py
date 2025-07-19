from dotenv import load_dotenv
import os
import ccxt
load_dotenv()
def load_bingx():
    
    api_key = os.getenv("api_key")
    api_secret = os.getenv("api_secret")
    bingx = ccxt.bingx({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot'  # MUY IMPORTANTE para usar futuros
    }})
    return bingx

if __name__ == "__main__":
    bingx = load_bingx()
    print(bingx.fetch_balance())