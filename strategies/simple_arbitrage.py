
from client import load_bingx
import talib
import numpy as np
import pprint
import pandas as pd
import time
import ccxt

def PIVOTS(high, low, close):
    """
    Calcula pivots clásicos y niveles S1, S2, R1, R2.
    Devuelve: pivot, r1, s1, r2, s2 (todos np.arrays)
    """
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    return pivot, r1, s1, r2, s2

def FIBONACCI_PIVOTS(high, low, close):
    """
    Calcula pivotes de Fibonacci y niveles de soporte/resistencia.
    Devuelve: pivot, r1, r2, r3, s1, s2, s3, r0618, r1000, r1618, s0618, s1000, s1618 (todos np.arrays)
    """
    pivot = (high + low + close) / 3
    diff = high - low

    r1 = pivot + (diff * 0.382)
    r2 = pivot + (diff * 0.618)
    r3 = pivot + (diff * 1.000)
    r1618 = pivot + (diff * 1.618)
    s1 = pivot - (diff * 0.382)
    s2 = pivot - (diff * 0.618)
    s3 = pivot - (diff * 1.000)
    s1618 = pivot - (diff * 1.618)

    # Niveles intermedios (opcional)
    r0618 = pivot + (diff * 0.236)
    r1000 = pivot + (diff * 1.000)
    s0618 = pivot - (diff * 0.236)
    s1000 = pivot - (diff * 1.000)

    return pivot, r1, r2, r3, s1, s2, s3

def simple_arbitrage_usdc_usdt(exchange):
 
    amount = 1.1
    balanse_usdc= exchange.fetch_balance()["USDC"]
    balanse_usdt= exchange.fetch_balance()["USDT"] 
    data = exchange.fetch_ohlcv("USDC/USDT","1h")
    price = np.array(data)[:,3]
    upper, middle, lower = talib.BBANDS(price,timeperiod=20, nbdevup=3, nbdevdn=2, matype= 1)
    pivotes = PIVOTS(np.array(data)[:,1],
                     np.array(data)[:,2],
                     np.array(data)[:,3])
    #print(upper[-1], middle[-1], lower[-1])
    if balanse_usdt['free']>amount:
        if price[-1] < lower[-1]:
            print(f'Buy USDC to {price[-1]}')
            bingx.create_order(
                symbol='USDC/USDT',
                type='limit',
                side='buy',
                amount=amount,
                price=lower[-1])
        else:
            print("Buy USDC")
            bingx.create_order(
                symbol='USDC/USDT',
                type='limit',
                side='buy',
                amount=amount,
                price=lower[-1])
            
    if balanse_usdc['free']>amount:
        if price[-1] > upper[-1]:
            print("Sell USDC")
            bingx.create_order(
                symbol='USDC/USDT',
                type='limit',
                side='sell',
                amount=amount,
                price=upper[-1])
        else:
            print("Sell USDC")
            bingx.create_order(
                symbol='USDC/USDT',
                type='limit',
                side='sell',
                amount=amount,
                price=upper[-1]+ 0.0001)

def simple_arbitrage_usdc_usdt_pivots(exchange)-> None :

    buy_orders = []
    sell_orders = []
    amount = 1.1
        
    balanse_usdc = exchange.fetch_balance()["USDC"]
    balanse_usdt = exchange.fetch_balance()["USDT"]
    data = exchange.fetch_ohlcv("USDC/USDT", "1d")
    price = np.array(data)[:, 3]  # precios de cierre

        # Calcula pivotes clásicos
    pivot, r1, r2, r3, s1, s2, s3 = FIBONACCI_PIVOTS(
            np.array(data)[:, 2],  # high
            np.array(data)[:, 3],  # low
            np.array(data)[:, 4]   # close
        )

    precios_compra = [round(pivot[-1],4), round(s1[-1],4), round(s2[-1],4), round(s3[-1],4)]
    precios_venta = [round(r1[-1],4), round(r2[-1],4), round(r3[-1],4)]  # Puedes ajustar esto según tu lógica

    for precio_compra in precios_compra:
        if (balanse_usdt['free'] > amount):
            if not existe_orden_abierta_compra_precio(exchange, 'USDC/USDT', precio_compra):
                print(f"Buy USDC at {precio_compra}")
                orden_compra = exchange.create_order(
                        symbol='USDC/USDT',
                        type='limit',
                        side='buy',
                        amount=amount,
                        price=precio_compra
                    )
                buy_orders.append(orden_compra)
    for i, buy_order in enumerate(buy_orders):   
        order_status = exchange.fetch_order(buy_order['id'], symbol='USDC/USDT')
        if order_status['status'] == 'closed':
            precio_venta = precios_venta[i] if i < len(precios_venta) else round(buy_order['price'] * 1.01, 4) 
            print("Compra ejecutada, creando orden de venta...")
            orden_venta = exchange.create_order(
                            symbol='USDC/USDT',
                            type='limit',
                            side='sell',
                            amount=amount,
                            price=precio_venta
                        )
        sell_orders.append(orden_venta)
    while True:
        for sell_order in sell_orders:
            order_status = exchange.fetch_order(sell_order['id'], symbol='USDC/USDT')
            if order_status['status'] == 'closed':
                print(f"Venta ejecutada a {sell_order['price']}")
                simple_arbitrage_usdc_usdt_pivots(exchange)# Llamada recursiva para continuar el ciclo
            else:
                print(f"Orden de venta pendiente a {sell_order['price']}") 
                time.sleep(10)  # Espera antes de volver a verificar el estado de las órdenes

def existe_orden_abierta_compra_precio(bingx, symbol, precio):
    """
    Verifica si hay una orden abierta de compra para el símbolo y precio dados.
    Devuelve True si existe, False si no.
    """
    open_orders = bingx.fetch_open_orders(symbol)
    for order in open_orders:
        if order['side'] == 'buy' and order['status'] == 'open' and float(order['price']) == float(precio):
            return True
    return False

def existe_orden_abierta_venta_precio(bingx, symbol, precio):
    """
    Verifica si hay una orden abierta de venta para el símbolo y precio dados.
    Devuelve True si existe, False si no.
    """
    open_orders = bingx.fetch_open_orders(symbol)
    for order in open_orders:
        if order['side'] == 'sell' and order['status'] == 'open' and float(order['price']) == float(precio):
            return True
    return False