from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort
from flask import Flask
from database import Database
import logging
import os
import math
import sqlite3

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('site-log.log')
logger.addHandler(handler)

app = Flask(__name__)

app.secret_key = '1234'

app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

site = Blueprint('site', __name__, template_folder='templates')

database = Database()

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        
        # Create variables for easy access
        username = request.form['email']
        password = request.form['password']

        if database.user_exists(username, password):

            logger.info("Login valido")
            session['logged_in'] = True
            return redirect(url_for(f'home', user_id = database.get_user_id(username, password)))
            
        else:
            logger.info("Login invalido")
    
    return render_template('login.html')
 
@app.route("/home/<user_id>")
def home(user_id):
        return render_template('home.html', user_id = user_id)

@app.route("/register", methods=['GET','POST'])
def register():
    if (request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'street' in request.form and 'number' in request.form and 'nbh' in request.form and 'city' in request.form and 'state' in request.form):
        
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        street = request.form['street']
        number = request.form['number']
        nbh = request.form['nbh']
        city = request.form['city']
        state = request.form['state']

        local_txt = f"{street}, {number} - {nbh}, {city} - {state}"

        if database.insert_user(email, password, local_txt):
            return redirect(url_for('login'))
    
    return render_template('register.html')

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

    return render_template('busca.html', comparativo=comparativo, userdat=userdat, cursos=cursos)


@app.route('/admin/<blk>', methods=['GET', 'POST'])
def admin(blk):
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

    return render_template('admin.html', cursos=cursos, faculdades=faculdades, usuarios=usuarios, historico=historico, blk=blk)

@app.route('/curso/I', methods=['GET', 'POST'])
def curso_add():
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("INSERT INTO CURSO (CURSO) VALUES (?)", (request.form['curson'], ))
    conn.commit()
    return redirect(url_for('admin', blk=1))

@app.route('/curso/D/<id>', methods=['GET', 'POST'])
def curso_del(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM CURSO WHERE CURSO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=1))


@app.route('/curso/U/<id>', methods=['GET', 'POST'])
def curso_upd(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE CURSO SET CURSO=? WHERE CURSO_ID=?", (request.form['curson'], id))
    conn.commit()
    return redirect(url_for('admin', blk=1))


@app.route('/faculdade/I', methods=['GET', 'POST'])
def faculdade_add():
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("INSERT INTO FACULDADE (FACULADE, LOCAL_TXT, LOCAL_LAT, LOCAL_LON) VALUES(?, ?, ?, ?)",
                 (request.form['faculaden'], request.form['local_txt'], request.form['local_lat'], request.form['local_lon']))
    conn.commit()
    return redirect(url_for('admin', blk=2))


@app.route('/faculdade/D/<id>', methods=['GET', 'POST'])
def faculdade_del(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM FACULDADE WHERE FACULDADE_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=2))


@app.route('/faculdade/U/<id>', methods=['GET', 'POST'])
def faculdade_upd(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE FACULDADE SET FACULADE=?, LOCAL_TXT=?, LOCAL_LAT=?, LOCAL_LON=? WHERE FACULDADE_ID=?",
                 (request.form['faculaden'], request.form['local_txt'], request.form['local_lat'], request.form['local_lon'], id))
    conn.commit()
    return redirect(url_for('admin', blk=2))


@app.route('/historico/D/<id>', methods=['GET', 'POST'])
def historico_del(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM HISTORICO WHERE HISTORICO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=3))


@app.route('/historico/U/<id>', methods=['GET', 'POST'])
def historico_upd(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE HISTORICO SET ANO=?, CANDIDATOS=?, VAGAS=? WHERE HISTORICO_ID=?",
                 (request.form['ano'], request.form['candidatos'], request.form['vagas'], id))
    conn.commit()
    return redirect(url_for('admin', blk=3))


@app.route('/usuario/D/<id>', methods=['GET', 'POST'])
def usuario_del(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("DELETE FROM USUARIO WHERE USUARIO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=4))


@app.route('/usuario/U/<id>', methods=['GET', 'POST'])
def usuario_upd(id):
    conn = sqlite3.connect('minhafacul.db')
    conn.execute("UPDATE USUARIO SET ADMINISTRADOR=1-ADMINISTRADOR WHERE USUARIO_ID=?", (id, ))
    conn.commit()
    return redirect(url_for('admin', blk=4))

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile(user_id):

    if (request.method == 'POST' and 'password' in request.form and 'password_c' in request.form):
        
        password = request.form['password']
        database.alter_password(user_id, password)

    email = database.get_user_email(user_id)
    local = database.get_user_local(user_id)

    return render_template('profile.html', email = email, local = local)


if __name__ == '__main__':
    app.run(debug=True)