from flask import Flask
app = Flask(__name__)
from flaskexample import views



if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000)
