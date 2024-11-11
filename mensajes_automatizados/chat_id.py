import requests

TOKEN = '7767406051:AAEs306YQtgA-Dd5Bq4OMlnCFfJPFsYRWkc'
url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'

response = requests.get(url)
updates = response.json()

# Revisa el ID del primer mensaje recibido
if 'result' in updates and len(updates['result']) > 0:
    chat_id = updates['result'][0]['message']['chat']['id']
    print("Tu chat_id es:", chat_id)
else:
    print("Aún no hay mensajes. Envía un mensaje al bot y vuelve a intentarlo.")