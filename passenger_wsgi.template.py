# PythonAnywhere WSGI template — copy/paste into your PythonAnywhere WSGI file
import sys
import os

# EDIT: set this to your PythonAnywhere project path
project_home = '/home/YOUR_PYANYWHERE_USERNAME/YOUR_REPO'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Recommended production settings
os.environ['FLASK_ENV'] = 'production'
# Set SECRET_KEY using the Web tab environment variables on PythonAnywhere

# Import the Flask app as 'application'
from app import app as application
