{% extends "welcome/welcome.html" %}
{% load static %}

{% block title %}Cambiar Foto de Perfil{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/profile.css' %}">
{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            
            <div class="profile-card animate-up">
                <div class="card-header-custom">
                    <h3>Actualizar Avatar</h3>
                    <p>Elige una imagen para tu perfil</p>
                </div>

                <div class="card-body-custom">
                    
                    <div class="avatar-preview-container">
                        <div class="avatar-frame">
                            {% if user.profile.avatar %}
                                <img id="avatar-preview" src="{{ user.profile.avatar.url }}" alt="Vista previa">
                            {% else %}
                                <img id="avatar-preview" src="{% static 'img/default-avatar.png' %}" alt="Sin foto">
                            {% endif %}
                        </div>
                        <div class="camera-icon">
                            <i class="fa-solid fa-camera"></i>
                        </div>
                    </div>

                    <form method="post" enctype="multipart/form-data" class="avatar-form">
                        {% csrf_token %}
                        
                        <div class="custom-file-area">
                            <label for="id_avatar" class="file-label">
                                <i class="fa-solid fa-cloud-arrow-up me-2"></i>
                                <span id="file-name">Seleccionar nueva foto...</span>
                            </label>
                            
                            <div class="d-none">
                                {{ form.avatar }} 
                            </div>

                            {% if form.avatar.errors %}
                                <div class="alert alert-danger mt-3 py-1 px-2 small text-center">
                                    {{ form.avatar.errors }}
                                </div>
                            {% endif %}
                        </div>

                        <div class="action-buttons">
                            <button type="submit" class="btn-save">
                                Guardar Cambios
                            </button>
                            <a href="{% url 'accounts:profile' %}" class="btn-cancel">
                                Cancelar
                            </a>
                        </div>
                    </form>

                </div>
            </div>

        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/profile.js' %}"></script>
{% endblock %}