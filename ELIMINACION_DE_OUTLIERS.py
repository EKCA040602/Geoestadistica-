#En esta parte vamos a generar dos tablas por separado : uno con los datos reales y otro con los datos logaritmicos.
from P1.py import cruda
import statistics
from statsmodels.stats.diagnostic import lilliefors
from scipy.stats import shapiro,pearsonr
from statsmodels.graphics.gofplots import qqplot

def conversion(archivo):
  archivo_log=archivo.copy()
  for i in archivo_log.iloc[:,25:].columns:
    archivo_log[i] = archivo_log[i].astype(float)
    archivo_log[i]=archivo_log[i].apply(math.log)
  return archivo_log
cruda_log=conversion(cruda)
cruda_log

class Unido():
  #Creamos un constructor en el que colocaremos los parametros a analizar
  def __init__(self,archivo:pd.DataFrame,cuenca,excel):
    self.archivo=archivo
    #Creamos una copia del archivo principal en el que analizaremos todo.
    self.df = self.archivo.copy()
    self.cuenca=cuenca
    self.excel=excel
  def base(self):

    #Discriminamos la data por CUENCAS  de modo que se me genera una tabla solo de los elementos que tiene esa litologia

    self.df = self.archivo[self.archivo["Cuenca"] == self.cuenca].copy()

    #EMPEZAMOS A REALIZAR LA ELIMINACION DE OUTLAYERS.

    self.df =self.df.iloc[:,25:].copy()

    # display(self.df.describe())

    for metal in self.df.columns:
      n=1
      cambio = True
      column_name=f"{metal}_filtrado"
      self.df[column_name]=self.df[metal]

      long=len(self.df)*0.15
      contador=0
      for iteracion in range(5):
        dk=self.df[column_name].describe().T
        inferior = dk["25%"] - 1.5 * (dk["75%"] - dk["25%"])
        superior = dk["75%"] + 1.5 * (dk["75%"] - dk["25%"])

        for p,q in zip(self.df[column_name].sort_values(ascending=False),self.df[column_name].sort_values(ascending=True)):
          if self.df[column_name].isna().sum() >=long:
            break          
          if p > superior:
            self.df[column_name][self.df[self.df[column_name] == p].index[0]]=None
          if self.df[column_name].isna().sum() >=long:
            break
          if q <inferior:
            self.df[column_name][self.df[self.df[column_name] == q].index[0]]=None

    self.df=self.df.iloc[:,int(-1*(len(self.df.columns)/2)):]

    print(f"Cantidad de datos TOTALES:{len(self.df)}")
    print(f"Cantidad de datos como MINIMO:{len(self.df)*0.85}")
    display(self.df.describe())

    zscore={}

#     #Realizamos un cicleo for en base a las dos columnas SIN OUTLAYERS

    for i in (list(self.df.columns)):
      #Generamos una copia en la variable elemento del Dataframe  a la variable elemento
      elemento=self.df.copy()
      #De dicha copia solo agarramos la columna que deseamos
      elemento=elemento[i]
      #Eliminamos los valores vacios
      elemento=elemento.dropna()
      #Ordenamos los valores
      elemento=elemento.sort_values(ascending=True)
      #Reseteamos el indice
      elemento=elemento.reset_index(drop=True)
      #Dentro del diccionario creamos una clave llamada Ejm Cd_Z que tendra valores convertidos a Zscore.
      zscore[f"{i}_Z"]=[x for x  in list((elemento-elemento.mean())/elemento.std()) if not math.isnan(x)]

    #Se asigna el valor de la variable a un atributo nombrado llamado self.zscore dentro del objeto actual

    self.zscore=zscore


#     #Para corroborar que el Zscore cumpla con los estandares de que la media sea 0 y la varianza 1 se crea otro diccionario que almacenara dichos elementos.
    mevar={}
    #Hacemos un cicleo del diccionario para hallar la media ,varianza y desviacion estandar de cada elemento.
    for i in self.zscore:
        media = statistics.mean(self.zscore.get(i))
        varianza = statistics.variance(self.zscore.get(i))
        desviacion_estandar = statistics.stdev(self.zscore.get(i))
        mevar[i]=[media,varianza,desviacion_estandar]

    mevar = pd.DataFrame(mevar, columns=mevar.keys())

    #Creamos dicha variable que sera como resultado al final de este codigo.
    self.mevar=mevar

    normalizados=[]

    #Realizamos el ciclo for para analizar lo mencionado anteriormente  con la prueba de KOLMOGOROV-SMIRNOF

    for i in self.zscore:

      # La diferencia de usar el ajuste de LILLIEFORS es que condidiona a que la distribucion sea mas estricta para una distribucion normal .
      # Sin el arreglo acepta data que visualmente podria ser una distribucion ,pero con el ajuste No .De modo que aqui para analisis no se usará
      # dicho ajuste debido a que empiricamente si se acepta estos datos visualmente

      #ARREGLO DE LILIEFORS --------------------------------------------

      ksl_stat, ksl_p_value = lilliefors(self.zscore.get(i))
      # print(f"{i}:{ksl_p_value}")
      if ksl_p_value  > 0.05:
            normalizados.append(f"{i}_NORMALIZADA")


    self.normalizados=normalizados
# Aqui se realiza un grafico compuesto por un histograma,boxplot y qqplot.Se hace uso de la libreria seaborn(sns) y qqplot

    # Creacion de la figura que va a contener 6 axs  (3 para el cada elemento )
    plt.style.use('ggplot')
    fig, ax = plt.subplots(ncols=3, nrows=len(self.zscore.keys()), figsize=(20, 100))
   
    f = 0
    for i in self.zscore:
          c = 0
          #Se crea el histograma
          sns.histplot(ax=ax[f,c],x=self.zscore.get(i),fill=True,stat="count",kde=True ,lw=4,bins=12,color="green")
          ax[f, c].set_xlabel(i, fontsize=10, labelpad=5)
          c=1
          #Se crea el boxplot
          sns.boxplot(ax=ax[f,c],y=self.zscore.get(i),color="lightblue")
          f += 1
    f=0
    c=2


    #Se hace la prueba shapiro
    for i in self.zscore:

      datos = self.zscore.get(i)
      datos_array = np.array(datos)

    #Se hace el grafico qqplot .Todo en una misma figura
      qqplot_data=qqplot(datos_array,line="q",ax=ax[f,c]).gca().lines
      f += 1
    f=0
    c=3
    #Se ordena los graficos automaticamente
    
    plt.tight_layout()
    #Se muestra el grafico
    plt.show()

    self.normalizados=[x[:-14]for x in self.normalizados]

    for x in self.df.columns:

      #Si el elemento no esta dentro de la lista que contiene a elementos normalizados borra dicho columna del elemento de la tabla
      if x not in self.normalizados:
        self.df=self.df.drop(x,axis=1)

    return  self.df,self.mevar,self.normalizados


a,b,c=Unido(cruda_log,"Cuenca Nepeña","EXCEL").base()
