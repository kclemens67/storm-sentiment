from flask import Flask
app = Flask(__name__)
from flaskexample import views



@app.errorhandler(500)
def page_not_found(e):
    return render_template('bad_output.html'), 500


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000)
