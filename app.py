# app.py
from flask import Flask, render_template, request, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)

# Retornar a sing up..........
@app.route('/')
def home():  
    return render_template('index.html')

@app.route('/index')
def index():  
    return render_template('index.html')

# Retornar a inicio..........
@app.route('/inicio', methods=['GET', 'POST'])
def location_inicio():
    return render_template('inicio.html')

# Retornar a terminos..........
@app.route('/terminos', methods=['GET', 'POST'])
def location_terminos():
    return render_template('terminos.html')

# Retornar a perfil..........
@app.route('/perfil', methods=['GET', 'POST'])
def location_perfil():
    return render_template('perfil.html')

# Conexión a Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

if __name__ == '__main__':
    app.run(debug=True)