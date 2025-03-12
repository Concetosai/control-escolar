...
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
import qrcode
import io
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_strong_random_secret_key_here'  # Change this to a secure random string

# Define DummyMail class
class DummyMail:
    def __init__(self, app=None):
        self.app = app
        
    def init_app(self, app):
        self.app = app
        
    def send(self, message):
        print(f"DUMMY MAIL: Would send email to {message.recipients}")
        print(f"DUMMY MAIL: Subject: {message.subject}")
        print(f"DUMMY MAIL: Body: {message.body}")
        return True

# Create a dummy message class
class Message:
    def __init__(self, subject, recipients, body):
        self.subject = subject
        self.recipients = recipients
        self.body = body

# Use DummyMail instead of Mail
mail = DummyMail(app)

# Simulated databases
attendance_records = {}
registered_students = {}
user_passwords = {}

# Formularios
class StudentForm(FlaskForm):
    first_name = StringField('Nombre(s)', validators=[DataRequired()])
    last_name = StringField('Apellidos', validators=[DataRequired()])
    parent_email = StringField('Correo de Padres/Tutores', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrar')

# Add admin credentials
admin_credentials = {
    "admin": "admin123"
}

class LoginForm(FlaskForm):
    student_number = StringField('Número de Estudiante o Usuario Admin', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    user_type = request.args.get('user_type', 'student')
    
    print("CSRF Token:", form.csrf_token.current_token)  # Debugging
    
    # Explicitly set the form action to include the user_type parameter
    form_action = url_for('login', user_type=user_type)
    
    if form.validate_on_submit():
        username = form.student_number.data
        password = form.password.data
        
        if username in admin_credentials and admin_credentials[username] == password:
            session['is_admin'] = True
            session['username'] = username
            return redirect(url_for('students_list'))
        elif username in user_passwords and user_passwords[username] == password:
            session['student_number'] = username
            session['is_admin'] = False
            return redirect(url_for('student_profile'))
        else:
            error = "Número de estudiante/usuario o contraseña incorrectos"
    
    if form.errors:
        print("Form validation errors:", form.errors)  # Debugging
    
    return render_template('login.html', form=form, error=error, user_type=user_type, form_action=form_action)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_number' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            flash('Acceso denegado. Se requieren privilegios de administrador.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/scan', methods=['GET', 'POST'])
@admin_required
def scan():
    if request.method == 'POST':
        student_number = request.form.get('student_number')
        if student_number:
            if student_number not in registered_students:
                return render_template('error.html', 
                    message="Error: Este estudiante no está registrado en el sistema.",
                    student_number=student_number)
            
            # Get student data
            student_data = registered_students[student_number]
            first_name = student_data['first_name']
            last_name = student_data['last_name']
            
            current_time = datetime.now()
            is_late = False
            
            # Check if entry is late (after 7:00 AM)
            if current_time.hour > 7 or (current_time.hour == 7 and current_time.minute > 0):
                is_late = True
            
            if student_number not in attendance_records:
                attendance_records[student_number] = {'entries': [], 'exits': [], 'late': []}
            
            if not attendance_records[student_number]['entries'] or \
               len(attendance_records[student_number]['entries']) == len(attendance_records[student_number]['exits']):
                attendance_records[student_number]['entries'].append(current_time)
                attendance_records[student_number]['late'].append(is_late)
                
                if is_late:
                    message = "Entrada registrada con retraso"
                else:
                    message = "Entrada registrada exitosamente"
                
                # Enviar correo de entrada
                email_sent = send_attendance_email(student_number, "entrada", is_late)
                if email_sent:
                    message += " y notificación enviada a los padres"
                else:
                    message += " pero no se pudo enviar notificación a los padres"
            else:
                attendance_records[student_number]['exits'].append(current_time)
                message = "Salida registrada exitosamente"
                # Enviar correo de salida
                email_sent = send_attendance_email(student_number, "salida")
                if email_sent:
                    message += " y notificación enviada a los padres"
                else:
                    message += " pero no se pudo enviar notificación a los padres"
            
            return render_template('scan_result.html', 
                                 time=current_time.strftime('%Y-%m-%d %H:%M:%S'),
                                 message=message,
                                 student_number=student_number,
                                 first_name=first_name,
                                 last_name=last_name,
                                 email_sent=email_sent,
                                 is_late=is_late)
    return render_template('scan.html')

@app.route('/attendance/<student_number>')
def attendance(student_number):
    if student_number in registered_students:
        student_data = registered_students[student_number]
        student_first_name = student_data['first_name']
        student_last_name = student_data['last_name']
        if student_number not in attendance_records:
            attendance_records[student_number] = {'entries': [], 'exits': []}
        records = attendance_records[student_number]
        paired_records = []
        for i in range(len(records['entries'])):
            entry = records['entries'][i]
            exit_time = records['exits'][i] if i < len(records.get('exits', [])) else None
            paired_records.append((entry, exit_time))
        return render_template('attendance.html', 
                             student_number=student_number,
                             first_name=student_first_name,
                             last_name=student_last_name,
                             records=paired_records)
    return render_template('error.html', 
                          message="Error: Este estudiante no está registrado en el sistema.",
                          student_number=student_number)

@app.route('/students')
@admin_required
def students_list():
    students = []
    for number, data in registered_students.items():
        students.append({
            'number': number,
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'registration_date': data['registration_date']
        })
    return render_template('students_list.html', students=students)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def landing():
    # Always show the landing page regardless of login status
    return render_template('landing.html')

@app.route('/home')
def home():
    # This can still redirect based on login status if needed
    if 'is_admin' in session and session['is_admin']:
        return redirect(url_for('students_list'))
    elif 'student_number' in session:
        return redirect(url_for('student_profile'))
    return redirect(url_for('landing'))

# Agrega esta función para enviar correos
# Modifica la función de envío de correos para incluir más información de depuración
def send_attendance_email(student_number, action):
    # Simple version that just logs and returns success
    print(f"Simulando envío de correo para estudiante {student_number}, acción: {action}")
    return True
    
    # The following code is kept but won't execute due to the return above
    try:
        if student_number in registered_students:
            student = registered_students[student_number]
            parent_email = student.get('parent_email')
            
            # Validate email format
            if not parent_email or '@' not in parent_email:
                print(f"Correo inválido para el estudiante {student_number}: {parent_email}")
                return False
                
            student_name = f"{student['first_name']} {student['last_name']}"
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subject = f"Registro de {action} - Control Escolar"
            
            if action == "entrada":
                body = f"Estimado padre/tutor,\n\nSu hijo(a) {student_name} ha registrado su entrada a la escuela a las {current_time}.\n\nSaludos cordiales,\nSistema de Control Escolar"
            else:
                body = f"Estimado padre/tutor,\n\nSu hijo(a) {student_name} ha registrado su salida de la escuela a las {current_time}.\n\nSaludos cordiales,\nSistema de Control Escolar"
            
            print(f"Intentando enviar correo a {parent_email} para {student_name}")
            
            msg = Message(
                subject=subject,
                recipients=[parent_email],
                body=body
            )
            
            mail.send(msg)
            print(f"Correo enviado exitosamente a {parent_email}")
            return True
        else:
            print(f"Estudiante {student_number} no encontrado en la base de datos")
            return False
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

# Function to generate student number
def generate_student_number():
    base_number = "TEC35-"  # Changed from previous prefix to TEC35-
    next_number = len(registered_students) + 1
    return f"{base_number}{next_number:03}"  # This formats the number with leading zeros (001, 002, etc.)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = StudentForm()
    if form.validate_on_submit():
        student_first_name = form.first_name.data
        student_last_name = form.last_name.data
        student_number = generate_student_number()  # Automatically generate student number
        password = form.password.data
        parent_email = form.parent_email.data
        
        # Store student information
        registered_students[student_number] = {
            'first_name': student_first_name,
            'last_name': student_last_name,
            'full_name': f"{student_last_name}, {student_first_name}",
            'parent_email': parent_email,
            'registration_date': datetime.now()
        }
        
        # Store password
        user_passwords[student_number] = password
        
        # Set session
        session['student_number'] = student_number
        session['is_admin'] = False
        
        print(f"Registration successful for student {student_number}, redirecting to profile.")
        
        return redirect(url_for('student_profile'))
    
    if form.errors:
        print("Form validation errors:", form.errors)
    
    return render_template('register.html', form=form)

@app.route('/profile')
@login_required
def student_profile():
    student_number = session['student_number']
    if student_number in registered_students:
        student_data = registered_students[student_number]
        student_first_name = student_data['first_name']
        student_last_name = student_data['last_name']
        qr_url = url_for('get_qr', first_name=student_first_name, last_name=student_last_name, number=student_number, _external=True)
        
        # Initialize attendance_data before using it
        attendance_data = []
        if student_number in attendance_records:
            records = attendance_records[student_number]
            for i in range(len(records.get('entries', []))):
                entry = records['entries'][i]
                exit_time = records['exits'][i] if i < len(records.get('exits', [])) else None
                attendance_data.append((entry, exit_time))
                
        return render_template('student_profile.html', 
                              first_name=student_first_name,
                              last_name=student_last_name,
                              student_number=student_number,
                              number=student_number, 
                              qr_url=qr_url,
                              records=attendance_data)
    return redirect(url_for('login'))

@app.route('/student_info')
def student_info():
    student_first_name = request.args.get('first_name')
    student_last_name = request.args.get('last_name')
    student_number = request.args.get('number')
    qr_url = url_for('get_qr', first_name=student_first_name, last_name=student_last_name, number=student_number, _external=True)
    return render_template('student.html', first_name=student_first_name, last_name=student_last_name, number=student_number, qr_url=qr_url)

@app.route('/get_qr')
def get_qr():
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')
    number = request.args.get('number', '')
    
    # Generate QR code
    student_first_name = request.args.get('first_name')
    student_last_name = request.args.get('last_name')
    student_number = request.args.get('number')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"Nombre: {student_first_name}\nApellidos: {student_last_name}\nNúmero: {student_number}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

# Agregar al final del archivo
# Al final del archivo app.py, añade o modifica:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)