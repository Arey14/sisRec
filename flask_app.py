from flask import Flask, jsonify, g, request
import sqlite3

app = Flask(__name__)
DATABASE = '/home/arey/sisRec/data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return db

def query_db(query, args=(), one=False):
    try:
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {e}")
        return []

@app.route('/')
def hello_world():
    return 'Hello from Flaskito!'

@app.route('/api/version/', methods=["GET"])
def api():
    return jsonify({"version" : 2})

from flask import abort

@app.route('/api/recomendar/usuario_id', methods=['GET'])
def usuarioRecomendar():
    # Obtener usuario_id de los parámetros de la consulta
    usuario_id = request.args.get('usuario_id')

    if not usuario_id:
        return jsonify({'error': 'usuario_id es requerido'}), 400

    # Consultar la base de datos para obtener los datos del usuario
    result = query_db('SELECT * FROM lectores WHERE id_lector = ?', [usuario_id], one=True)

    if result:
        # Obtener los libros más populares, excluyendo aquellos ya leídos por el usuario
        bestseller = query_db('''
            SELECT x.id_libro, COUNT(x.id_libro) as cuenta
            FROM interacciones x
            WHERE x.id_libro NOT IN (
                SELECT i.id_libro
                FROM interacciones i
                WHERE i.id_lector = ?
            )
            GROUP BY x.id_libro
            ORDER BY cuenta DESC
            LIMIT 5
        ''', [usuario_id])

        # Si no hay libros recomendados, devolver una lista vacía
        if bestseller:
            # Crear una lista solo con los IDs de los libros recomendados
            recomendacion = [book['id_libro'] for book in bestseller]
            return jsonify({'recomendacion': recomendacion}),200

        else:
            return jsonify({'recomendacion': []}),200  # Si no hay libros recomendados, devolver una lista vacía

    else:
        # Usamos abort() de Flask para lanzar un error 404 con un mensaje personalizado
        abort(404, "El usuario no existe")

"""@app.route('/api/libros')
def libros():
    try:
        libros = query_db('SELECT * FROM libros')
        # Convert the tuple list to a list of dictionaries
        libros_dict = [dict(row) for row in libros]
        return jsonify({'libros': libros_dict})
    except Exception as e:
        app.logger.error(f"Error fetching libros: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
"""
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

