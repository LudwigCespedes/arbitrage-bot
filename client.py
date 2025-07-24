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

    bingx.options['maxRetriesOnFailure'] = 5 # if we get an error like the ones mentioned above we will retry up to three times per request
    bingx.options['maxRetriesOnFailureDelay'] = 1000 # we will wait 1000ms (1s) between retries
    
    return bingx

if __name__ == "__main__":
    bingx = load_bingx()
    print(bingx.fetch_balance())