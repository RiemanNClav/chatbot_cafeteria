
import pandas as pd

class Precios():
    def __init__(self, sheet_name):
        self.sheet_name = sheet_name

    def obtener_precios(self):

        hoja1 = self.sheet_name
        data = hoja1.get_all_records()

        df = pd.DataFrame(data)
        
        #categoria_bebidas dicc
        dicc = {}
        df1 = df[df["producto"] == "bebida"]
        df1["precio"] = df1["precio"].astype("str")
        df1["concatenar"] = df1["subcategoria"] + ' - ' + df1["precio"] + ' ' + df1["moneda"]
        categorias = df1.categoria.unique()
        for categoria in categorias:
            aux = list(df1[df1["categoria"] == categoria ].concatenar.unique())
            dicc[categoria] = aux

        return dicc


if __name__ == "__main__":
    clase = GoogleDrive()
    clase.obtener_datos_sheet("registro_ventas")