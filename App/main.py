from flask import Flask, render_template             

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

@app.route("/slopeOne")
def slopeOne():
    return render_template("slopeOne.html")

@app.route("/addUser")
def addUser():
	return render_template("adduser.html")

@app.route("/addMovie")
def addMovie():
	return render_template("addmovie.html")

if __name__ == "__main__":
    app.run(debug=True)
  	#We made two new changes	
