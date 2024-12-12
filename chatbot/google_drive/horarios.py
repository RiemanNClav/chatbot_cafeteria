import os 
import re 
from datetime import datetime, timedelta
from dataclasses import dataclass
import pytz


@dataclass
class HorariosConfig:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        horarios_path: str=os.path.join(base_dir, 'horarios', "horarios.csv")
        horarios_particulares_path: str=os.path.join(base_dir, 'horarios', "horario_particular.txt")


class Horarios:
        def __init__(self):
                self.horarios_config = HorariosConfig()

        def leer_txt_en_lista(self, archivo):

                with open(archivo, 'r') as file:
                        lineas = [linea.strip() for linea in file.readlines()]

                return lineas
        
        def fecha_actual(self):
                utc = pytz.utc
                cdmx_tz = pytz.timezone("America/Mexico_City")
                utc_now = datetime.now(utc)
                cdmx_time = utc_now.astimezone(cdmx_tz)
                
                # hora_actual = datetime.now()
                dia_despues = cdmx_time - timedelta(days=1)
                hora_actual2 = cdmx_time.strftime("%H:%M")
                fecha_actual = cdmx_time.strftime("%Y-%m-%d")

                dicc = {
                        'Monday': 'lunes',
                        'Tuesday': 'martes',
                        'Wednesday': 'miercoles',
                        'Thursday': 'jueves',
                        'Friday': 'viernes',
                        'Saturday': 'sabado',
                        'Sunday': 'domingo'}
                
                dia_despues = int(dia_despues.strftime("%Y-%m-%d").split('-')[2])
                fecha_actual = cdmx_time.strftime("%Y-%m-%d")
                dia_actual = int(fecha_actual.split('-')[2])
                mes_actual = int(fecha_actual.split('-')[1])
                
                nombre_dia_actual = cdmx_time.strftime("%A")
                nombre_dia = dicc[nombre_dia_actual]

                return fecha_actual, dia_actual, nombre_dia, mes_actual, hora_actual2, dia_despues
        
        def fecha_mes_siguiente(self, dia, mes):
                hoy = datetime.now()
                año_actual = hoy.year

                if mes == 12:
                        mes_siguiente = 1
                        año_siguiente = año_actual + 1
                else:
                        mes_siguiente = mes + 1
                        año_siguiente = año_actual
                
                try:
                        fecha_siguiente = datetime(año_siguiente, mes_siguiente, dia)
                        return fecha_siguiente.strftime("%Y-%m-%d")
                except ValueError:
                        return "Fecha no válida (ej. no existe el 30 de febrero)"
        
        def resumir_horarios(self, horarios) -> list:
                horario_habitual='HORARIO HABITUAL\n'
                dias_ordenados = list(horarios.items())
                resumen = []
                inicio = dias_ordenados[0][0]
                anterior_horario = dias_ordenados[0][1]
                for i in range(1, len(dias_ordenados)):
                        dia, horario = dias_ordenados[i]
                        if horario != anterior_horario:
                                if inicio == dias_ordenados[i-1][0]:
                                        resumen.append(f"{inicio} de {anterior_horario}")
                                else:
                                        resumen.append(f"{inicio} a {dias_ordenados[i-1][0]} de {anterior_horario}")
                                
                                inicio = dia
                                
                        anterior_horario = horario
        
                if inicio == dias_ordenados[-1][0]:
                        resumen.append(f"{inicio} de {anterior_horario}")
                else:
                        resumen.append(f"{inicio} a {dias_ordenados[-1][0]} de {anterior_horario}")

                
                for r in resumen:
                        horario_habitual += r + '\n'

                return resumen

        def expand_days(self, responses: list):
                horario_particular = 'HORARIO PARTICULAR\n'
                days_schedule = {}
                resumen = []
                for response in responses:
                        r = response.replace('[', "").replace("]", "")
                        horario_particular += r + '\n'
                        resumen.append(r)
                        pattern = r'\[(.*?)\]'
                        matches = re.findall(pattern, response)
                        
                        date_pattern = r'\w+\s(\d+)'
                        
                        horario = re.search(r'(\d{1,2}(am|pm)-\d{1,2}(am|pm))', response).group(0)
                        
                        for match in matches:
                                dates = re.findall(date_pattern, match)
                                if "al" in match:
                                        start_date = int(dates[0])
                                        end_date = int(dates[1])
                                        
                                        for day in range(start_date, end_date + 1):
                                                days_schedule[day] = horario
                                
                                else:
                                        for date in dates:
                                                day = int(date)
                                                days_schedule[day] = horario
                
        
                return days_schedule, resumen
        
        def print_horario(self, horario_habitual: dict, horario_particular: list):
                # horarios = pd.read_csv(self.horarios_config.horarios_path)
                # horario_general = dict(zip(horarios.dia, horarios.horario_habitual))

                horario_general = horario_habitual
                # particulares = self.horarios_config.horarios_particulares_path
                particulares = horario_particular

                horario_habitual = self.resumir_horarios(horario_general)
                # lista_renglones = self.leer_txt_en_lista(particulares)
                lista_renglones = particulares
                if lista_renglones != []:
                        particulares, horario_particular = self.expand_days(lista_renglones)
                        aux = ["2"]
                else:
                        aux = ["1"]
                        particulares = ["1"]
                        horario_particular = ["2"]
                
                dicc = {"particulares": aux,
                        "horario_particular": horario_particular,
                        "horario_habitual": horario_habitual}
                
                return dicc, horario_general, particulares
                
        def horario(self, horario_habitual: dict, horario_particular: list):
                fecha_actual_str, dia_actual, nombre_dia, mes_actual, hora_actual, dia_anterior = self.fecha_actual()
                _, horario_general, particulares = self.print_horario(horario_habitual, horario_particular)
                ## QUIERE DECIR QUE NO HAY PARTICULARES
                if particulares == ['1']:
                        dia = horario_general[nombre_dia]

                else:
                        if dia_actual in list(particulares.keys()):
                                dia = particulares[dia_actual]

                        else:
                                dia = horario_general[nombre_dia]

                                particular_maximo = max(particulares.keys())
                                dia_totales = [i for i in range(0,dia_actual)]
                                fecha_particularidad_siguiente_str = self.fecha_mes_siguiente(dia_actual, mes_actual)
                                fecha_particularidad_siguiente = datetime.strptime(fecha_particularidad_siguiente_str, "%Y-%m-%d")
                                fecha_actual = datetime.strptime(fecha_actual_str, "%Y-%m-%d")
                                diff_fechas = fecha_particularidad_siguiente - fecha_actual
                                # CASO 1 SI DIA ACTUAL > QUE LA PARTICULARIDAD MAXIMA
                                if dia_actual > particular_maximo:
                                        os.remove(self.horarios_config.horarios_particulares_path)

                                # CASO 2: 
                                elif dia_actual <= particular_maximo and (diff_fechas in dia_totales):
                                        os.remove(self.horarios_config.horarios_particulares_path)

                horarios_am = {str(i)+'am': str(i) for i in range(1,13)}
                horarios_pm = dict(zip( [str(i)+'pm' for i in range(1,12)], [str(i) for i in range(13,24)] ))
   
                estandarizacion_horarios = horarios_am | horarios_pm

                horario_trabajo = dia.split('-')
                
                inf_hora = int(estandarizacion_horarios[horario_trabajo[0]])
                sup_hora = int(estandarizacion_horarios[horario_trabajo[1]])
                hora_entera = float(hora_actual.replace(":", '.'))

                botton2=0
                
                if (inf_hora <= hora_entera) and (hora_entera <= sup_hora):
                        disponiblidad = 'Si tenemos servicio!!\n'
                        botton = 1
                else:
                        botton = 0
                        if hora_entera < inf_hora:
                                disponiblidad = f"Aun no tenemos servicio,  te recordamos que nuestro horario es de {dia}, gracias"
                                botton2 = 1
                        elif hora_entera > sup_hora:
                                disponiblidad = f"Lo siento, ya hemos cerrado, te recordamos que nuestro servicio fue de {dia}, gracias"
                                botton2 = 2

                dicc = {"botton": botton,
                        "botton2": botton2,
                        "dia": dia}
                
                return dicc
                
        def action_acotar_ubicacion(self, horario, horario_particular):
            
            dicc = self.horario(horario, horario_particular)

            return dicc

        def action_get_horario(self, horario, horario_particular):

            dicc, _, _ = self.print_horario(horario, horario_particular)

            return dicc
    
        
if __name__=="__main__":
        
        horario = sheets["horarios"]

        horarios = {"lunes": "8am-8pm", }
        horario_particular = sheets["horario_particular"]

        diccionario1, diccionario2 = clase_google_drive.preprocesamiento_horarios(horario, horario_particular)
        dicc = clase_horarios.action_acotar_ubicacion(diccionario1, diccionario2)

        botton = dicc["botton"]
        botton2 = dicc["botton2"]
        dia = dicc["dia"]
