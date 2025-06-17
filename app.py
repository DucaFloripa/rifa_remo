from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uma_chave_qualquer_para_flash')  # para mensagens flash

# Usa DATABASE_URL da variável de ambiente ou fallback para SQLite local
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    nome = db.Column(db.String(80), nullable=False)
    contato = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='reservado', nullable=False)

@app.before_first_request
def criar_tabelas():
    """Cria as tabelas no banco de dados antes da primeira requisição."""
    db.create_all()

@app.route('/')
def index():
    reservas = Reserva.query.order_by(Reserva.numero).all()
    return render_template('index.html', reservas=reservas)

@app.route('/reservar', methods=['POST'])
def reservar():
    try:
        numero = int(request.form['numero'])
        nome = request.form['nome'].strip()
        contato = request.form['contato'].strip()

        if not nome or not contato:
            flash("Nome e contato são obrigatórios.", "error")
            return redirect(url_for('index'))

        # Verifica se o número já foi reservado
        if Reserva.query.filter_by(numero=numero).first():
            flash("Número já reservado. Escolha outro.", "error")
            return redirect(url_for('index'))

        nova_reserva = Reserva(numero=numero, nome=nome, contato=contato)
        db.session.add(nova_reserva)
        db.session.commit()
        flash("Reserva feita com sucesso!", "success")
    except ValueError:
        flash("Número inválido.", "error")
    except Exception as e:
        flash(f"Erro ao reservar: {e}", "error")

    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    reservas = Reserva.query.order_by(Reserva.numero).all()
    return render_template('admin.html', reservas=reservas)

@app.route('/confirmar/<int:id>')
def confirmar(id):
    reserva = Reserva.query.get_or_404(id)
    reserva.status = 'pago'
    db.session.commit()
    flash(f"Reserva {reserva.numero} confirmada como paga.", "success")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

