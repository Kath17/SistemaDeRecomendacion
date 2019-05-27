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
clavesTotal = []

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
    for it in clavesTotal:
        a = calcularSimilitudCosenoAjustado_mp(ratingsItem1, it)
        if a:
            #similitudes.append((item, a[0], a[1]))
            similitudes[a[0]] = a[1]
    
    print("Saving to file")
    serialize_obj(similitudes, item+"_similitudes")
    del similitudes
    del ratingsItem1
    gc.collect()
    print("saved")

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

    #reload = 0 carga desde el archivo en la carpeta de pkls, relaod=1, no considera el pkl y lo vuelve a generar
    def predecirSimilitudCosenoAjustado(self, usuario, itemObj, reload=0):
        if usuario in data[itemObj]:
            print("Usuario ya califico dicho item")
            return data[itemObj][usuario]

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
            inicial = time.time()
            number_of_workers = 12
            with Pool(number_of_workers) as p:
                p.map(calcularSimilitudes1Item_mp, chunk)

            print("Tiempo para calcular similitudes de 500 peliculas", time.time()-inicial)
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