## flask --app flask_app --debug run
from flask import Flask, jsonify, abort
import os
import sqlite3


app = Flask(__name__)


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def sql_select(query, params=None):
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data.db"))
    con.row_factory = sqlite3.Row # esto es para que devuelva registros en el fetchall
    cur = con.cursor()
    if params:
        res = cur.execute(query, params)
    else:
        res = cur.execute(query)

    ret = res.fetchall()
    con.close()


    return ret


###


@app.route("/api/version", methods=["GET"])
def version():
    return jsonify({"version": 2})


@app.route("/api/recomendar/<string:id_lector>", methods=["GET"])
def recomendar(id_lector):
    res = sql_select("SELECT count(*) AS cant FROM lectores WHERE id_lector = ?", [id_lector])


    if res[0]['cant'] == 0:
        abort(404, f"El lector '{id_lector}' no existe")


    ### MAGIA
    # q = """
    #     SELECT id_libro
    #       FROM libros
    #      WHERE id_libro NOT IN (SELECT id_libro FROM interacciones WHERE id_lector = ?)
    #      LIMIT 5;
    # """
    q = """
        SELECT id_libro
          FROM (SELECT id_libro, count(*) FROM interacciones WHERE rating >= 5 GROUP BY 1 ORDER BY 2 DESC)
         WHERE id_libro NOT IN (SELECT id_libro FROM interacciones WHERE id_lector = ?)
         LIMIT 5
    """
    ### MAGIA

    recomendacion = [r['id_libro'] for r in sql_select(q, [id_lector])]


    return jsonify({"recomendacion": recomendacion})

