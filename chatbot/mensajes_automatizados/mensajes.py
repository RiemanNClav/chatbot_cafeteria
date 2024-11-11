import os
import requests

# Lee el token de Telegram y el chat ID de las variables de entorno
TELEGRAM_TOKEN = '7767406051:AAEs306YQtgA-Dd5Bq4OMlnCFfJPFsYRWkc'
CHAT_ID = "7355671533"

def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=payload)



if __name__ == '__main__':
    enviar_alerta_telegram("SI SE ENVIAN LOS MENSAJES!")