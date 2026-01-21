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
    

