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


def scan_similitudes_files():
    import glob, os
    owd = os.getcwd()
    os.chdir("similitudes_pkl_files/")
    similitudes_calculadas = []
    for file in glob.glob("*_similitudes.pkl"):
        item = file.split("_")[0]
        similitudes_calculadas.append(item)
    os.chdir(owd)
    return similitudes_calculadas

def serialize_obj(obj, name):
    with open('similitudes_pkl_files/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

data = {}
productid2name = {}
promedios = {}

def loadDataset():
    global data
    global productid2name
    global promedios
    recomendador = Recomendador({})
    data = recomendador.load_obj("ratings_products27m")
    productid2name = recomendador.load_obj("product_movies27m")
    promedios = recomendador.load_obj("promedios_users27m")


def calcularSimilitudCosenoAjustado_mp(ratingsItem1, item2):

    tInit = time.time()
    #ratingsItem1 = data[item1]
    ratingsItem2 = data[item2]
    num=0
    dem1=0
    dem2=0

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
    
    #print("Time to calculate between 2:", time.time()-tInit)
    if dem1==0 or dem2==0: #Ambas peliculas no tienen usuarios en comun que los hayan calificado
        similitud = 0
    else:
        similitud = num/(sqrt(dem1)*sqrt(dem2))
        return [item2, similitud] #Cambio, solo retornar los que tienen similitud, modificar las recomendaciones para considerar el caso en que no existe como 0
    #print("Time to calculate between 2:", time.time()-tInit)
    #return [item2, similitud]

def calcularSimilitudes1Item_mp(item):
    similitudes = {}
    ratingsItem1 = data[item]

    #similitudes.setdefault(item, {})
    for it in data.keys():
        a = calcularSimilitudCosenoAjustado_mp(ratingsItem1, it)
        if a:
            #similitudes.append((item, a[0], a[1]))
            similitudes[a[0]] = a[1]
    
    serialize_obj(similitudes, item+"_similitudes")
    del similitudes
    del ratingsItem1
    gc.collect()



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
            data = data

    def normalizar(self, rating):
        minR = 1
        maxR = 5
        return (2*(rating-minR)-(maxR-minR))/(maxR - minR)
    
    def denormalizar(self, Nrating):
        minR = 1
        maxR = 5
        return (1/2)*((Nrating+1)*(maxR-minR)) + minR

    def predecirSimilitudCosenoAjustado(self, usuario, itemObj):
        if usuario in data[itemObj]:
            print("Usuario ya califico dicho item")
            return data[itemObj][usuario]
        
        items = data.keys()
        itemsNoCalificados = []
        itemsCalificados = {}
        for it in items:
            if usuario in data[it]:
                itemsCalificados[it] = data[it][usuario]
                self.calcularSimilitudCosenoAjustado(itemObj, it)
        num=0
        dem=0
        for item in itemsCalificados: #items calificados por el usuario
            num+= self.desviaciones[itemObj][item]*self.normalizar(data[item][usuario])
            dem+= abs(self.desviaciones[itemObj][item])

        if dem==0: return 0
        NR = num/dem
        R = self.denormalizar(NR)
        return R

    
    def calcularSimilitudesCosenoTodos_mp(self, read_sim):
        procesados = []
        i = 0
        #claves = list(data.keys())
        claves = sorted(data, key=lambda k: len(data[k]), reverse=True)
        print("Total de peliculas calificadas:", len(claves))
        claves = list(set(claves) - set(read_sim)) #similitudes que faltan calcular
        del read_sim
        n = 50
        chunks = [claves[i * n:(i + 1) * n] for i in range((len(claves) + n - 1) // n )]
        print("total de subarrays:", len(chunks))
        print("Iniciando calculo concurrente")
        for chunk in chunks:
            inicial = time.time()
            number_of_workers = 12
            with Pool(number_of_workers) as p:
                p.map(calcularSimilitudes1Item_mp, chunk)

            print("Tiempo para calcular similitudes de 50 peliculas", time.time()-inicial)
            gc.collect()


    def loadUsers2(self, database):
        for user in database:
            for item in database[user]:
                if item not in data:
                    data[item] = {}
                data[item][user] = database[user][item]
    

    def convertProductID2name(self, id):
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id

    def load_similitudes_item(self, item):
        with open('similitudes_pkl_files/' + item + '_similitudes.pkl', 'rb') as f:
            self.desviaciones.update(pickle.load(f))

    
    def save_obj(self, obj, name ):
        with open('pkl_files/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, name ):
        with open('pkl_files/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)

    def addUser(self, newuser):
        if newuser not in data:
            data[newuser] = {}

        print("Usuario agregado")
    
    def calificarItem(self, user, item, rating):
        if user not in data:
            data[user] = {}
        data[user][item] = float(rating)

    def getCalificacionesUsuario(self, user):
        return data[user]

if __name__ == '__main__':
    recomendador = Recomendador({}, k=4, metric='coseno', n=10)
    #recomendador.loadDataset("ml-latest/")
    tInit = time.time()
    loadDataset()
    print("time to load data:", time.time()-tInit)
    #createTableSimilitudes()
    t = time.time()
    print("Iniciando calculo de similitudes")
    #calcularSimilitudes1Item_mp("1")
    print("Time to calculate similitudes:", time.time()-t)
    
    ready_sim = scan_similitudes_files()
    recomendador.calcularSimilitudesCosenoTodos_mp(ready_sim)

    #t=time.time()
    #recomendador.loadMovieLens27M("ml-latest/")
    #print("Time to load data ratings:", time.time()-t)
    #recomendador.loadUsers2(users3)
    #print("Total time to load data: " , time.process_time()-t)

    '''
    r
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
    
    #print(recomendador.calcularSimilitudCosenoAjustado("Kacey Musgraves", "Imagine Dragons"))
    #NR = recomendador.normalizar(2)
    #print(NR)
    #R = recomendador.denormalizar(NR)
    #print(R)
    #print(recomendador.predecirSimilitudCosenoAjustado("David", "Kacey Musgraves"))
