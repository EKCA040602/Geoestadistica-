from ELIMINACION_DE_OUTLIERS.py import cruda_log,sin_outliers,datos_normalizados
#Lo primero que se va a hacer es discriminar la data importante.Es decir la que cumple con una distribucion normal
#Aqui se observa la correlacion de Pearson y un clustering Jerarquico para agrupar como medida de distancia la correlacion de Pearson.

from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt

class Correlacion():
  def __init__(self,datasin,datos_normalizados,categoria):
    self.data=datasin.copy()
    self.normalizados=datos_normalizados.copy()
    self.categoria=categoria
    self.df = datasin.copy()


  def base(self):
     for cat in self.categoria:
      self.df = self.data[self.data["Cuenca"] == cat].copy()
      self.df =self.df.iloc[:,25:].copy()
      
      for metal in self.df.columns:
        if metal[:2] not in self.normalizados[cat]:
          self.df=self.df.drop(metal,axis=1)

      corr = self.df.corr()
      display(corr) 

    # Calcular la matriz de distancias (usando 1 - coeficiente de correlación para obtener distancias)
      distance_matrix = 1 - corr

      # Convertir la matriz de distancias en un vector plano (para scipy)
      distance_vector = squareform(distance_matrix)

      # Calcular el enlace del clustering jerárquico utilizando la matriz de distancias
      linkage_matrix = linkage(distance_vector, method='average')

      # Visualizar el dendrograma
      plt.figure(figsize=(10,5))
      dendrogram(linkage_matrix, labels=self.df.columns, orientation='top', distance_sort='descending', show_leaf_counts=True)
      plt.title(f'Dendrograma de Clustering Jerárquico en Datos Geoquímicos de la categoria {cat}')
      plt.xlabel('Muestras Geoquímicas')
      plt.ylabel('Distancia')
      plt.tight_layout()
      plt.show()

Correlacion(sin_outliers,datos_normalizados,categoria).base()
