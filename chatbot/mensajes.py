import requests
import io
import yaml
import os



class MensajesAutomatizados:
    def __init__(self, nombre_ticket):
        self.n = nombre_ticket

    def enviar_archivo_telegram(self, file_content, nombre, telefono, TELEGRAM_TOKEN, CHAT_ID):
        """Envía un archivo de texto a Telegram como documento sin guardarlo en el sistema."""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        try:
            # Convertir el contenido a un archivo en memoria
            file_in_memory = io.BytesIO(file_content.encode('utf-8'))
            file_in_memory.name = self.n  # Nombre del archivo para Telegram

            files = {'document': file_in_memory}
            data = {'chat_id': CHAT_ID, 'caption': f'📄{nombre}-{telefono}.'}
            response = requests.post(url, data=data, files=files)

            if response.status_code == 200:
                print("✅ Archivo enviado exitosamente a Telegram")
            else:
                print(f"⚠️ Error al enviar archivo a Telegram: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"Error enviando archivo: {e}")


    def generar_ticket_en_memoria(self, ticket_data, ticket_bebidas, forma_pago, total):
        """Genera el contenido del ticket como un archivo de texto en memoria."""
        contenido = []

        # Encabezado del ticket
        contenido.append("                  Tory Cafe")
        contenido.append("   Poniente 128 #505, Col. Industrial Vallejo,")
        contenido.append("          Alcaldia Azcapotzalco, CDMX")
        contenido.append("-------------------------------------")


        # Agregar datos generales del ticket
        for key, value in ticket_data.items():
            contenido.append(f"{key} = {value}")
        contenido.append("-------------------------------------")

        # Clasificar los registros por tipo de producto
        registros_bebidas = [t for t in ticket_bebidas if t['producto'] == 'bebidas']
        registros_alimentos = [t for t in ticket_bebidas if t['producto'] == 'alimentos']
        registros_promociones = [t for t in ticket_bebidas if t['producto'] == 'promociones']

        # Agregar registros clasificados
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
        contenido.append(f"          Forma de pago: {forma_pago}")
        contenido.append(f"          Vendedor: Tory Cafe")
        contenido.append(f"          Mesero: Tory Cafe")
        contenido.append(f"          Gracias por su compra!")
        contenido.append(f"          No hay devoluciones")

        return "\n".join(contenido)
    


    def enviar(self, ticket_data, ticket_bebidas, nombre, telefono, forma_pago, total, TELEGRAM_TOKEN, CHAT_ID):
        contenido_ticket = self.generar_ticket_en_memoria(ticket_data, ticket_bebidas, forma_pago, total)
        self.enviar_archivo_telegram(contenido_ticket, nombre, telefono, TELEGRAM_TOKEN, CHAT_ID)

if __name__ == '__main__':
    # Datos de ejemplo para el ticket
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

    clase = MensajesAutomatizados("316-2552-1401.txt")



    secrets = credentials_from_secrets()
    telegram_token = secrets['telegram']['access_token']
    chat_id = secrets['telegram']['chat_id']
    clase.enviar(ticket_data, ticket_bebidas, "Angel Uriel", "5565637294", "Efectivo", "total", telegram_token, chat_id)

