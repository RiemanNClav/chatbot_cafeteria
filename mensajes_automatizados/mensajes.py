import os
import requests
import yfinance as yf

STOCK_SYMBOL = "AAPL"  # Símbolo de la acción (ejemplo: Apple)
TARGET_PRICE = 150.00  # Precio objetivo


# Lee el token de Telegram y el chat ID de las variables de entorno
TELEGRAM_TOKEN = '7767406051:AAEs306YQtgA-Dd5Bq4OMlnCFfJPFsYRWkc'
CHAT_ID = "7355671533"

def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=payload)

def verificar_precio():
    stock = yf.Ticker(STOCK_SYMBOL)
    precio_actual = stock.history(period="1d")['Close'][-1]  # Último precio de cierre

    print(f"Precio actual de {STOCK_SYMBOL}: {precio_actual}")
    
    if precio_actual >= TARGET_PRICE:
        mensaje = f"¡Alerta! El precio de {STOCK_SYMBOL} ha alcanzado ${precio_actual:.2f}, superando el objetivo de ${TARGET_PRICE}."
        enviar_alerta_telegram(mensaje)


if __name__ == '__main__':
    verificar_precio()