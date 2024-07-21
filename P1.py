#archivo -->Data cruda
#excel -->Tipo de digestion y elementos.
#limite -->Porcentaje de censura
#NR --> Valor que aparece en las columnas (son como vacios que se tienen que eliminar)
#EP -->Elementos pathfinders que a pesar que no se encuentren como adecuados para el tipo de metodo de analisis se usa por razones geoquimicas.

import os
import pandas as pd
import numpy as np
import geopandas as gpd

import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import LineString, Point, Polygon

DATA=pd.read_excel("/content/DATA_MADRE.xlsx")
EXCEL=pd.read_excel("/content/VERIFICACION_DE_ELEMENTOS.xlsx")
metodo="4 acidos"
limite=45
NR="N.R."
EP=["Co","Ag","Mo","Au"]

#OJITO  AQUI SE CODIFICA CON JUPYTER DEBIDO A LOS LIMITES DE COLAB
#Ten cuidado con el sistema de referencia que se usa ,eso puede generar complicaciones
#Data shaperfile de la litologia.
#Data shaperfile de cuenca

os.environ['SHAPE_RESTORE_SHX'] = 'YES'

SHAPE_GE=gpd.read_file("/content/SHAPE_GEOLOGIA.shp")
SHAPE_CUEN=gpd.read_file("/content/SHAPE_CUENCAS.shp")


class Purga():
    
    #Definimos los parametros 
    def __init__(self,archivo,excel,metodo,limite,NR,EP,geologia):
        self.archivo=archivo
        self.excel=excel
        self.metodo=metodo
        self.limite=limite
        self.NR=NR
        self.EP=EP
        self.geologia=geologia
        
    #Creamos una funcion llamada base .
    def base(self):
    
    #Borramos la data que no sirve
    
        #Dentro de la variable columna colocamos los nombres de las columnas
        columna=list(self.archivo.columns)
    
        #Creamos una variable llamada columna vacia ,aqui se almacenaran los nombres de las columnas que tienen valores vacios .
        columna_vacia=[]
    
        #Realizamos un ciclo for de modo que me indique las columnas con datos vacios.
        for i in columna:
            if  self.archivo[i].dtype=="object" and all (self.archivo[i].isin([self.NR])):
                columna_vacia.append(i)
    
        #Se eliminan las columnas.
        self.archivo=self.archivo.drop(columna_vacia,axis=1)
    
    #Usamos un archivo EXCEL con el que vamos a discriminar los elementos que  son aptos.
    
        #Identificamos los elementos que cumplen con el tipo de digestion.
        metodo=self.excel[(self.excel["1ER METODO"]==self.metodo) | (self.excel["2DO METODO"]==self.metodo)]
        elementos=list(metodo["SIMBOLO"])
        
        #En la variable se guardan como lista los elementos que cumplen con la digestion.
        self.elementos=elementos
    
        #Es necesario tener presentes elementos que a pesar de que no sean aptos en la digestion.Se tiene que colocar debido a que son utiles en el analisis
        #Es por eso que es necesario agregarlos.
        
        #Creamos una copia de la tabla pero solo de los datos descriptivos.
        elementos_guardados=self.archivo.iloc[:,:25].copy()
    
    
        #Se incorporan los elementos a la tabla copia creada .
        for i in self.archivo.iloc[:,25:].columns:
            if i[:2] in EP:
                elementos_guardados[i]=self.archivo[i].copy()
    
        self.elementos_guardados=elementos_guardados.iloc[:,25:].copy()
    
    
        #Aqui eliminamos las columnas que no estan dentro de los elementos aceptables para la digestion.
        for x in self.archivo.iloc[:,25:].columns:
            if x[:2] not in self.elementos:
                self.archivo=self.archivo.drop(x,axis=1)
        
        #Aqui incorporamos los elementos pathfinders.
        for guardado in self.elementos_guardados.columns:
            if guardado not in list(self.archivo.iloc[:,25:].columns):
                self.archivo[guardado]=self.elementos_guardados[guardado].copy()
            
    
        #Primero convertimos las columnas en tipo de dato "object" debido a que hay valores "<" y ">"
        for i in self.archivo.iloc[:,25:]:
            self.archivo[i] = self.archivo[i].astype(object)
    
        #Creamos un diccionario que va a almacenar los porcentajes de elementos "<" tiene cada columna.
        censura={}
    
        #Se hace un ciclo for para identificar los %.
        for i  in self.archivo.iloc[:,25:]:
            c=0
            for j in range(0,len(self.archivo)):
                if (str(self.archivo[i][j]).startswith("<")):
                    c+=1
            d=round(((c*100)/len(self.archivo)),2)
    
            censura[i]=d
        #Si la cantidad de datos "<" es 100% se elimina la columna.
        censura_copy = censura.copy()
    
        for i in censura_copy.keys():
          if censura.get(i)==0:
            del censura[i]
    
        for i in censura.keys():
            
            if censura.get(i)==100:
                self.archivo=self.archivo.drop(i,axis=1)
                
            elif censura.get(i)>self.limite:
                ubicacion=self.archivo.iloc[:,:25].copy()
                
                ubicacion[i]=self.archivo[i]
    
                for y in range(0,len(ubicacion)):
    
                    if  str(ubicacion[i][y]).startswith("<"):
                        
                        ubicacion=ubicacion.drop(y)
                        
    
                geoubicacion=gpd.GeoDataFrame(ubicacion,geometry=gpd.points_from_xy(ubicacion.Longitud_X,ubicacion.Latitud_Y),crs='EPSG:4326')
    
                self.geologia=self.geologia.to_crs(epsg=4326)
    
                xmin =geoubicacion.geometry.x.min()
                ymin =geoubicacion.geometry.y.min()
                xmax =geoubicacion.geometry.x.max()
                ymax =geoubicacion.geometry.y.max()
    
                square_vertices = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]
                square_polygon = Polygon(square_vertices)
                square_gdf = gpd.GeoDataFrame( geometry=[square_polygon],crs="EPSG:4326")
    
                interseccion=gpd.overlay(self.geologia,square_gdf,how="intersection")
    
                fig,ax=plt.subplots(1)
    
                interseccion.plot(ax=ax,column="UNIDAD")
                geoubicacion.plot(ax=ax,color="black")
                ax.set_title(f"Distribucion de la poblacion del elemento: {i}")
                plt.show()
    
                rpta=int(input("Respecto a la poblacion identificada ¿Los puntos estan dispersos o estan agrupados? \n  Desagrupado --> 0 \n  Agrupado    --> 1 \n \n  RESPUESTA :  "))
                print("\n")
                while rpta not in [0,1]:
                    rpta=int(input("Respecto a la poblacion identificada ¿Los puntos estan dispersos o estan agrupados? \n  Desagrupado --> 0 \n  Agrupado    --> 1 \n \n RESPUESTA : "))
          
                if rpta==0:
                    self.archivo=self.archivo.drop(i,axis=1)
                    
                elif rpta==1:
                    self.archivo[i] = self.archivo[i].apply(lambda x: None  if str(x)=="<1" else x) 
                    
        for i in censura_copy.keys():
          if censura.get(i)==100:
            del censura[i]
        
        for i  in censura.keys():
          if i in self.archivo.iloc[:,25:].columns:
            for j in range(0,len(self.archivo)):
              if str(self.archivo[i][j]).startswith("<") :
                  self.archivo[i][j]=str(float(self.archivo[i][j][1:])/2)
                  
        for i in self.archivo.iloc[:,25:].columns:
          for j in range(0,len(self.archivo)):
            if str(self.archivo[i][j]).startswith(">"):
              self.archivo[i][j]=str(float(self.archivo[i][j][1:])+0.1)
              
            self.archivo[i] = self.archivo[i].astype(object)  
              
        for i in self.archivo.iloc[:,25:].columns:
          self.archivo[i] = self.archivo[i].astype(float)

        return self.archivo
        
cruda =Purga(DATA,EXCEL,metodo,limite,NR,EP,SHAPE_GE).base()
