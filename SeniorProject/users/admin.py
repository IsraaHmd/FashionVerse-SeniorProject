from django.contrib import admin

from users.models import CustomUser  # Import your custom User model

admin.site.register(CustomUser)  # Register the User model
