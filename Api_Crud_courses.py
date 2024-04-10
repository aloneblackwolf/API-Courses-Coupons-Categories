from flask import Flask, jsonify, request
import psycopg2
from flask import abort

app = Flask(__name__)

conexion = psycopg2.connect(
    user='postgres',
    password='1234',
    host='localhost',
    port='5432',
    database='E-Commerce'
)

@app.route('/select_all')
def index():
    # Utiliza la conexión a la base de datos
    cur = conexion.cursor()
    ## Consulta SQL, para traer todos los cursos de la bd pero sin un orden especifico
    cur.execute("SELECT * FROM courses ORDER BY RANDOM()")
    ## Recorre todas las filas de la bd de la tabla para obtener los datos
    rows = cur.fetchall()
    ## Cerramos el cursor
    cur.close()
    ## Cerramos la conexion
    conexion.close()
    # Devuelve alguna respuesta al navegador
    return jsonify({'data': rows})

@app.route('/select_busqueda/<frase>', methods=['GET'])
def select_frase(frase):
    # Utiliza la conexión a la base de datos
    cur = conexion.cursor()
    
    # Agrega comodines '%' alrededor de la frase de búsqueda para que coincida con cualquier parte del valor
    frase_like = f"%{frase}%"
    
    # Consulta SQL para seleccionar cursos donde el título contenga la frase de búsqueda (insensible a mayúsculas/minúsculas)
    consulta = "SELECT * FROM courses WHERE LOWER(title) LIKE LOWER(%s)"
    
    # Ejecuta la consulta SQL con la frase de búsqueda como parámetro
    cur.execute(consulta, (frase_like,))
    
    # Obtiene los resultados de la consulta
    rows = cur.fetchall()
    
    # Cierra el cursor
    cur.close()
    ## Cerramos la conexion
    conexion.close()
    
    # Valida si hay resultados
    if not rows:
        # Si no hay resultados, devuelve un mensaje y código 404
        return jsonify({'message': 'No se encontraron resultados asociados. '}), 404
    else:
        # Si hay resultados, devuelve los datos como respuesta JSON
        return jsonify({'data': rows}), 200

@app.route('/select_curso/<id_curso>', methods=['GET'])
def select_curso(id_curso):
    # Utiliza la conexión a la base de datos
    cur = conexion.cursor()

    # Consulta SQL para seleccionar el curso con el ID especificado
    consulta = "SELECT * FROM courses WHERE course_id = %s"

    # Ejecuta la consulta SQL con el ID del curso como parámetro
    cur.execute(consulta, (id_curso,))

    # Obtiene el resultado de la consulta
    row = cur.fetchone()

    # Cierra el cursor
    cur.close()
    ## Cerramos la conexion
    conexion.close()

    # Valida si se encontró el curso
    if not row:
        # Si no se encontró el curso, devuelve un mensaje y código 404
        return jsonify({'message': 'No se encontró el curso con el ID indicado. '}), 404
    else:
        # Si se encontró el curso, devuelve los datos como respuesta JSON
        return jsonify({'data': row}), 200


@app.route('/delete_curso/<id_curso>', methods=['DELETE'])
def delete_curso(id_curso):
    # Utiliza la conexión a la base de datos
    cur = conexion.cursor()

    # Consulta SQL para eliminar el curso con el ID especificado
    consulta = "DELETE FROM courses WHERE course_id = %s"

    # Ejecuta la consulta SQL con el ID del curso como parámetro
    cur.execute(consulta, (id_curso,))

    # Obtiene el número de filas afectadas
    filas_afectadas = cur.rowcount

    # Se confirman los cambios
    conexion.commit()
    # Cierra el cursor
    cur.close()
    ## Cerramos la conexion
    conexion.close()

    # Valida si se eliminó el curso
    if filas_afectadas == 0:
        # Si no se eliminó el curso, devuelve un mensaje y código 404
        return jsonify({'message': 'No se encontró el curso con el ID indicado'}), 404
    else:
        # Si se eliminó el curso, devuelve un mensaje de éxito y código 200
        return jsonify({'message': 'Curso eliminado exitosamente.'}), 200


@app.route('/insertar', methods=['POST'])
def insertar_curso():
    # Obtener los datos del cuerpo de la solicitud
    datos_curso = request.json
    
    # Validar que los campos necesarios estén presentes en la solicitud
    campos_obligatorios = ['id_curso', 'titulo', 'descripcion', 'precio', 'img']
    if not all(campo in datos_curso for campo in campos_obligatorios):
        abort(400, 'Faltan campos obligatorios en la solicitud')
    
    # Obtener los datos de la solicitud
    id_curso = datos_curso['id_curso']
    titulo = datos_curso['titulo']
    descripcion = datos_curso['descripcion']
    precio = datos_curso['precio']
    img = datos_curso['img']
    
    # Validar que el precio sea un número positivo
    if not isinstance(precio, (int, float)) or precio <= 0:
        abort(400, 'El precio debe ser un número positivo')
    
    # Crear un cursor para ejecutar las consultas(insert)
    cursor = conexion.cursor()
    
    # Consulta SQL para insertar un nuevo curso en la tabla courses
    consulta = "INSERT INTO courses (course_id, title, description, price, img) VALUES (%s, %s, %s, %s, %s)"
    
    # Se ejecuta la consulta SQL, pasandole como parametro los datos de la solicitud
    cursor.execute(consulta, (id_curso, titulo, descripcion, precio, img))
    
    # Se confirman los cambios
    conexion.commit()
    
    # Cerrar el cursor y la conexion
    cursor.close()
    conexion.close()
    
    return jsonify({'Mensaje': 'Curso registrado correctamente'}), 201

@app.route('/modificar_curso', methods=['PUT'])
def modificar_curso():
    # Obtener los datos del cuerpo de la solicitud
    datos_curso = request.json

    # Validar que los campos necesarios estén presentes en la solicitud
    campos_obligatorios = ['id_curso', 'titulo', 'descripcion', 'precio', 'img']
    if not all(campo in datos_curso for campo in campos_obligatorios):
        abort(400, 'Faltan campos obligatorios en la solicitud')

    # Obtener los datos de la solicitud
    id_curso = datos_curso['id_curso']
    titulo = datos_curso['titulo']
    descripcion = datos_curso['descripcion']
    precio = datos_curso['precio']
    img = datos_curso['img']

    # Validar que el precio sea un número positivo
    if not isinstance(precio, (int, float)) or precio <= 0:
        abort(400, 'El precio debe ser un número positivo')

    # Crea un cursor para ejecutar las consultas (update)
    cursor = conexion.cursor()

    # Consulta SQL para modificar un curso en la tabla courses
    consulta = "UPDATE courses SET title = %s, description = %s, price = %s, img = %s WHERE course_id = %s"

    # Se ejecuta la consulta SQL, pasándole como parámetros los datos de la solicitud
    cursor.execute(consulta, (titulo, descripcion, precio, img, id_curso))

    # Se confirman los cambios
    conexion.commit()

    # Cierra el cursor y la conexión
    cursor.close()
    conexion.close()

    # Valida si se modificó el curso
    if cursor.rowcount == 0:
        # Si no se modificó el curso, devuelve un mensaje de error
        return jsonify({'message': 'No se encontró el curso con el ID {}'.format(id_curso)}), 404
    else:
        # Si se modificó el curso, devuelve un mensaje de éxito
        return jsonify({'message': 'Curso modificado exitosamente.'}), 200



# Ejecutar la aplicación en el puerto 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)
