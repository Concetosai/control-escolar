import shutil
from datetime import datetime
import os

def backup_database():
    # Crear directorio de respaldos si no existe
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generar nombre del archivo de respaldo con fecha y hora
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_file)
    
    # Realizar el respaldo
    shutil.copy2('school.db', backup_path)
    return backup_path