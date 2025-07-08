from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import random
from django.utils import timezone

class CustomUser(AbstractUser):
    #Usernmame in AbstractUser: username = models.CharField(max_length=150, unique=True) 
    # Ensure the email field is unique and required (cannot be null or blank)
    email = models.EmailField(unique=True, blank=False, null=False)

    #password, first_name, last_name already defined in AbstractUser. By deault they are:
    #first_name = models.CharField(max_length=150, blank=True)
    #last_name = models.CharField(max_length=150, blank=True)

    #First_name, Last_name, and Phone number are required upon checkout
    phone_number=models.CharField(max_length=15, blank=True, null=True)

    #Upon login(authentication), the user has to enter email and the password, by default in django they should enter username and password
    #to change that:
    USERNAME_FIELD = 'email'  # Login with email instead of username
    REQUIRED_FIELDS = ['username']  #→ username and email required when creating a superuser, email because it is specified above as username field so it will be required anyways

    #Profile Image Upload (URL option is not available for profile picture)
    profile_image_upload = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.email + ' ' + self.username  # Adds a space between email and username
    """
    def get_profile_image(self):
            
            if self.profile_image_upload:
                return self.profile_image_upload.url
            # Return a default image path or URL
            return "/static/images/default_profile.png"
    """
