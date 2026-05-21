"""
Configuracao do banco de dados SQLite
Sistema de Controle de Gastos Pessoais
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(200), default='https://ui-avatars.com/api/?name=User&background=1e293b&color=fff')
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id, 'public_id': self.public_id, 'name': self.name,
            'email': self.email, 'avatar': self.avatar, 'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'transactions_count': len(self.transactions)
        }

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(7), default='#64748b')
    icon = db.Column(db.String(30), default='tag')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'type': self.type, 'color': self.color, 'icon': self.icon}

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(30), default='dinheiro')
    is_recurring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'amount': self.amount, 'type': self.type,
            'date': self.date.strftime('%Y-%m-%d'), 'description': self.description,
            'payment_method': self.payment_method, 'is_recurring': self.is_recurring,
            'category': self.category.to_dict() if self.category else None,
            'user_id': self.user_id, 'created_at': self.created_at.strftime('%d/%m/%Y %H:%M')
        }

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

def create_default_categories():
    default_categories = [
        {'name': 'Alimentacao', 'type': 'expense', 'color': '#ef4444', 'icon': 'utensils'},
        {'name': 'Transporte', 'type': 'expense', 'color': '#f97316', 'icon': 'car'},
        {'name': 'Moradia', 'type': 'expense', 'color': '#eab308', 'icon': 'home'},
        {'name': 'Saude', 'type': 'expense', 'color': '#22c55e', 'icon': 'heart-pulse'},
        {'name': 'Educacao', 'type': 'expense', 'color': '#3b82f6', 'icon': 'graduation-cap'},
        {'name': 'Lazer', 'type': 'expense', 'color': '#a855f7', 'icon': 'gamepad-2'},
        {'name': 'Vestuario', 'type': 'expense', 'color': '#ec4899', 'icon': 'shirt'},
        {'name': 'Servicos', 'type': 'expense', 'color': '#14b8a6', 'icon': 'wrench'},
        {'name': 'Outros', 'type': 'expense', 'color': '#64748b', 'icon': 'more-horizontal'},
        {'name': 'Salario', 'type': 'income', 'color': '#22c55e', 'icon': 'briefcase'},
        {'name': 'Freelance', 'type': 'income', 'color': '#3b82f6', 'icon': 'laptop'},
        {'name': 'Investimentos', 'type': 'income', 'color': '#a855f7', 'icon': 'trending-up'},
        {'name': 'Presente', 'type': 'income', 'color': '#f97316', 'icon': 'gift'},
        {'name': 'Outros', 'type': 'income', 'color': '#64748b', 'icon': 'more-horizontal'},
    ]
    for cat_data in default_categories:
        if not Category.query.filter_by(name=cat_data['name'], type=cat_data['type'], user_id=None).first():
            db.session.add(Category(**cat_data))
    db.session.commit()

def init_db(app):
    with app.app_context():
        db.create_all()
        create_default_categories()
        print("Banco de dados inicializado com sucesso!")
