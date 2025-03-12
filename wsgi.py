import sys
import os

# Add the directory containing your app.py to the Python path
path = '/home/rodmx/mysite'
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app object from your app.py file
from app import app as application