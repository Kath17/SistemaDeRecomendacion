import sys
import codecs 
import time
import math
from math import sqrt
import gc

import pickle

from multiprocessing import Queue
from multiprocessing import Pool
from multiprocessing import Process, Manager
import itertools

import sqlite3 as lite
def createTableSimilitudes():
    '''
    similitudes = [
        ('1', '2', 0.82223),
        ('1', '3', -7.0123122),
        ('1', '4', -0.123),
        ('1', '5', 10.123),
        ('2', '1', 1.23523),
        ('2', '3', 0.123123),
        ('2', '4', -0.1232142312)
    ]
    '''
    con = lite.connect('similitudes_database.db')
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS similitudes")
        cur.execute("CREATE TABLE similitudes(item1 TEXT, item2 TEXT, sim REAL)")
        #cur.executemany("INSERT INTO similitudes VALUES(?, ?, ?)", similitudes)

con = lite.connect('similitudes_database.db')
conRatings = lite.connect('ratings_sql.db')

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

def scan_desviaciones_files():
    import glob, os
    owd = os.getcwd()
    os.chdir("pkl_files/")
    desviaciones_calculadas = []
    for file in glob.glob("*_desviaciones.pkl"):
        item = file.split("_")[0]
        desviaciones_calculadas.append(item)
    frecuencias_calculadas = []
    for file in glob.glob("*_frecuencias.pkl"):
        item = file.split("_")[0]
        frecuencias_calculadas.append(item)
    os.chdir(owd)
    desv_calculadas = intersection(desviaciones_calculadas, frecuencias_calculadas)
    return desv_calculadas


def scan_similitudes_files():
    import glob, os
    owd = os.getcwd()
    os.chdir("pkl_files/")
    similitudes_calculadas = []
    for file in glob.glob("*_similitudes.pkl"):
        item = file.split("_")[0]
        similitudes_calculadas.append(item)
    os.chdir(owd)
    return similitudes_calculadas

def serialize_obj(obj, name):
    with open('pkl_files/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

#mgr = Manager()
#dRatings = mgr.dict()

data = {}
productid2name = {}
promedios = {}
#Load data for Slope one
'''
with open('pkl_files/' + "ratings_products27m" + '.pkl', 'rb') as f:
    print("Cargando data ...")
    t=time.time()
    data = pickle.load(f)
    print("Time to load data:", time.time()-t)
    #dRatings.update(data)
'''

def loadMovieLens27MCosenoAjustado():
    global data
    global productid2name
    global promedios
    recomendador = Recomendador({})
    data = recomendador.load_obj("ratings_products27m")
    '''
    f = codecs.open("ml-latest/ratings.csv", 'r', 'utf8')
    promedios = {}
    contadores = {}
    ratingsSQL = []
    
    for line in f:
        try:
            fields = line.split(',')
            user = fields[0].strip('"')
            movie = fields[1].strip('"')
            rating = float(fields[2].strip().strip('"'))
            if movie in data:
                currentRatings = data[movie]
            else:
                currentRatings = {}
            if user not in promedios:
                promedios[user] = 0.0
                contadores[user] = 0
            promedios[user] += rating
            contadores[user] += 1
            currentRatings[user] = rating
            data[movie] = currentRatings
            ratingsSQL.append((user, movie, rating))
        except Exception as e:
            print(e)
            continue

    with open('pkl_files/'+ "ratings_products27m" + '.pkl', 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    for user in promedios:
        promedios[user] /= contadores[user]
    with open('pkl_files/'+ "promedios_users27m" + '.pkl', 'wb') as f:
        pickle.dump(promedios, f, pickle.HIGHEST_PROTOCOL)
    f.close()

    #lo siguiente es nuevo, es para evitar usar la RAM y jalar los ratings desde disco
    
    con = lite.connect('ratings_sql.db')
    with con:
        cur = con.cursor()
        cur.executemany("INSERT INTO ratings VALUES(?, ?, ?)", ratingsSQL)
    '''
    
    '''
    f = codecs.open("ml-latest/movies.csv", 'r', 'utf8')
    for line in f:
        fields = line.split(',')
        movieId = fields[0].strip('"')
        title = fields[1].strip('"')
        genre = fields[2].strip().strip('"')
        title = title + ', ' + genre
        productid2name[movieId] = title
    f.close()


    with open('pkl_files/'+ "product_movies27m" + '.pkl', 'wb') as f:
        pickle.dump(productid2name, f, pickle.HIGHEST_PROTOCOL)
    '''
    
    
    productid2name = recomendador.load_obj("product_movies27m")
    promedios = recomendador.load_obj("promedios_users27m")
    #print(productid2name)

'''
with open('pkl_files/' + "mp_dict_ratings_products27m" + '.pkl', 'rb') as f:
    pickle.load(f)
print("Time to load manager dict from disk:", time.time()-t)
'''

users2 = {"Amy": {"Taylor Swift": 4, "PSY": 3, "Whitney Houston": 4},
 "Ben": {"Taylor Swift": 5, "PSY": 2},
 "Clara": {"PSY": 3.5, "Whitney Houston": 4},
 "Daisy": {"Taylor Swift": 5, "Whitney Houston": 3}}

users3 = {"David": {"Imagine Dragons": 3, "Daft Punk": 5,
 "Lorde": 4, "Fall Out Boy": 1},
 "Matt": {"Imagine Dragons": 3, "Daft Punk": 4,
 "Lorde": 4, "Fall Out Boy": 1},
 "Ben": {"Kacey Musgraves": 4, "Imagine Dragons": 3,
 "Lorde": 3, "Fall Out Boy": 1},
 "Chris": {"Kacey Musgraves": 4, "Imagine Dragons": 4,
 "Daft Punk": 4, "Lorde": 3, "Fall Out Boy": 1},
 "Tori": {"Kacey Musgraves": 5, "Imagine Dragons": 4,
 "Daft Punk": 5, "Fall Out Boy": 3}}


def calcularDesviacion2Items_mp(item1, item2):
    
    ratingsItem1 = data[item1]
    ratingsItem2 = data[item2]
    desviacion = 0.0
    frecuencia = 0

    if len(ratingsItem1) < len(ratingsItem2):
        for user in ratingsItem1:
            if user in ratingsItem2:
                frecuencia += 1
                desviacion += ratingsItem1[user]-ratingsItem2[user]
                #gc.collect()
        if frecuencia!= 0:
            desviacion /= frecuencia
        
        del ratingsItem1
        del ratingsItem2
        del item1
        return [item2, desviacion, frecuencia]
    else:
        for user in ratingsItem2:
            if user in ratingsItem1:
                frecuencia += 1
                desviacion += ratingsItem1[user]-ratingsItem2[user]
                #gc.collect()
        if frecuencia!= 0:
            desviacion /= frecuencia
        
        del ratingsItem1
        del ratingsItem2
        del item1
        return [item2, desviacion, frecuencia]


def calcularDesviaciones1Item_mp(item):
    desviaciones = {}
    frecuencias = {}
    for it in data.keys():
        a = calcularDesviacion2Items_mp(item, it)
        desviaciones.setdefault(item, {})
        frecuencias.setdefault(item, {})
        desviaciones[item][a[0]] = a[1]
        frecuencias[item][a[0]] = a[2]
        del a

    serialize_obj(desviaciones, item+"_desviaciones")
    serialize_obj(frecuencias, item+"_frecuencias")
    del desviaciones
    del frecuencias
    gc.collect()


def calcularSimilitudCosenoAjustado_mp(ratingsItem1, item2):

    cur = conRatings.cursor()
    #print("Enter to coseno ajustado")
    cur.execute("SELECT userId, rating FROM ratings where itemId=:itemId", {"itemId":item2})
    ratingsItem2 = cur.fetchall()

    

    #0: user, 1: movieid, 2: rating


    tInit = time.time()
    #ratingsItem1 = data[item1]
    #ratingsItem2 = data[item2]



    #usuarios = [] #usuarios que necesitamos su promedio
    #print("Initiating sim coseno")
    num=0
    dem1=0
    dem2=0

    if len(ratingsItem1) < len(ratingsItem2):
        ratingsItem2 = {x[0]:x[1] for x in ratingsItem2}
        for row in ratingsItem1:
            user = row[0]
            if user in ratingsItem2:
                num += (row[1] - promedios[user])*(ratingsItem2[user]-promedios[user])
                dem1 += (row[1] - promedios[user])**2
                dem2 += (ratingsItem2[user] - promedios[user])**2
    else:
        ratingsItem1 = {x[0]:x[1] for x in ratingsItem1}
        for row in ratingsItem2:
            user = row[0]
            if user in ratingsItem1:
                num += (row[1] - promedios[user])*(ratingsItem2[user]-promedios[user])
                dem1 += (row[1] - promedios[user])**2
                dem2 += (ratingsItem2[user] - promedios[user])**2
    


    '''
    if len(ratingsItem1) < len(ratingsItem2):
        for user in ratingsItem1:
            if user in ratingsItem2:
                num += (ratingsItem1[user] - promedios[user])*(ratingsItem2[user]-promedios[user])
                dem1 += (ratingsItem1[user] - promedios[user])**2
                dem2 += (ratingsItem2[user] - promedios[user])**2
    else:
        for user in ratingsItem2:
            if user in ratingsItem1:
                num += (ratingsItem1[user] - promedios[user])*(ratingsItem2[user]-promedios[user])
                dem1 += (ratingsItem1[user] - promedios[user])**2
                dem2 += (ratingsItem2[user] - promedios[user])**2
    '''
    #print("Time to calculate between 2:", time.time()-tInit)
    if dem1==0 or dem2==0: #Ambas peliculas no tienen usuarios en comun que los hayan calificado
        similitud = 0
    else:
        similitud = num/(sqrt(dem1)*sqrt(dem2))
        return [item2, similitud] #Cambio, solo retornar los que tienen similitud, modificar las recomendaciones para considerar el caso en que no existe como 0
    #print("Time to calculate between 2:", time.time()-tInit)
    #return [item2, similitud]

def calcularSimilitudes1Item_mp(item):
    similitudes = []
    #similitudes.setdefault(item, {})
    cur = conRatings.cursor()
    print("time to extract from database:")
    tt = time.time()
    cur.execute("SELECT userId, rating FROM ratings where itemId=:itemId", {"itemId":item})
    ratingsItem1 = cur.fetchall()
    print("TIME:", time.time()-tt)
    for it in data.keys():
        a = calcularSimilitudCosenoAjustado_mp(ratingsItem1, it)
        if a:
            similitudes.append((item, a[0], a[1]))
            del a
    
    return similitudes
    #with con:
    cur = con.cursor()
    print(similitudes)
    cur.executemany("INSERT INTO similitudes VALUES(?, ?, ?)", similitudes)
    #serialize_obj(similitudes, item+"_similitudes")
    del similitudes
    gc.collect()

'''
def calcularSimilitudCosenoAjustado_mp(item1, item2):
    tInit = time.time()
    print("Initiating sim coseno")
    averages = {}
    for (key, ratings) in data.items():
        averages[key] = (float(sum(ratings.values())) / len(ratings.values()))
    num = 0 # numerator
    dem1 = 0 # first half of denominator
    dem2 = 0
    for (user, ratings) in data.items():
        if item1 in ratings and item2 in ratings:
            avg = averages[user]
            num += (ratings[item1] - avg) * (ratings[item2] - avg)
            dem1 += (ratings[item1] - avg)**2
            dem2 += (ratings[item2] - avg)**2
    print("Time to calculate between 2:", time.time()-tInit)
    if dem1==0 or dem2==0:
        sim = 0
    else:
        sim = num / (sqrt(dem1) * sqrt(dem2))
    return [item2, sim]

def calcularSimilitudes1Item_mp(item):
    similitudes = []
    #similitudes.setdefault(item, {})
    print(productid2name)
    for it in productid2name:
        print(it)
        a = calcularSimilitudCosenoAjustado_mp(item, it)
        similitudes.append((item, a[0], a[1]))
        del a
   
    con = lite.connect('similitudes_database.db')
    with con:
        cur = con.cursor()
        cur.executemany("INSERT INTO similitudes VALUES(?, ?, ?)", similitudes)
    #serialize_obj(similitudes, item+"_similitudes")
    del similitudes
    gc.collect()
'''

class Recomendador:

    def __init__(self, data, k=1, metric='pearson', n=5):
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        self.metric = metric
        self.umbral = 3
        self.frecuencias = {}
        self.desviaciones = {}

        if type(data).__name__ == 'dict':
            self.data = data

    def calcularSimilitudCosenoAjustado(self, item1, item2):
        ratingsItem1 = self.data[item1]
        ratingsItem2 = self.data[item2]
        promedios = {}
        usuarios = [] #usuarios que necesitamos su promedio
        for user in ratingsItem1:
            if user in ratingsItem2:
                usuarios.append(user)
        for user in usuarios:
            contador = 0
            if user not in promedios:
                promedios[user] = 0.0
            for item in self.data.keys(): #recorrer peliculas
                if user in self.data[item]:
                    promedios[user] += self.data[item][user] #obtiene rating
                    contador+=1
            promedios[user] /= contador
        num=0
        dem1=0
        dem2=0
        for user in promedios:
            num += (ratingsItem1[user] - promedios[user])*(ratingsItem2[user]-promedios[user])
            dem1 += (ratingsItem1[user] - promedios[user])**2
            dem2 += (ratingsItem2[user] - promedios[user])**2
        
        similitud = num/(sqrt(dem1)*sqrt(dem2))
        if item1 not in self.desviaciones:
            self.desviaciones[item1] = {}
        self.desviaciones[item1][item2] = similitud
        return similitud

    def normalizar(self, rating):
        minR = 1
        maxR = 5
        return (2*(rating-minR)-(maxR-minR))/(maxR - minR)
    
    def denormalizar(self, Nrating):
        minR = 1
        maxR = 5
        return (1/2)*((Nrating+1)*(maxR-minR)) + minR

    def predecirSimilitudCosenoAjustado(self, usuario, itemObj):
        if usuario in self.data[itemObj]:
            print("Usuario ya califico dicho item")
            return self.data[itemObj][usuario]
        
        items = self.data.keys()
        itemsNoCalificados = []
        itemsCalificados = {}
        for it in items:
            if usuario in self.data[it]:
                itemsCalificados[it] = self.data[it][usuario]
                self.calcularSimilitudCosenoAjustado(itemObj, it)
        num=0
        dem=0
        for item in itemsCalificados: #items calificados por el usuario
            num+= self.desviaciones[itemObj][item]*self.normalizar(self.data[item][usuario])
            dem+= abs(self.desviaciones[itemObj][item])

        if dem==0: return 0
        NR = num/dem
        R = self.denormalizar(NR)
        return R


    def calcularDesviaciones1Item_mp(self, item):
        #ratingsItem = self.data[item]
        #dictlist = [(item, ratingsItem, it, self.data[it]) for it in self.data.keys() if it!=item]
        dictlist = [(item, it) for it in data.keys() if it!=item]
        print("Total de peliculas:",len(dictlist))
        
        t = time.process_time()
        number_of_workers = 56
        with Pool(number_of_workers) as p:
            desviaciones = p.starmap(calcularDesviacion2Items_mp, dictlist)
        
        for a in desviaciones:
            self.desviaciones.setdefault(item, {})
            self.frecuencias.setdefault(item, {})
            self.desviaciones[item][a[0]] = a[1]
            self.frecuencias[item][a[0]] = a[2]
        
        #print(self.desviaciones)

    #ready_desv son las distancias y desviaciones ya calculadas
    def calcularDesviacionesTodos_mp(self, read_desv):
        procesados = []
        i = 0
        #items = data.keys()
        #dictlist = [it for it in list(data.keys())[:500]]
        #dictlist = [it for it in list(data.keys())] #Lista de todas las peliculas calificadas 
        claves = list(data.keys())
        claves = list(set(claves) - set(read_desv)) #restan calcular
        del read_desv
        n = 500
        # Usando compresion de listas
        #print(claves)
        chunks = [claves[i * n:(i + 1) * n] for i in range((len(claves) + n - 1) // n )]
        #print(chunks)
        print("total de subarrays:", len(chunks))
        print("Iniciando calculo concurrente")
        for chunk in chunks:
            inicial = time.time()
            number_of_workers = 56
            with Pool(number_of_workers) as p:
                #desviaciones = p.map(calcularDesviaciones1Item_mp, dictlist)
                p.map(calcularDesviaciones1Item_mp, chunk)
            print("Tiempo para calcular desviaciones de 500 peliculas", time.time()-inicial)
            gc.collect()
    
    def calcularSimilitudesCosenoTodos_mp(self, read_sim):
        procesados = []
        i = 0
        claves = list(data.keys())
        print("Total de peliculas calificadas:", len(claves))
        claves = list(set(claves) - set(read_sim)) #similitudes que faltan calcular
        del read_sim
        n = 12
        chunks = [claves[i * n:(i + 1) * n] for i in range((len(claves) + n - 1) // n )]
        print("total de subarrays:", len(chunks))
        print("Iniciando calculo concurrente")
        for chunk in chunks:
            inicial = time.time()
            number_of_workers = 12
            with Pool(number_of_workers) as p:
                inserts = p.map(calcularSimilitudes1Item_mp, chunk)

            cur = con.cursor()
            for insert in inserts:
                #print(insert)
                print("Insertando")
                cur.executemany("INSERT INTO similitudes VALUES(?, ?, ?)", insert)
                del insert
            del inserts               
            gc.collect()

            print("Tiempo para calcular similitudes de 500 peliculas", time.time()-inicial)
            gc.collect()

    def recomendacionesSlopeOne(self, usuario):
        items = self.data.keys()
        itemsNoCalificados = []
        itemsCalificados = {}
        
        for it in items:
            if usuario not in self.data[it]:
                itemsNoCalificados.append(it)
            else:
                itemsCalificados[it] = self.data[it][usuario]

        #print("Items calificados:")
        #print(itemsCalificados)
        recomendaciones = {}
        frecuencias = {}
        for noItem in itemsNoCalificados:
            self.calcularDesviaciones1Item_mp(noItem)
            for item, rating in itemsCalificados.items():
                if item in self.desviaciones[noItem]:
                    freq = self.frecuencias[noItem][item]
                    recomendaciones.setdefault(noItem, 0.0)
                    frecuencias.setdefault(noItem, 0)
                    # Sumar a la suma corriente que representa el numero de la formula
                    recomendaciones[noItem] += (self.desviaciones[noItem][item] + rating) * freq
                    # mantener una suma corriente de la frecuencia de noItem
                    frecuencias[noItem] += freq

        recomendaciones = [(self.convertProductID2name(k), v / frecuencias[k]) for (k, v) in recomendaciones.items()]
        # finalmente ordenar y retornar
        recomendaciones.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        return recomendaciones

    def recomendacionesSlopeOneItem(self, usuario, itemObj):
        if usuario in self.data[itemObj]:
            print("Usuario ya califico dicho item")
            return self.data[itemObj][usuario]
        
        items = self.data.keys()
        itemsNoCalificados = []
        itemsCalificados = {}
        for it in items:
            if usuario in self.data[it]:
                itemsCalificados[it] = self.data[it][usuario]
        
        recomendaciones = {}
        frecuencias = {}
        self.calcularDesviaciones1Item_mp(itemObj)
        for item, rating in itemsCalificados.items():
            if item in self.desviaciones[itemObj]:
                freq = self.frecuencias[itemObj][item]
                recomendaciones.setdefault(itemObj, 0.0)
                frecuencias.setdefault(itemObj, 0)
                # Sumar a la suma corriente que representa el numero de la formula
                recomendaciones[itemObj] += (self.desviaciones[itemObj][item] + rating) * freq
                # mantener una suma corriente de la frecuencia de itemObj
                frecuencias[itemObj] += freq

        recomendaciones = [(self.convertProductID2name(k), v / frecuencias[k]) for (k, v) in recomendaciones.items()]
        # finalmente ordenar y retornar
        recomendaciones.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        #print(self.desviaciones)
        return recomendaciones
        

    def loadMovieRatingsDB(self, path=''):
        self.data = {}
        import pandas as pd
        self.data2 = pd.io.parsers.read_csv(path + "Movie_Ratings",sep=",",index_col=0, skip_blank_lines =True)

        for key in self.data2: #loop trought users
            newRatings = {}
            for k,v in self.data2[key].iteritems():
                if not pd.isnull(v):
                    newRatings[k] = v
            self.data[key] = newRatings

    '''
    def loadUsers2(self, database):
        for user in database:
            for item in database[user]:
                if item not in data:
                    data[item] = {}
                data[item][user] = database[user][item]
    '''

    def loadUsers2(self, database):
        for user in database:
            for item in database[user]:
                if item not in self.data:
                    self.data[item] = {}
                self.data[item][user] = database[user][item]
                
    def convertProductID2name(self, id):
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id

    def loadBookDB(self, path=''):
        self.data = self.load_obj("ratings_books")
        self.productid2name = self.load_obj("product_books")
    
        f = codecs.open(path + "BX-Users.csv", 'r', 'utf8')
        for line in f:
            fields = line.split(';')
            userid = fields[0].strip('"')
            location = fields[1].strip('"')
            if len(fields) > 3:
                age = fields[2].strip().strip('"')
            else:
                age = 'NULL'
            if age != 'NULL':
                value = location + '  (age: ' + age + ')'
            else:
                value = location
            self.userid2name[userid] = value
            self.username2id[location] = userid
        f.close()

    #Load movielens

    def loadMovieLens(self, path=''):
        self.data = self.load_obj("ratings10m")
        self.productid2name = self.load_obj("product_movies10m")
    
    #Load movielens 20M
    def loadMovieLens20M(self, path=''):
        self.data = self.load_obj("ratings20m")
        self.productid2name = self.load_obj("product_movies20m")

    #Load movielens 27M 
    def loadMovieLens27MCosenoAjustado(self, path=''):
        data = self.load_obj("ratings27m")
        '''
        f = codecs.open(path + "ratings.csv", 'r', 'utf8')
        for line in f:
            try:
                fields = line.split(',')
                user = fields[0].strip('"')
                movie = fields[1].strip('"')
                rating = float(fields[2].strip().strip('"'))
                if user in data:
                    currentRatings = data[user]
                else:
                    currentRatings = {}
                currentRatings[movie] = rating
                data[user] = currentRatings
            except Exception:
                continue
        self.save_obj(data, "ratings27m")
        f.close()
        '''
        productid2name = self.load_obj("product_movies27m")
        print(productid2name)

    def loadMovieLens27MSlopeOne(self, path=''):
        self.data = self.load_obj("ratings_products27m")
        '''
        f = codecs.open(path + "ratings.csv", 'r', 'utf8')
        for line in f:
            try:
                fields = line.split(',')
                user = fields[0].strip('"')
                movie = fields[1].strip('"')
                rating = float(fields[2].strip().strip('"'))
                if movie in self.data:
                    currentRatings = self.data[movie]
                else:
                    currentRatings = {}
                currentRatings[user] = rating
                self.data[movie] = currentRatings
            except Exception:
                continue
        self.save_obj(self.data, "ratings_products27m")
        f.close()
	'''
        '''
        f = codecs.open(path + "movies.csv", 'r', 'utf8')
        for line in f:
            fields = line.split(',')
            movieId = fields[0].strip('"')
            title = fields[1].strip('"')
            genre = fields[2].strip().strip('"')
            title = title + ', ' + genre
            self.productid2name[movieId] = title
        f.close()
	
        self.save_obj(self.productid2name,"product_movies27m")
        '''
        self.productid2name = self.load_obj("product_movies27m")
        
    def load_desviaciones_item(self, item):
        return self.load_obj(item+"_desviaciones")
    
    def load_frecuencias_item(self, item):
        return self.load_obj(item+"_frecuencias")

    def load_similitudes_item(self, item):
        return self.load_obj(item+"_similitudes")
    
    def calcDesviaciones(self):
        if self.metric == "coseno_ajustado":
            self.calcularDesviaciones()
        elif self.metric == "slope_one":
            self.calcularDesviacionesSlopeOne()
    
    def save_obj(self, obj, name ):
        with open('pkl_files/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, name ):
        with open('pkl_files/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)

    def addUser(self, newuser):
        if newuser not in self.data:
            self.data[newuser] = {}

        print("Usuario agregado")
    
    def calificarItem(self, user, item, rating):
        if user not in self.data:
            self.data[user] = {}
        self.data[user][item] = float(rating)

    def getCalificacionesUsuario(self, user):
        return self.data[user]

if __name__ == '__main__':
    recomendador = Recomendador({}, k=4, metric='coseno', n=10)
    #recomendador.loadMovieLens27MCosenoAjustado("ml-latest/")
    tInit = time.time()
    loadMovieLens27MCosenoAjustado()
    print("time to load data:", time.time()-tInit)
    createTableSimilitudes()
    t = time.time()
    #print("Iniciando calculo de similitudes")
    #calcularSimilitudes1Item_mp("1")
    #print("Time to calculate similitudes:", time.time()-t)
    
    recomendador.calcularSimilitudesCosenoTodos_mp([])

    #t=time.time()
    #recomendador.loadMovieLens27M("ml-latest/")
    #print("Time to load data ratings:", time.time()-t)
    #recomendador.loadUsers2(users3)
    #print("Total time to load data: " , time.process_time()-t)
    #print(recomendador.productid2name.keys())
    #recomendador.parallelDesviaciones()
    #recomendador.loadMovieRatingsDB("dataset/")
    #recomendador.data = users2
    #print(len(recomendador.data['1']))
    #print("num de peliculas:", len(recomendador.productid2name.keys()))
    #t=time.process_time()
    #recomendador.calcularDesviacion2Items('Taylor Swift','PSY')
    #recomendador.calcularDesviacion2Items('PSY','Taylor Swift')
    #recomendador.calcularDesviacion2Items('1', '15')
    #recomendador.calcularDesviaciones1Item('1')
    #before = time.time()
    #recomendador.calcularDesviaciones1Item_mp('1')
    #recomendador.calcularDesviaciones1Item_mp('2')
    #recomendador.calcularDesviaciones1Item_mp('3')
    #after = time.time()
    #recomendador.calcularDesviaciones1Item('1')
    #print(recomendador.desviaciones)
    #print(recomendador.frecuencias)
    #print("Total time to calculate desviation 2 items: " , after-before)
    
    #ready_desv = scan_desviaciones_files()
    #recomendador.calcularDesviacionesTodos_mp(ready_desv)


    '''
    ready_sim = scan_similitudes_files()
    calcularSimilitudes1Item_mp("Kacey Musgraves")
    calcularSimilitudes1Item_mp("Imagine Dragons")
    calcularSimilitudes1Item_mp("Daft Punk")
    calcularSimilitudes1Item_mp("Lorde")
    print(recomendador.load_similitudes_item("Kacey Musgraves"))
    print(recomendador.load_similitudes_item("Imagine Dragons"))
    print(recomendador.load_similitudes_item("Daft Punk"))
    print(recomendador.load_similitudes_item("Lorde"))
    '''
    
    #recomendador.calcularSimilitudesCosenoTodos_mp(ready_sim)

    #calcularDesviaciones1Item_mp('136598')
    
    #print(calcularDesviacion2Items_mp('PSY','Taylor Swift'))

    #print(recomendador.load_desviaciones_item('Taylor Swift'))
    #print(recomendador.load_desviaciones_item('PSY'))
    #print(recomendador.load_desviaciones_item('Whitney Houston'))
    #recomendador.calcularDesviacion2Items('PSY','Taylor Swift')

    #print(recomendador.desviaciones['1'])
    #print(recomendador.desviaciones['1']['2'])
    #print(recomendador.desviaciones['1']['3'])
    #recomendador.desviaciones = {}
    #recomendador.frecuencias = {}
    #recomendador.calcularDesviacion2Items('1','2')
    #print(recomendador.desviaciones['1']['2'])
    #print("RECOMENDACIONES SLOPE ONE:")
    #print(recomendador.recomendacionesSlopeOne('4895'))
    #print(recomendador.recomendacionesSlopeOneItem('Ben', 'Whitney Houston'))
    #print(recomendador.recomendacionesSlopeOneItem('1', '1'))
    #print(recomendador.recomendacionesSlopeOneItem('4895', '2'))
    #print(recomendador.recomendacionesSlopeOneItem('4895', '2'))
    #print(recomendador.recomendacionesSlopeOneItem('4895', '3'))
    
    #recomendador.loadUsers2(users3)
    #print("Total time to load data: " , time.process_time()-t)
    #print(recomendador.productid2name.keys())
    #recomendador.parallelDesviaciones()
    #recomendador.loadMovieRatingsDB("dataset/")
    #recomendador.data = users2
    #print(len(recomendador.data['1']))
    #print("num de peliculas:", len(recomendador.productid2name.keys()))
    #t=time.process_time()
    #recomendador.calcularDesviacion2Items('Taylor Swift','PSY')
    #recomendador.calcularDesviacion2Items('PSY','Taylor Swift')
    #recomendador.calcularDesviacion2Items('1', '15')
    #recomendador.calcularDesviaciones1Item('1')
    #recomendador.calcularDesviaciones1Item_mp('1')
    #recomendador.calcularDesviaciones1Item('1')
    #print(recomendador.desviaciones)
    #print(recomendador.frecuencias)
    #print("Total time to calculate desviation 2 items: " , time.process_time()-t)
    #print(recomendador.desviaciones['1'])
    #print(recomendador.desviaciones['1']['2'])
    #recomendador.desviaciones = {}
    #recomendador.frecuencias = {}
    #recomendador.calcularDesviacion2Items('1','1')
    #recomendador.calcularDesviacion2Items('1','2')
    #print(recomendador.desviaciones['1']['2'])
    #print(recomendador.frecuencias)
    #recomendador.calcularDesviacion2Items('1','3')
    #print(recomendador.desviaciones['1']['3'])
    #print(recomendador.frecuencias)
    #print("RECOMENDACIONES SLOPE ONE:")
    #print(recomendador.recomendacionesSlopeOne('4895'))
    #print(recomendador.recomendacionesSlopeOneItem('Ben', 'Whitney Houston'))
    #print(recomendador.recomendacionesSlopeOneItem('1', '1'))
    #print(recomendador.desviaciones)
    #print(recomendador.recomendacionesSlopeOneItem('4895', '2'))
    #print(recomendador.desviaciones)
    #print(recomendador.recomendacionesSlopeOneItem('4895', '2'))
    #print(recomendador.recomendacionesSlopeOneItem('4895', '3'))
    #print(recomendador.calcularSimilitudCosenoAjustado("Kacey Musgraves", "Imagine Dragons"))
    #NR = recomendador.normalizar(2)
    #print(NR)
    #R = recomendador.denormalizar(NR)
    #print(R)
    #print(recomendador.predecirSimilitudCosenoAjustado("David", "Kacey Musgraves"))
