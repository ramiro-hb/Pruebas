from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import threading
import serial
import random

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['THREADS_PER_PAGE'] = 2

db_path = os.path.join(os.path.dirname(__file__), 'base_de_datos.db')

db_local = threading.local()

#ser = serial.Serial('/dev/tty.usbmodem101', 115200)

def get_db():
    db = getattr(db_local, 'conn', None)
    if db is None:
        db = db_local.conn = sqlite3.connect(db_path)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(db_local, 'conn', None)
    if db is not None:
        db.close()

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

        return redirect(url_for('dashboard'))
    else:
        error = 'Usuario o contraseña incorrectos'
        return render_template('inicio.html', error=error)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        with app.app_context():
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)
            ''', (usuario, contrasena))
            conn.commit()

        return redirect(url_for('inicio'))
    else:
        return render_template('crear_cuenta.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', error=None)

@app.route('/historial')
def historial():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM voltaje
            ''')
        datos = cursor.fetchall()
        #print(datos)
        return jsonify(datos)
    
@app.route('/historial-dashboard')
def historial_dashboard():
    return render_template('historial_dashboard.html')



def simulate_arduino_data():
    # Simular datos como voltaje y corriente
    simulated_voltage = random.uniform(0, 2)  # Ejemplo: un valor aleatorio entre 0 y 2
    simulated_current = random.uniform(0, 10)   # Ejemplo: un valor aleatorio entre 0 y 10
    return "Simulated", simulated_voltage, simulated_current
# Variable para almacenar el último valor simulado
last_simulated_value = None

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
