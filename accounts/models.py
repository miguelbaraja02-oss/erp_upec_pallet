from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# CREAR EL MODELO PARA USUARIOS
class User(AbstractUser):
    first_name = models.CharField(
        max_length = 50, 
        blank = False,
        null = False,
    )
    last_name = models.CharField(
        max_length = 50, 
        blank = False, 
        null = False,
    )
    email = models.EmailField(
        unique = True,
        blank = False, 
        null = False,
    )
    
    ## PARA CREAR MAS CAMPOS ROLE, ETC.
    
    def __str__ (self):
        return f"{self.username} {self.email}"
    
    
    
#### FOTOS DEL USUARIO (AVATAR) #####
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )


    # NUEVOS CAMPOS
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


