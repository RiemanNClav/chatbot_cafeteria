from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


import random
from datetime import datetime, timedelta
import uuid
import requests
import pandas as pd
import os


##MODULOS
##---------------------------------------------------##
from google_drive.preprocesamiento_sheets import GoogleDrive, GoogleSheet, InsertData
from google_drive.horarios import Horarios
##---------------------------------------------------##

clase_google_drive = GoogleDrive()

clase_horarios = Horarios()

sheets = clase_google_drive.obtener_sheets()

APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:5056')

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


        response = "HORARIO HABITUAL\n"
        request_horario_habitual = horario_habitual
        for resp in request_horario_habitual:
            response += f"{resp}\n"

        if particulares == ['2']:
            response += "HORARIO PARTICULAR\n"
            request_horario_particular = horario_particular
            for resp in request_horario_particular:
                response += f"{resp}\n"
            
        response += '\n'

        response += "Realiza tu pedido escribiendo 'hacer pedido', de lo contrario consulta otra opción del panel."

        dispatcher.utter_message(text=response)

        return []    
## -----------------------------------ACOTAR UBICACION------------------------------------------

# class ActionGetAcotarUbicacion(Action):

#     def name(self) -> Text:
#         return "action_acotar_ubicacion"
    

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         api = GoogleDrive()
#         dicc = api.action_acotar_ubicacion()
#         botton = dicc["botton"]
#         botton2 = dicc["botton2"]
#         dia = dicc["dia"]

#         if botton == 1:
#             disponiblidad = 'Si tenemos servicio!!\n'
#             disponiblidad += "Perfecto, gracias por tu confianza\n"
#             disponiblidad += "\n"
#             disponiblidad += "Antes de comenzar, queremos validar tu *DIRECCION*, ingresala manualmente:\n"

#         else:
#             if botton2 == 1:
#                 disponiblidad = f"Aun no tenemos servicio,  te recordamos que nuestro horario es de {dia}, gracias"
#             elif botton2 == 2:
#                 disponiblidad = f"Lo siento, ya hemos cerrado, te recordamos que nuestro servicio fue de {dia}, gracias"


#         dispatcher.utter_message(text=disponiblidad)

#         return [] 
    
## ---------------------------------------------VALIDAR TELEFONO--------------------------------------------------------
class ActionGetAcotarUbicacion(Action):

    def name(self) -> Text:
        return "action_validar_telefono"
    

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
            disponiblidad += "Antes de comenzar, queremos validar tu *NUMERO DE TELEFONO*, ingresalo porfavor:\n"

        else:
            if botton2 == 1:
                disponiblidad = f"Aun no tenemos servicio,  te recordamos que nuestro horario es de {dia}, gracias"
            elif botton2 == 2:
                disponiblidad = f"Lo siento, ya hemos cerrado, te recordamos que nuestro servicio fue de {dia}, gracias"


        dispatcher.utter_message(text=disponiblidad)

        return [] 


## --------------------------------------------HACER PEDIDO-----------------------------------------------------

# class ActionGetPedido(Action):

#     def name(self) -> Text:
#         return "action_registro_nombre"
    

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         api = ApiAddress()
#         direccion = tracker.get_slot("direccion")

#         try:
#             result, radio, distancia = api.bola_cerrada(direccion)
#             print(f"radio: {radio}")
#             print('------------------')
#             print(f"distancia: {distancia}")
#             if result == 1:
#                 response = "Increible, Si tenemos cobertura hasta tu direción!!"
#                 response += "\n"
#                 response += "Te comparto brevemente un [link](https://elevenlabs.io/app/speech-synthesis), por favor llénalo.\n"
#                 response += "Una vez completado, escribe el NUMERO DE REGISTRO que se te proporcionó:"
#             else:
#                 response = "Lo siento, pero nuestros repartidores locales no llegan hasta tu ubicación :(\n"
#                 response += "te invito a que hagas tu pedido por uber eats, te comparto brevemente un link, *enviar link*"
#         except:
#             response = "Lo siento, no hemos podido encontrar tu dirección, vuelve a escribirla porfavor\n"

#         dispatcher.utter_message(text=response)

#         return [] 
    
## ----------------------------------------------------HACER PEDIDO 2--------------------------------------------
class ActionGetPedido(Action):

    def name(self) -> Text:
        return "action_registro_telefono"
    
    def fecha_actual(self):

        fecha = datetime.now()
        fecha_str = fecha.strftime("%Y-%m-%d")
                
        hora_str = str(fecha.strftime("%H:%M").replace(':', '.'))
        hora_float = float(hora_str)


        return fecha_str, hora_float

    def numeros_aleatorios(self):
        numero = random.randint(1,2000)
        return numero
    
    def convertir_telefono_id(self, numero_telefono):
        numero_str = str(numero_telefono)
        id_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, numero_str))
        return id_uuid
    
    def request(self, id_registro_venta, token_sesion):
                                    
            # Enviar el token y el teléfono a Flask
            url = f"{APP_BASE_URL}/guardar_token"

            data = {
                "id_registro_venta": id_registro_venta,
                "token_sesion": token_sesion
            }

            response = requests.post(url, json=data)
            if response.status_code == 200:
                print('se ha enviado')
                return response.json()['enlace']
            else:
                print("No se envio")


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        telefono = tracker.get_slot("telefono")
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
            enlace = self.request(id_registro_venta, token)

            response = f"Te comparto brevemente un link {enlace}, por favor llénalo.\n"
            response += "Una vez completado, escribe *registrado*, asi podremos confirmarlo."
            response += "\n"
            dispatcher.utter_message(text=response)

            response = "CONSIDERACIONES"
            response += "\n"
            response += "1. El link solo permite un click, si apretaste y saliste sin completar, tendrás que volver a ingresar tu número "
            response += "\n"
            response += "2. Si tuviste algun problema accediendo al link, o algo no salio bien, escribe *problema* "
            dispatcher.utter_message(text=response)

            return [SlotSet("id_registro_venta", id_registro_venta)]
        
        except:
            response = "Ha habido un problema, vuelve a ingresar tu número porfavor."
            dispatcher.utter_message(text=response)

        return []

#------------------------------------------------------CONFIRMAR PEDIDO--------------------------------------------
    
class ActionSaveData(Action):
    def name(self) -> Text:
        return "action_save_data"
    

    def obtener_hora_menos_30_min(self):
        hora_actual = datetime.now()
        nueva_hora = hora_actual + timedelta(minutes=30)

        hora = int(nueva_hora.strftime("%H:%M").split(':')[0])


        if hora in list(range(12, 19)):
            return f'{nueva_hora.strftime("%H:%M")} de la tarde'
        elif hora in list(range(19, 24)):
            return f'{nueva_hora.strftime("%H:%M")} de la noche'
        else:
            return f'{nueva_hora.strftime("%H:%M")} de la mañana'
        

    def fecha_actual(self):
        fecha = datetime.now()
                
        hora_str = str(fecha.strftime("%H:%M").replace(':', '.'))
        hora_float = float(hora_str)

        return hora_float
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        confirmacion = tracker.get_slot("numero")

        id_registro_venta = tracker.get_slot("id_registro_venta")

        if confirmacion.lower() == "registrado":
            
            telefono = tracker.get_slot("telefono")
            
            registro_ventas = sheets["registro_ventas"]
            hoja1 = registro_ventas
            hoja1 = hoja1.get_all_values()
            df = pd.DataFrame(hoja1[1:], columns=hoja1[0])

            df = df[ (df["telefono"] == telefono) & (df["id_registro_venta"] == id_registro_venta) ][["id_registro_venta", "numero_registro", "nombre", "telefono", "fecha_registro", "hora_registro"]]
            nombre = df['nombre'].iloc[0] if not df.empty else None
            clase_google_sheet = GoogleSheet(registro_ventas)

            if nombre != None:

                procedencia = "Chatbot"
                clase_google_sheet.update_cell_by_id(id_registro_venta, "hora_confirmacion", self.fecha_actual())
                clase_google_sheet.update_cell_by_id(id_registro_venta, "status_confirmacion", 1)

                response = f"{nombre}, tu pedido ha quedado registrado, espera máxima de 30 min\n"
                response += f"si no recibes tu pedido antes de las {self.obtener_hora_menos_30_min()}, (siempre y cuando haya sido aceptado)  tu siguiente compra es gratis\n"
                response += f"(si quieres ver el seguimiento, escribe 'seguimiento pedido')"
                response += f"\n"

                clientes = sheets["clientes"]
                clase_insert_data = InsertData(clientes)

                data = clientes.get_all_records()
                df = pd.DataFrame(data)
                numero_clientes = list(df.telefono.unique())

                if telefono not in numero_clientes:
                    correo_electronico = tracker.get_slot("correo")
                    nombre_ = nombre
                    telefono_ = telefono
                    correo = correo_electronico
                    procedencia_ = procedencia

                    values = [nombre_, telefono_, correo, procedencia_]
                    clase_insert_data.insert_data(values)
                else:
                    pass

            else:
                response = "No se ha podido encontrar tu pedido, porfavor vuelve a crear un link, escribiendo 'hacer pedido'"

        else:
            clase_google_sheet.update_cell_by_id(id_registro_venta, "problemas", "HAY PROBLEMAS EN REGISTRO")
            response = "Te comparto el telefono de Tory Cafe, para que puedas llamar y puedan atenderte en breve."


        dispatcher.utter_message(text=response)
        return []
    
