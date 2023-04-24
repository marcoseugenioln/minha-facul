from flask import Flask, render_template, request
from markupsafe import escape
import sqlite3
import math

app = Flask(__name__)

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


@app.route('/')
def home():
    return 'Teste ok'


@app.route('/busca/<userid>', methods=['GET', 'POST'])
def busca(userid):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        # Atualiza os dados de local e curso selecionado
        #TODO
        conn.execute("UPDATE USUARIO SET CURSO_ID=?, LOCAL_TXT=?, LOCAL_LAT=?, LOCAL_LON=? WHERE USUARIO_ID=?;",
                     (request.form['curso_id'], request.form['local_txt'], request.form['local_lat'], request.form['local_lon'], userid))
        conn.commit()

    # Consulda dados do usário para construir a busca
    c.execute("SELECT USUARIO_ID, EMAIL, CURSO_ID, LOCAL_TXT, LOCAL_LAT, LOCAL_LON FROM USUARIO WHERE USUARIO_ID=?", (userid))
    userdat = c.fetchall()

    # Consulta a tabela de cursos e retorna uma lista de tuplas com os dados
    c.execute("SELECT CURSO_ID, CURSO FROM CURSO")
    cursos = c.fetchall()

    if (userdat[0][2]>0 and userdat[0][4] != '' and userdat[0][5] != ''):
        # Curso já selecionado e local definido
        c.execute("SELECT * FROM COMPARATIVO WHERE CURSO_ID=?", (userdat[0][2]))
        comparativo = c.fetchall()
        comparativo = ajustaComparativo(comparativo, (userdat[0][4], userdat[0][5]))
    else:
        comparativo = None

    return render_template('busca.html', comparativo=comparativo, userdat=userdat, cursos=cursos)


if __name__ == '__main__':
    app.run(debug=True)
