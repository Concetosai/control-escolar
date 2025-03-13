{% extends "layout.html" %}

{% block title %}Perfil de Estudiante{% endblock %}

{% block styles %}
<style>
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        font-family: Arial, sans-serif;
    }
    .profile-container {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    h1 {
        text-align: center;
        color: #333;
    }
    .student-photo {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        overflow: hidden;
        margin-bottom: 20px;
        border: 3px solid #4CAF50;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        position: relative;
    }
    .profile-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .no-photo {
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #e0e0e0;
        color: #757575;
        font-size: 60px;
    }
    .photo-update-button {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: rgba(0, 0, 0, 0.5);
        padding: 5px;
        text-align: center;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .student-photo:hover .photo-update-button {
        opacity: 1;
    }
    .photo-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 3px;
        cursor: pointer;
        font-size: 12px;
    }
    .student-info {
        text-align: center;
        margin-bottom: 20px;
    }
    .student-info p {
        margin: 5px 0;
        font-size: 18px;
    }
    .qr-container {
        text-align: center;
        margin: 20px 0;
    }
    .qr-container img {
        max-width: 200px;
        border: 1px solid #ddd;
    }
    .button-container {
        text-align: center;
        margin-top: 20px;
    }
    .button {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 4px;
        margin: 0 5px;
    }
    .button:hover {
        background-color: #45a049;
    }
    
    /* Modal styles */
    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
    }
    .modal-content {
        background-color: white;
        margin: 10% auto;
        padding: 20px;
        width: 80%;
        max-width: 500px;
        border-radius: 8px;
    }
    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }
    .close:hover {
        color: black;
    }
    #camera-container {
        margin-top: 20px;
        text-align: center;
    }
    #video {
        width: 100%;
        max-width: 400px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    #canvas {
        display: none;
    }
    .camera-buttons {
        margin-top: 10px;
    }
    #photo-preview {
        margin-top: 10px;
        max-width: 400px;
        border: 1px solid #ddd;
        border-radius: 4px;
        display: none;
    }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h1>Perfil de Estudiante</h1>
    
    <div class="profile-container">
        <div class="student-photo">
            {% if student_image %}
            <img src="{{ url_for('static', filename='uploads/' + student_image) }}" alt="Foto de {{ first_name }}" class="profile-image">
            {% else %}
            <div class="no-photo">
                <i class="fas fa-user"></i>
            </div>
            {% endif %}
            <div class="photo-update-button">
                <button id="update-photo-btn" class="photo-btn">Actualizar Foto</button>
            </div>
        </div>
        
        <div class="student-info">
            <p><strong>Nombre:</strong> {{ first_name }} {{ last_name }}</p>
            <p><strong>Número de Estudiante:</strong> {{ student_number }}</p>
        </div>
        
        <div class="qr-container">
            <h2>Tu Código QR</h2>
            <p>Muestra este código al entrar y salir de la escuela</p>
            <img src="{{ qr_url }}" alt="Código QR">
        </div>
        
        <div class="button-container">
            <a href="{{ url_for('attendance', student_number=student_number) }}" class="button">Ver Registro de Asistencia</a>
            <a href="{{ url_for('logout') }}" class="button">Cerrar Sesión</a>
        </div>
    </div>
    
    <!-- Photo Update Modal -->
    <div id="photoModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>Actualizar Foto</h2>
            
            <div id="camera-container">
                <video id="video" autoplay></video>
                <canvas id="canvas"></canvas>
                <img id="photo-preview" alt="Vista previa de la foto">
                
                <div class="camera-buttons">
                    <button type="button" id="start-camera" class="button">Iniciar Cámara</button>
                    <button type="button" id="take-photo" class="button" disabled>Tomar Foto</button>
                    <button type="button" id="retake-photo" class="button" style="display:none">Tomar Otra</button>
                    <button type="button" id="save-photo" class="button" style="display:none">Guardar Foto</button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Modal elements
        const modal = document.getElementById('photoModal');
        const updatePhotoBtn = document.getElementById('update-photo-btn');
        const closeBtn = document.querySelector('.close');
        
        // Camera elements
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const photoPreview = document.getElementById('photo-preview');
        const startCameraBtn = document.getElementById('start-camera');
        const takePhotoBtn = document.getElementById('take-photo');
        const retakePhotoBtn = document.getElementById('retake-photo');
        const savePhotoBtn = document.getElementById('save-photo');
        
        let stream = null;
        
        // Open modal
        updatePhotoBtn.addEventListener('click', function() {
            modal.style.display = 'block';
        });
        
        // Close modal
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
            stopCamera();
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
                stopCamera();
            }
        });
        
        // Start camera
        startCameraBtn.addEventListener('click', async function() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        facingMode: 'user',
                        width: { ideal: 640 },
                        height: { ideal: 480 }
                    } 
                });
                video.srcObject = stream;
                startCameraBtn.disabled = true;
                takePhotoBtn.disabled = false;
            } catch (err) {
                console.error('Error accessing camera:', err);
                alert('No se pudo acceder a la cámara. Por favor, asegúrate de que tienes una cámara conectada y has dado permiso para usarla.');
            }
        });
        
        // Take photo
        takePhotoBtn.addEventListener('click', function() {
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert to data URL and display preview
            const dataURL = canvas.toDataURL('image/png');
            photoPreview.src = dataURL;
            photoPreview.style.display = 'block';
            
            // Show retake and save buttons
            takePhotoBtn.style.display = 'none';
            retakePhotoBtn.style.display = 'inline-block';
            savePhotoBtn.style.display = 'inline-block';
        });
        
        // Retake photo
        retakePhotoBtn.addEventListener('click', function() {
            photoPreview.style.display = 'none';
            takePhotoBtn.style.display = 'inline-block';
            retakePhotoBtn.style.display = 'none';
            savePhotoBtn.style.display = 'none';
        });
        
        // Save photo
        savePhotoBtn.addEventListener('click', function() {
            // Convert canvas to blob
            canvas.toBlob(function(blob) {
                // Create form data
                const formData = new FormData();
                formData.append('student_image', blob, 'student_photo.png');
                
                // Send to server
                fetch('{{ url_for("update_photo") }}', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Foto actualizada correctamente');
                        // Reload page to show new photo
                        window.location.reload();
                    } else {
                        alert('Error al actualizar la foto: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al actualizar la foto');
                });
            });
            
            // Close modal and stop camera
            modal.style.display = 'none';
            stopCamera();
        });
        
        // Stop camera function
        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        }
    });
</script>
{% endblock %}