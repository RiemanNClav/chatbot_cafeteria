import io

class MensajesAutomatizados:
    def __init__(self, nombre_ticket):
        self.n = nombre_ticket

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
                contenido.append("-------------------------------------")

        agregar_registro(contenido, "Registro de Bebidas", registros_bebidas)
        agregar_registro(contenido, "Registro de Alimentos", registros_alimentos)
        agregar_registro(contenido, "Registro de Promociones", registros_promociones)

        contenido.append(f"TOTAL = {total} MXN")
        contenido.append("-----------------------------------------------")
        contenido.append(f"          Forma de pago: {forma_pago}")
        contenido.append(f"          Vendedor: Tory Cafe")
        contenido.append(f"          Mesero: Tory Cafe")
        contenido.append(f"          Gracias por su compra!")
        contenido.append(f"          No hay devoluciones")

        return "\n".join(contenido)

    def enviar_archivo(self, file_content):
        """
        Devuelve el archivo en memoria (BytesIO) que puede ser usado como texto adjunto en un mensaje.
        """
        try:
            file_in_memory = io.BytesIO(file_content.encode('utf-8'))
            file_in_memory.name = f"{self.n}.txt"  # Asignar nombre al archivo
            return file_in_memory
        except Exception as e:
            print(f"Error enviando archivo: {e}")
            return None

    def enviar(self, ticket_data, ticket_bebidas, nombre, telefono, forma_pago, total):
        """
        Genera y devuelve el archivo en memoria para ser enviado como parte de un mensaje.
        """
        contenido_ticket = self.generar_ticket_en_memoria(ticket_data, ticket_bebidas, forma_pago, total)
        archivo_en_memoria = self.enviar_archivo(contenido_ticket)
        return archivo_en_memoria


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
    clase.enviar(ticket_data, ticket_bebidas, "Angel Uriel", "5565637294")