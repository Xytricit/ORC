"""
ORC Web App - ASGI version for Vercel
Using Starlette instead of Flask for serverless compatibility
"""
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
import os

# Setup
templates = Jinja2Templates(directory="templates")
SECRET_KEY = os.getenv('ORC_SECRET_KEY', 'dev-secret-change-me')

# Simple user storage (in-memory for now)
users_db = {}

async def landing(request):
    """Landing page"""
    user = request.session.get('user')
    if user:
        return RedirectResponse(url='/dashboard', status_code=302)
    return templates.TemplateResponse('landing.html', {'request': request})

async def signin_get(request):
    """Show signin page"""
    user = request.session.get('user')
    if user:
        return RedirectResponse(url='/dashboard', status_code=302)
    return templates.TemplateResponse('auth/signin.html', {'request': request})

async def signin_post(request):
    """Handle signin"""
    form = await request.form()
    username = form.get('username')
    password = form.get('password')
    
    # Check credentials (simplified for demo)
    # In production, use proper password hashing
    for user_id, user_data in users_db.items():
        if user_data['username'] == username and user_data['password'] == password:
            request.session['user'] = user_data
            return RedirectResponse(url='/dashboard', status_code=302)
    
    return templates.TemplateResponse('auth/signin.html', {
        'request': request,
        'error': 'Invalid credentials'
    })

async def signin(request):
    """Route signin requests"""
    if request.method == 'GET':
        return await signin_get(request)
    else:
        return await signin_post(request)

async def signup_get(request):
    """Show signup page"""
    user = request.session.get('user')
    if user:
        return RedirectResponse(url='/dashboard', status_code=302)
    return templates.TemplateResponse('auth/signup.html', {'request': request})

async def signup_post(request):
    """Handle signup"""
    form = await request.form()
    username = form.get('username')
    email = form.get('email')
    password = form.get('password')
    
    # Check if user exists
    for user_data in users_db.values():
        if user_data['username'] == username or user_data['email'] == email:
            return templates.TemplateResponse('auth/signup.html', {
                'request': request,
                'error': 'User already exists'
            })
    
    # Create user
    user_id = str(len(users_db) + 1)
    user_data = {
        'id': user_id,
        'username': username,
        'email': email,
        'password': password  # In production, hash this!
    }
    users_db[user_id] = user_data
    request.session['user'] = user_data
    
    return RedirectResponse(url='/dashboard', status_code=302)

async def signup(request):
    """Route signup requests"""
    if request.method == 'GET':
        return await signup_get(request)
    else:
        return await signup_post(request)

async def signout(request):
    """Handle signout"""
    request.session.clear()
    return RedirectResponse(url='/', status_code=302)

async def dashboard(request):
    """Dashboard page"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/auth/signin', status_code=302)
    return templates.TemplateResponse('dashboard/home.html', {
        'request': request,
        'user': user
    })

# Routes
routes = [
    Route('/', landing),
    Route('/auth/signin', signin, methods=['GET', 'POST']),
    Route('/auth/signup', signup, methods=['GET', 'POST']),
    Route('/auth/signout', signout),
    Route('/dashboard', dashboard),
]

# Create ASGI app
app = Starlette(
    debug=True,
    routes=routes,
    middleware=[
        Middleware(SessionMiddleware, secret_key=SECRET_KEY)
    ]
)

# Vercel needs this
handler = app
