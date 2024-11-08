
import os
import time
from email.message import EmailMessage
import smtplib
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


class GoogleDrive():
    def __init__(self):
        pass

    def access(self):
        ruta_credenciales = "credentials-service-account.json"  # Reemplaza con la ruta a tu archivo JSON de credenciales    
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

        return ruta_credenciales, scopes
    
    def obtener_datos_sheet(self, hoja):
        ruta_credenciales, scopes = self.access()

        # CREDENCIALES
        credenciales = Credentials.from_service_account_file(ruta_credenciales, scopes=scopes)
        cliente = gspread.authorize(credenciales)

        # HORARIO HABITUAL
        hoja1 = cliente.open(hoja).get_worksheet(3)
        data = hoja1.get_all_records()

        return data 
    
    def enviar_correo(self, nombre, correo):
        sender_email = "angel.chavez.clavellina@gmail.com"
        receiver_email = correo
        password = "qkgf zivf wlfa sgxy"  # Contraseña de aplicación de Gmail
        subject = "¡Promociones Especiales para Ti!"

        # Contenido del correo en HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .header {{ background-color: #8B4513; color: white; padding: 10px; text-align: center; font-size: 24px; }}
                .body {{ padding: 20px; font-family: Arial, sans-serif; color: #333333; }}
                .cta {{ display: block; width: 200px; margin: 20px auto; padding: 15px; text-align: center; color: white; background-color: #8B4513; text-decoration: none; font-weight: bold; border-radius: 5px; }}
                .footer {{ text-align: center; color: #aaaaaa; font-size: 12px; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">¡Promociones Especiales para Ti, {nombre}!</div>
            <div class="body">
                <p>Hola {nombre},</p>
                <p>Estamos emocionados de ofrecerte descuentos exclusivos en nuestros productos. No pierdas esta oportunidad de aprovechar precios increíbles.</p>
                <p>Haz clic en el enlace a continuación para ver nuestras ofertas:</p>
                <a href="https://wa.me/14155238886" class="cta">Enviar Whatsapp</a>
            </div>
            <div class="footer">
                <p>Este correo fue enviado por [Tu Empresa]. Si no deseas recibir más correos, puedes <a href="#">cancelar la suscripción</a>.</p>
            </div>
        </body>
        </html>
        """

        # Configuración del mensaje
        message = EmailMessage()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.set_content("Este es un correo de prueba con contenido HTML.")  # Texto alternativo en caso de que no se pueda ver el HTML
        message.add_alternative(html_content, subtype="html")

        # Enviar el correo
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(message)


    def enviar_correos_programados(self):
        # Lee los datos de los clientes
        data = self.obtener_datos_sheet("base_datos_tory_cafe")
        for contacto in data:
            nombre = contacto.get("nombre")
            correo = contacto.get("correo")            
            self.enviar_correo(nombre, correo)
            print("Correo enviado exitosamente a", nombre)


if __name__ == "__main__":
    clase = GoogleDrive()
    clase.enviar_correos_programados()
    