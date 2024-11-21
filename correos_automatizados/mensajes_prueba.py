
import os
import time
from email.message import EmailMessage
import smtplib
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime

## pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client


class GoogleDrive():
    def __init__(self):
        pass

    def access(self):
        ruta_credenciales = "credentials-service-account.json"  # Reemplaza con la ruta a tu archivo JSON de credenciales    
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

        return ruta_credenciales, scopes
    
    def obtener_datos_sheet(self, file_id):
        ruta_credenciales, scopes = self.access()

        # CREDENCIALES
        credenciales = Credentials.from_service_account_file(ruta_credenciales, scopes=scopes)
        service = build('docs', 'v1', credentials=credenciales)

        document = service.documents().get(documentId=file_id).execute()
        content = document.get('body').get('content', [])

        # Extraer el texto del documento
        texto = ""
        for element in content:
            if 'paragraph' in element:
                for run in element['paragraph']['elements']:
                    if 'textRun' in run:
                        texto += run['textRun']['content']

        return texto

    
    def enviar_correo(self, nombre, correo, plantilla):
        sender_email = "angel.chavez.clavellina@gmail.com"
        receiver_email = correo
        password = "qkgf zivf wlfa sgxy"  # Contraseña de aplicación de Gmail
        subject = "¡Promociones Especiales para Ti!"

        # Reemplazar la variable {nombre} en la plantilla
        html_content = plantilla.replace("{nombre}", nombre)

        # Configurar el correo
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = correo
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        # Enviar el correo
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, correo, msg.as_string())
            print(f"Correo enviado a {correo}")



    def enviar_correos_programados(self):
        file_id = '1brOoIxh40UtUI9V8efkh5iy337eZxE_CaJVznkzF9EA'
        plantilla = self.obtener_datos_sheet(file_id)
        self.enviar_correo("Angel", "angel.chavez.clavellina@gmail.com", plantilla)


if __name__ == "__main__":
    clase = GoogleDrive()
    clase.enviar_correos_programados()