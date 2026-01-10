"""
Standalone ORC Web App - Vercel Compatible
Just authentication and dashboard, no heavy dependencies
"""
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('ORC_SECRET_KEY', 'dev-secret-change-me')

# Simple in-memory storage for now (we'll add database later)
users_db = {}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(user_id)

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/auth/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user
        user = None
        for u in users_db.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'error')
    
    return render_template('auth/signin.html')

@app.route('/auth/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        for u in users_db.values():
            if u.username == username or u.email == email:
                flash('User already exists', 'error')
                return redirect(url_for('signup'))
        
        # Create user
        user_id = str(len(users_db) + 1)
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        users_db[user_id] = user
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('auth/signup.html')

@app.route('/auth/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/home.html')

# Vercel needs this
handler = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
