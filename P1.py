#archivo -->Data cruda
#excel -->Tipo de digestion y elementos.
#limite -->Porcentaje de censura
#NR --> Valor que aparece en las columnas (son como vacios que se tienen que eliminar)
#EP -->Elementos pathfinders que a pesar que no se encuentren como adecuados para el tipo de metodo de analisis se usa por razones geoquimicas.

import pandas as pd
import numpy as np

DATA=pd.read_excel("/content/DATA_MADRE.xlsx")
EXCEL=pd.read_excel("/content/VERIFICACION_DE_ELEMENTOS.xlsx")
NR=input("Alguna de sus columnas esta llena de un simbolo o dos letras en TODA esa columna ,si es asi  INDICA CUAL ES LA LETRA .")
EP=input("De igual manera ,tienes que identificar cuales elementos seran tus mas importantes sin contabilizar ")
metodo=input("Colocar el nombre de la digestion a usar : Ejemplo -->  4 acidos")
class Purga():
    def __init__(self,archivo,excel,metodo,limite,NR,EP):
        self.archivo=archivo
        self.excel=excel
        self.metodo=metodo
        self.limite=limite
        self.NR=NR
        self.EP=EP
    def base(self):
        metodo=self.excel[(self.excel["1ER METODO"]==self.metodo) | (self.excel["2DO METODO"]==self.metodo)]
        elementos=list(metodo["SIMBOLO"])