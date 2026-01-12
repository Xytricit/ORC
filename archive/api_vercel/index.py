"""
Vercel serverless entry point for ORC web app
"""
from orc.web.app_new import app

# Vercel needs this for serverless functions
handler = app
