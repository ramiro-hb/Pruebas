from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import os
import threading
import serial
import random
from wtforms import StringField, PasswordField, validators

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['THREADS_PER_PAGE'] = 2
app.secret_key = 'your secret key'  # Asegúrate de establecer una clave secreta

db_path = os.path.join(os.path.dirname(__file__), 'base_de_datos.db')

db_local = threading.local()

#ser = serial.Serial('/dev/tty.usbmodem101', 115200)

def get_db():
    if not hasattr(db_local, 'conn'):
        db_local.conn = sqlite3.connect(db_path, check_same_thread=False)
    return db_local.conn


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(db_local, 'conn', None)
    if db is not None:
        db.commit()
        
with app.app_context():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            contrasena TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voltaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            valor REAL NOT NULL
        )
    ''')

    conn.commit()

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']

    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?
        ''', (usuario, contrasena))
        resultado = cursor.fetchone()

    if resultado:
        if 'error' in request.args:
            request.args.pop('error')

        session['username'] = usuario  # Almacenar el nombre de usuario en la sesión
        return redirect(url_for('dashboard'))
    else:
        error = 'Usuario o contraseña incorrectos'
        return render_template('inicio.html', error=error)


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('inicio'))

from flask_wtf import FlaskForm as Form

class RegistrationForm(Form):
   usuario = StringField('Usuario', [validators.Length(min=4, max=10)])
   contrasena = PasswordField('Contraseña', [validators.Length(min=5, max=10), validators.DataRequired()])

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        usuario = form.usuario.data
        contrasena = form.contrasena.data

        with app.app_context():
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)
            ''', (usuario, contrasena))
            conn.commit()

        return redirect(url_for('inicio'))
    else:
        return render_template('crear_cuenta.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('inicio'))  # Redirigir al inicio si el usuario no está en sesión
    return render_template('dashboard.html', error=None)


@app.route('/sensor2')
def sensor2():
    # Aquí va el código para generar y mostrar información para el sensor 2
    pass

@app.route('/historial')
def historial():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM voltaje
            ''')
        datos = cursor.fetchall()
        return jsonify(datos)

@app.route('/historial-dashboard')
def historial_dashboard():
    return render_template('historial_dashboard.html')

def simulate_arduino_data():
    # Simular datos como voltaje y corriente
    simulated_voltage = random.uniform(0, 2)  # Ejemplo: un valor aleatorio entre 0 y 2
    simulated_current = random.uniform(0, 10)   # Ejemplo: un valor aleatorio entre 0 y 10
    return "Simulated", simulated_voltage, simulated_current

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    simulate_arduino = True  # Cambiar a False para usar datos reales del Arduino

    if simulate_arduino:
        sensor_data, voltage, current = simulate_arduino_data()
    else:
        arduino_data = ser.readline().decode().strip()
        sensor_data, voltage, current = arduino_data.split(',')

    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO voltaje (valor) VALUES (?)
        ''', (voltage,))
    conn.commit()
    
    return jsonify(sensor_data=sensor_data, voltage=voltage, current=current)

if __name__ == '__main__':
    app.run(debug=True)