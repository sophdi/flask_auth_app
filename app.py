# app.py
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Ініціалізація Flask додатку
app = Flask(__name__)
app.config['SECRET_KEY'] = '98d263e3b5fc7e2409cf56eb12b5003e'  # Використовуємо сильний секретний ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ініціалізація бази даних
db = SQLAlchemy(app)

# Налаштування Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модель користувача
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Маршрути
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Перевірка логіну та пароля
        if not user or not user.check_password(password):
            flash('Будь ласка, перевірте дані для входу і спробуйте знову.')
            return redirect(url_for('login'))
        
        # Якщо все правильно, авторизуємо користувача
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Перевірка, чи існує користувач
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Логін вже існує')
            return redirect(url_for('signup'))
        
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email вже використовується')
            return redirect(url_for('signup'))
        
        # Створення нового користувача
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        # Додавання до бази даних
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Створення таблиці, якщо вона не існує
    with app.app_context():
        db.create_all()
    app.run(debug=True)