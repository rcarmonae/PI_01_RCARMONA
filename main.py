from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import pandas as pd
import ast
import gdown

########## 1. OBTENCIÓN DE LOS DATASETS #############
'''1.0 Descargar los datasets en formato csv y crea los dataframes que se van a consultar'''
'''
url_movies = 'https://drive.google.com/uc?id=1LYliTXV6FADRqej88ixcr5igXoYCibEY&export=download'
url_movies_cast = 'https://drive.google.com/uc?id=1LScbmoB4tHy_lyWL2N2S45hk0BLjkHtE&export=download'
url_movies_crew = 'https://drive.google.com/uc?id=1LVYzsoXO_rNGCwWBfjo4v3UOUnosnT1E&export=download'

gdown.download(url_movies, 'csv_movies.csv', quiet=False, format='csv')
gdown.download(url_movies_cast, 'csv_cast.csv', quiet=False, format='csv')
gdown.download(url_movies_crew, 'csv_crew.csv', quiet=False, format='csv')
'''

df_movies = pd.read_csv('csv_movies.csv', low_memory=False)
df_cast = pd.read_csv('csv_cast.csv', low_memory=False)
df_crew = pd.read_csv('csv_crew.csv', low_memory=False)

'''Cambia al tipo de dato necesario'''
df_movies['release_date'] = pd.to_datetime(df_movies['release_date'], errors = 'coerce')
df_movies['release_year'] = pd.to_numeric(df_movies['release_year'], errors='coerce')
df_crew['release_date'] = pd.to_datetime(df_crew['release_date'], errors = 'coerce')
df_crew['revenue'] = pd.to_numeric(df_crew['revenue'], errors='coerce')
df_crew['budget'] = pd.to_numeric(df_crew['budget'], errors='coerce')
# -----------
''' 1.1 Acceso a los diccionarios sin desanidar:'''

############ESTA PARTE NO ESTA CONTENIDA EN EL DATASET DE movies_dataset_filtrado_RMCE.csv -- df_movies 
# Y NO SE SI SE VA A OCUPAR PARA EL MODELO DE ML######
'''Para hacer legibles las LISTAS de DICCIONARIOS:
   Convierte las listas a diccionarios para consultas posteriores'''
#columna_list_variables_movies= ['genres','production_companies','production_countries', 'spoken_languages']
'''Del dataset movies'''
#for columna_list in columna_list_variables_movies:
#    df[columna_list] = df[columna_list].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
###############################

'''Del dataset df_cast'''
df_cast['cast'] = df_cast['cast'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
'''Del dataset df_cast'''
df_crew['crew'] = df_crew['crew'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])


########## 2. DESARROLLO API: DISPONIBILIZAR LOS DATOS USANDO FastAPI #############

app = FastAPI()


@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes:str):
    '''Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes históricamente'''
       ## Primero se transforma el nombre del mes en español al número del mes que corresponde. Se hace con un diccionario donde se definen las equivalencias:
    months_number = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12}
        
## Se filtra el dataframe para obtener solo los registros cuya fecha de estreno ("release_date") haya ocurrido durante el mes especificado en el 
# input de la función
    month_records = df_movies[(df_movies['release_date'].dt.month == months_number.get(mes.lower()))]

#Mide el número de registros encontrados en el filtro anterior
    respuesta = len(month_records)
    
    return {'mes':mes, 'cantidad':respuesta}

@app.get('/cantidad_filmaciones_dia{dia}')
def cantidad_filmaciones_dia(dia:str):
    '''Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrenaron ese dia históricamente'''
    ## Primero se transforma el nombre del dia en español al inglés. Se hace con un diccionario donde se definen las equivalencias:
    day_spanish = {
    'lunes': 'Monday',
    'martes': 'Tuesday',
    'miercoles': 'Wednesday',
    'miércoles': 'Wednesday',
    'jueves': 'Thursday',
    'viernes': 'Friday',
    'sabado': 'Saturday',
    'domingo': 'Sunday'}

## Se filtra el dataframe para obtener solo los registros cuyo día de estreno ("release_date") haya ocurrido los días especificados en el 
# input de la función
    day_records = df_movies[(df_movies['release_date'].dt.day_name() == day_spanish.get(dia.lower()))]

#Cuenta el número de registros encontrados en el filtro anterior
    respuesta = len(day_records)
    
    return {'día':dia, 'cantidad':respuesta}

@app.get('/score_titulo/{titulo}')
def score_titulo(titulo:str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score'''
    #Filtrar el df para obtener solo los renglones cuyo título coincide con el input :
    title_records = df_movies[df_movies['title']==titulo]
    
     #Guarda el año y el score en variables, almacena solo los valores
    estreno = [int(x) for x in title_records['release_year']]
    score = title_records['popularity']
    
    #Crea un dataframe para presentar el resultado. Esto ayuda a presentar los resultados que tienen más de una película con el 
    #mismo título (ejemplo: Cinderella)
    respuesta = {
            'Título': titulo,
            'Año': estreno,
            'Score': score
    }
    
    #respuesta = pd.DataFrame(respuesta)

    #return respuesta
    return {'titulo':titulo, 'anio':estreno, 'popularidad':score}

@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo:str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, la cantidad de votos y el valor promedio de las votaciones. 
    La misma variable deberá de contar con al menos 2000 valoraciones, 
    caso contrario, debemos contar con un mensaje avisando que no cumple esta condición y que por ende, no se devuelve ningun valor.'''
    
    #Filtrar el df para obtener solo los renglones cuyo título coincide con el input :
    title_records = df_movies[df_movies['title']== titulo]

    #Extrae los valores de la cantidad de votos y el valor promedio de las votaciones:
    votos_num = title_records['vote_count'].values
    votos_prom = title_records['vote_average'].values

    #Evalúa si el número de votos es mayor a 2000. Se utiliza any() para poder evaluar varios valores de "cantidad de votos" para los casos en los
    # existe más de una película con el mismo título (p.e. "Doctor Strange" o "Titanic"). En la base de datos, no existen películas con el mismo título
    # y que además tengan más de 2000 votaciones. Dependiendo de si hay más de 2000 votos o no es el return correspondiente
    if (votos_num > 2000).any()  :
        votos_num = votos_num.max()
        title_records = title_records[title_records['vote_count']==votos_num]
        votos_prom = title_records['vote_average']
        return {'titulo':titulo,'Numero de votos':int(votos_num),'Promedio de votos':float(votos_prom)}
            
    else: 
       #return print ('El número de votaciones es menor a 2000. No devuelve información para este título')
    
        return {'El número de votaciones es menor a 2000. No devuelve información para este título'}

@app.get('/get_actor/{nombre_actor}')
def get_actor(nombre_actor:str):
    '''Se ingresa el nombre de un actor que se encuentre dentro de un dataset debiendo devolver el éxito del mismo medido a través del retorno. 
    Además, la cantidad de películas que en las que ha participado y el promedio de retorno'''

        # Función para verificar si el valor buscado está presente en un diccionario
    def contiene_valor(diccionario):
          return any(nombre_actor in d.values() for d in diccionario)

    # Se aplica la función en el dataset completo, las filas que cumplen con el valor se guardan en "filtrado"
    filtrado = df_cast[df_cast['cast'].apply(contiene_valor)]   

    # Determina el número de películas con títulos diferentes en las que ha participado como ACTOR (no como director)
    cantidad_pelis = len(filtrado['title'].unique())

    # Calcula el retorno de todas sus películas: retorno_total = revenue_total/budget_total
    retorno_total = filtrado['revenue'].sum()/filtrado['budget'].sum()

    # Calcula el PROMEDIO del retorno de todas sus películas
    retorno_promedio = filtrado['return'].mean()
    #print('Número de películas en las que ha participado como actor: ', cantidad_pelis)
    #print('El éxito del actor, de acuerdo a la suma del retorno de inversión de todas sus películas es: ', retorno_total)
    #print('El promedio del retorno de inversión de todas sus películas es: ', retorno_promedio)
    #return print('Número de películas en las que ha participado como actor: ', cantidad_pelis, 
    #                '\nEl éxito del actor, de acuerdo a la suma del retorno de inversión de todas sus películas es: ', retorno_total,
    #                '\nEl promedio del retorno de inversión de todas sus películas es: ', retorno_promedio)  

    return {'actor':nombre_actor, 'cantidad_filmaciones':cantidad_pelis, 'retorno_total':retorno_total, 'retorno_promedio':retorno_promedio}

@app.get('/get_director/{nombre_director}')
def get_director(nombre_director:str):
     # Función para verificar si el valor buscado está presente en un diccionario
     def contiene_valor(diccionario):
          return any(nombre_director in d.values() for d in diccionario)

     # Se aplica la función en el dataset completo, las filas que cumplen con el valor se guardan en "filtrado"
     filtrado = df_crew[df_crew['crew'].apply(contiene_valor)] 

     # Calcula el retorno de todas sus películas: retorno_total = revenue_total/budget_total
     retorno_total_director = filtrado['revenue'].sum()/filtrado['budget'].sum()

     #rb = pd.DataFrame({'REVENUE': df['revenue'], 'FECHA DE LANZAMIENTO': df['release_date']})
     respuestas = pd.DataFrame({'PELÍCULA': filtrado['title'],'FECHA DE LANZAMIENTO': filtrado['release_date'],'COSTO': filtrado['budget'],'GANANCIA': filtrado['revenue'], 'RETORNO': filtrado['return']})
     
  

     #Dar formato a la tabla de salida 
     #pd.set_option('display.colheader_justify', 'center')
     #pd.set_option('display.float_format', lambda x: f'{x:.2f}')
     
     #return print('El éxito del actor, de acuerdo a la suma del retorno de inversión de todas sus películas es: ', retorno_total_director,'\nA continuación, alguna información acerca de su filmografía:\n',respuestas.to_string(index=False))
     return 'El éxito del director, de acuerdo a la suma del retorno de inversión de todas sus películas es: ', retorno_total_director,'continuación, alguna información acerca de su filmografía:',respuestas
     #return {'director':nombre_director, 'retorno_total_director':retorno_total_director, 
        #'peliculas':filtrado['title'], 'anio':filtrado['release_date'], 'retorno_pelicula':filtrado['return'], 
        #'budget_pelicula':filtrado['budget'], 'revenue_pelicula':filtrado['revenue']}

# ML
#@app.get('/recomendacion/{titulo}')
#def recomendacion(titulo:str):
#    '''Ingresas un nombre de pelicula y te recomienda las similares en una lista'''
#    return {'lista recomendada': respuesta}