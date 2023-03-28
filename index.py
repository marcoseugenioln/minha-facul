from flask import Flask, redirect, url_for, request, render_template, Blueprint

app = Flask(__name__)

site = Blueprint('site', __name__, template_folder='templates')
 
@app.route("/")
def index():
    return render_template("index.html")
 
if __name__ == '__main__':
    app.run(debug=True)