#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import tkinter as tk
#from tkinter import *
#from tkinter import ttk
import sys
#from tkinter.colorchooser import askcolor
#from tkinter import messagebox

# Crea una clase Python para definir el interfaz de usuario de
# la aplicación. Cuando se cree un objeto del tipo 'Aplicacion'
# se ejecutará automáticamente el método __init__() qué 
# construye y muestra la raiz con todos sus widgets: 
# ttk.Button(raiz, text='Cargar DataSet').pack(side=TOP) # Ubicar arrib
import codecs 
import time
import math
from math import sqrt

import pickle

from multiprocessing import Queue
from multiprocessing import Pool
from multiprocessing import Process, Manager
import itertools
#import pandas as pd

users = {"Angelica": {"Blues Traveler": 3.5, "Broken Bells": 2.0, "Norah Jones": 4.5, "Phoenix": 5.0,
"Slightly Stoopid": 1.5,
"The Strokes": 2.5, "Vampire Weekend": 2.0},
"Bill": {"Blues Traveler": 2.0, "Broken Bells": 3.5,
"Deadmau5": 4.0, "Phoenix": 2.0,
"Slightly Stoopid": 3.5, "Vampire Weekend": 3.0},
"Chan": {"Blues Traveler": 5.0, "Broken Bells": 1.0,
"Deadmau5": 1.0, "Norah Jones": 3.0,
"Phoenix": 5, "Slightly Stoopid": 1.0},
"Dan": {"Blues Traveler": 3.0, "Broken Bells": 4.0,
"Deadmau5": 4.5, "Phoenix": 3.0,
"Slightly Stoopid": 4.5, "The Strokes": 4.0,
"Vampire Weekend": 2.0},
"Hailey": {"Broken Bells": 4.0, "Deadmau5": 1.0,
"Norah Jones": 4.0, "The Strokes": 4.0,
"Vampire Weekend": 1.0},
"Jordyn": {"Broken Bells": 4.5, "Deadmau5": 4.0, "Norah Jones": 5.0,
"Phoenix": 5.0, "Slightly Stoopid": 4.5,
"The Strokes": 4.0, "Vampire Weekend": 4.0},
"Sam": {"Blues Traveler": 5.0, "Broken Bells": 2.0,
"Norah Jones": 3.0, "Phoenix": 5.0,
"Slightly Stoopid": 4.0, "The Strokes": 5.0},
"Veronica": {"Blues Traveler": 3.0, "Norah Jones": 5.0,
"Phoenix": 4.0, "Slightly Stoopid": 2.5,
"The Strokes": 3.0}}

users2 = {"Amy": {"Taylor Swift": 4, "PSY": 3, "Whitney Houston": 4},
 "Ben": {"Taylor Swift": 5, "PSY": 2},
 "Clara": {"PSY": 3.5, "Whitney Houston": 4},
 "Daisy": {"Taylor Swift": 5, "Whitney Houston": 3}}


import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    text = text[0]
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


#Similitud cose multi_processing
def similitudCoseno_mp(ratingsUser, ratingsUser2):
    xoy = 0
    normax = 0
    normay = 0
    for key in ratingsUser[1]:
        normax+=pow(ratingsUser[1][key],2)
        if key in ratingsUser2[1]:
            xoy+=ratingsUser[1][key]*ratingsUser2[1][key]
    for key in ratingsUser2[1]:
        normay+=pow(ratingsUser2[1][key],2)
    normax = sqrt(normax)
    normay = sqrt(normay)
    if normax*normay==0: return (ratingsUser2[0],0)
    distance = xoy/(normax*normay)
    if distance>1: distance=1
    return (int(ratingsUser2[0]),distance)


def pearson_mp(ratingsUser, ratingsUser2):
    sum_xy = 0
    sum_x = 0
    sum_y = 0
    sum_x2 = 0
    sum_y2 = 0
    n = 0
    for key in ratingsUser[1]:
        if key in ratingsUser2[1]:
            n += 1
            x = ratingsUser[1][key]
            y = ratingsUser2[1][key]
            sum_xy += x * y
            sum_x += x
            sum_y += y
            sum_x2 += pow(x, 2)
            sum_y2 += pow(y, 2)
    if n == 0:
        return (ratingsUser2[0], 0)
    denominator = (sqrt(sum_x2-pow(sum_x, 2)/n) * sqrt(sum_y2-pow(sum_y, 2)/n))
    if denominator == 0:
        distance = 0
    else:
        distance = (sum_xy - (sum_x * sum_y) / n) / denominator
    if distance>1: distance=1
    return (int(ratingsUser2[0]), distance)

def distanciaManhattan_mp(ratingsUser, ratingsUser2):
    distancia = 0
    enComun = False
    for key in ratingsUser[1]:
        if key in ratingsUser2[1]:
            distancia += abs(ratingsUser[1][key] - ratingsUser2[1][key])
            enComun = True
    if enComun:
        if distancia>1: distancia=1
        return (int(ratingsUser2[0]), distancia)
    else:
        return (int(ratingsUser2[0]), -1)


def distanciaEuclidiana_mp(ratingsUser, ratingsUser2):
    distancia = 0
    enComun = False
    for key in ratingsUser[1]:
        if key in ratingsUser2[1]:
            distancia += math.pow((ratingsUser[1][key] - ratingsUser2[1][key]),2)
            enComun = True
    if enComun:
        distance = math.sqrt(distancia)
        if distance>1:distance=1
        return (int(ratingsUser2[0]), distance)
    else:
        return (int(ratingsUser2[0]), 0)
    
def computeSimilarity(item1, item2, ratings):
    promedios = {}
    for (key, ratings) in ratings.items():
        promedios[key] = (float(sum(ratings.values())) / len(ratings.values()))
    num = 0 # numerator
    dem1 = 0 # first half of denominator
    dem2 = 0
    for (user, ratings) in ratings.items():
        if item1 in ratings and item2 in ratings:
            avg = promedios[user]
            num += (ratings[item1] - avg) * (ratings[item2] - avg)
            dem1 += (ratings[item1] - avg)**2
            dem2 += (ratings[item2] - avg)**2
    return num / (sqrt(dem1) * sqrt(dem2))




#SlopeOne, multiprocessing, para los ratings de cada usuario
def calcularDesviaciones_mp(ratingsUser):
    print("Calculating desviacion")
    frequencies = {}
    deviations = {}
    # for each item & rating in that set of ratings:
    for (item, rating) in ratingsUser.items():
        frequencies.setdefault(item, {})
        deviations.setdefault(item, {})
        # for each item2 & rating2 in that set of ratings:
        for (item2, rating2) in ratingsUser.items():
            if item != item2:
                # add the difference between the ratings to our computation
                frequencies[item].setdefault(item2, 0)
                deviations[item].setdefault(item2, 0.0)
                frequencies[item][item2] += 1
                deviations[item][item2] += rating - rating2
    return deviations, frequencies


def calcularDesviacion2Items_mp(item2, ratingsItem2, item1, ratingsItem1):
    desviacion = 0.0
    frecuencia = 0
    for user, rating in ratingsItem1.items():
        if user in ratingsItem2:
            rating2 = ratingsItem2[user]
            frecuencia += 1
            desviacion += rating2-rating
    #del ratingsItem1
    #del ratingsItem2
    if frecuencia!= 0:
        desviacion /= frecuencia
    return [item1, desviacion, frecuencia]


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


    def calcularDesviacion2Items(self, item1, item2):
        ratingsItem2 = self.data[item1]
        ratingsItem1 = self.data[item2]

        for user, rating in ratingsItem1.items():
            self.frecuencias.setdefault(item1, {})
            self.desviaciones.setdefault(item1, {})
            if user in ratingsItem2:
                rating2 = ratingsItem2[user]
                self.frecuencias[item1].setdefault(item2, 0)
                self.desviaciones[item1].setdefault(item2, 0.0)
                self.frecuencias[item1][item2] += 1
                self.desviaciones[item1][item2] += rating - rating2
        if item2 in self.desviaciones[item1] and item2 in self.frecuencias[item1]:
            self.desviaciones[item1][item2] /= self.frecuencias[item1][item2]
    
    def calcularDesviaciones1Item(self, item):
        items = self.data.keys()
        for it in items:
            self.calcularDesviacion2Items(item, it)

    def calcularDesviaciones1Item_mp(self, item):
        ratingsItem = self.data[item]
        dictlist = []
        dictlist = [(item, ratingsItem, it, self.data[it]) for it in self.data.keys() if it!=item]
        print("Total de peliculas:",len(dictlist))
        
        
        t = time.process_time()
        #number_of_workers = 32
	n_cores = multiprocessing.cpu_count()
        with Pool(n_cores) as p:
            desviaciones = p.starmap(calcularDesviacion2Items_mp, dictlist)
        
        '''
        for a in desviaciones:
            self.desviaciones.setdefault(item, {})
            self.frecuencias.setdefault(item, {})
            self.desviaciones[item][a[0]] = a[1]
            self.frecuencias[item][a[0]] = a[2]
        '''


    '''
    def calcularDesviacionesTodos(self):
        procesados = []
        for item in self.data.keys():

            ratingsItem = self.data[item]
            dictlist = []
            dictlist = [(it, self.data[it], item, ratingsItem) for it in self.data.keys()]            
            
            t = time.process_time()
            number_of_workers = 10
            with Pool(number_of_workers) as p:
                desviaciones = p.starmap(calcularDesviacion2Items_mp, dictlist)
        
            self.desviaciones[item] = desviaciones
            del desviaciones
    '''

    def parallelDesviaciones(self):
        return

    #SlopeOne
    '''
    def calcularDesviaciones(self):
        print("Begin calc desviaciones")
        #print(self.data.values())
        print("Tamanio total de valores a calcular: {}".format(len(self.data.values())))
        i = 1
        t=time.process_time()
        for ratings in self.data.values(): #Obtiene los ratings de cada usuario
            # for each item & rating in that set of ratings:
            #print("Ratings:")
            #print(ratings)
            for (item, rating) in ratings.items():
                self.frequencies.setdefault(item, {})
                self.deviations.setdefault(item, {})
                # for each item2 & rating2 in that set of ratings:
                for (item2, rating2) in ratings.items():
                    if item != item2:
                        # add the difference between the ratings
                        # to our computation
                        self.frequencies[item].setdefault(item2, 0)
                        self.deviations[item].setdefault(item2, 0.0)
                        self.frequencies[item][item2] += 1
                        self.deviations[item][item2] += rating - rating2
            i = i+1
            
            if (i % 5000 == 0):
                print("Total time to Calculate desviation {} : {}".format(i,time.process_time()-t))
                t = time.process_time()
                self.save_obj(self.frequencies, "ml27m_frequencies"+str(i))
                self.save_obj(self.deviations, "ml27m_deviations"+str(i))

        for (item, ratings) in self.deviations.items():
            for item2 in ratings:
                ratings[item2] /= self.frequencies[item][item2]
        print("Process finish")
    '''

    def calcularDesviacionesSlopeOne(self):
        for ratings in self.data.values(): # para cada persona en los datos obtenemos sus ratings
            for (item, rating) in ratings.items(): #Para cada item y rating en el conjunto de ratings
                self.frecuencias.setdefault(item, {}) #Datos por defecto para evitar errores
                self.desviaciones.setdefault(item, {}) #Datos por defecto para evitar errores
                for (item2, rating2) in ratings.items(): #Para cada item2 y rating2 en el conjunto de ratings
                    if item != item2: #Deben ser diferentes al item actual
                        # Agregar la diferencia entre los ratings a nuestros calculos
                        self.frecuencias[item].setdefault(item2, 0)
                        self.desviaciones[item].setdefault(item2, 0.0)
                        self.frecuencias[item][item2] += 1
                        self.desviaciones[item][item2] += rating - rating2

        for (item, ratings) in self.desviaciones.items():
            for item2 in ratings:
                ratings[item2] /= self.frecuencias[item][item2]

    #Slope one consiste de dos partes
    #1:(hecho antes de tiempo) calcular desviaciones entre cada par de items
    #2: Usar desviaciones para hacer predicciones


    def recomendacionesSlopeOne(self, ratingsUsuario):
        recomendaciones = {}
        frecuencias = {}
        for (userItem, userRating) in ratingsUsuario.items():  # para cada item y rating en las recomendaciones del usuario
            for (diffItem, diffRatings) in self.desviaciones.items(): # para cada item en nuestro dataset que el usuario no ha calificado
                if diffItem not in ratingsUsuario and userItem in self.desviaciones[diffItem]:
                    freq = self.frecuencias[diffItem][userItem]
                    recomendaciones.setdefault(diffItem, 0.0)
                    frecuencias.setdefault(diffItem, 0)
                    # Sumar a la suma corriente que representa el numero de la formula
                    recomendaciones[diffItem] += (diffRatings[userItem] + userRating) * freq
                    # mantener una suma corriente de la frecuencia de diffitem
                    frecuencias[diffItem] += freq

        recomendaciones = [(self.convertProductID2name(k), v / frecuencias[k]) for (k, v) in recomendaciones.items()]
        # finalmente ordenar y retornar
        recomendaciones.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
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

    
    def loadUsers2(self, data):
        for user in data:
            for item in data[user]:
                if item not in self.data:
                    self.data[item] = {}
                self.data[item][user] = data[user][item]
                
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
    def loadMovieLens27M(self, path=''):
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
        #self.productid2name = self.load_obj("product_movies27m")
        

    def distanciaMinkowski(self, usuario1, usuario2, r):
        distancia = 0
        for key in usuario1:
            if key not in usuario1: 
                continue
            if key in usuario2:
                distancia += math.pow(abs(usuario1[key] - usuario2[key]),r)
        return math.pow(distancia, 1/r)


    def cacularDistanciasKnn(self, username):
        usuarios = list(self.data.keys())
        tamTotal = len(usuarios)
        print("Total de usuarios:", tamTotal)
        self.username = username
        ratingsUser = [username,self.data[username]]
        dictlist = []
        dictlist = [ (ratingsUser, [k,v]) for k, v in self.data.items() if k != username]
        t = time.process_time()
        number_of_workers = 24
        with Pool(number_of_workers) as p:
            if self.metric == "pearson":
                distances = p.starmap(pearson_mp, dictlist)
            elif self.metric == "manhattan":
                distances = p.starmap(distanciaManhattan_mp, dictlist)
            elif self.metric == "euclidiana":
                distances = p.starmap(distanciaEuclidiana_mp, dictlist)
            elif self.metric == "coseno":
                distances = p.starmap(similitudCoseno_mp, dictlist)
            
        print("time to process: " , time.process_time()-t)
        import pandas as pd
        if self.metric == "pearson":
            #distances.sort(key=lambda artistTuple: artistTuple[1], reverse=True) # ordenar basado en la distancia, de menor a mayor
            df = pd.DataFrame(distances)
            sorted_values = df.sort_values(by=[1,0], ascending=[False,True])
            distances = sorted_values.agg(list,1).tolist()
        elif self.metric == "manhattan":
            #distances.sort(key=lambda artistTuple: artistTuple[1]) # ordenar basado en la distancia, de menor a mayor
            df = pd.DataFrame(distances)
            sorted_values = df.sort_values(by=[1,0], ascending=[True,True])
            distances = sorted_values.agg(list,1).tolist()
        elif self.metric == "euclidiana":
            #distances.sort(key=lambda artistTuple: artistTuple[1]) # ordenar basado en la distancia, de menor a mayor
            df = pd.DataFrame(distances)
            sorted_values = df.sort_values(by=[1,0], ascending=[True,True])
            distances = sorted_values.agg(list,1).tolist()
        elif self.metric == "minkowski":
            #distances.sort(key=lambda artistTuple: artistTuple[1]) # ordenar basado en la distancia, de menor a mayor
            df = pd.DataFrame(distances)
            sorted_values = df.sort_values(by=[1,0], ascending=[True,True])
            distances = sorted_values.agg(list,1).tolist()
        elif self.metric == "coseno":
            #distances.sort(key=lambda artistTuple: artistTuple[1], reverse=True) # ordenar basado en la distancia, de menor a mayor
            df = pd.DataFrame(distances)
            sorted_values = df.sort_values(by=[1,0], ascending=[False,True])
            distances = sorted_values.agg(list,1).tolist()
        return distances
    
    def calcDesviaciones(self):
        if self.metric == "coseno_ajustado":
            self.calcularDesviaciones()
        elif self.metric == "slope_one":
            self.calcularDesviacionesSlopeOne()
    
    '''
    def calcDesviaciones(self):
        usuarios = list(self.data.keys())
        tamTotal = len(usuarios)
        print("Total de usuarios:", tamTotal)
        t = time.process_time()
        number_of_workers = 5
        #print(self.data.values())
        #dictlist = [ (ratingsUser, [k,v]) for k, v in self.data.items() if k != username]
        #listaRatings = [self.data.values()]
        #listaRatings = list(self.data.values())
        listaRatings = [{'2': 3.5, '29': 3.5, '32': 3.5, '47': 3.5, '50': 3.5, '112': 3.5, '151': 4.0, '223': 4.0, '253': 4.0, '260': 4.0, '293': 4.0, '296': 4.0, '318': 4.0, '337': 3.5, '367': 3.5, '541': 4.0, '589': 3.5, '593': 3.5, '653': 3.0, '919': 3.5, '924': 3.5, '1009': 3.5, '1036': 4.0, '1079': 4.0, '1080': 3.5, '1089': 3.5, '1090': 4.0, '1097': 4.0, '1136': 3.5, '1193': 3.5, '1196': 4.5, '1198': 4.5, '1200': 4.0, '1201': 3.0, '1208': 3.5, '1214': 4.0, '1215': 4.0, '1217': 3.5, '1219': 4.0, '1222': 3.5, '1240': 4.0, '1243': 3.0, '1246': 3.5, '1249': 4.0, '1258': 4.0, '1259': 4.0, '1261': 3.5, '1262': 3.5, '1266': 4.0, '1278': 4.0, '1291': 3.5, '1304': 3.0, '1321': 4.0, '1333': 4.0, '1348': 3.5, '1350': 3.5, '1358': 4.0, '1370': 3.0, '1374': 4.0, '1387': 4.0, '1525': 3.0, '1584': 3.5, '1750': 3.5, '1848': 3.5, '1920': 3.5, '1967': 4.0, '1994': 3.5, '1997': 3.5, '2021': 4.0, '2100': 4.0, '2118': 4.0, '2138': 4.0, '2140': 4.0, '2143': 4.0, '2173': 4.0, '2174': 4.0, '2193': 4.0, '2194': 3.5, '2253': 3.5, '2288': 4.0, '2291': 4.0, '2542': 4.0, '2628': 4.0, '2644': 3.5, '2648': 3.5, '2664': 3.5, '2683': 3.5, '2692': 3.5, '2716': 3.5, '2761': 3.0, '2762': 4.0, '2804': 3.5, '2872': 4.0, '2918': 3.5, '2944': 4.0, '2947': 3.5, '2959': 4.0, '2968': 4.0, '3000': 3.5, '3030': 3.0, '3037': 3.5, '3081': 4.0, '3153': 4.0, '3265': 3.5, '3438': 3.5, '3476': 3.5, '3479': 4.0, '3489': 4.0, '3499': 4.0, '3889': 4.0, '3932': 3.0, '3996': 4.0, '3997': 3.5, '4011': 4.0, '4027': 4.0, '4105': 3.5, '4128': 4.0, '4133': 3.0, '4226': 3.5, '4306': 4.0, '4446': 3.5, '4467': 4.0, '4571': 4.0, '4720': 3.5, '4754': 4.0, '4878': 3.5, '4896': 4.0, '4911': 4.0, '4915': 3.0, '4941': 3.5, '4980': 3.5, '4993': 5.0, '5026': 4.0, '5039': 4.0, '5040': 3.0, '5146': 3.5, '5171': 4.0, '5540': 4.0, '5679': 3.5, '5797': 4.0, '5816': 4.0, '5898': 3.5, '5952': 5.0, '5999': 3.5, '6093': 4.0, '6242': 3.5, '6333': 4.0, '6502': 3.5, '6539': 4.0, '6754': 4.0, '6755': 3.5, '6774': 4.0, '6807': 3.5, '6834': 3.5, '6888': 3.0, '7001': 3.5, '7045': 3.5, '7046': 4.0, '7153': 5.0, '7164': 3.5, '7247': 3.5, '7387': 3.5, '7389': 4.0, '7438': 4.0, '7449': 3.5, '7454': 4.0, '7482': 3.0, '7757': 4.0, '8368': 4.0, '8482': 3.5, '8507': 5.0, '8636': 4.5, '8690': 3.5, '8961': 4.0, '31696': 4.0}, {'3': 4.0, '62': 5.0, '70': 5.0, '110': 4.0, '242': 3.0, '260': 5.0, '266': 5.0, '469': 3.0, '480': 5.0, '541': 5.0, '589': 5.0, '891': 2.0, '908': 4.0, '924': 5.0, '1121': 3.0, '1196': 5.0, '1210': 5.0, '1214': 5.0, '1249': 5.0, '1259': 5.0, '1270': 5.0, '1327': 5.0, '1356': 5.0, '1544': 5.0, '1580': 4.0, '1673': 4.0, '1748': 5.0, '1965': 3.0, '1969': 2.0, '1970': 2.0, '1971': 2.0, '1972': 2.0, '1973': 3.0, '1974': 5.0, '1986': 2.0, '2291': 2.0, '2454': 4.0, '2455': 4.0, '2791': 2.0, '2858': 3.0, '2948': 5.0, '2951': 4.0, '3150': 4.0, '3159': 3.0, '3173': 4.0, '3450': 5.0, '3513': 5.0, '3534': 3.0, '3555': 4.0, '3565': 3.0, '3703': 4.0, '3753': 4.0, '3917': 4.0, '3918': 3.0, '3923': 4.0, '3926': 4.0, '3927': 5.0, '3928': 5.0, '3930': 5.0, '3937': 4.0, '3959': 5.0}, {'1': 4.0, '24': 3.0, '32': 4.0, '50': 5.0, '160': 3.0, '173': 2.0, '175': 5.0, '196': 3.0, '223': 5.0, '260': 5.0, '316': 5.0, '318': 5.0, '329': 5.0, '337': 3.0, '440': 3.0, '442': 3.0, '457': 5.0, '480': 5.0, '490': 5.0, '512': 2.0, '541': 5.0, '589': 4.0, '593': 5.0, '610': 4.0, '718': 3.0, '780': 3.0, '788': 4.0, '858': 5.0, '904': 5.0, '905': 3.0, '919': 4.0, '924': 5.0, '953': 5.0, '968': 3.0, '1037': 3.0, '1060': 5.0, '1073': 5.0, '1077': 4.0, '1079': 4.0, '1084': 5.0, '1089': 5.0, '1094': 4.0, '1097': 5.0, '1103': 4.0, '1125': 4.0, '1127': 3.0, '1129': 5.0, '1179': 3.0, '1188': 2.0, '1193': 4.0, '1196': 5.0, '1197': 5.0, '1198': 5.0, '1199': 4.0, '1200': 4.0, '1206': 5.0, '1208': 5.0, '1210': 5.0, '1213': 5.0, '1214': 5.0, '1215': 4.0, '1219': 4.0, '1220': 5.0, '1221': 5.0, '1222': 5.0, '1225': 3.0, '1228': 3.0, '1230': 5.0, '1240': 5.0, '1242': 5.0, '1247': 5.0, '1257': 5.0, '1258': 5.0, '1259': 5.0, '1261': 5.0, '1266': 5.0, '1270': 5.0, '1272': 4.0, '1276': 5.0, '1278': 5.0, '1288': 2.0, '1304': 5.0, '1307': 4.0, '1321': 5.0, '1330': 3.0, '1333': 4.0, '1345': 4.0, '1356': 5.0, '1372': 3.0, '1373': 4.0, '1374': 5.0, '1375': 5.0, '1376': 4.0, '1396': 3.0, '1544': 4.0, '1584': 4.0, '1603': 4.0, '1653': 4.0, '1674': 4.0, '1676': 5.0, '1721': 4.0, '1762': 4.0, '1779': 3.0, '1810': 3.0, '1831': 5.0, '1876': 4.0, '1882': 4.0, '1909': 5.0, '1917': 4.0, '1921': 4.0, '2009': 5.0, '2011': 3.0, '2012': 3.0, '2018': 4.0, '2028': 4.0, '2034': 4.0, '2046': 5.0, '2053': 3.0, '2054': 4.0, '2076': 5.0, '2093': 5.0, '2105': 4.0, '2117': 5.0, '2118': 5.0, '2140': 4.0, '2150': 5.0, '2236': 4.0, '2288': 5.0, '2311': 4.0, '2329': 4.0, '2366': 4.0, '2371': 4.0, '2391': 5.0, '2407': 4.0, '2428': 4.0, '2448': 5.0, '2455': 4.0, '2505': 4.0, '2528': 4.0, '2529': 5.0, '2530': 4.0, '2531': 3.0, '2532': 4.0, '2533': 3.0, '2541': 1.0, '2551': 4.0, '2567': 3.0, '2571': 5.0, '2574': 3.0, '2613': 4.0, '2615': 4.0, '2628': 5.0, '2640': 4.0, '2642': 3.0, '2643': 1.0, '2657': 3.0, '2662': 3.0, '2668': 4.0, '2676': 1.0, '2694': 4.0, '2699': 3.0, '2710': 5.0, '2722': 4.0, '2750': 4.0, '2788': 5.0, '2791': 5.0, '2797': 4.0, '2808': 4.0, '2857': 3.0, '2872': 5.0, '2900': 3.0, '2901': 3.0, '2916': 4.0, '2918': 5.0, '2947': 4.0, '2948': 4.0, '2949': 4.0, '2968': 5.0, '2985': 5.0, '2986': 2.0, '3033': 5.0, '3039': 5.0, '3070': 4.0, '3072': 4.0, '3098': 4.0, '3142': 4.0, '5060': 5.0}, {'6': 3.0, '10': 4.0, '19': 3.0, '32': 1.0, '165': 3.0, '329': 3.0, '350': 4.0, '356': 4.0, '367': 3.0, '368': 4.0, '370': 4.0, '377': 4.0, '380': 3.0, '420': 3.0, '431': 4.0, '440': 3.0, '454': 5.0, '480': 4.0, '489': 4.0, '519': 3.0, '520': 4.0, '531': 3.0, '548': 3.0, '586': 4.0, '589': 4.0, '594': 4.0, '596': 4.0, '733': 5.0}]
        print(len(listaRatings[0]))

        with Pool(number_of_workers) as p:
            if self.metric == "coseno_ajustado":
                deviations, frequencies = p.map(calcularDesviaciones_mp, listaRatings)
            elif self.metric == "slope_one":
                deviations, frequencies = p.map(calcularDesviaciones_mp, listaRatings)
        from collections import Counter
        deviations = {}
        deviations = Counter(deviations)
        frequencies = {}
        frequencies = Counter(frequencies)
        with Pool(number_of_workers) as p:
            for dev, freq in p.map(calcularDesviaciones_mp, listaRatings):
                print("dev:",freq)
        print(dict(deviations))

    '''

    def save_obj(self, obj, name ):
        with open('pkl_files/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, name ):
        with open('pkl_files/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)

    def calcularKVecinos(self, user):
        try: 
            nearest = self.cacularDistanciasKnn(user)  #obtener la lista de usuarios, ordenados desde mas cercano a mas lejano
        except Exception as e:
            print(e)
            print("No se encontro el usuario en la Base de datos")
            return []
        vecinos = []
        #nearest.sort(key=lambda tuple: (-tuple[1], tuple[0]))
        #nearest.sort(key=lambda tuple: tuple[0])

        #nearest.sort(key=natural_keys)
        '''
        df = pd.DataFrame(nearest)
        sorted_values = df.sort_values(by=[1,0], ascending=[False,True])
        sorted_list = sorted_values.agg(list,1).tolist()

        print(sorted_list)
        vecinos = sorted_list
        '''
        print(nearest[:100])
        for i in range(self.k):
            vecinos.append(nearest[i])
        return vecinos

    def recommend(self, user):
        userRatings = self.data[user] #obtener las calificaciones del usuario
        try: 
            nearest = self.cacularDistanciasKnn(user)  #obtener la lista de usuarios, ordenados desde mas cercano a mas lejano
        except Exception as e:
            print(e)
            print("No se encontro el usuario en la Base de datos")
            return []

        sumaDistancias = 0.0
        for i in range(self.k):
            print("Vecino cercano:", nearest[i])
            sumaDistancias += nearest[i][1]
        if sumaDistancias == 0.0:
            print("No se encontraron recomendaciones")
            return []
        recommendations = {}
        for i in range(self.k):        # acumular las calificaciones de los k vecinos
            weight = nearest[i][1] / sumaDistancias  # calcular su porcentaje 
            name = nearest[i][0] # obtener el nombre de la persona

            if name==user:
                continue
            #print (name)
            neighborRatings = self.data[name] # obtener las calififaciones de esa persona
            #print(neighborRatings)
            #print("Vecino cercano:" + name)
            for artist in neighborRatings: #buscar las calificaciones que el vecino hizo y el usuario no hizo
                if not artist in userRatings:
                    if neighborRatings[artist] >= self.umbral or self.umbral==0:
                        if artist not in recommendations:
                            #    if neighborRatings[artist] > userRatings[artist]:
                            recommendations[artist] = neighborRatings[artist]
                        else:
                            #if neighborRatings[artist] > userRatings[artist]:
                            recommendations[artist] = (recommendations[artist] + neighborRatings[artist])/2
                        
        recommendations = list(recommendations.items())
        recommendations = [(self.convertProductID2name(k), v)
                          for (k, v) in recommendations]
        recommendations.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        return recommendations[:self.n] # devolver las recomendaciones solicitadas

    def porcentajeProyectado(self, user, item):
        userRatings = self.data[user] #obtener las calificaciones del usuario
        #print("Calificaciones del usuario:") #print(userRatings)
        try: 
            nearest = self.cacularDistanciasKnn(user)  #obtener la lista de usuarios, ordenados desde mas cercano a mas lejano
        except Exception as e:
            print(e)
            print("No se encontro el usuario en la Base de datos")
            return []

        sumaDistancias = 0.0
        for i in range(self.k):
            if item not in self.data[nearest[i][0]]:  #el vecino no califico esa pelicula
                continue
            sumaDistancias += nearest[i][1]
        if sumaDistancias == 0.0:
           print("No se encontraron recomendaciones")
           return []

        recommendations = {}
        for i in range(self.k):        # acumular las calificaciones de los k vecinos
            weight = nearest[i][1] / sumaDistancias  # calcular su porcentaje 
            name = nearest[i][0] # obtener el nombre de la persona
            neighborRatings = self.data[name] # obtener las calififaciones de esa persona
            if item not in neighborRatings:#el vecino no califico esa pelicula
                continue
            print("Name:", name, ":", neighborRatings[item])
            if item not in recommendations:
                recommendations[item] = neighborRatings[item] * weight
            else:
                recommendations[item] = (recommendations[item] + neighborRatings[item] * weight)
        return recommendations[item]

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
    t=time.process_time()
    recomendador.loadMovieLens27M("ml-latest/")
    #recomendador.loadUsers2(users2)
    print("Total time to load data: " , time.process_time()-t)
    #print(recomendador.productid2name.keys())
    #recomendador.parallelDesviaciones()
    #recomendador.loadMovieRatingsDB("dataset/")
    #recomendador.data = users2
    #print(len(recomendador.data['1']))
    #print("num de peliculas:", len(recomendador.productid2name.keys()))
    t=time.process_time()
    #recomendador.calcularDesviacion2Items('Taylor Swift','PSY')
    #recomendador.calcularDesviacion2Items('PSY','Taylor Swift')
    #recomendador.calcularDesviacion2Items('1', '15')
    '''
    recomendador.calcularDesviacion2Items('1','2')
    recomendador.calcularDesviacion2Items('1','3')
    '''
    #recomendador.calcularDesviaciones1Item('1')
    recomendador.calcularDesviaciones1Item_mp('1')
    #recomendador.calcularDesviaciones1Item('1')
    #print(recomendador.desviaciones)
    #print(recomendador.frecuencias)
    print("Total time to calculate desviation 2 items: " , time.process_time()-t)
    '''
    recomendador.metric="slope_one"
    recomendador.calcDesviaciones()
    userRatings = recomendador.data['Ben']
    recomendaciones = recomendador.recomendacionesSlopeOne(userRatings)
    print(recomendador.desviaciones)
    print(recomendaciones)
    '''
'''
#su -c "echo 3 >'/proc/sys/vm/drop_caches' && swapoff -a && swapon -a && printf '\n%s\n' 'Ram-cache and Swap Cleared'" root
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  CODIGO  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Aplicacion():

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
            self.treeview_sort_column(tv, col, not reverse))

    def __init__(self):
        raiz = Tk()
        raiz.geometry('1000x650')
        raiz.configure() #bg = '#2D866B'
        raiz.title('SISTEMA DE RECOMENDACION - TOPICOS DE BASE DE DATOS (UNSA)')

        #imagen = PhotoImage(file="/home/hayde/Escritorio/FINAL TBD/unsa3.gif")
        #Label(raiz, image=imagen, bd=0).side="right"
# ++++++++++++++++++++++++++++++++++++++++ FUNCIONES DEL CODIGO PRINCIPAL +++++++++++++++++++++++++++++++++++
        
        self.recomendador = Recomendador({}, k=4, metric='coseno', n=10)
        self.txtUserID = StringVar()
        self.txtKVecinos = StringVar()
        self.txtKVecinos.set("4")
        self.txtTCargaBD = StringVar()
        self.txtTEjecucion = StringVar()
        self.txtIdNewUser = StringVar()

        self.txtUserIdRating = StringVar()
        self.txtItemIdRating = StringVar()
        self.txtRatRating = StringVar()

        self.txtUserID1 = StringVar()
        self.txtUserID2 = StringVar()
        self.txtItem = StringVar()
        self.txtUmbral = StringVar()
        self.txtUmbral.set("2")

        self.txtNRecomendaciones = StringVar()
        self.txtNRecomendaciones.set("10")

# ++++++++++++++++++++++++++++++++++++ ++++++++++++++++++++++++++++++++++++++++++++++++
        self.Tabla_Resultados = ttk.Treeview(raiz)
        self.Tabla_Resultados.place(x=230, y=15, width=500, height=400)
        self.Tabla_Resultados["columns"] = ("1", "2","3","4")
        self.Tabla_Resultados.column("1", width=150)
        self.Tabla_Resultados.column("2", width=50)
        self.Tabla_Resultados.column("3", width=50)
        #self.Tabla_Resultados.column("4", width=50)

        self.Tabla_Resultados.heading("1", text="Distancia", command=lambda: self.treeview_sort_column(self.Tabla_Resultados, "1", False))
        self.Tabla_Resultados.heading("2", text="Pelicula", command=lambda: self.treeview_sort_column(self.Tabla_Resultados, "2", False))
        self.Tabla_Resultados.heading("3", text="Puntaje", command=lambda: self.treeview_sort_column(self.Tabla_Resultados, "3", False))
        #self.Tabla_Resultados.heading("4", text="Vecino", command=lambda: self.treeview_sort_column(self.Tabla_Resultados, "4", False))
     
# ++++++++++++++++++++++++++++++++++++ COMBOBOX 01: DATASET ++++++++++++++++++++++++++++++++++++++++++++++++

        Label_Data=LabelFrame(raiz,text='Paso 1:')
        Label_Data.place(x=10,y=15, width=200, height=120)

        Etiqueta_Dataset=Label(Label_Data, text='Eliga DataSet')
        Etiqueta_Dataset.place(x=10,y=30, width=150, height=30)
        Etiqueta_Dataset.pack()

        self.ListaDespleDataset = ttk.Combobox(Label_Data, values=["Libros 1M","Peliculas 10M","Peliculas 20M","Peliculas 27M"])
        self.ListaDespleDataset.place(x=10,y=60, width=180, height=30)
        self.ListaDespleDataset.current(3)
        self.ListaDespleDataset.pack()

        Button_CargarDataset=Button(Label_Data, text='CARGAR DATASET', command=self.loadDataset)
        Button_CargarDataset.place(x=10,y=150, width=150, height=30)
        Button_CargarDataset.pack()
#++++++++++++++++++++++++++++++++++++++++ PASO @ +++++++++++++++++++++++++++++++++++++++++++++++
        Label_Algoritmo=LabelFrame(raiz,text='Paso 2:')
        Label_Algoritmo.place(x=10,y=150, width=200, height=110)

        Etiqueta_Distancias=Label(Label_Algoritmo, text='Eliga Distancia: ')
        Etiqueta_Distancias.place(x=20,y=150, width=150, height=30)
        Etiqueta_Distancias.pack()

        self.ListaDespleDistancia = ttk.Combobox(Label_Algoritmo, values=["Manhattan","Similitud Coseno","Pearson","Euclidiana", "Coseno ajustado", "Slope One"])
        self.ListaDespleDistancia.place(x=10,y=20, width=180, height=30)
        self.ListaDespleDistancia.current(1)
        self.ListaDespleDistancia.pack()

        btnCalcularDesviaciones=Button(Label_Algoritmo, text='Calcular Desviaciones', command=self.calcularDesviaciones)
        btnCalcularDesviaciones.place(x=10,y=30, width=150, height=30)
        btnCalcularDesviaciones.pack()
# ++++++++++++++++++++++++++++++++++++ COMBOBOX 01: OPCIONAL ++++++++++++++++++++++++++++++++++++++++++++++++
        Label_Opcional=LabelFrame(raiz,text='Paso 3:')
        Label_Opcional.place(x=10, y=280, width=200, height=200)

        self.ListaDespleAccion = ttk.Combobox(Label_Opcional, values=["K Vecinos Cercanos","Recomendar Peliculas","Porcentaje proyectado","Comparar Dos Usuarios", "Obtener Calificaciones del Usuario"])
        self.ListaDespleAccion.place(x=10,y=140, width=180, height=30)
        self.ListaDespleAccion.current(1)

        Etiqueta_Usuario1=Label(Label_Opcional, text='Usuario 1')
        Etiqueta_Usuario1.place(x=10,y=250, width=150, height=30)
        Etiqueta_Usuario1.pack()

        Entrada_Usuario1=Entry(Label_Opcional, text=' ',  textvariable=self.txtUserID1)
        Entrada_Usuario1.place(x=10,y=300, width=150, height=30)
        Entrada_Usuario1.pack()
        
        Etiqueta_Usuario2=Label(Label_Opcional, text='Usuario 2')
        Etiqueta_Usuario2.place(x=10,y=110, width=150, height=30)
        Etiqueta_Usuario2.pack()

        Entrada_Usuario2=Entry(Label_Opcional, text=' ',  textvariable=self.txtUserID2)
        Entrada_Usuario2.place(x=10,y=145, width=150, height=30)
        Entrada_Usuario2.pack()

        Etiqueta_Usuario3=Label(Label_Opcional, text='Item')
        Etiqueta_Usuario3.place(x=10,y=250, width=150, height=30)
        Etiqueta_Usuario3.pack()

        Entrada_Usuario3=Entry(Label_Opcional, text=' ',  textvariable=self.txtItem)
        Entrada_Usuario3.place(x=10,y=210, width=150, height=30)
        Entrada_Usuario3.pack()
    
    
        ################################# LADO Izquierdo ########################################
        Label_HacerRecomendacion=LabelFrame(raiz, text='HACER RECOMENDACION')
        Label_HacerRecomendacion.place(x=140, y=470, width=200, height=150)

        Etiqueta_Usuario=Label(Label_HacerRecomendacion, text='ID del usuario')
        Etiqueta_Usuario.place(x=500, y=110, width=150, height=25)
        Etiqueta_Usuario.pack()

        Entrada_Usuario=Entry(Label_HacerRecomendacion, text=' ',  textvariable=self.txtUserID)
        Entrada_Usuario.place(x=500, y=140, width=150, height=30)
        Entrada_Usuario.pack()

        Etiqueta_KVecinos=Label(Label_HacerRecomendacion, text='K')
        Etiqueta_KVecinos.place(x=700, y=110, width=90, height=25)
        Etiqueta_KVecinos.pack()

        Entrada_KVecinos=Entry(Label_HacerRecomendacion, text=' ', textvariable = self.txtKVecinos)
        Entrada_KVecinos.place(x=700, y=140, width=90, height=25)
        Entrada_KVecinos.pack()

        Button_Recomendar=Button(Label_HacerRecomendacion, text='EJECUTAR (PASO 3)',command=self.ejecutarAccion)
        Button_Recomendar.place(x=500, y=180, width=150, height=40)
        Button_Recomendar.pack()

# ++++++++++++++++++++++++++++++++++++ ++++++++++++++++++++++++++++++++++++++++++++++++
        Label_Resultado=LabelFrame(raiz,text='')
        Label_Resultado.place(x=380, y=470, width=200, height=150)

        Etiqueta_Umbral=Label(Label_Resultado, text='Umbral')
        Etiqueta_Umbral.place(x=795, y=110, width=90, height=30)
        Etiqueta_Umbral.pack()

        Entrada_Umbral=Entry(Label_Resultado, text=' ', textvariable=self.txtUmbral)
        Entrada_Umbral.place(x=795, y=140, width=90, height=30)
        Entrada_Umbral.pack()

        Etiqueta_Umbral=Label(Label_Resultado, text='# Recomendaciones')
        Etiqueta_Umbral.place(x=795, y=110, width=90, height=30)
        Etiqueta_Umbral.pack()

        Entrada_nRecomendaciones=Entry(Label_Resultado, text=' ', textvariable=self.txtNRecomendaciones)
        Entrada_nRecomendaciones.place(x=795, y=140, width=90, height=30)
        Entrada_nRecomendaciones.pack()
        #+++++++++++++++++++++++++++++++++++++++++ SALIR / TIEMPOS +++++++++++++++++++++++++++++++++++++++        

        LabelTiempos=LabelFrame(raiz,text='TIEMPOS')
        LabelTiempos.place(x=600, y=470, width=200, height=150)

        Etiqueta_TCarga=Label(LabelTiempos, text='Tiempo Carga_BD')
        Etiqueta_TCarga.place(x=140, y=530, width=150, height=30)
        Etiqueta_TCarga.pack()

        self.Entrada_TCarga=Entry(LabelTiempos, text=' ', textvariable=self.txtTCargaBD)
        self.Entrada_TCarga.place(x=140, y=565, width=150, height=30)
        self.Entrada_TCarga.pack()

        Etiqueta_TEjecucion=Label(LabelTiempos, text='Tiempo Ejecucion')

        Etiqueta_TEjecucion.place(x=300, y=530, width=150, height=30)
        Etiqueta_TEjecucion.pack()

        Entrada_TEjecucion=Entry(LabelTiempos, text=' ', textvariable=self.txtTEjecucion)
        Entrada_TEjecucion.place(x=300, y=565, width=150, height=30)
        Entrada_TEjecucion.pack()

        Button_Salir=Button(raiz, text='Salir', command=raiz.destroy)
        Button_Salir.place(x=860, y=20, width=100, height=40)

#************************************************* TIEMPO REAL **********************************************   
        Label_Nuevo=LabelFrame(raiz,text='TIEMPO REAL')
        Label_Nuevo.place(x=750, y=100, width=225, height=350)
        #+++++++++++++++++++++++++++++++++++++++++ CALIFICAR PELICULA+++++++++++++++++++++++++++++++++++++++        

        Label_RegistrarUsua=LabelFrame(Label_Nuevo, text='Registrar Nuevo Usuario')
        Label_RegistrarUsua.place(x=600, y=10, width=200, height=250)
        Label_RegistrarUsua.pack()

        Etiqueta_IDuserNuevo=Label(Label_RegistrarUsua, text='ID Usuario nuevo')
        Etiqueta_IDuserNuevo.place(x=600, y=340, width=100, height=35) 
        Etiqueta_IDuserNuevo.pack()

        Entrada_IDusuario=Entry(Label_RegistrarUsua, text='', textvariable=self.txtIdNewUser)
        Entrada_IDusuario.place(x=600, y=340, width=100, height=35) 
        Entrada_IDusuario.pack()

        Button_Agregar=Button(Label_RegistrarUsua, text='Agregar', command=self.addUser)
        Button_Agregar.place(x=600, y=340, width=100, height=40) 
        Button_Agregar.pack()
        #+++++++++++++++++++++++++++++++++++++++++ CALIFICAR PELICULA+++++++++++++++++++++++++++++++++++++++        

        Label_CalificarPeli=LabelFrame(Label_Nuevo, text='Calificar Pelicula')
        Label_CalificarPeli.place(x=820, y=15, width=180, height=250)
        Label_CalificarPeli.pack()

        Etiqueta_IDUsuario=Label(Label_CalificarPeli, text='ID Usuario')
        Etiqueta_IDUsuario.place(x=810, y=425, width=100, height=35)
        Etiqueta_IDUsuario.pack()

        Entrada_IDUsuario=Entry(Label_CalificarPeli, text=' ', textvariable=self.txtUserIdRating)
        Entrada_IDUsuario.place(x=30, y=460, width=100, height=35)
        Entrada_IDUsuario.pack()

        Etiqueta_IDPelicula=Label(Label_CalificarPeli, text='ID Pelicula')
        Etiqueta_IDPelicula.place(x=140, y=425, width=100, height=35)
        Etiqueta_IDPelicula.pack()

        Entrada_IDPelicula=Entry(Label_CalificarPeli, text=' ', textvariable=self.txtItemIdRating)
        Entrada_IDPelicula.place(x=140, y=460, width=100, height=35)
        Entrada_IDPelicula.pack()

        Etiqueta_Calificacion=Label(Label_CalificarPeli, text='0-10')
        Etiqueta_Calificacion.place(x=250, y=425, width=100, height=35)
        Etiqueta_Calificacion.pack()

        Entrada_Calificacion=Entry(Label_CalificarPeli, text=' ', textvariable=self.txtRatRating)
        Entrada_Calificacion.place(x=250, y=460, width=100, height=35)
        Entrada_Calificacion.pack()

        Button_Calificar=Button(Label_CalificarPeli, text='Calificar', command=self.calificarItem)
        Button_Calificar.place(x=370, y=435, width=100, height=40) 
        Button_Calificar.pack()
#************************************************* TIEMPO REAL **********************************************


       
        # Mostrar la raiz
        raiz.mainloop() 

    def loadDataset(self):
        value = self.ListaDespleDataset.get()

        t= time.process_time()
        if value == "Libros 1M":
            self.recomendador.loadBookDB("dataset/BX-Dump/")
        elif value == "Peliculas 10M":
            self.recomendador.loadMovieLens("ml-10M100K/")
        elif value == "Peliculas 20M":
            self.recomendador.loadMovieLens20M("ml-20m/")
        elif value == "Peliculas 27M":
            self.recomendador.loadMovieLens27M("ml-latest/")

        print("Total time to load data: " , time.process_time()-t)
        self.txtTCargaBD.set(time.process_time()-t)
    
    def ejecutarAccion(self):
        accion = self.ListaDespleAccion.get()
        if accion == "K Vecinos Cercanos":
            self.calcularKVecinos()
        elif accion == "Recomendar Peliculas":
            self.recomendarItems()
        elif accion == "Porcentaje proyectado":
            self.calcularPorcentajeProyectado()
        elif accion == "Comparar Dos Usuarios":
            self.compararUsuarios()
        else: #Obtener calificaciones del usuario
            self.ObtenerCalificacionesUsuario()


    def setMedidaDistancia(self):
        metrica = self.ListaDespleDistancia.get()

        if metrica == "Manhattan":
            self.recomendador.metric = "manhattan"
            print("USANDO: manhattan")
        elif metrica == "Similitud Coseno":
            self.recomendador.metric = "coseno"
            print("USANDO: coseno")
        elif metrica == "Pearson":
            self.recomendador.metric = "pearson"
            print("USANDO: pearson")
        elif metrica == "Euclidiana":
            self.recomendador.metric = "euclidiana"
            print("USANDO: euclidiana")
    
    def calcularPorcentajeProyectado(self):
        self.setMedidaDistancia()
        self.recomendador.k = int(self.txtKVecinos.get())
        t = time.process_time()
        porcentaje = self.recomendador.porcentajeProyectado(self.txtUserID1.get(), self.txtItem.get())
        self.txtTEjecucion.set(time.process_time()-t)
        self.Tabla_Resultados.delete(*self.Tabla_Resultados.get_children())
        nombreItem = self.recomendador.convertProductID2name(self.txtItem.get())
        self.Tabla_Resultados.insert("", 0, text="", values=("", nombreItem, porcentaje))

        print(porcentaje)

    def calcularKVecinos(self):
        self.recomendador.k = int(self.txtKVecinos.get())
        self.setMedidaDistancia()
        t = time.process_time()
        vecinos = self.recomendador.calcularKVecinos(self.txtUserID1.get())
        self.txtTEjecucion.set(time.process_time()-t)

        self.Tabla_Resultados.delete(*self.Tabla_Resultados.get_children())
        for vecino in vecinos:
            self.Tabla_Resultados.insert("", 0, text=vecino[0], values=(vecino[1], "",""))

        print(vecinos)

    def compararUsuarios(self):
        usuario1 = self.txtUserID1.get()
        usuario2 = self.txtUserID2.get()
        us1 = [usuario1, self.recomendador.data[usuario1]]
        us2 = [usuario2, self.recomendador.data[usuario2]]
        self.setMedidaDistancia()
        t= time.process_time()
        if self.recomendador.metric == "pearson":
            resultado = pearson_mp(us1, us2)
        elif self.recomendador.metric == "manhattan":
            resultado = distanciaManhattan_mp(us1, us2)
        elif self.recomendador.metric == "euclidiana":
            resultado = distanciaEuclidiana_mp(us1, us2)
        elif self.recomendador.metric == "coseno":
            resultado = similitudCoseno_mp(us1, us2)
        self.txtTEjecucion.set(time.process_time()-t)
        self.Tabla_Resultados.delete(*self.Tabla_Resultados.get_children())
        self.Tabla_Resultados.insert("", 0, text=usuario1+","+usuario2, values=(resultado[1], "",""))
        

    def recomendarItems(self):
        print("Recomendando para:", self.txtUserID.get())
        print("CON K:", self.txtKVecinos.get())
        self.recomendador.k = int(self.txtKVecinos.get())
        self.recomendador.n = int(self.txtNRecomendaciones.get())
        self.recomendador.umbral = float(self.txtUmbral.get())
        self.setMedidaDistancia()

        t= time.process_time()
        recomendaciones = self.recomendador.recommend(self.txtUserID.get())
        self.txtTEjecucion.set(time.process_time()-t)
        print("Total time to process data: " , time.process_time()-t)

        self.Tabla_Resultados.delete(*self.Tabla_Resultados.get_children())

        for item in recomendaciones:
            self.Tabla_Resultados.insert("", 0, text="", values=("", item[0],item[1]))

        print(recomendaciones)

    def ObtenerCalificacionesUsuario(self):
        userId = self.txtUserID1.get()
        calificaciones = self.recomendador.getCalificacionesUsuario(userId)
        self.Tabla_Resultados.delete(*self.Tabla_Resultados.get_children())
        i = 0
        for movieID in calificaciones:
            if i>=int(self.txtNRecomendaciones.get()): break
            rating = calificaciones[movieID]
            movieName = self.recomendador.convertProductID2name(movieID)
            self.Tabla_Resultados.insert("", 0, text="", values=("", movieName,rating))
            i = i+1
        
    def addUser(self):
        self.recomendador.addUser(self.txtIdNewUser.get())
        messagebox.showinfo("Agregado", "Usuario agregado")

    def calificarItem(self):
        self.recomendador.calificarItem(self.txtUserIdRating.get(), self.txtItemIdRating.get(), self.txtRatRating.get())
        messagebox.showinfo("Agregado", "Calificación agregada:" + self.txtUserIdRating.get()  + "," + self.txtItemIdRating.get() + ", " + self.txtRatRating.get())

    def calcularDesviaciones(self):

                
        #r = recommender(users2)
        #r.calcularDesviaciones()
        #g = users2['Ben']
        #r.slopeOneRecommendations(g)

        #[('Whitney Houston', 3.375)]

        metrica = self.ListaDespleDistancia.get()
        if metrica == "Coseno ajustado":
            self.recomendador.metric = "coseno_ajustado"
            print("USANDO: COSENO AJUSTADO")
        elif metrica == "Slope One":
            self.recomendador.metric = "slope_one"
            print("USANDO: SLOPE ONE")
        self.recomendador.calcDesviaciones()
        print(self.recomendador.frequencies())
        print(self.recomendador.deviations())

def main():
    mi_app = Aplicacion()
    return 0

if __name__ == '__main__':
    main()
'''
