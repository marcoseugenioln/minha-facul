from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort
from flask import Flask
from database import Database
import logging
import os
import math
import sqlite3
import requests
import urllib.parse

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('site-log.log')
logger.addHandler(handler)

app = Flask(__name__)
app.secret_key = '1234'
site = Blueprint('site', __name__, template_folder='templates')

database = Database()
 
@app.route("/")
def index():
        return redirect(url_for(f'login'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    is_login_valid = True

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        
        # Create variables for easy access
        username = request.form['email']
        password = request.form['password']

        if database.user_exists(username, password):
            user_id = database.get_user_id(username, password)

            if database.is_admin(user_id):
                return redirect(url_for(f'admin', blk = 1, user_id = user_id))
                
            else:
                return redirect(url_for(f'busca', user_id = user_id))
        else:
            is_login_valid = False
    
    return render_template('login.html', is_login_valid = is_login_valid)

@app.route("/register", methods=['GET','POST'])
def register():

    is_password_valid = True
    is_email_valid = True

    courses = database.get_courses()

    if (request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'password_c' in request.form and 'local_txt' in request.form and 'course' in request.form):
        
        email = request.form['email']
        password = request.form['password']
        password_c = request.form['password_c']
        local_txt = request.form['local_txt']
        course = request.form['course']

        response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyAGVxQoVpwxbdrDaaXy4Ok6ao_MiURaIrU&address={urllib.parse.quote(local_txt, safe="")}')
        location = response.json()['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']

        if database.insert_user(email, password, password_c, local_txt, latitude, longitude, course):
            return redirect(url_for('login'))
        else:
            if len(email) > 300:
                is_email_valid = False
            elif len(password)> 64:
                is_password_valid = False
            elif password_c != password:
                is_password_valid = False                
    
    return render_template('register.html', is_password_valid = is_password_valid, is_email_valid = is_email_valid, courses=courses)

def chord_length_sc(lon_1, lat_1, lon_2, lat_2):
    # https://en.wikipedia.org/wiki/Great-circle_distance ### From chord length
    # distancia aproximada em km

    dx = math.cos(lon_2) * math.cos(lat_2) - math.cos(lon_1) * math.cos(lat_1)
    dy = math.cos(lon_2) * math.sin(lat_2) - math.cos(lon_1) * math.sin(lat_1)
    dz = math.sin(lon_2) - math.sin(lon_1)

    cc = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2) + math.pow(dz, 2))

    return 2 * math.asin(cc / 2.0) * 6371


def ajustaComparativo(base, ref):
    fator = math.pi / 180
    ref_lat, ref_lon = ref
    ref_lat = ref_lat * fator
    ref_lon = ref_lon * fator
    resp = []
    for x in base:
        _, _, faculdade, _, local_lat, local_lon, cpv, cpv_1, cpv_2 = x
        resp.append((faculdade, round(chord_length_sc(local_lon * fator, local_lat * fator, ref_lon, ref_lat), 2), round(cpv, 2), round(cpv_1, 2), round(cpv_2, 2)))

    return resp

@app.route('/busca/<user_id>', methods=['GET', 'POST'])
def busca(user_id):
    #todo: checar se usuário esta logado
    conn = sqlite3.connect('minhafacul.db')
    c = conn.cursor()

    if request.method == 'POST':
        # Atualiza os dados de local e curso selecionado
        conn.execute("UPDATE USUARIO SET CURSO_ID=?, LOCAL_TXT=?, LOCAL_LAT=?, LOCAL_LON=? WHERE USUARIO_ID=?;",
                     (request.form['curso_id'], request.form['local_txt'], request.form['local_lat'], request.form['local_lon'], user_id))
        conn.commit()

    # Consulda dados do usário para construir a busca
    c.execute("SELECT USUARIO_ID, EMAIL, CURSO_ID, LOCAL_TXT, LOCAL_LAT, LOCAL_LON FROM USUARIO WHERE USUARIO_ID=?", (user_id, ))
    userdat = c.fetchall()

    # Consulta a tabela de cursos e retorna uma lista de tuplas com os dados
    c.execute("SELECT CURSO_ID, CURSO FROM CURSO")
    cursos = c.fetchall()

    if (userdat[0][2]>0 and userdat[0][4] != '' and userdat[0][5] != ''):
        # Curso já selecionado e local definido
        c.execute(f"SELECT * FROM COMPARATIVO WHERE CURSO_ID={userdat[0][2]}")
        comparativo = c.fetchall()
        comparativo = ajustaComparativo(comparativo, (userdat[0][4], userdat[0][5]))
    else:
        comparativo = None

    return render_template('busca.html', user_id = user_id, is_admin = database.is_admin(user_id), comparativo=comparativo, userdat=userdat, cursos=cursos)


@app.route('/admin/<blk>/<user_id>', methods=['GET', 'POST'])
def admin(blk, user_id):
    #TODO: checar se o usuário está logado e é administrador!
    conn = sqlite3.connect('minhafacul.db')
    c = conn.cursor()

    c.execute("SELECT CURSO_ID, CURSO FROM CURSO ORDER BY CURSO")
    cursos = c.fetchall()

    c.execute("SELECT FACULDADE_ID, FACULADE, LOCAL_TXT, LOCAL_LAT, LOCAL_LON FROM FACULDADE ORDER BY FACULADE")
    faculdades = c.fetchall()

    c.execute("SELECT HISTORICO_ID, FACULADE, CURSO, ANO, CANDIDATOS, VAGAS FROM HISTORICO_DET ORDER BY ANO, FACULADE, CURSO")
    historico = c.fetchall()

    c.execute("SELECT USUARIO_ID, EMAIL, ADMINISTRADOR FROM USUARIO ORDER BY EMAIL")
    usuarios = c.fetchall()

    return render_template('admin.html', cursos=cursos, faculdades=faculdades, usuarios=usuarios, historico=historico, blk=blk, user_id=user_id)

@app.route('/curso/I/<user_id>', methods=['GET', 'POST'])
def curso_add(user_id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("INSERT INTO CURSO (CURSO) VALUES (?)", (request.form['curson'], ))
    conn.commit()
    return redirect(url_for('admin', blk=1, user_id = user_id))

@app.route('/curso/D/<user_id>/<id>', methods=['GET', 'POST'])
def curso_del(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM CURSO WHERE CURSO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=1, user_id = user_id))


@app.route('/curso/U/<user_id>/<id>', methods=['GET', 'POST'])
def curso_upd(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE CURSO SET CURSO=? WHERE CURSO_ID=?", (request.form['curson'], id))
    conn.commit()
    return redirect(url_for('admin', blk=1, user_id = user_id))


@app.route('/faculdade/I/<user_id>', methods=['GET', 'POST'])
def faculdade_add(user_id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("INSERT INTO FACULDADE (FACULADE, LOCAL_TXT, LOCAL_LAT, LOCAL_LON) VALUES(?, ?, ?, ?)",
                 (request.form['faculaden'], request.form['local_txt'], request.form['local_lat'], request.form['local_lon']))
    conn.commit()
    return redirect(url_for('admin', blk=2, user_id = user_id))


@app.route('/faculdade/D/<user_id>/<id>', methods=['GET', 'POST'])
def faculdade_del(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM FACULDADE WHERE FACULDADE_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=2, user_id = user_id))

@app.route('/faculdade/U/<user_id>/<id>', methods=['GET', 'POST'])
def faculdade_upd(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE FACULDADE SET FACULADE=?, LOCAL_TXT=?, LOCAL_LAT=?, LOCAL_LON=? WHERE FACULDADE_ID=?",
                 (request.form['faculaden'], request.form['local_txt'], request.form['local_lat'], request.form['local_lon'], id))
    conn.commit()
    return redirect(url_for('admin', blk=2, user_id = user_id))

@app.route('/historico/D/<user_id>/<id>', methods=['GET', 'POST'])
def historico_del(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM HISTORICO WHERE HISTORICO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=3, user_id = user_id))


@app.route('/historico/U/<user_id>/<id>', methods=['GET', 'POST'])
def historico_upd(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE HISTORICO SET ANO=?, CANDIDATOS=?, VAGAS=? WHERE HISTORICO_ID=?",
                 (request.form['ano'], request.form['candidatos'], request.form['vagas'], id))
    conn.commit()
    return redirect(url_for('admin', blk=3, user_id = user_id))


@app.route('/usuario/D/<user_id>/<id>', methods=['GET', 'POST'])
def usuario_del(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM USUARIO WHERE USUARIO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=4, user_id = user_id))


@app.route('/usuario/U/<user_id>/<id>', methods=['GET', 'POST'])
def usuario_upd(user_id, id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE USUARIO SET ADMINISTRADOR=1-ADMINISTRADOR WHERE USUARIO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=4, user_id = user_id))

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile(user_id):

    if (request.method == 'POST' and 'email' in request.form and 'email_c' in request.form):
        database.alter_email(user_id, request.form['email'])

    if (request.method == 'POST' and 'password' in request.form and 'password_c' in request.form):
        database.alter_password(user_id, request.form['password'])

    if (request.method == 'POST' and 'course' in request.form):
        database.alter_course(user_id, request.form['course'])

    if (request.method == 'POST' and 'local_txt' in request.form):

        local_txt = request.form['local_txt']

        database.alter_local(user_id, local_txt)

    email = database.get_user_email(user_id)
    local = database.get_user_local(user_id)

    return render_template(
        'profile.html', 
        user_id = user_id, 
        email = email, 
        local = local, 
        lat = database.get_user_latitude(user_id), 
        lng = database.get_user_longitude(user_id), 
        course = database.get_user_course(user_id),
        courses = database.get_courses(),
        is_admin = database.is_admin(user_id)
        )

if __name__ == '__main__':
    app.run(debug=True)