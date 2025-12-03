from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Base de datos SQLite
DB_PATH = "inventario_restaurantes.db"

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT NOT NULL,
            telefono TEXT NOT NULL,
            hora_apertura TEXT NOT NULL,
            hora_cierre TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Crear tabla al iniciar
crear_tabla()

def formato_hora_12h(hora):
    """Convierte formato 24h (HH:MM) a formato 12h (HH:MM AM/PM)"""
    try:
        dt = datetime.strptime(hora, "%H:%M")
        return dt.strftime("%I:%M %p")
    except:
        return hora

# 🔹 Obtener restaurantes con hora formateada en AM/PM
def obtener_restaurantes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, direccion, telefono, hora_apertura, hora_cierre
        FROM restaurantes
        ORDER BY fecha_creacion DESC
    """)
    datos = cursor.fetchall()
    conn.close()
    
    # Convertir formato de horas
    resultado = []
    for row in datos:
        resultado.append((
            row[0],  # nombre
            row[1],  # direccion
            row[2],  # telefono
            formato_hora_12h(row[3]),  # hora_apertura formateada
            formato_hora_12h(row[4])   # hora_cierre formateada
        ))
    return resultado

def registrar_restaurante(nombre, direccion, telefono, hora_apertura, hora_cierre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO restaurantes (nombre, direccion, telefono, hora_apertura, hora_cierre)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, direccion, telefono, hora_apertura, hora_cierre))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    restaurantes = obtener_restaurantes()
    return render_template("index.html", restaurantes=restaurantes)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        if usuario == "admin" and contrasena == "12345":
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Credenciales incorrectas"

    return render_template("login.html")

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")
    return render_template("admin.html")

@app.route("/registrar", methods=["POST"])
def registrar():
    if "admin" not in session:
        return redirect("/login")

    nombre = request.form["nombre"]
    direccion = request.form["direccion"]
    telefono = request.form["telefono"]
    hora_apertura = request.form["hora_apertura"]
    hora_cierre = request.form["hora_cierre"]

    registrar_restaurante(nombre, direccion, telefono, hora_apertura, hora_cierre)

    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
