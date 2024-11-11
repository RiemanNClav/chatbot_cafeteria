from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import os

from preprocesamiento_sheets import GoogleDrive, GoogleSheet, InsertData
from coordenadas import ApiAddress
from precios import Precios

clase_google_drive = GoogleDrive()
sheets = clase_google_drive.obtener_sheets()

precios = sheets["precios"]

clase_precios = Precios(precios)
categorias_bebidas = clase_precios.obtener_precios()


app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_unica_y_segura'

# Obtener la URL base desde una variable de entorno
APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:5056')


@app.route("/<token>", methods=["GET", "POST"])
def registrar_pedido(token):
    session['token'] = token

    if request.method == "POST":
        nombre = request.form.get("nombre")
        cantidad_bebidas = int(request.form.get("cantidad_bebidas"))
        session['nombre'] = nombre

        bebidas = []
        for i in range(cantidad_bebidas):
            bebida = {
                'categoria': request.form.get(f"categoria_bebida_{i}"),
                'subcategoria': request.form.get(f"subcategoria_bebida_{i}"),
                'tipo_leche': request.form.get(f"tipo_leche_{i}"),
                'azucar': request.form.get(f"azucar_{i}"),
                'consideraciones': request.form.get(f"consideraciones_{i}")
            }
            bebidas.append(bebida)

        session['bebidas'] = bebidas

        return redirect(url_for("resumen_pedido", token=token))

    return render_template("home.html", token=token, categorias_bebidas=categorias_bebidas)

# El resto del código permanece igual



# Ruta para mostrar el resumen, que también requiere el mismo token
@app.route("/resumen/<token>", methods=["GET", "POST"])
def resumen_pedido(token):


    if request.method == "POST":
        if 'confirmar_pedido' in request.form:
            # Aquí puedes manejar la confirmación, por ejemplo, guardar en una base de datos
            response = f"Pedido realizado, ¡Gracias!\n"
            response += "En el chatbot, favor de escribir la palabra 'registrado'"
            return response
        elif 'reiniciar' in request.form:
            session.clear()  # Limpiar la sesión para reiniciar el formulario
            return redirect(url_for("registrar_pedido", token=token))

    # Cargar los datos del resumen desde la sesión
    sheet_bebidas = sheets["registro_bebidas"]
    clase_insert_data = InsertData(sheet_bebidas)

    nombre = session.get('nombre')
    bebidas = session.get("bebidas")
    cantidad_bebidas = len(bebidas)

    total = 0
    registro_bebidas = sheets["registro_bebidas"]
    registro_bebidas = GoogleSheet(registro_bebidas)

    registro_ventas = sheets["registro_ventas"]
    registro_ventas = GoogleSheet(registro_ventas)

    for i in range(cantidad_bebidas):
        dicc = bebidas[i]
        subcategoria = dicc["subcategoria"].split('-')[0]
        precio = float(dicc["subcategoria"].split('-')[1].replace('MXN', '').strip())
        new_token = token + '_' + str(i+1)
        clase_insert_data.insert_data(new_token, i+1)
        registro_bebidas.update_cell_by_id(new_token, "nombre", nombre)
        registro_bebidas.update_cell_by_id(new_token, "categoria", dicc["categoria"])
        registro_bebidas.update_cell_by_id(new_token,  "subcategoria", subcategoria)
        registro_bebidas.update_cell_by_id(new_token, "tipo_leche", dicc["tipo_leche"])
        registro_bebidas.update_cell_by_id(new_token, "azucar_extra", dicc["azucar"])
        registro_bebidas.update_cell_by_id(new_token, "consideraciones", dicc["consideraciones"])
        registro_bebidas.update_cell_by_id(new_token, "precio", precio)

        total += precio


    registro_ventas.update_cell_by_id(token, "nombre", nombre)
    registro_ventas.update_cell_by_id(token, "cantidad_bebidas", cantidad_bebidas)

    latitud = session.get('latitud')
    longitud = session.get('longitud')

    clase_api_adress = ApiAddress()

    direccion = clase_api_adress.api_request_object_1(latitud, longitud)
    _, radio, distancia= clase_api_adress.bola_cerrada(latitud, longitud)


    registro_ventas.update_cell_by_id(token, "direccion", direccion)
    registro_ventas.update_cell_by_id(token, "cobertura", "DENTRO DEL RADIO DE COBERTURA")

    registro_ventas.update_cell_by_id(token, "radio_km", radio)
    registro_ventas.update_cell_by_id(token, "distancia", distancia)

    bebidas = session.get('bebidas', [])
    
    return render_template("resumen.html", nombre=nombre, direccion=direccion, bebidas=bebidas, total=total, token=token)

@app.route('/guardar_ubicacion', methods=['POST'])
def guardar_ubicacion():
    clase_api_adress = ApiAddress()

    data = request.json
    latitud = data.get("latitud")
    longitud = data.get("longitud")

    print(f"Latitud: {latitud}, Longitud: {longitud}")
    result, _, _ = clase_api_adress.bola_cerrada(latitud, longitud)

    if result == 1:
        session['latitud'] = latitud
        session['longitud'] = longitud
        return jsonify({"message": "Ubicación recibida correctamente"})
    else:
        return jsonify({"message": "Localmente NO tenemos cobertura hasta tu direccion, favor de pedir por Uber Eats, gracias!"})

# Nueva ruta para guardar el token y generar el enlace único
@app.route('/guardar_token', methods=['POST'])
def guardar_token():
    data = request.json
    token_sesion = data.get('token_sesion')
    # token_sesion = "62a483fc-9d2b-4f44-adf8-9bcea9bd0a14"
    # Genera el enlace único con el token
    enlace = f"{APP_BASE_URL}/{token_sesion}"

    # Aquí puedes guardar el id_registro_venta y el token_sesion en tu base de datos si es necesario.
    # Ejemplo:
    # clase.guardar_token_en_bd(id_registro_venta, token_sesion)

    # Retornar el enlace al chatbot
    return jsonify({"enlace": enlace})


# Página de error si el token no es válido
@app.route('/error')
def error():
    return "Token inválido o ya ha sido usado."


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5056)