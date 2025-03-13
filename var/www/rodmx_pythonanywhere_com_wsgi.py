import sys
import os

# Add your project directory to the sys.path
path = '/home/rodmx/mysite'
if path not in sys.path:
    sys.path.append(path)

# Activate your virtual environment
activate_this = '/home/rodmx/myenv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import your app from app.py
from app import app as application