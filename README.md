# Geoestadistica-
Curso de geoestadística utilizando Phyton 
Existen 3 archivos por ahora.

  PREPROCESAMIENTO :
  Prepara la data con eliminacion de columnas sin valores ,se elimina columnas de acuerdo al tipo de digestion y tambien se elimina de acuerdo al % de limite de     
  deteccion total en la poblacion de la muestra .Respecto al ultimo factor .Se recomienda copiar el script en Jupyter y no en Colab debido a que el colab tiene     
  problemas al usar geopandas.
  Resultado: Una tabla procesada .
     
  ELIMINACION DE OUTLIERS:
  Hay una funcion que me convierte la tabla procesada a logaritmos.
  Ya depende del usuario usar logaritmos o no .Se recomienda usarlos .Resultado tabla cruda_log
  Elimina outliers .Aqui lo hace por categorias (grupos) no obstante toda la data esta en una misma tabla.Resultado tabla con celdas vacias llamada sin_outliers
  Aqui tambien se hace Graficos para analizar 
    1.Grafico elemento por categorias (histograma-boxplot)
    2.Todos los elementos por categoria. (histograma-boxplot-qqplot)
  Se procede a identificar si los elementos de  cada categoria cumple con la normalidad. Y se genera un diccionario ejm Cuenca Santa :[Pb,Zn,Cd] ...
  Resultado : Diccionario 
  
  CORRELACION :
  Aqui se usa la tabla sin_outliers y el diccionario llamado datos_normalizados 
  Se observa la tabla de correlacion y uso de clustering jerarquico (supervisado)
  Resultado :Tabla de correlacion y dendograma 
  
  Se hizo una comparativa de la data logatitmicos sin y con outliers .Con respecto a la correlacion y si.Eliminar los datos es efectivo puesto que genera una mejor 
  correlacion 
  entre las variables.
  Asimismo se hizo una prueba de datos  reales sin y con outiliers .Y sucede lo mismo.En pocas palabras la eliminacion por ahora para el analisis es apropiado.Ya 
  que brinda un mejor analisis entre los elementos.No obstante siempre hay que tenerlo presente.

  
