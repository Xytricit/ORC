# Production Configuration for ORC Web Application

# Flask configuration
DEBUG = False
TESTING = False
SECRET_KEY = 'orc-secret-key-change-in-production'

# Server configuration
HOST = '0.0.0.0'
PORT = 8000
THREADS = 4

# Security settings
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Database settings
DATABASE_PATH = '.orc/index.db'
MAX_FILE_SIZE_MB = 10

# Analysis settings
MAX_COMPLEXITY_THRESHOLD = 10
MIN_COMPLEXITY_THRESHOLD = 2
PARALLEL_WORKERS = 4

# Ignore patterns
IGNORE_PATTERNS = [
    '.git/',
    '__pycache__/',
    '.venv/',
    'venv/',
    'node_modules/',
    '.orc/',
    'dist/',
    'build/',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.DS_Store',
    'Thumbs.db'
]

# File extensions to analyze
FILE_EXTENSIONS = [
    '.py', '.js', '.ts', '.jsx', '.tsx', 
    '.html', '.htm', '.css', 
    '.json', '.yaml', '.yml', 
    '.md', '.markdown',
    '.scss', '.sass', '.less'
]

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'orc_web.log'