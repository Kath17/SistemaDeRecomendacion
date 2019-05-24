from flask import Flask, render_template, request         
import time  

import sys
sys.path.insert(0, '../Cosine_Slopone_itembased')
import cosenoajustado

recomendador = cosenoajustado.Recomendador({}, k=4, metric='coseno', n=10)
tInit = time.time()

import os
owd = os.getcwd()
os.chdir("../Cosine_Slopone_itembased/")
cosenoajustado.loadDataset()
os.chdir(owd)
print("time to load data:", time.time()-tInit)


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

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

	if request.method == 'POST':
		usuario = request.form['usuario_slopeone']
		item = request.form['item_slopeone']
		print(usuario)
		#usuario = '1'
		#item = '3'
		t = time.time()
		owd = os.getcwd()
		os.chdir("../Cosine_Slopone_itembased/")
		predecido = recomendador.predecirSimilitudCosenoAjustado(usuario, item, reload=0)
		os.chdir(owd)
		tiempoCalculo = time.time()-t
		print("Time to calculate similitud:", tiempoCalculo)
	else:
		usuario = ''
		item = ''
	#print(user)
	#return render_template("slopeOne.html")
	
	temp = ["Firulais","abc","cde"]
	return render_template("slopeOne.html",result = temp, usuario = usuario, item=item, predecido=predecido, tiempoCalculo=tiempoCalculo)

@app.route("/addUser")
def addUser():
	return render_template("adduser.html")

@app.route("/addMovie")
def addMovie():
	return render_template("addmovie.html")

if __name__ == "__main__":
    app.run(debug=True)
  	#We made two new changes	
