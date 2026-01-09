"""
Authentication routes for ORC Web Application
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from orc.web.models import db, User
from orc.web.forms import SignUpForm, SignInForm
from datetime import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    form = SignUpForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Auto login after signup
            login_user(user)
            flash('Account created successfully! Welcome to ORC.', 'success')
            return redirect(url_for('dashboard.home'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            print(f"Signup error: {e}")
    
    return render_template('auth/signup.html', form=form)


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    form = SignInForm()
    
    if form.validate_on_submit():
        # Find user by username or email
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Login user
            login_user(user, remember=form.remember_me.data)
            flash('Signed in successfully!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.home'))
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('auth/signin.html', form=form)


@auth.route('/signout')
@login_required
def signout():
    """User logout"""
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('main.landing'))
