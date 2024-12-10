import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import io
from twilio.rest import Client

class MensajesAutomatizados:
    def __init__(self, nombre_ticket):
        self.n = nombre_ticket

    def enviar_archivo_telegram(self, file_content, nombre, telefono, TELEGRAM_TOKEN, CHAT_ID):
        """Envía un archivo de texto a Telegram como documento sin guardarlo en el sistema."""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        try:
            file_in_memory = io.BytesIO(file_content.encode('utf-8'))
            file_in_memory.name = self.n

            files = {'document': file_in_memory}
            data = {'chat_id': CHAT_ID, 'caption': f'📄{nombre}-{telefono}.'}
            response = requests.post(url, data=data, files=files)

            if response.status_code == 200:
                print("✅ Archivo enviado exitosamente a Telegram")
            else:
                print(f"⚠️ Error al enviar archivo a Telegram: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"Error enviando archivo: {e}")

    def enviar_archivo_correo(self, file_content, destinatario_email, remitente_email, remitente_password):
        """Envía el ticket por correo electrónico como un archivo adjunto."""
        try:
            # Crear el mensaje
            mensaje = MIMEMultipart()
            mensaje['From'] = remitente_email
            mensaje['To'] = destinatario_email
            mensaje['Subject'] = 'Tu ticket de compra - Tory Cafe'

            # Agregar el cuerpo del correo
            cuerpo = "Adjunto encontrarás tu ticket de compra. Muchas gracias por elegir Tory Cafe!"
            mensaje.attach(MIMEText(cuerpo, 'plain'))

            # Adjuntar el archivo
            file_in_memory = io.BytesIO(file_content.encode('utf-8'))
            file_in_memory.name = self.n

            adjunto = MIMEBase('application', 'octet-stream')
            adjunto.set_payload(file_in_memory.read())
            encoders.encode_base64(adjunto)
            adjunto.add_header('Content-Disposition', f'attachment; filename={self.n}')
            mensaje.attach(adjunto)

            # Conectar al servidor SMTP y enviar el correo
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login(remitente_email, remitente_password)
            texto = mensaje.as_string()
            servidor.sendmail(remitente_email, destinatario_email, texto)
            servidor.quit()

            print("✅ Ticket enviado exitosamente por correo electrónico")

        except Exception as e:
            print(f"Error enviando correo electrónico: {e}")

    def generar_ticket_en_memoria(self, ticket_data, ticket_bebidas, total):
        contenido = []

        contenido.append("                  Tory Cafe")
        contenido.append("   Poniente 128 #505, Col. Industrial Vallejo,")
        contenido.append("          Alcaldia Azcapotzalco, CDMX")
        contenido.append("-------------------------------------")

        for key, value in ticket_data.items():
            contenido.append(f"{key} = {value}")
        contenido.append("-------------------------------------")

        registros_bebidas = [t for t in ticket_bebidas if t['producto'] == 'bebidas']
        registros_alimentos = [t for t in ticket_bebidas if t['producto'] == 'alimentos']
        registros_promociones = [t for t in ticket_bebidas if t['producto'] == 'promociones']

        def agregar_registro(contenido, titulo, registros):
            if registros:
                contenido.append(f"           {titulo}")
                for i, ticket in enumerate(registros, start=1):
                    contenido.append(f"      {titulo[:-1]} {i}")
                    for key, value in ticket.items():
                        contenido.append(f"{key} = {value}")
                contenido.append("-------------------------------------")
            else:
                contenido.append(f"       No hay {titulo[:-1].lower()}s")
                contenido.append("------------------------------------------------")

        agregar_registro(contenido, "Registro de Bebidas", registros_bebidas)
        agregar_registro(contenido, "Registro de Alimentos", registros_alimentos)
        agregar_registro(contenido, "Registro de Promociones", registros_promociones)

        contenido.append(f"            TOTAL = {total} MXN")
        contenido.append("-----------------------------------------------")
        contenido.append(f"          Vendedor: Tory Cafe")
        contenido.append(f"          Mesero: Tory Cafe")
        contenido.append(f"          Gracias por su compra!")
        contenido.append(f"          No hay devoluciones")

        return "\n".join(contenido)

    def enviar(self, ticket_data, ticket_bebidas, nombre, telefono, total, TELEGRAM_TOKEN, CHAT_ID, remitente_email, remitente_password, destinatario_email):
        contenido_ticket = self.generar_ticket_en_memoria(ticket_data, ticket_bebidas, total)
        self.enviar_archivo_telegram(contenido_ticket, nombre, telefono, TELEGRAM_TOKEN, CHAT_ID)
        self.enviar_archivo_correo(contenido_ticket, destinatario_email, remitente_email, remitente_password)

if __name__ == '__main__':
    ticket_data = {
        "id_registro_venta": "12345",
        "Fecha": "2024-11-13",
        "Nombre": "Juan Pérez",
        "Correo": "juan.perez@example.com",
        "Teléfono": "1234567890",
        "Procedencia": "Ciudad de México"
    }

    ticket_bebidas = [
        {'producto': 'bebidas', 'categoria': 'Bebidas Calientes', 'subcategoria': 'Flat White', 'tipo_leche': 'Deslactosada', 'azucar_extra': 'Si', 'consideraciones': '', 'precio': 765},
        {'producto': 'alimentos', 'categoria': 'Frappuccino', 'subcategoria': 'Cate Frapuccino', 'tipo_leche': 'Deslactosada', 'azucar_extra': 'Si', 'consideraciones': 'Muy cargado', 'precio': 786},
        {'producto': 'promociones', 'categoria': 'Bebidas Frias', 'subcategoria': 'Helado Shaken Lemon Black Tee', 'tipo_leche': 'Deslactosada', 'azucar_extra': 'Si', 'consideraciones': 'Mucha azúcar', 'precio': 7654}
    ]

    clase = MensajesAutomatizados("ticket.txt")

    telegram_token = "7767406051:AAEs306YQtgA-Dd5Bq4OMlnCFfJPFsYRWkc"
    chat_id = "7355671533"
    remitente_email = "angel.chavez.clavellina@gmail.com"
    remitente_password = "qkgf zivf wlfa sgxy"
    destinatario_email = "pyrat.solutions@gmail.com"

    clase.enviar(ticket_data, ticket_bebidas, "Angel Uriel", "5565637294", "1000", telegram_token, chat_id, remitente_email, remitente_password, destinatario_email)
