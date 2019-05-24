from flask import Flask, render_template, request           

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
	#user = request.form['usuario_slopeone']
	#print(user)
	#return render_template("slopeOne.html")
	temp = ["Firulais","abc","cde"]
	return render_template("slopeOne.html",result = temp)

@app.route("/addUser")
def addUser():
	return render_template("adduser.html")

@app.route("/addMovie")
def addMovie():
	return render_template("addmovie.html")

if __name__ == "__main__":
    app.run(debug=True)
  	#We made two new changes	
