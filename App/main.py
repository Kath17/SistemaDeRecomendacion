from flask import Flask, render_template             

app = Flask(__name__)

@app.route("/")

def home():
    return render_template("index.html")

@app.route("/prueba")

def salvador():
    return render_template("prueba.html")

if __name__ == "__main__":
    app.run(debug=True)
  	#We made two new changes	