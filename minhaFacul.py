from flask import Flask, render_template, request, redirect, url_for

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
    #todo: checar se usuário esta logado
    conn = sqlite3.connect('minhafacul.db')
    c = conn.cursor()

    if request.method == 'POST':
        # Atualiza os dados de local e curso selecionado
        conn.execute("UPDATE USUARIO SET CURSO_ID=?, LOCAL_TXT=?, LOCAL_LAT=?, LOCAL_LON=? WHERE USUARIO_ID=?;",
                     (request.form['curso_id'], request.form['local_txt'], request.form['local_lat'], request.form['local_lon'], userid))
        conn.commit()

    # Consulda dados do usário para construir a busca
    c.execute("SELECT USUARIO_ID, EMAIL, CURSO_ID, LOCAL_TXT, LOCAL_LAT, LOCAL_LON FROM USUARIO WHERE USUARIO_ID=?", (userid, ))
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


if __name__ == '__main__':
    app.run(debug=True)
