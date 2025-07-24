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
    
    s1 = pivot - (diff * 0.382)
    s2 = pivot - (diff * 0.618)
    s3 = pivot - (diff * 1.000)



    return pivot, r1, r2, r3, s1, s2, s3

def simple_arbitrage_usdc_usdt_pivots(exchange):
    last_timestamp = None
    amount = 1.1

    while True:
        data = exchange.fetch_ohlcv("USDC/USDT", "1d")
        # El timestamp de la última vela diaria
        current_timestamp = data[-1][0]

        # Solo recalcula si hay una nueva vela diaria
        if current_timestamp != last_timestamp:
            last_timestamp = current_timestamp
            print("Nueva vela diaria detectada, recalculando pivotes y precios...")

            pivot, r1, r2, r3, s1, s2, s3 = FIBONACCI_PIVOTS(
                np.array(data)[:, 2],  # high
                np.array(data)[:, 3],  # low
                np.array(data)[:, 4]   # close
            )
            precios_compra = [round(pivot[-1],4), round(s1[-1],4), round(s2[-1],4), round(s3[-1],4)]
            precios_venta = [round(r1[-1],4), round(r2[-1],4), round(r3[-1],4)]

        # Ejecuta el ciclo de arbitraje con los precios actualizados
        ciclo_arbitraje(exchange, 'USDC/USDT', amount, precios_compra, precios_venta)

        time.sleep(60)  # Espera 1 minuto antes de volver a revisar

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
def make_order_limit_buy(exchange, symbol, amount, price):
    """
    Crea una orden de compra limitada.
    """
    balanse_usdt = exchange.fetch_balance()["USDT"]
    precio_compra = price
    if (balanse_usdt['free'] > amount):
        if not existe_orden_abierta_compra_precio(exchange, symbol, precio_compra):
            print(f"Buy USDC at {precio_compra}")
            buy_order = exchange.create_order(
                        symbol=symbol,
                        type='limit',
                        side='buy',
                        amount=amount,
                        price=precio_compra
                    )
    return buy_order

def make_order_limit_sell(exchange, symbol, amount, price):
    """
    Crea una orden de venta limitada.
    """
    balanse_usdc = exchange.fetch_balance()["USDC"]
    precio_venta = price
    if (balanse_usdc['free'] > amount):
        if not existe_orden_abierta_venta_precio(exchange, symbol, precio_venta):
            print(f"Sell USDC at {precio_venta}")
            sell_order = exchange.create_order(
                        symbol=symbol,
                        type='limit',
                        side='sell',
                        amount=amount,
                        price=precio_venta
                    )
    return sell_order

def ciclo_arbitraje(exchange, symbol, amount, precios_compra, precios_venta):
    while True:
        # Revisar órdenes de venta ejecutadas
        open_sell_orders = exchange.fetch_open_orders(symbol)
        for order in open_sell_orders:
            if order['side'] == 'sell' and order['status'] == 'closed':
                for precio in precios_compra:
                # Coloca orden de compra al siguiente precio
                    precio_compra = precio # O el que corresponda según tu lógica
                    make_order_limit_buy(exchange, symbol, amount, precio_compra)
                    

        # Revisar órdenes de compra ejecutadas
        open_buy_orders = exchange.fetch_open_orders(symbol)
        for order in open_buy_orders:
            if order['side'] == 'buy' and order['status'] == 'closed':
                # Coloca orden de venta al siguiente precio
                for precio in precios_venta:
                    precio_venta = round(precio, 4)
                    make_order_limit_sell(exchange, symbol, amount, precio_venta)
        time.sleep(10)  # Espera antes de volver a revisar
        

# Llama a la función principal con tus parámetros
