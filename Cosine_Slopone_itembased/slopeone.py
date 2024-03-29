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


def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

def scan_desviaciones_files():
    import glob, os
    owd = os.getcwd()
    os.chdir("desviaciones_pkl_files/")
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

def serialize_obj(obj, name):
    with open('desviaciones_pkl_files/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

data = {}
productid2name = {}
promedios = {}
clavesTotal = []

def loadDataset():
    global data
    global productid2name
    global promedios
    recomendador = Recomendador({})
    data = recomendador.load_obj("ratings_products27m")
    productid2name = recomendador.load_obj("product_movies27m")
    promedios = recomendador.load_obj("promedios_users27m")

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


def calcularDesviacion2Items_mp(ratingsItem1, item2):
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
            del ratingsItem2
            return [item2, desviacion, frecuencia]
    else:
        for user in ratingsItem2:
            if user in ratingsItem1:
                frecuencia += 1
                desviacion += ratingsItem1[user]-ratingsItem2[user]
                #gc.collect()
        if frecuencia!= 0:
            desviacion /= frecuencia   
            del ratingsItem2
            return [item2, desviacion, frecuencia]


def calcularDesviaciones1Item_mp(item):
    t = time.time()
    desviaciones = {}
    frecuencias = {}
    ratingsItem1 = data[item]
    for it in clavesTotal:
        a = calcularDesviacion2Items_mp(ratingsItem1, it)
        if a:
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
    #print("total time:", time.time()-t)


class Recomendador:

    def __init__(self, data):
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        self.umbral = 3
        self.frecuencias = {}
        self.desviaciones = {}

        if type(data).__name__ == 'dict':
            data = data

    #ready_desv son las distancias y desviaciones ya calculadas
    def calcularDesviacionesTodos_mp(self, read_desv):
        procesados = []
        i = 0
        
        global clavesTotal
        clavesTotal = sorted(data, key=lambda k: len(data[k]), reverse=False)
        print("Total de peliculas calificadas:", len(clavesTotal))
        #claves = list(set(clavesTotal) - set(read_sim)) #similitudes que faltan calcular
        claves  = [i for i in clavesTotal if not i in read_desv] #similitudes que faltan calcular
        '''
        claves = list(data.keys())
        claves = list(set(claves) - set(read_desv)) #restan calcular
        '''
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
    

    def recomendacionesSlopeOne(self, usuario):
        items = data.keys()
        itemsNoCalificados = []
        itemsCalificados = {}
        
        for it in items:
            if usuario not in data[it]:
                itemsNoCalificados.append(it)
            else:
                itemsCalificados[it] = data[it][usuario]

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

    def recomendacionesSlopeOneItem(self, usuario, itemObj, reload=0):
        #print(self.desviaciones)
        if usuario in data[itemObj]:
            print("Usuario ya califico dicho item")
            return data[itemObj][usuario]
        
        ####
        if reload==1: #VOlver a realizar la carga
            calcularDesviaciones1Item_mp(itemObj)

        resSuccess = self.load_desviaciones_item(itemObj)

        if not resSuccess: #si no se encontro el archivo
            calcularDesviaciones1Item_mp(itemObj)
            self.load_desviaciones_item(itemObj)

        ####

        items = data.keys()
        itemsNoCalificados = []
        itemsCalificados = {}
        for it in items:
            if usuario in data[it]:
                itemsCalificados[it] = data[it][usuario]
        
        recomendaciones = {}
        frecuencias = {}
        #calcularDesviaciones1Item_mp(itemObj)
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
        
    def load_desviaciones_item(self, item):
        with open('desviaciones_pkl_files/' + item + "_desviaciones" + '.pkl', 'rb') as f:
            self.desviaciones.update(pickle.load(f))

    def load_frecuencias_item(self, item):
        with open('desviaciones_pkl_files/' + item + "_frecuencias" + '.pkl', 'rb') as f:
            self.frecuencias.update(pickle.load(f))
    
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
        if newuser not in data:
            data[newuser] = {}

        print("Usuario agregado")
    
    def calificarItem(self, user, item, rating):
        if user not in data:
            data[user] = {}
        data[user][item] = float(rating)

    def getCalificacionesUsuario(self, user):
        return data[user]

'''
if __name__ == '__main__':
    recomendador = Recomendador({}, k=4, metric='coseno', n=10)
    tInit = time.time()
    loadDataset()
    print("time to load data:", time.time()-tInit)
    t = time.time()

    ready_desv = scan_desviaciones_files()
    recomendador.calcularDesviacionesTodos_mp(ready_desv)

'''