"""
Sistema de Controle de Gastos Pessoais
Servidor Flask - Aplicacao completa
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Category, Transaction, PasswordReset, init_db
from datetime import datetime, timedelta
from functools import wraps
import os, uuid, csv, io

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sistema-controle-gastos-2024-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///controle_gastos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faca login para acessar esta pagina.'
login_manager.login_message_category = 'warning'

os.makedirs('static/uploads', exist_ok=True)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Sua conta esta desativada.', 'error')
                return redirect(url_for('login'))
            login_user(user, remember=remember)
            flash(f'Bem-vindo, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('E-mail ou senha incorretos.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not name or not email or not password:
            flash('Todos os campos sao obrigatorios.', 'error')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('As senhas nao coincidem.', 'error')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Este e-mail ja esta cadastrado.', 'error')
            return redirect(url_for('register'))
        user = User(name=name, email=email)
        user.set_password(password)
        if User.query.count() == 0:
            user.role = 'admin'
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faca login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = str(uuid.uuid4())
            reset = PasswordReset(email=email, token=token, expires_at=datetime.utcnow() + timedelta(hours=24))
            db.session.add(reset)
            db.session.commit()
            flash(f'Link de recuperacao gerado: token={token}', 'info')
        else:
            flash('Se o e-mail existir, enviaremos instrucoes.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Voce saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    today = datetime.today()
    first_day = today.replace(day=1)
    income_month = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id, Transaction.type == 'income', Transaction.date >= first_day
    ).scalar() or 0
    expense_month = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id, Transaction.type == 'expense', Transaction.date >= first_day
    ).scalar() or 0
    balance = income_month - expense_month
    recent_transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).limit(5).all()
    months, income_data, expense_data = [], [], []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        months.append(month_date.strftime('%b/%Y'))
        inc = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id, Transaction.type == 'income',
            Transaction.date >= month_start, Transaction.date <= month_end
        ).scalar() or 0
        exp = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id, Transaction.type == 'expense',
            Transaction.date >= month_start, Transaction.date <= month_end
        ).scalar() or 0
        income_data.append(inc)
        expense_data.append(exp)
    category_expenses = db.session.query(
        Category.name, Category.color, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(Transaction.user_id == user_id, Transaction.type == 'expense').group_by(Category.id).all()
    category_labels = [c[0] for c in category_expenses]
    category_data = [float(c[2]) for c in category_expenses]
    category_colors = [c[1] for c in category_expenses]
    return render_template('dashboard.html',
        income_month=income_month, expense_month=expense_month, balance=balance,
        recent_transactions=recent_transactions, months=months, income_data=income_data,
        expense_data=expense_data, category_labels=category_labels,
        category_data=category_data, category_colors=category_colors)

@app.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def api_transactions():
    if request.method == 'POST':
        data = request.get_json() or request.form
        transaction = Transaction(
            title=data.get('title'), amount=float(data.get('amount', 0)), type=data.get('type'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d'), description=data.get('description'),
            payment_method=data.get('payment_method', 'dinheiro'), is_recurring=bool(data.get('is_recurring')),
            user_id=current_user.id, category_id=int(data.get('category_id')))
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'success': True, 'transaction': transaction.to_dict()}), 201
    query = Transaction.query.filter_by(user_id=current_user.id)
    if request.args.get('type'): query = query.filter_by(type=request.args.get('type'))
    if request.args.get('category'): query = query.filter_by(category_id=request.args.get('category'))
    if request.args.get('date_from'): query = query.filter(Transaction.date >= datetime.strptime(request.args.get('date_from'), '%Y-%m-%d'))
    if request.args.get('date_to'): query = query.filter(Transaction.date <= datetime.strptime(request.args.get('date_to'), '%Y-%m-%d'))
    if request.args.get('search'): query = query.filter(Transaction.title.ilike(f'%{request.args.get("search")}%'))
    sort_by, sort_order = request.args.get('sort_by', 'date'), request.args.get('sort_order', 'desc')
    query = query.order_by(getattr(Transaction, sort_by).desc() if sort_order == 'desc' else getattr(Transaction, sort_by).asc())
    return jsonify({'transactions': [t.to_dict() for t in query.all()]})

@app.route('/api/transactions/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_transaction_detail(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    if request.method == 'GET':
        return jsonify(transaction.to_dict())
    elif request.method == 'PUT':
        data = request.get_json() or request.form
        transaction.title = data.get('title', transaction.title)
        transaction.amount = float(data.get('amount', transaction.amount))
        transaction.type = data.get('type', transaction.type)
        transaction.date = datetime.strptime(data.get('date'), '%Y-%m-%d') if data.get('date') else transaction.date
        transaction.description = data.get('description', transaction.description)
        transaction.payment_method = data.get('payment_method', transaction.payment_method)
        transaction.is_recurring = bool(data.get('is_recurring', transaction.is_recurring))
        transaction.category_id = int(data.get('category_id', transaction.category_id))
        db.session.commit()
        return jsonify({'success': True, 'transaction': transaction.to_dict()})
    elif request.method == 'DELETE':
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/categories')
@login_required
def api_categories():
    categories = Category.query.filter((Category.user_id == None) | (Category.user_id == current_user.id)).all()
    return jsonify({'categories': [c.to_dict() for c in categories]})

@app.route('/users')
@login_required
@admin_required
def users():
    return render_template('users.html', users=User.query.all())

@app.route('/api/users')
@login_required
@admin_required
def api_users():
    return jsonify({'users': [u.to_dict() for u in User.query.all()]})

@app.route('/api/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def api_user_detail(id):
    user = User.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(user.to_dict())
    elif request.method == 'PUT':
        data = request.get_json() or request.form
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)
        user.is_active = data.get('is_active', user.is_active)
        if data.get('password'): user.set_password(data.get('password'))
        db.session.commit()
        return jsonify({'success': True, 'user': user.to_dict()})
    elif request.method == 'DELETE':
        if user.id == current_user.id:
            return jsonify({'error': 'Nao pode excluir seu proprio usuario'}), 400
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/api/reports/summary')
@login_required
def api_reports_summary():
    period = request.args.get('period', 'month')
    today = datetime.today()
    if period == 'week': start_date = today - timedelta(days=today.weekday())
    elif period == 'month': start_date = today.replace(day=1)
    elif period == 'year': start_date = today.replace(month=1, day=1)
    else: start_date = datetime(2000, 1, 1)
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id, Transaction.type == 'income', Transaction.date >= start_date
    ).scalar() or 0
    total_expense = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id, Transaction.type == 'expense', Transaction.date >= start_date
    ).scalar() or 0
    by_category = db.session.query(
        Category.name, Category.color, Category.type, db.func.sum(Transaction.amount)
    ).join(Transaction).filter(Transaction.user_id == current_user.id, Transaction.date >= start_date).group_by(Category.id).all()
    monthly = db.session.query(
        db.func.strftime('%Y-%m', Transaction.date), Transaction.type, db.func.sum(Transaction.amount)
    ).filter(Transaction.user_id == current_user.id, Transaction.date >= start_date).group_by(
        db.func.strftime('%Y-%m', Transaction.date), Transaction.type).all()
    return jsonify({
        'period': period, 'total_income': total_income, 'total_expense': total_expense,
        'balance': total_income - total_expense,
        'by_category': [{'name': c[0], 'color': c[1], 'type': c[2], 'amount': float(c[3])} for c in by_category],
        'monthly': [{'month': m[0], 'type': m[1], 'amount': float(m[2])} for m in monthly]
    })

@app.route('/api/export/<format>')
@login_required
def export_data(format):
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Data', 'Titulo', 'Tipo', 'Categoria', 'Valor', 'Metodo', 'Descricao'])
        for t in transactions:
            writer.writerow([t.date.strftime('%d/%m/%Y'), t.title, 'Receita' if t.type == 'income' else 'Despesa',
                t.category.name if t.category else '', f'{t.amount:.2f}', t.payment_method, t.description or ''])
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')), mimetype='text/csv',
            as_attachment=True, download_name=f'transacoes_{datetime.now().strftime("%Y%m%d")}.csv')
    elif format == 'excel' and PANDAS_AVAILABLE:
        data = []
        for t in transactions:
            data.append({'Data': t.date.strftime('%d/%m/%Y'), 'Titulo': t.title,
                'Tipo': 'Receita' if t.type == 'income' else 'Despesa',
                'Categoria': t.category.name if t.category else '', 'Valor': t.amount,
                'Metodo': t.payment_method, 'Descricao': t.description or ''})
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(data).to_excel(writer, sheet_name='Transacoes', index=False)
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True, download_name=f'transacoes_{datetime.now().strftime("%Y%m%d")}.xlsx')
    elif format == 'pdf' and REPORTLAB_AVAILABLE:
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
            textColor=colors.HexColor('#0f172a'), spaceAfter=30)
        elements.append(Paragraph('Relatorio de Transacoes', title_style))
        elements.append(Spacer(1, 20))
        table_data = [['Data', 'Titulo', 'Tipo', 'Categoria', 'Valor']]
        for t in transactions:
            table_data.append([t.date.strftime('%d/%m/%Y'), t.title,
                'Receita' if t.type == 'income' else 'Despesa',
                t.category.name if t.category else '', f'R$ {t.amount:.2f}'])
        table = Table(table_data, colWidths=[80, 150, 80, 100, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.HexColor('#ffffff')])
        ]))
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        return send_file(output, mimetype='application/pdf',
            as_attachment=True, download_name=f'transacoes_{datetime.now().strftime("%Y%m%d")}.pdf')
    return jsonify({'error': 'Formato nao suportado'}), 400

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/api/settings/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json() or request.form
    current_user.name = data.get('name', current_user.name)
    current_user.email = data.get('email', current_user.email)
    if data.get('password'):
        if data.get('password') == data.get('confirm_password'):
            current_user.set_password(data.get('password'))
        else:
            return jsonify({'error': 'Senhas nao coincidem'}), 400
    db.session.commit()
    return jsonify({'success': True, 'user': current_user.to_dict()})

@app.errorhandler(404)
def not_found(e):
    return render_template('login.html'), 404

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True, host='0.0.0.0', port=5000)
