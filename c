{% extends "layout.html" %}

{% block title %}Registro de Asistencia{% endblock %}

{% block styles %}
<style>
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        font-family: Arial, sans-serif;
    }
    .attendance-container {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
    }
    h1, h2 {
        text-align: center;
        color: #333;
    }
    .student-info {
        text-align: center;
        margin-bottom: 20px;
    }
    .student-info p {
        margin: 5px 0;
        font-size: 18px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    th {
        background-color: #4CAF50;
        color: white;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
    .no-records {
        text-align: center;
        margin: 20px 0;
        font-style: italic;
        color: #666;
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
    }
    .button:hover {
        background-color: #45a049;
    }
    .late-entry {
        color: #ff8c00; /* Orange color for late entries */
        font-weight: bold;
    }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h1>Registro de Asistencia</h1>
    
    <div class="attendance-container">
        <div class="student-info">
            <p><strong>Estudiante:</strong> {{ first_name }} {{ last_name }}</p>
            <p><strong>Número:</strong> {{ student_number }}</p>
        </div>
        
        {% if records %}
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Entrada</th>
                    <th>Salida</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {% for entry, exit, is_late in records %}
                <tr>
                    <td>{{ entry.strftime('%Y-%m-%d') }}</td>
                    <td>{{ entry.strftime('%H:%M:%S') }}</td>
                    <td>{{ exit.strftime('%H:%M:%S') if exit else 'Pendiente' }}</td>
                    <td>
                        {% if is_late %}
                        <span class="late-entry">Entrada con retraso</span>
                        {% else %}
                        A tiempo
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="no-records">
            No hay registros de asistencia para este estudiante.
        </div>
        {% endif %}
        
        <div class="button-container">
            <a href="{{ url_for('student_profile') }}" class="button">Volver al Perfil</a>
        </div>
    </div>
</div>
{% endblock %}