from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort
from flask import Flask
from database import Database
import os

app = Flask(__name__)

app.secret_key = '1234'

site = Blueprint('site', __name__, template_folder='templates')

database = Database()

database.create_users_table()
 
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        if database.user_exists(username, password):
            session['logged_in'] = True
            return redirect(url_for('home'))
            
        else:
            flash('login inválido')
    
    return render_template('login.html')
 
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/register")
def register():
    return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True)