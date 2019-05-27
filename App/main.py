from flask import Flask, render_template, request         
import time  


import sys
sys.path.insert(0, '../Cosine_Slopone_itembased')
import recomendador

recSystem = recomendador.Recomendador({})
tInit = time.time()

import os
owd = os.getcwd()
os.chdir("../Cosine_Slopone_itembased/")
recomendador.loadDataset()
recomendador.loadLinks()
os.chdir(owd)
print("time to load data:", time.time()-tInit)
print(len(recomendador.clavesTotal))


app = Flask(__name__)
usuario = "10"
k_value = 10

@app.route("/",methods=['GET','POST'])
def home():
    owd = os.getcwd()
    os.chdir("../Cosine_Slopone_itembased/")
    ListaVistas = recSystem.YaVistos(usuario)
    #print(ListaVistas)

    ListaIMDB = {}
    for i in ListaVistas:
        ListaIMDB[i[1]] =  recSystem.getImdbIdByMovieId(i[1])
    #toRecommend = recSystem.recomendarKItems(usuario,k_value)
    #print(toRecommend)
    os.chdir(owd)
    return render_template("index.html",result = ListaVistas[:3], usuario = usuario, ListaIMDB = ListaIMDB)

@app.route("/prueba")
def salvador():
    return render_template("prueba.html")

@app.route("/ranking")
def ranking():
    return render_template("ranking.html")

@app.route("/slopeOne",methods=['GET','POST'])
def slopeOne():
	#render_template("slopeOne.html")
	predecido = ''
	tiempoCalculo = ''
	imdbId = ''
	mensaje = ''

	if request.method == 'POST':
		usuario = request.form['usuario_slopeone']
		item = request.form['item_slopeone']
		metodo = request.form["itembased_m"]

		#print(usuario)
		t = time.time()
		owd = os.getcwd()
		os.chdir("../Cosine_Slopone_itembased/")

		if metodo=="slopeone":
			predecido = recSystem.recomendacionesSlopeOneItem(usuario, item, reload=0)
			if type(predecido) is dict:
				mensaje = predecido["mensaje"]
				predecido = predecido["rating"]
			else:
				if predecido == []:
					mensaje = "El item no tiene niguna relación con el usuario"
					predecido = 0
				else:
					predecido = predecido[0][1]
		else:
			predecido = recSystem.predecirSimilitudCosenoAjustado(usuario, item, reload=0)
			if type(predecido) is dict:
				mensaje = predecido["mensaje"]
				predecido = predecido["rating"]
			
		os.chdir(owd)
		tiempoCalculo = time.time()-t

		imdbId = recSystem.getImdbIdByMovieId(item)

		print("Time to calculate similitud:", tiempoCalculo)
	else:
		usuario = ''
		item = ''
	#print(user)
	#return render_template("slopeOne.html")
	
	temp = ["Firulais","abc","cde"]
	return render_template("slopeOne.html",result = temp, usuario = usuario, item=item, predecido=predecido, tiempoCalculo=tiempoCalculo, imdbId=imdbId, mensaje=mensaje)

@app.route("/addUser")
def addUser():
	return render_template("adduser.html")

@app.route("/addMovie", methods=['GET','POST'])
def addMovie():
	if request.method == 'POST':
		print("add movie post")
		usuario = request.form['userid']
		item = request.form['itemid']
		rating = request.form["rating"]
		owd = os.getcwd()
		os.chdir("../Cosine_Slopone_itembased/")
		recSystem.agregarRating(usuario, item, rating)
		os.chdir(owd)
	return render_template("addmovie.html")

@app.route("/mostrarKPrimeros", methods=['GET','POST'])
def mostrarKPrimeros():
	predecido = ''
	tiempoCalculo = ''
	imdbId = ''
	mensaje = ''
	resultados = ""
	if request.method == 'POST':
		item_slopeone = request.form["item_slopeone"]
		k_slopeone = request.form["k_slopeone"]
		metodo = request.form["itembased_m"]

		owd = os.getcwd()
		os.chdir("../Cosine_Slopone_itembased/")

		if metodo!="slopeone":
			resultados = recSystem.getKPrimerosCosenoByItem(item_slopeone, k_slopeone)
		else:
			resultados = recSystem.getKPrimerosSlopeOneByItem(item_slopeone, k_slopeone)
		
		os.chdir(owd)
	return render_template("cargarFila.html", resultados=resultados)

if __name__ == "__main__":
    app.run(debug=True)
  	#We made two new changes	
