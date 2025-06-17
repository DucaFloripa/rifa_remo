from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Obtém a URL do banco via variável de ambiente 'DATABASE_URL'
# Se não estiver definida, usa SQLite local como fallback (útil para testes locais)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    nome = db.Column(db.String(80))
    contato = db.Column(db.String(120))
    status = db.Column(db.String(20), default='reservado')

@app.before_first_request
def criar_tabelas():
    db.create_all()

@app.route('/')
def index():
    reservas = Reserva.query.order_by(Reserva.numero).all()
    return render_template('index.html', reservas=reservas)

@app.route('/reservar', methods=['POST'])
def reservar():
    numero = int(request.form['numero'])
    nome = request.form['nome']
    contato = request.form['contato']

    # Verifica se o número já foi reservado
    if Reserva.query.filter_by(numero=numero).first():
        return "Número já reservado. Volte e escolha outro número."

    reserva = Reserva(numero=numero, nome=nome, contato=contato)
    db.session.add(reserva)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    reservas = Reserva.query.order_by(Reserva.numero).all()
    return render_template('admin.html', reservas=reservas)

@app.route('/confirmar/<int:id>')
def confirmar(id):
    reserva = Reserva.query.get(id)
    if reserva:
        reserva.status = 'pago'
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Roda a aplicação na porta 5000 acessível externamente
    app.run(host='0.0.0.0', port=5000)

