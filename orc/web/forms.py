"""
Forms for ORC Web Application
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from orc.web.models import User


class SignUpForm(FlaskForm):
    """User registration form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=120, message='Name must be between 2 and 120 characters')
    ])
    
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    accept_terms = BooleanField('I accept the Terms and Conditions', validators=[
        DataRequired(message='You must accept the terms and conditions')
    ])
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please sign in or use a different email.')


class SignInForm(FlaskForm):
    """User login form"""
    username = StringField('Username or Email', validators=[
        DataRequired()
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    
    remember_me = BooleanField('Remember Me')


class ProjectForm(FlaskForm):
    """Create/Edit project form"""
    name = StringField('Project Name', validators=[
        DataRequired(),
        Length(min=2, max=120, message='Name must be between 2 and 120 characters')
    ])
    
    path = StringField('Project Path', validators=[
        DataRequired(),
        Length(max=500)
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=1000, message='Description must be less than 1000 characters')
    ])


class APIConfigForm(FlaskForm):
    """API provider configuration form"""
    provider = SelectField('AI Provider', choices=[
        ('ollama', 'Ollama (Local)'),
        ('groq', 'Groq'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic (Claude)'),
        ('gemini', 'Google Gemini'),
        ('deepseek', 'DeepSeek')
    ], validators=[DataRequired()])
    
    api_key = StringField('API Key', validators=[
        Length(max=255)
    ])
    
    model_name = StringField('Model Name', validators=[
        Length(max=100)
    ])
    
    base_url = StringField('Base URL', validators=[
        Length(max=255)
    ])
    
    is_default = BooleanField('Set as default provider')


class AccountSettingsForm(FlaskForm):
    """Account settings form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=120)
    ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])


class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired()
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
