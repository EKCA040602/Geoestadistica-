#En esta parte vamos a generar dos tablas por separado : uno con los datos reales y otro con los datos logaritmicos.
from P1.py import cruda
import statistics
from statsmodels.stats.diagnostic import lilliefors
from statsmodels.graphics.gofplots import qqplot
from scipy.stats import shapiro,pearsonr, norm
from sklearn.preprocessing import StandardScaler
import scipy.stats as stats
import plotly.graph_objects as go
import ipywidgets as widgets

#-------------------------------------------------------------------------

def conversion(archivo):
  archivo_log=archivo.copy()
  for i in archivo_log.iloc[:,25:].columns:
    archivo_log[i] = archivo_log[i].astype(float)
    archivo_log[i]=archivo_log[i].apply(math.log)
  return archivo_log
cruda_log=conversion(cruda)

#------------------------------------------------------------------------
#Aqui vamos a analizar todas las categorias y todo estara en una  misma tabla
class Outliers():
  #Creamos un constructor en el que colocaremos los parametros a analizar

  def __init__(self,archivo,categoria):

    self.archi=archivo.copy()
    self.categoria=categoria

    #Creamos una copia del archivo principal en el que analizaremos todo.

    self.df = self.archi.copy()

  def base(self):

    for cat in self.categoria:

      self.df = self.archi[self.archi["Cuenca"] == cat].copy()

    #EMPEZAMOS A REALIZAR LA ELIMINACION DE OUTLAYERS.

      self.df =self.df.iloc[:,25:].copy()

      for metal in self.df.columns:
        for x in range(4):
          long=len(self.df)*0.15
          contador=0

          dk=self.df[metal].describe().T
          inferior = dk["25%"] - 1.5 * (dk["75%"] - dk["25%"])
          superior = dk["75%"] + 1.5 * (dk["75%"] - dk["25%"])

          for p,q in zip(self.df[metal].sort_values(ascending=False),self.df[metal].sort_values(ascending=True)):
            if self.df[metal].isna().sum() >=long:
              break
            if p > superior:
              self.archi.loc[self.df[self.df[metal]==p].index[0],metal]=None
              self.df[metal][self.df[self.df[metal] == p].index[0]]=None

            if self.df[metal].isna().sum() >=long:
              break
            if q <inferior:
              self.archi.loc[self.df[self.df[metal]==q].index[0],metal]=None
              self.df[metal][self.df[self.df[metal] == q].index[0]]=None

    return self.archi


sin_outliers=Outliers(cruda_log,categoria).base()

#------------------------------------------------------------------------------------

#GRAFICOS 

#Analisis de un elemento por litologia .Se muestra un grafico de como se comporta un elemento en las diferentes categorias.

class Elemento_y_litologias():
    def __init__(self,data,datasin):
        self.data=data
        self.datasin=datasin
        self.cat=list(self.data["Cuenca"].unique())

    def base(self):
     
      def graficos(elemento):
        plt.style.use('ggplot')
        fig, ax = plt.subplots(ncols=2,nrows=2,figsize=(15, 10))
        sns.kdeplot(ax=ax[0,0],data=self.data,x=elemento,hue="Cuenca")
        sns.boxplot(ax=ax[0,1],data=self.data,y=elemento,hue="Cuenca",gap=0.2)
        ax[0,1].set_ylabel("")
        ax[0,1].legend( loc="best")
      
        sns.kdeplot(ax=ax[1,0],data=self.datasin,x=elemento,hue="Cuenca")
        sns.boxplot(ax=ax[1,1],data=self.datasin,y=elemento,hue="Cuenca",gap=0.2)
        ax[1,1].set_ylabel("")
        ax[1,1].legend( loc="best")

        fig.suptitle("COMPARACION DE ELEMENTO POR LITOLOGIAS",fontsize=20)
        plt.tight_layout()
        plt.show()

      widgets.interact(graficos,elemento=list(self.data.columns)[25:])

grafico1=Elemento_y_litologias(cruda_log,sin_outliers)

grafico1.base()

#--------------------------------------------------------------

# Analisis de todos los elementos en una categoria o grupo.Aqui se presentan las tablas con y sin outliers .Se hace una comparativa 
#de la data en Histograma ,Boxplot y QQplot


class Grafico_lith_and_all_elements():
  def __init__(self,data,datasin):
    scaler = StandardScaler()
    self.columnas=list(data.columns[25:])
    self.data=data
    self.data [self.columnas] = scaler.fit_transform(self.data[self.columnas])
    self.datasin=datasin
    self.datasin[self.columnas] = scaler.fit_transform(self.datasin[self.columnas])

   

  def base(self):
    def grafico(categoria):
      plt.style.use('ggplot')
      fig,ax=plt.subplots(ncols=2,nrows=len(self.data.columns[25:]),figsize=(10,40))
      f=0
      for i in self.data.columns[25:]:
        c=0

        sns.histplot(ax=ax[f,c],x=self.data[self.data["Cuenca"]==categoria][i],kde=True,color="chocolate",stat="density",lw=3)
        ax[f,c].set_ylabel(i[:2],fontsize=20)
        ax[f,c].set_xlabel(" ")

        np.random.seed(0)  # Fijar la semilla para reproducibilidad
        datos = np.random.normal(0, 1, len(self.data[self.data["Cuenca"]==categoria]))
        sns.kdeplot(ax=ax[f,c],x=datos,color="black",lw=3)

        c=1

        sns.histplot(ax=ax[f,c],x=self.datasin[self.datasin["Cuenca"]==categoria][i],kde=True,color="green",stat="density",lw=3)
        sns.kdeplot(ax=ax[f,c],x=datos,color="black",lw=3)
        ax[f,c].set_ylabel(" ")
        ax[f,c].set_xlabel(" ")

        f+=1

      ax[0,0].set_title('HISTOGRAMA CON OUTLAYERS',fontsize=20)
      ax[0,1].set_title('HISTOGRAMA SIN OUTLAYERS',fontsize=20)
      plt.tight_layout()
      plt.show()
      print("-----------------------------------------------------------------")
      plt.style.use('ggplot')
      fig,ax=plt.subplots(ncols=2,nrows=len(self.data.columns[25:]),figsize=(10,40))
      f=0
      for i in self.data.columns[25:]:
        c=0

        sns.boxplot(ax=ax[f,c],x=self.data[self.data["Cuenca"]==categoria][i],color="chocolate",flierprops={"marker": "x"})
        ax[f,c].set_ylabel(i[:2],fontsize=20)
        ax[f,c].set_xlabel(" ")

        c=1
        sns.boxplot(ax=ax[f,c],x=self.datasin[self.datasin["Cuenca"]==categoria][i],color="green",flierprops={"marker": "x"})
        ax[f,c].set_ylabel(" ")
        ax[f,c].set_xlabel(" ")

        f+=1

      ax[0,0].set_title('BOXPLOT CON OUTLAYERS',fontsize=20)
      ax[0,1].set_title('BOXPLOT SIN OUTLAYERS',fontsize=20)
      plt.tight_layout()
      plt.show()
      print("-----------------------------------------------------------------")
      fig,ax=plt.subplots(ncols=2,nrows=len(self.data.columns[25:]),figsize=(10,40))
      f=0
      for i in self.data.columns[25:]:
        c=0

        qqplot_data=qqplot(self.data[self.data["Cuenca"]==categoria][i],line="q",ax=ax[f,c]).gca().lines
        ax[f,c].set_ylabel(i[:2],fontsize=20)
        ax[f,c].set_xlabel(" ")

        c=1
        qqplot_data2=qqplot(self.datasin[self.datasin["Cuenca"]==categoria][i],line="q",ax=ax[f,c]).gca().lines
        ax[f,c].set_ylabel(" ")
        ax[f,c].set_xlabel(" ")

        f+=1

      ax[0,0].set_title('QQPLOT CON OUTLAYERS',fontsize=20)
      ax[0,1].set_title('QQPLOT SIN OUTLAYERS',fontsize=20)
      plt.tight_layout()
      plt.show()

    widgets.interact(grafico,categoria=categoria)


Grafico_lith_and_all_elements(cruda_log,sin_outliers).base()

#----------------------------------------------------------------------------------------
#Elementos normalizados para cada categoria 

class Normalizados():
  def __init__(self,archivo,categoria):

    self.archivo=archivo.copy()
    self.categoria=categoria
    self.df = self.archivo.copy()

  def base(self):

    conjunto={}
    for cat in self.categoria:
      normalizados=[]
      self.df = self.archivo[self.archivo["Cuenca"] == cat].copy()

      self.df =self.df.iloc[:,25:].copy()

      for metal in self.df.columns:
        limpio=self.df.dropna(subset=[metal]).copy()
        
        ksl_stat, ksl_p_value = lilliefors(limpio[metal])
        if ksl_p_value  > 0.05:
            normalizados.append(f"{metal}")

      conjunto[cat]=normalizados

    self.conjunto=conjunto
    return self.conjunto

Normalizados(sin_outliers,categoria).base()

#------------------------------------------------------------------------------------------

