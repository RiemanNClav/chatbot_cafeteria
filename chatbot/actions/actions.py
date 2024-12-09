from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


import random
from datetime import datetime, timedelta
import uuid
import requests
import pandas as pd
import Levenshtein
import pytz
import yaml



##MODULOS
##---------------------------------------------------##
from google_drive.preprocesamiento_sheets import GoogleDrive, GoogleSheet, InsertData
from google_drive.horarios import Horarios
from mensajes import MensajesAutomatizados
from facturas.generarFactura import generar_factura, enviar_factura_por_correo
##---------------------------------------------------##

clase_google_drive = GoogleDrive()

clase_horarios = Horarios()

sheets = clase_google_drive.obtener_sheets()


## ------------------------------VER HORARIO----------------------------------  ya quedo
class ActionGetHorario(Action):

    def name(self) -> Text:
        return "action_get_horario"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("ENTRA LA ACCION")
        horario = sheets["horarios"]
        horario_particular = sheets["horario_particular"]


        diccionario1, diccionario2 = clase_google_drive.preprocesamiento_horarios(horario, horario_particular)

        dicc = clase_horarios.action_get_horario(diccionario1, diccionario2)
        particulares = dicc['particulares']
        horario_particular = dicc["horario_particular"]
        horario_habitual = dicc["horario_habitual"]


        response = "*HORARIO HABITUAL*\n"
        request_horario_habitual = horario_habitual
        for resp in request_horario_habitual:
            response += f"{resp}\n"

        if particulares == ['2']:
            response += "*HORARIO PARTICULAR*\n"
            request_horario_particular = horario_particular
            for resp in request_horario_particular:
                response += f"{resp}\n"
            
        response += '\n'

        response += "Realiza tu pedido escribiendo *Hacer pedido*, de lo contrario consulta otra opción del panel."

        dispatcher.utter_message(text=response)

        return []    

## ---------------------------------------------VALIDAR TELEFONO--------------------------------------------------------
class ActionValidarPreferencia(Action):

    def name(self) -> Text:
        return "action_validar_preferencia"
    

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        horario = sheets["horarios"]
        horario_particular = sheets["horario_particular"]

        diccionario1, diccionario2 = clase_google_drive.preprocesamiento_horarios(horario, horario_particular)
        dicc = clase_horarios.action_acotar_ubicacion(diccionario1, diccionario2)

        botton = dicc["botton"]
        botton2 = dicc["botton2"]
        dia = dicc["dia"]

        if botton == 1:
            disponiblidad = 'Si tenemos servicio!!\n'
            disponiblidad += "Perfecto, gracias por tu confianza\n"
            disponiblidad += "\n"
            disponiblidad += "¿Quieres programar tu pedido para una hora en particular o pedirlo para entrega inmediata?\n"
            disponiblidad += "Escribe *Programar* o *Inmediato*"
            validar_servicio=True
        else:
            if botton2 == 1:
                disponiblidad = f"Aun no tenemos servicio,  te recordamos que nuestro horario es de {dia}, gracias"
            elif botton2 == 2:
                disponiblidad = f"Lo siento, ya hemos cerrado, te recordamos que nuestro servicio fue de {dia}, gracias"
            validar_servicio=False


        dispatcher.utter_message(text=disponiblidad)

        return [SlotSet("programar", None), SlotSet("inmediato", None), SlotSet("telefono", None),  SlotSet("correo", None) , SlotSet("hora", None), SlotSet("validar_servicio", validar_servicio)]
    


class ActionProgramarPedido(Action):

    def name(self) -> Text:
        return "action_programar_pedido"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disponiblidad = "Increíble, especifica la hora, utilizando el siguiente formato.\n"
        disponiblidad += "Ej. Horarios antes de las 12pm: 10:30, 11:15, 9:10 ... \n"
        disponiblidad += "Ej. Horarios después de las 12pm: 13:06, 18:43, ... \n"


        dispatcher.utter_message(text=disponiblidad)

        return [SlotSet("inmediato", None)]


## --------------------------------------------MODALIDAD DEL PEDIDO-----------------------------------------------------


class ActionRegistroCorreoElectronico(Action):

    def name(self) -> Text:
        return "action_registro_correo_electronico"
    
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        recoger_enviar = tracker.get_slot("recoger_enviar")
        telefono = tracker.get_slot("telefono")

        if ("env"  in recoger_enviar.lower()) or ("ust" in recoger_enviar.lower()) :
            preferencia_pedido = 'enviar'

        
        else:
            preferencia_pedido = "recoger"

        clientes = sheets["clientes"]
        data = clientes.get_all_records()
        df = pd.DataFrame(data)[["telefono", "correo", "nombre"]]
        df["telefono"] = df["telefono"].astype("str")
        df = df[ (df["telefono"] == telefono) ]

        if len(df) != 0:
            nombre = df['nombre'].iloc[0] if not df.empty else None
            correo = df['correo'].iloc[0] if not df.empty else None
            disponiblidad = f"{nombre}, un gusto volver a saber de ti, gracias por seguir confiando en nososotros\n"
            disponiblidad += f"te pido porfavor que escribas *Link*, para poderte enviar nuestro link de registros."
            validar_correo = correo
            nombre_validar = True


        else:
            disponiblidad = f"Correcto, ya por ultimo ingresa también tu *Correo Electrónico*"
            validar_correo = None
            nombre_validar = False

        dispatcher.utter_message(text=disponiblidad)

        return [SlotSet("validar_correo", validar_correo), SlotSet("preferencia_pedido", preferencia_pedido), SlotSet("nombre_validar", nombre_validar)]
    

    

## ----------------------------------------------------HACER PEDIDO 2--------------------------------------------
class ActionRegistroLink(Action):

    def name(self) -> Text:
        return "action_registro_link"
    
    def fecha_actual(self):

        utc = pytz.utc
        cdmx_tz = pytz.timezone("America/Mexico_City")
        utc_now = datetime.now(utc)
        cdmx_time = utc_now.astimezone(cdmx_tz)

        # fecha = datetime.now()
        fecha_str = cdmx_time.strftime("%Y-%m-%d")
                
        hora_str = str(cdmx_time.strftime("%H:%M").replace(':', '.'))
        hora_float = float(hora_str)


        return fecha_str, hora_float

    def numeros_aleatorios(self):
        numero = random.randint(1,2000)
        return numero
    
    def convertir_telefono_id(self, numero_telefono):
        numero_str = str(numero_telefono)
        id_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, numero_str))
        return id_uuid
    
    def request_enviar(self, id_registro_venta, token_sesion):
        url = "https://b730-2806-2a0-1220-8638-90b9-fd10-deaa-9835.ngrok-free.app/guardar_token"
        data = {
            "id_registro_venta": id_registro_venta,
            "token_sesion": token_sesion
        }

        try:
            response = requests.post(url, json=data, timeout=10)  # Añade un timeout para evitar bloqueos
            response.raise_for_status()  # Levanta una excepción si el status no es 2xx
            print('Se ha enviado request enviar')
            
            # Asegúrate de que la respuesta contenga la clave 'enlace'
            if 'enlace' in response.json():
                return response.json()['enlace']
            else:
                print("La respuesta no contiene el enlace")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar el request: {e}")
            return None


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        programar = tracker.get_slot("programar")
        inmediato = tracker.get_slot("inmediato")
        
        filtro_seguridad1 = True
        validar_servicio = tracker.get_slot("validar_servicio")
        if validar_servicio == True:
            if programar == None and inmediato == None:
                filtro_seguridad1 = False
            
            recoger_enviar = tracker.get_slot("recoger_enviar")
            telefono = tracker.get_slot("telefono")
            correo = tracker.get_slot("correo")
            

            filtro_seguridad2 = True
            if (recoger_enviar == None)  or (telefono == None) or  (correo == None):
                filtro_seguridad2 = False

            if filtro_seguridad2 == True and filtro_seguridad1 == True:

                token = str(uuid.uuid4())
                numero_registro = self.numeros_aleatorios()
                fecha_registro, hora_registro = self.fecha_actual()

                id_registro_venta = str(numero_registro) + "-" + telefono[-4:] + '-' + str(hora_registro).replace('.', '')
                id_cliente = self.convertir_telefono_id(telefono)

                values = [id_registro_venta, id_cliente, token, numero_registro, 
                        " ", telefono, " ", fecha_registro, 
                        hora_registro, " ", 1, " ", " ", " ", " ", " "]
                
                registro_ventas = sheets["registro_ventas"]
                clase_insert_data = InsertData(registro_ventas)
                clase_insert_data.insert_data(values)


                try:
                    enlace = self.request_enviar(id_registro_venta, token)
                    response = f"Ingresa al siguiente enlace {enlace}, por favor llénalo.\n"
                    response += "Una vez completado, escribe *Registrado*, asi podremos confirmarlo."
                    response += "\n"
                    response += f"(Aveces pueden haber errores debido al internet, si llegaste hasta *Confirmar Pedido* y te salió error, con confianza escribre *Registrado* y nos pondremos en contacto contigo)"

                    dispatcher.utter_message(text=response)

                    response = "CONSIDERACIONES"
                    response += "\n"
                    response += "1. El link solo permite un click, si apretaste y saliste sin completar, tendrás que volver a *Ingresar tu número* "
                    response += "\n"
                    response += "2. Si tuviste algun problema accediendo al link, o algo no salio bien, escribe *Problema* "
                    dispatcher.utter_message(text=response)

                    validar_enlace = True
                    if enlace == None:
                        validar_enlace = None

                    return [SlotSet("id_registro_venta", id_registro_venta), SlotSet("fecha_registro", fecha_registro), SlotSet("hora_registro", hora_registro), SlotSet("token", token), SlotSet("validar_enlace", validar_enlace)]
                
                except Exception as e:
                    print(f"Error en la acción personalizada: {e}")
                    response = "Ha habido un problema, vuelve a ingresar tu número porfavor."
                    dispatcher.utter_message(text=response)
                    return []
            else:
                response = "No hemos registrado todos los datos necesarios para tu compra, escribe *Hacer pedido* y registralos porfavor!"
                dispatcher.utter_message(text=response)
                return []
        else:
            response = "No hemos registrado todos los datos necesarios para tu compra, escribe *Hacer pedido* y registralos porfavor!"
            dispatcher.utter_message(text=response)
            return []

#------------------------------------------------------CONFIRMAR PEDIDO--------------------------------------------
    
class ActionSaveData(Action):
    def name(self) -> Text:
        return "action_save_data"
    

    def obtener_hora_menos_30_min(self):

        utc = pytz.utc
        cdmx_tz = pytz.timezone("America/Mexico_City")
        utc_now = datetime.now(utc)
        cdmx_time = utc_now.astimezone(cdmx_tz)

        # hora_actual = datetime.now()
        nueva_hora = cdmx_time + timedelta(minutes=30)

        hora = int(nueva_hora.strftime("%H:%M").split(':')[0])


        if hora in list(range(12, 19)):
            return f'{nueva_hora.strftime("%H:%M")} de la tarde'
        elif hora in list(range(19, 24)):
            return f'{nueva_hora.strftime("%H:%M")} de la noche'
        else:
            return f'{nueva_hora.strftime("%H:%M")} de la mañana'
        

    def fecha_actual(self):
        utc = pytz.utc
        cdmx_tz = pytz.timezone("America/Mexico_City")
        utc_now = datetime.now(utc)
        cdmx_time = utc_now.astimezone(cdmx_tz)
                
        hora_str = str(cdmx_time.strftime("%H:%M").replace(':', '.'))
        hora_float = float(hora_str)

        return hora_float
    
    def categoria_mas_parecida(self, cadena, lista_categorias):
        categoria_parecida = None
        distancia_minima = float('inf')
        
        for categoria in lista_categorias:
            distancia = Levenshtein.distance(cadena, categoria)
            
            if distancia < distancia_minima:
                distancia_minima = distancia
                categoria_parecida = categoria
                
        return categoria_parecida
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        confirmacion = tracker.get_slot("numero")
        telefono = tracker.get_slot("telefono")
        id_registro_venta = tracker.get_slot("id_registro_venta")
        dicc1 = None
        dicc2 = None

        validar_correo = tracker.get_slot("validar_correo")
        validar_factura = None
        correo = validar_correo
        if validar_correo == None:
            correo = tracker.get_slot("correo")


        registro_ventas = sheets["registro_ventas"]
        clase_google_sheet = GoogleSheet(registro_ventas)


        registrado_levenshtein = self.categoria_mas_parecida(confirmacion.lower(), ["registrado", "problema"])

        with open("credentials.yml", "r") as file:
            config = yaml.safe_load(file)
            telegram_token = config.get("telegram", {}).get("access_token", "")
            chat_id = config.get("telegram", {}).get("chat_id", "")

        with open("secrets.yml", "r") as file:
            config2 = yaml.safe_load(file)
            password = config2.get("password", {}).get("password", "")

        if registrado_levenshtein == "registrado":

            hoja1 = registro_ventas
            hoja1 = hoja1.get_all_values()
            df = pd.DataFrame(hoja1[1:], columns=hoja1[0])

            try:
                df = df[ (df["telefono"] == telefono) & (df["id_registro_venta"] == id_registro_venta) ][["id_registro_venta", "numero_registro", "nombre", "telefono", "fecha_registro", "hora_registro"]]
                nombre = df['nombre'].iloc[0]
            except:
                nombre = " "

            print(f"Nombre: {nombre}")

            validar_enlace = tracker.get_slot("validar_enlace")

            if (validar_enlace == True) and (len(df) == 1) and (nombre != " "):

                fecha_actual = self.fecha_actual()
                clase_google_sheet.update_cell_by_id(id_registro_venta, "hora_confirmacion", fecha_actual)
                clase_google_sheet.update_cell_by_id(id_registro_venta, "status_confirmacion", 1)

                response = f"{nombre}, tu pedido ha quedado registrado!\n"
                inmediato = tracker.get_slot("inmediato")

                if inmediato == None:
                    response += f"Si no recibes tu pedido en un tiempo a lo más de 30 min después de la hora programada, tu siguente compra es gratis!!\n"
                else:
                    response += f"Si no recibes tu pedido antes de las {self.obtener_hora_menos_30_min()} tu siguiente compra es gratis\n"
                response += f"\n"

                nombre_ = nombre
                telefono_ = telefono

                fecha_registro = tracker.get_slot("fecha_registro")
                hora_registro = tracker.get_slot("hora_registro")

                token_sesion = tracker.get_slot("token")

                registro_bebidas = sheets["registro_bebidas"]
                data = registro_bebidas.get_all_records()
                df = pd.DataFrame(data)[["token_sesion", "producto", "categoria", "subcategoria", "tipo_leche", "azucar_extra", "consideraciones", "precio"]]
                df["token"] = df["token_sesion"].apply(lambda x: x.split('_')[0])
                filter = df[df["token"] == token_sesion].drop(["token_sesion", "token"], axis=1)
                ticket_personalizacion = filter.to_dict(orient='records')

                data2 = registro_ventas.get_all_records()
                df2 = pd.DataFrame(data2)
                filter2 = df2[df2["token_sesion"] == token_sesion ][["direccion", "total"]]
                
                direccion = filter2['direccion'].iloc[0]
                total = filter2['total'].iloc[0]


                FILE_NAME = f"{id_registro_venta}.txt"


                preferencia = tracker.get_slot("preferencia_pedido")

                if inmediato == None:
                    hora= tracker.get_slot("hora")
                    mensaje_eleccion = f"Hora pedido programado {hora}"
                    if preferencia == "enviar":
                        mensaje_preferencia = "Enviar pedido programado"

                    else:
                        mensaje_preferencia = "Recogerá su pedido programado"

                else:
                    mensaje_eleccion = f"Entrega inmediata"
                    if preferencia == "enviar":
                            mensaje_preferencia = "Enviar pedido inmediato"
                    else: 
                            mensaje_preferencia = "Recogerá su pedido en cuanto antes"



                ticket_data = {
                                "id_registro_venta": id_registro_venta,
                                "Fecha de registro": fecha_registro,
                                "Hora de confirmación": fecha_actual,
                                "Nombre": nombre_,
                                "Correo": correo,
                                "Telefono": telefono,
                                "Elección de Entrega": mensaje_eleccion,
                                "Preferencia de Entrega": mensaje_preferencia,
                                "Dirección": direccion}
        
                
                clase = MensajesAutomatizados(FILE_NAME)
                clase.enviar(ticket_data, ticket_personalizacion, nombre, telefono_, "Efectivo", total, telegram_token, chat_id)

                dicc1 = ticket_data
                dicc2 = ticket_personalizacion

                response += f"Tu Ticket de compra es el siguiente: Hola\n"
                response += "\n"
                response += f"Si requieres factura, porfavor escribir *factura* y en breve te la haremos llegar."
                validar_factura = True

                nombre_validar = tracker.get_slot("nombre_validar") 
                clientes = sheets["clientes"]

                if nombre_validar == False:
                    clase_insert_data = InsertData(clientes)
                    procedencia_ = "Chatbot"
                    values = ["", nombre_, telefono_, correo, "", procedencia_]
                    clase_insert_data.insert_data(values)
                else:
                    clase_google_sheet = GoogleSheet(clientes)
                    clase_google_sheet.update_cell_by_id(telefono_, "nombre", nombre)


            else:
                response = "No se ha podido encontrar tu pedido, porfavor vuelve a crear un link escribiendo tu *Correo Electrónico*"

        else:
            clase_google_sheet.update_cell_by_id(id_registro_venta, "problema", "HAY PROBLEMAS EN REGISTRO")

            FILE_NAME = f"TicketVenta-{id_registro_venta}.txt"

            ticket_data = {"id_registro_venta": id_registro_venta,
                           "Teléfono": telefono,
                           "Correo": correo,
                           "Nombre": "HAY PROBLEMAS, COMUNICATE DE INMEDIATO CON ESTA PERSONA"}
            
            clase = MensajesAutomatizados(FILE_NAME)
            ticket_personalizacion = {}
            clase.enviar(ticket_data, ticket_personalizacion,  "PROBLEMAS", telefono, "NA", "NA", telegram_token, chat_id)
            # response += f"Tu ticket es el siguiente: {ticket}"

            response = "En breve se comunicarán contigo, gracias por la espera!."

        dispatcher.utter_message(text=response)
        return [SlotSet("programar", None), SlotSet("inmediato", None), SlotSet("telefono", None),  SlotSet("correo", None) ,SlotSet("hora", None), SlotSet("validar_factura", validar_factura), SlotSet("dicc1", dicc1), SlotSet("dicc2", dicc2), SlotSet("password", password)]
    
    # -----------------------------------------------------------------------------------------------------------------------------------------

class ActionRegistroCorreoElectronico(Action):

    def name(self) -> Text:
        return "action_factura"
    
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        validar_factura = tracker.get_slot("validar_factura")

        if validar_factura == True:

            ticket_data = tracker.get_slot("dicc1")
            
            fecha = ticket_data["Fecha de registro"]


            ticket_data = {
                "Num. Venta": ticket_data["id_registro_venta"],
                "Nombre Cliente": ticket_data["Nombre"],
                "Correo Electronico": ticket_data["Correo"],
                "Teléfono": ticket_data["Telefono"],
            }

            ticket_productos = tracker.get_slot("dicc2")
            
            password = tracker.get_slot("password")
  
            pdf_buffer = generar_factura(ticket_data, ticket_productos, fecha)
            enviar_factura_por_correo(ticket_data, pdf_buffer, password)
            
            response = "Se te ha enviado tu Factura por Correo Electrónico\n"
            response += "Si tienes algun problema para acceder, no te haya llegado el correo, lo que sea que este sucediendo\n"
            response += "comunicate directamente con nosotros y en breve nos pondremos en contacto contigo: +525565637294"

        else:
            response = "No tenemos ningun registro de tu pedido, favor de escribir tu *Correo Electrónico*"

        dispatcher.utter_message(text=response)
        return [SlotSet("validar_factura", None), SlotSet("dicc1", None), SlotSet("dicc2", None)]

        