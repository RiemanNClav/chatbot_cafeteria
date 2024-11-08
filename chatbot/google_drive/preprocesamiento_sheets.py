import pandas as pd
import uuid

import gspread
from google.oauth2.service_account import Credentials

class GoogleDrive:
    def __init__(self):
        pass

    def access(self):
        ruta_credenciales = "google_drive/credentials-service-account.json"   
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

        return ruta_credenciales, scopes
    
    def obtener_sheets(self):
        ruta_credenciales, scopes = self.access()

        credenciales = Credentials.from_service_account_file(ruta_credenciales, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        
        base_datos = cliente.open("base_datos_tory_cafe")
        sheets = {
            "registro_ventas": base_datos.get_worksheet(0),
            "registro_bebidas": base_datos.get_worksheet(1),
            "precios": base_datos.get_worksheet(2),
            "clientes": base_datos.get_worksheet(3),
            "horarios": base_datos.get_worksheet(4),
            "horario_particular": base_datos.get_worksheet(5)
        }

        return sheets
        
        # .get_worksheet(2)
        # data = hoja1.get_all_records()

    def preprocesamiento_horarios(self, horarios, horario_particular):

        ## HORARIO HABITUAL
        diccionario1 = dict((horarios.get_all_values()[1:]))

        ## HORARIO PARTICULAR
        diccionario2 = dict(horario_particular.get_all_values()[1:])
        diccionario2 = list(diccionario2.values())

        return diccionario1, diccionario2
    

class GoogleSheet:
    def __init__(self, sheet_name):
        self.sheet = sheet_name

    def read_data(self, range): #range = "A1:E1". Data devolvera un array de la fila 1 desde la columna A hasta la E
        data = self.sheet.get(range)
        return data

    def read_data_by_uid(self, uid):
        data = self.sheet.get_all_records()
        df = pd.DataFrame(data)
        print(df)
        filtered_data = df[df['uid'] == uid]
        return filtered_data #devuelve un data frame de una tabla, de dos filas siendo la primera las cabeceras de las columnas y la segunda los valores filtrados para acceder a un valor en concreto df["nombre"].to_string()
    
    def write_data(self, range, values): #range ej "A1:V1". values must be a list of list
        self.sheet.update(range, values)

    def write_data_by_uid(self, uid, values): 
        # Find the row index based on the UID
        cell = self.sheet.find(uid)
        row_index = cell.row
        # Update the row with the specified values
        self.sheet.update(f"A{row_index}:E{row_index}", values)

    def get_last_row_range(self):   
        last_row = len(self.sheet.get_all_values()) + 1
        deta = self.sheet.get_values()
        range_start = f"A{last_row}"
        range_end = f"{chr(ord('A') + len(deta[0]) - 1)}{last_row}"
        return f"{range_start}:{range_end}"
    
    def get_all_values(self):
        #self.sheet.get_all_values () # this return a list of list, so the get all records is easier to get values filtering
        return self.sheet.get_all_records() # thislar colum
    
    def delete_row_by_uid(self, uid):
        try:
            # Buscar el UID en la hoja
            cell = self.sheet.find(uid)
            row_index = cell.row
            # Borrar la fila
            self.sheet.delete_rows(row_index)
            print(f"Fila con UID {uid} borrada exitosamente.")
        except gspread.exceptions.CellNotFound:
            print(f"UID {uid} no encontrado.")

    def update_cell_by_id(self, id_registro_venta, column_name, new_value):
        try:
            # Buscar la fila del UID
            data = self.sheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Encontrar el índice de la columna
            col_index = df.columns.get_loc(column_name) + 1  # +1 porque las columnas empiezan desde 1 en Google Sheets

            # Buscar el UID en la hoja
            cell = self.sheet.find(id_registro_venta)
            row_index = cell.row

            # Actualizar el valor en la celda específica
            self.sheet.update_cell(row_index, col_index, new_value)
            print(f"Celda en la fila {row_index}, columna '{column_name}' actualizada a '{new_value}'.")
        except gspread.exceptions.CellNotFound:
            print(f"UID {id_registro_venta} no encontrado.")
        except KeyError:
            print(f"Columna '{column_name}' no encontrada.")
    

class InsertData:
    def __init__(self, sheet_name):
        self.sheet = sheet_name

    def insert_data(self, values):
        clase = GoogleSheet(self.sheet)

        
        value = [values]
        range = clase.get_last_row_range()
        clase.write_data(range, value)


if __name__=="__main__":
    values = ["1", "2", "token", "numero_registro", 
                " ", "telefono", " ", "fecha_registro", 
                "hora_registro", " ", 1, " ", " ", " ", " ", " "]
        
    clase_insert_data = InsertData("registro_ventas")
    clase_insert_data.insert_data(values)