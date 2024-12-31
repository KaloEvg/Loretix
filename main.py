import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = 'base_datos.db'
UPLOAD_FOLDER = 'Static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'ico'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_next_image_name(tipo):
    folder_name = "Peliculas" if tipo.lower() == "pelicula" else "Series"
    folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(folder, exist_ok=True)  

    existing_files = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]
    max_number = 0
    for file in existing_files:
        name, ext = file.rsplit('.', 1)
        if '_' in name:
            try:
                number = int(name.split('_')[-1])
                max_number = max(max_number, number)
            except ValueError:
                pass

    return f"{folder_name.lower()}_{max_number + 1}.jpg"

@app.route('/')
def inicio():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT * FROM destacadas WHERE tipo = 'pelicula' ORDER BY posicion")
        peliculas_destacadas = c.fetchall()

        c.execute("SELECT * FROM destacadas WHERE tipo = 'serie' ORDER BY posicion")
        series_destacadas = c.fetchall()

    return render_template('index.html', peliculas_destacadas=peliculas_destacadas, series_destacadas=series_destacadas)



@app.route('/peliculas')
def mostrar_peliculas():
    generos = ["Acción", "Comedia", "Drama", "Fantasía", "Terror", "Romance", "Aventura", "Thriller"]
    peliculas_por_genero = {}
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for genero in generos:
            c.execute('SELECT * FROM contenido WHERE tipo = ? AND genero = ?', ('pelicula', genero))
            peliculas_por_genero[genero] = c.fetchall()
    return render_template('peliculas.html', generos=generos, peliculas_por_genero=peliculas_por_genero)

@app.route('/series')
def mostrar_series():
    generos = ["Acción", "Comedia", "Drama", "Fantasía", "Terror", "Romance", "Aventura", "Thriller"]
    series_por_genero = {}
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for genero in generos:
            c.execute('SELECT * FROM contenido WHERE tipo = ? AND genero = ?', ('serie', genero))
            series_por_genero[genero] = c.fetchall()
    return render_template('series.html', generos=generos, series_por_genero=series_por_genero)

@app.route('/add_contenido', methods=['GET', 'POST'])
def add_contenido():
    if 'admin' in session and session['admin']:
        if request.method == 'POST':
            tipo = request.form['tipo']
            genero = request.form['genero']
            titulo = request.form['titulo']
            anio = request.form['anio']
            imagen = request.files['imagen']

            if imagen and allowed_file(imagen.filename):
                new_image_name = get_next_image_name(tipo)
                folder_name = "Peliculas" if tipo.lower() == "pelicula" else "Series"
                folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                image_path = os.path.join(folder, new_image_name)

                imagen.save(image_path)

                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    ruta_imagen = f"{folder_name}/{new_image_name}"
                    cursor.execute('''INSERT INTO contenido (tipo, genero, titulo, anio, imagen)
                                      VALUES (?, ?, ?, ?, ?)''', (tipo, genero, titulo, anio, ruta_imagen))
                    conn.commit()
                    flash('Contenido añadido correctamente', 'success')
                return redirect(url_for('add_contenido'))
            else:
                flash('Formato de imagen no permitido.', 'error')

        generos = ["Acción", "Comedia", "Drama", "Fantasía", "Terror", "Romance", "Aventura", "Thriller"]
        return render_template('add_contenido.html', generos=generos)
    flash('Acceso no autorizado.', 'danger')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_usuario = error_password = ""
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM usuarios WHERE usuario = ?', (usuario,))
            user = c.fetchone()

            if not user:
                error_usuario = "Usuario no encontrado."
            elif not check_password_hash(user[2], password):
                error_password = "Contraseña incorrecta."
            else:
                session['usuario'] = usuario
                session['admin'] = bool(user[5])
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('inicio') if session['admin'] else url_for('inicio'))
    return render_template('login.html', error_usuario=error_usuario, error_password=error_password)

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('admin'):
        return render_template('admin_dashboard.html', usuario=session['usuario'])
    flash('Acceso no autorizado.', 'danger')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('admin', None)
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))

@app.route('/add_to_list/<int:contenido_id>', methods=['POST'])
def add_to_list(contenido_id):
    if 'usuario' not in session:
        flash("Debes iniciar sesión para añadir a tu lista.", "danger")
        return redirect(url_for('login'))

    usuario = session['usuario']
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        c.execute("SELECT mi_lista FROM usuarios WHERE usuario = ?", (usuario,))
        result = c.fetchone()
        mi_lista = result[0] if result and result[0] else ""

        ids = mi_lista.split(',') if mi_lista else []
        if str(contenido_id) not in ids:
            ids.append(str(contenido_id))
            c.execute("UPDATE usuarios SET mi_lista = ? WHERE usuario = ?", (','.join(ids), usuario))
            conn.commit()
            flash("Añadido a tu lista correctamente.", "success")
        else:
            flash("Este contenido ya está en tu lista.", "info")

    return redirect(request.referrer)


@app.route('/mi_lista', methods=['GET', 'POST'])
def mi_lista():
    if 'usuario' not in session:
        flash("Debes iniciar sesión para ver tu lista.", "danger")
        return redirect(url_for('login'))

    usuario = session['usuario']
    contenido_lista = []

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT mi_lista FROM usuarios WHERE usuario = ?", (usuario,))
        result = c.fetchone()
        mi_lista = result['mi_lista'] if result and result['mi_lista'] else ""

        if mi_lista:
            ids = mi_lista.split(',')
            query = f"SELECT * FROM contenido WHERE id IN ({','.join(['?'] * len(ids))})"
            c.execute(query, ids)
            contenido_lista = c.fetchall()

        if request.method == 'POST':
            borrar_id = request.form['borrar_id']
            ids.remove(borrar_id)
            c.execute("UPDATE usuarios SET mi_lista = ? WHERE usuario = ?", (','.join(ids), usuario))
            conn.commit()
            flash("Contenido eliminado de tu lista.", "success")
            return redirect(url_for('mi_lista'))

    return render_template('mi_lista.html', contenido_lista=contenido_lista)

@app.route('/contenido/<int:contenido_id>')
def detalle_contenido(contenido_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE contenido SET clicks = clicks + 1 WHERE id = ?", (contenido_id,))
        conn.commit()
        c.execute("SELECT * FROM contenido WHERE id = ?", (contenido_id,))
        contenido = c.fetchone()
    return render_template('detalle.html', contenido=contenido)

@app.route('/modificar_contenido', methods=['GET', 'POST'])
def modificar_contenido():
    if not session.get('admin'): 
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        contenido_id = request.form['id']
        titulo = request.form['titulo']
        genero = request.form['genero']
        tipo = request.form['tipo']
        anio = request.form['anio']

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE contenido 
                SET titulo = ?, genero = ?, tipo = ?, anio = ?
                WHERE id = ?
            ''', (titulo, genero, tipo, anio, contenido_id))
            conn.commit()
            flash('Contenido modificado correctamente.', 'success')
        return redirect(url_for('modificar_contenido'))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contenido')
        contenido = cursor.fetchall()

    return render_template('modificar_contenido.html', contenido=contenido)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    error_usuario = error_password = ""
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        confirmar_password = request.form['confirm_password']
        email = request.form['email']
        fecha_nacimiento = request.form['fecha_nacimiento']

        if password != confirmar_password:
            error_password = "Las contraseñas no coinciden."
        else:
            hashed_password = generate_password_hash(password)
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                try:
                    c.execute('''INSERT INTO usuarios (usuario, password, email, fecha_nacimiento, admin)
                                 VALUES (?, ?, ?, ?, ?)''', 
                                 (usuario, hashed_password, email, fecha_nacimiento, False))
                    conn.commit()
                    flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError:
                    error_usuario = "El usuario ya existe."

    return render_template('registro.html', error_usuario=error_usuario, error_password=error_password)

@app.route('/borrar_contenido', methods=['GET', 'POST'])
def borrar_contenido():
    if not session.get('admin'):
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        contenido_id = request.form['id']
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM contenido WHERE id = ?', (contenido_id,))
            conn.commit()
            flash('Contenido eliminado correctamente.', 'success')
        return redirect(url_for('borrar_contenido'))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contenido')
        contenido = cursor.fetchall()

    return render_template('borrar_contenido.html', contenido=contenido)

@app.route('/add_destacadas', methods=['GET', 'POST'])
def add_destacadas():
    if not session.get('admin'):
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('login'))

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT id, titulo, tipo, genero, anio, imagen FROM contenido")
        contenido = c.fetchall()

        c.execute("SELECT * FROM destacadas")
        destacadas = c.fetchall()

        if request.method == 'POST':
            contenido_id = request.form['contenido_id']
            posicion = int(request.form['posicion'])

            c.execute("SELECT tipo, genero, titulo, anio, imagen FROM contenido WHERE id = ?", (contenido_id,))
            item = c.fetchone()

            if not item:
                flash('El contenido no existe.', 'danger')
                return redirect(url_for('add_destacadas'))

            tipo = item['tipo']

            try:
                c.execute("DELETE FROM destacadas WHERE posicion = ? AND tipo = ?", (posicion, tipo))
                conn.commit() 

                c.execute('''
                    INSERT INTO destacadas (posicion, tipo, genero, titulo, anio, imagen)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (posicion, tipo, item['genero'], item['titulo'], item['anio'], item['imagen']))
                conn.commit()

                flash(f'{tipo.capitalize()} "{item["titulo"]}" añadida a la posición {posicion} en destacados.', 'success')
            except sqlite3.IntegrityError as e:
                conn.rollback() 
                flash(f'Error: No se pudo añadir el contenido. {str(e)}', 'danger')

            return redirect(url_for('add_destacadas'))

    return render_template('add_destacadas.html', contenido=contenido, destacadas=destacadas)



def obtener_contenido_por_ids(ids, conn):
    if ids:
        query = f"SELECT * FROM contenido WHERE id IN ({','.join(['?'] * len(ids))})"
        c = conn.cursor()
        c.execute(query, ids)
        return c.fetchall()
    return []


if __name__ == '__main__':
    app.run(debug=True)
