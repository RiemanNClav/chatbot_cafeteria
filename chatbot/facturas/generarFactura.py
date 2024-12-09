from fpdf import FPDF
import io
from email.message import EmailMessage
import smtplib

# Función para generar la factura en PDF
def generar_factura(ticket_data, ticket_productos, fecha):
    # Crear una instancia del PDF
    pdf = FPDF()
    pdf.add_page()

    # Agregar logo (si existe)
    logo_path = 'facturas/logo.png'
    if logo_path:
        pdf.image(logo_path, x=160, y=8, w=40)

    # Encabezado de la factura
    pdf.set_xy(10, 5)
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 6, 'Tory Cafe', ln=True)
    pdf.cell(0, 6, 'Poniente 128 #505, Col. Industrial Vallejo,', ln=True)
    pdf.cell(0, 6, 'Alcaldia Azcapotzalco, CDMX', ln=True)

    # Fecha
    pdf.set_font('Arial', style='B', size=12)
    pdf.cell(0, 6, f'Fecha: {fecha}', ln=True)

    # Ajustar espacio vertical
    pdf.ln(5)

    # Título de la factura
    pdf.set_font('Arial', size=16)
    pdf.cell(0, 8, txt='FACTURA', ln=True, align='C')

    pdf.set_font('Arial', style='B', size=12)
    pdf.cell(0, 8, f'Número Factura: {ticket_data["Num. Venta"]}', ln=True, align='C')

    # Datos del cliente
    pdf.set_font('Arial', style='B', size=12)
    pdf.cell(0, 6, 'DATOS DEL CLIENTE', ln=True, align='L')
    pdf.cell(0, 6, '------------------------------------', ln=True, align='L')

    pdf.set_font('Arial', size=12)
    for clave, valor in ticket_data.items():
        pdf.set_font('Arial', style='B', size=12)
        pdf.cell(40, 5, f'{clave}:', align='L')
        pdf.set_font('Arial', size=12)
        pdf.cell(0, 5, f'{valor}', ln=True, align='L')

    pdf.cell(0, 6, '------------------------------------', ln=True, align='L')

    # Detalles del servicio
    pdf.set_font('Arial', style='B', size=12)
    pdf.cell(0, 6, 'DETALLES DEL SERVICIO', ln=True, align='L')
    pdf.cell(0, 6, '------------------------------------', ln=True, align='L')

    # Crear encabezados de la tabla
    pdf.set_font('Arial', size=12, style='B')
    pdf.cell(40, 8, 'Producto', border=1, align='C')
    pdf.cell(40, 8, 'Categoría', border=1, align='C')
    pdf.cell(70, 8, 'Subcategoría', border=1, align='C')
    pdf.cell(40, 8, 'Precio', border=1, align='C')
    pdf.ln()

    # Agregar filas dinámicas
    pdf.set_font('Arial', size=12)
    total_precio = 0
    for producto in ticket_productos:
        pdf.cell(40, 6, producto['producto'], border=1, align='C')
        pdf.cell(40, 6, producto['categoria'], border=1, align='C')
        pdf.cell(70, 6, producto['subcategoria'], border=1, align='C')
        pdf.cell(40, 6, f"MXN {producto['precio']}", border=1, align='C')
        pdf.ln()
        total_precio += producto['precio']

    # Agregar subtotal y total
    pdf.cell(0, 6, '------------------------------------', ln=True, align='L')
    pdf.set_font('Arial', size=12, style='B')
    pdf.cell(150, 6, 'Subtotal:', border=0, align='R')
    pdf.cell(40, 6, f"MXN {total_precio}", border=0, align='R', ln=True)

    pdf.cell(150, 6, 'Total:', border=0, align='R')
    pdf.cell(40, 6, f"MXN {total_precio}", border=0, align='R', ln=True)

    # Guardar en memoria
    pdf_buffer = io.BytesIO()
    pdf_buffer.write(pdf.output(dest='S').encode('latin1'))
    pdf_buffer.seek(0)# Reinicia el puntero al inicio del buffer
    return pdf_buffer


# Función para enviar la factura por correo
def enviar_factura_por_correo(ticket_data, pdf_buffer, password):
    sender_email = "angel.chavez.clavellina@gmail.com"
    receiver_email = ticket_data["Correo Electronico"]
    password_ = password   # Usa una contraseña de aplicación de Gmail
    subject = "Factura de compra - Tory Cafe"
    nombre_cliente = ticket_data["Nombre Cliente"]

    # Contenido del correo
    body = f"""
    Hola {nombre_cliente},
    
    Adjunto a este correo encontrarás la factura correspondiente a tu compra en Tory Cafe.
    
    ¡Gracias por tu preferencia!
    
    Saludos,
    Equipo de Tory Cafe
    """

    # Crear el mensaje de correo
    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.set_content(body)

    # Adjuntar el archivo PDF
    pdf_filename = f'Factura_{ticket_data["Num. Venta"]}.pdf'
    message.add_attachment(pdf_buffer.read(), maintype='application', subtype='pdf', filename=pdf_filename)

    # Enviar el correo
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, password_)
        smtp.send_message(message)
    print(f"Factura enviada a {receiver_email}")



if __name__ == '__main__':

    fecha = "2024-12-08"

    ticket_data = {
        "Num. Venta": "12345",
        "Nombre Cliente": "Juan Pérez",
        "Correo Electronico": "pyrat.solutions@gmail.com",
        "Teléfono": "1234567890",
    }
    
    ticket_productos = [
        {'producto': 'bebidas', 'categoria': 'Bebidas Calientes', 'subcategoria': 'Flat White', 'precio': 765},
        {'producto': 'alimentos', 'categoria': 'Frappuccino', 'subcategoria': 'Cate Frapuccino', 'precio': 786},
        {'producto': 'alimentos', 'categoria': 'Bebidas Calientes', 'subcategoria': 'Flat White', 'precio': 765}
    ]

    pdf_buffer = generar_factura(ticket_data, ticket_productos, fecha)
    enviar_factura_por_correo(ticket_data, pdf_buffer, password)
