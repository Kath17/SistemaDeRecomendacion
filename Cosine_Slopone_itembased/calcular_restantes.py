import sys
import codecs 
import time
import math
from math import sqrt
import gc
import operator

import pickle

from multiprocessing import Queue
from multiprocessing import Pool
from multiprocessing import Process, Manager
import itertools

import sqlite3 as lite
import pandas as pd

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 


data = {}
productid2name = {}
promedios = {}
clavesTotal = []
links = {}

def loadDataset():
    global data
    global productid2name
    global promedios
    global clavesTotal
    recomendador = Recomendador({})
    data = recomendador.load_obj("ratings_products27m")
    productid2name = recomendador.load_obj("product_movies27m")
    promedios = recomendador.load_obj("promedios_users27m")
    clavesTotal = sorted(data, key=lambda k: len(data[k]), reverse=False)

def loadLinks():
    global links
    links = pd.read_csv("links.csv", dtype = {'imdbId': str})
    links = links.set_index("movieId")
    #print(links["imdbId"][int("1")])


###DESVIACIONES PARA SLOPE ONE
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

#SIMILITUDES PARA COSENO AJUSTADO

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

def serialize_obj_similitudes(obj, name):
    with open('similitudes_pkl_files/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


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
        if similitud>1:
            similitud=1
        return [item2, similitud] #Cambio, solo retornar los que tienen similitud, modificar las recomendaciones para considerar el caso en que no existe como 0
    #print("Time to calculate between 2:", time.time()-tInit)
    #return [item2, similitud]

def calcularSimilitudes1Item_mp(item):
    similitudes = {}
    ratingsItem1 = data[item]

    #similitudes.setdefault(item, {})
    for it in clavesTotal:
        a = calcularSimilitudCosenoAjustado_mp(ratingsItem1, it)
        if a:
            #similitudes.append((item, a[0], a[1]))
            similitudes[a[0]] = a[1]
    
    print("Saving to file")
    serialize_obj_similitudes(similitudes, item+"_similitudes")
    del similitudes
    del ratingsItem1
    gc.collect()
    print("saved")



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
    
    def agregarRating(self, userId, itemId, rating):
        if itemId not in data:
            data[itemId] = {}
        rating = float(rating)
        data[itemId][userId] = rating
        print("Nuevas desviación y frecuencias:")
        for item in clavesTotal:
            #print("item:", item)
            if userId in data[item]: #peliculas que el usuario califico
                resSuccess = self.load_desviaciones_item(item)
                if not resSuccess:
                    print("No encuentra archivo")
                    continue
                self.load_frecuencias_item(item)
                '''
                x = self.desviaciones[item]
                a = self.desviaciones[item][itemId]
                b = self.frecuencias[item][itemId]
                '''
                nuevaDesviacion = (self.desviaciones[item][itemId]*self.frecuencias[item][itemId]*(rating-data[item][userId]))/(self.frecuencias[item][itemId] + 1)
                self.desviaciones[item][itemId] = nuevaDesviacion
                self.frecuencias[item][itemId] += 1

                serialize_obj(self.desviaciones, item+"_desviaciones2")
                serialize_obj(self.frecuencias, item+"_frecuencias2")

                print(self.desviaciones[item][itemId], " - ", self.frecuencias[item][itemId])
                del self.desviaciones
                del self.frecuencias

        #calcularDesviaciones1Item_mp(itemId)
    
    def getImdbIdByMovieId(self, itemId):
        return links["imdbId"][int(itemId)]

    def normalizar(self, rating):
        minR = 1
        maxR = 5
        return (2*(rating-minR)-(maxR-minR))/(maxR - minR)
    
    def denormalizar(self, Nrating):
        minR = 1
        maxR = 5
        return (1/2)*((Nrating+1)*(maxR-minR)) + minR

    def getKPrimerosCosenoByItem(self, item, K):
        resSuccess = self.load_similitudes_item(item)

        #if not resSuccess: #si no se encontro el archivo
        calcularSimilitudes1Item_mp(item)
        self.load_similitudes_item(item)

        similitudes_item = self.desviaciones[item]
        similitudes_item = {int(k):v for k,v in similitudes_item.items()}
        df = pd.DataFrame(similitudes_item.items())
        sorted_values = df.sort_values(by=[1,0], ascending=[False,True])
        similitudes_item = sorted_values.agg(list,1).tolist()

        print(similitudes_item)
        return similitudes_item[:int(K)]

    def getKPrimerosSlopeOneByItem(self, item, K):
        resSuccess = self.load_desviaciones_item(item)

        if not resSuccess: #si no se encontro el archivo
            calcularDesviaciones1Item_mp(item)
            self.load_desviaciones_item(item)
            self.load_frecuencias_item(item)

        desviaciones_item = self.desviaciones[item]
        desviaciones_item = {int(k):v for k,v in desviaciones_item.items()}
        df = pd.DataFrame(desviaciones_item.items())
        sorted_values = df.sort_values(by=[1,0], ascending=[False,True])
        desviaciones_item = sorted_values.agg(list,1).tolist()

        return desviaciones_item[:int(K)]


    #reload = 0 carga desde el archivo en la carpeta de pkls, relaod=1, no considera el pkl y lo vuelve a generar
    def predecirSimilitudCosenoAjustado(self, usuario, itemObj, reload=0):
        if usuario in data[itemObj]:
            print("Usuario ya califico dicho item")
            return {"mensaje": "Usuario ya califico dicho item", "rating": data[itemObj][usuario]}

        if reload==1: #VOlver a realizar la carga
            calcularSimilitudes1Item_mp(itemObj)

        resSuccess = self.load_similitudes_item(itemObj)

        if not resSuccess: #si no se encontro el archivo
            calcularSimilitudes1Item_mp(itemObj)
            self.load_similitudes_item(itemObj)

        items = data.keys()
        itemsNoCalificados = []
        itemsCalificados = []
        for it in items:
            if usuario in data[it]:
                itemsCalificados.append(it)
                #itemsCalificados[it] = data[it][usuario]
                #self.calcularSimilitudCosenoAjustado(itemObj, it)
        num=0
        dem=0
        for item in itemsCalificados: #items calificados por el usuario
            if item in self.desviaciones[itemObj]:
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
        global clavesTotal
        clavesTotal = sorted(data, key=lambda k: len(data[k]), reverse=False)
        print("Total de peliculas calificadas:", len(clavesTotal))
        #claves = list(set(clavesTotal) - set(read_sim)) #similitudes que faltan calcular
        claves  = [i for i in clavesTotal if not i in read_sim] #similitudes que faltan calcular

        '''
        filee = open("faltan_calcular.txt","w") 
        for cl in claves:
            filee.write(cl+"\n") 
        filee.close() 
        '''
        
        del read_sim
        n = 12
        chunks = [claves[i * n:(i + 1) * n] for i in range((len(claves) + n - 1) // n )]
        print("total de subarrays:", len(chunks))
        print("Iniciando calculo concurrente")
        for chunk in chunks:
            '''
            for a in chunk:
                inicial = time.time()
                calcularSimilitudes1Item_mp(a)
                print("Tiempo para calcular Similitudes de un item", time.time()-inicial)

            '''
            inicial = time.time()
            number_of_workers = 4
            with Pool(number_of_workers) as p:
                p.map(calcularSimilitudes1Item_mp, chunk)
            
            print("Tiempo para calcular Similitudes de 12 items", time.time()-inicial)
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
        try:
            with open('similitudes_pkl_files/' + item + '_similitudes.pkl', 'rb') as f:
                self.desviaciones[item] = pickle.load(f)
            return True
        except:
                return False

            #self.desviaciones.update(pickle.load(f))
            #print(self.desviaciones)


    ####### slope one ################3

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
        n = 20
        # Usando compresion de listas
        #print(claves)
        chunks = [claves[i * n:(i + 1) * n] for i in range((len(claves) + n - 1) // n )]
        #print(chunks)
        print("total de subarrays:", len(chunks))
        print("Iniciando calculo concurrente")
        for chunk in chunks:
            inicial = time.time()
            number_of_workers = 7
            with Pool(number_of_workers) as p:
                #desviaciones = p.map(calcularDesviaciones1Item_mp, dictlist)
                p.map(calcularDesviaciones1Item_mp, chunk)
            print("Tiempo para calcular desviaciones de 12 peliculas", time.time()-inicial)
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
            return {"mensaje": "Usuario ya califico dicho item", "rating": data[itemObj][usuario]}
        
        ####
        if reload==1: #VOlver a realizar la carga
            calcularDesviaciones1Item_mp(itemObj)

        resSuccess = self.load_desviaciones_item(itemObj)

        if not resSuccess: #si no se encontro el archivo
            print("NO se encontro el archivo, volviendo a calcula")
            calcularDesviaciones1Item_mp(itemObj)
            self.load_desviaciones_item(itemObj)
            self.load_frecuencias_item(itemObj)
        
        resSuccessFrec = self.load_frecuencias_item(itemObj)
        if not resSuccessFrec: #si no se encontro el archivo
            print("NO se encontro el archivo, volviendo a calcula")
            calcularDesviaciones1Item_mp(itemObj)
            self.load_desviaciones_item(itemObj)
            self.load_frecuencias_item(itemObj)

        print(self.desviaciones[itemObj])
        print("DIvision")

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

    def load_desviaciones_item(self, item):
        try:
            with open('desviaciones_pkl_files/' + item + "_desviaciones" + '.pkl', 'rb') as f:
                self.desviaciones.update(pickle.load(f))
                #print(self.desviaciones)
            return True
        except:
                return False

        

    def load_frecuencias_item(self, item):
        try:
            with open('desviaciones_pkl_files/' + item + "_frecuencias" + '.pkl', 'rb') as f:
                self.frecuencias.update(pickle.load(f))
            return True
        except:
                return False
        

    
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
    recomendador = Recomendador({})
    tInit = time.time()
    loadDataset()
    print("time to load data:", time.time()-tInit)
    t = time.time()

    ready_desv = scan_desviaciones_files()
    recomendador.calcularDesviacionesTodos_mp(ready_desv)


'''

if __name__ == '__main__':
    recomendador = Recomendador({})
    #recomendador.loadDataset("ml-latest/")
    tInit = time.time()
    loadDataset()
    print("time to load data:", time.time()-tInit)
    #createTableSimilitudes()
    #t = time.time()
    #print("Iniciando calculo de similitudes")
    #calcularSimilitudes1Item_mp("1")
    #print("Time to calculate similitudes:", time.time()-t)
    
    ready_sim = scan_similitudes_files()
    recomendador.calcularSimilitudesCosenoTodos_mp(ready_sim)
'''