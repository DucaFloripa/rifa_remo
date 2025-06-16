from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "rifa.db"

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE rifa (
                numero INTEGER PRIMARY KEY,
                nome TEXT,
                contato TEXT,
                status TEXT
            )
        ''')
        for i in range(1, 101):
            c.execute("INSERT INTO rifa (numero, status) VALUES (?, ?)", (i, 'disponivel'))
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT numero FROM rifa WHERE status = 'disponivel'")
    numeros_disponiveis = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template("index.html", numeros=numeros_disponiveis)

@app.route('/comprar', methods=['POST'])
def comprar():
    numero = request.form['numero']
    nome = request.form['nome']
    contato = request.form['contato']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status FROM rifa WHERE numero = ?", (numero,))
    status = c.fetchone()

    if status and status[0] == 'disponivel':
        c.execute("UPDATE rifa SET nome = ?, contato = ?, status = 'reservado' WHERE numero = ?", (nome, contato, numero))
        conn.commit()

    conn.close()
    return redirect('/')

@app.route('/admin')
def admin():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM rifa WHERE status != 'disponivel'")
    vendidos = c.fetchall()
    conn.close()
    return render_template("admin.html", vendidos=vendidos)

@app.route('/confirmar/<int:numero>')
def confirmar(numero):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE rifa SET status = 'pago' WHERE numero = ?", (numero,))
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
