#archivo -->Data cruda
#excel -->Tipo de digestion y elementos.
#limite -->Porcentaje de censura
#NR --> Valor que aparece en las columnas (son como vacios que se tienen que eliminar)
#EP -->Elementos pathfinders que a pesar que no se encuentren como adecuados para el tipo de metodo de analisis se usa por razones geoquimicas.

import pandas as pd
import numpy as np
import geopandas as gpd

DATA=pd.read_excel("/content/DATA_MADRE.xlsx")
EXCEL=pd.read_excel("/content/VERIFICACION_DE_ELEMENTOS.xlsx")
metodo="4 acidos"
limite=45
NR="N.R."
EP=["Co","Ag","Mo","Au"]



class Purga():
    def __init__(self,archivo,excel,metodo,limite,NR,EP):
        self.archivo=archivo
        self.excel=excel
        self.metodo=metodo
        self.limite=limite
        self.NR=NR
        self.EP=EP
    def base(self):
  
      #Borramos la data que no sirve 
      columna=list( self.archivo.columns)
      columna_vacia=[]
      for i in columna:
        if  self.archivo[i].dtype=="object" and all (self.archivo[i].isin([self.NR])):
            columna_vacia.append(i)
      self.archivo=self.archivo.drop(columna_vacia,axis=1)

      #Usamos un archivo EXCEL con el que vamos a discriminar los elementos que  son aptos.

      metodo=self.excel[(self.excel["1ER METODO"]==self.metodo) | (self.excel["2DO METODO"]==self.metodo)]
      elementos=list(metodo["SIMBOLO"])
      self.elementos=elementos

      elementos_guardados=self.archivo.iloc[:,:25].copy()

      #Es bien sabido que se aceptaran otros elementos de modo que serviran como PATHFINDERS.

      for i in self.archivo.iloc[:,25:].columns:
        if i[:2] in EP:
          elementos_guardados[i]=self.archivo[i].copy()

      self.elementos_guardados=elementos_guardados.iloc[:,25:].copy()


      for x in self.archivo.iloc[:,25:].columns:
        if x[:2] not in self.elementos:
          self.archivo=self.archivo.drop(x,axis=1)

      for guardado in self.elementos_guardados.columns:
        if guardado not in list(self.archivo.iloc[:,25:].columns):
          self.archivo[guardado]=self.elementos_guardados[guardado].copy()

      #Identificar columnas con poblaciones con bajo limite de deteccion.

      for i in self.archivo.iloc[:,25:]:
        self.archivo[i] = self.archivo[i].astype(object)

      censura={}

      for i  in self.archivo.iloc[:,25:]:
        c=0
        for j in range(0,len(self.archivo)):
          if (str(self.archivo[i][j]).startswith("<")):
            c+=1
        d=round(((c*100)/len(self.archivo)),2)

        censura[i]=d

      for i in censura.keys():
        if censura.get(i)==100:
          self.archivo=self.archivo.drop(i,axis=1)
        elif censura.get(i)>self.limite:
          ubicacion=self.archivo.iloc[:,:25].copy()
          ubicacion[i]=self.archivo[i]

          for y in range(0,len(ubicacion)):
            if  str(ubicacion[i][y]).startswith("<"):
              ubicacion=ubicacion.drop(y)
          self.ubicacion=gpd.GeoDataFrame(ubicacion,geometry=gpd.points_from_xy(ubicacion.Longitud_X,ubicacion.Latitud_Y))
          self.ubicacion.plot()


Purga(DATA,EXCEL,metodo,limite,NR,EP).base()
      
