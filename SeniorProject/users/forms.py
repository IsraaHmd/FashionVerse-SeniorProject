from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.core.exceptions import ValidationError
import re

class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        error_messages = {
                'username': {
                    'unique': 'Username already exists.',
                    'required': 'Please enter a username.',
                },
                'email': {
                    'required': 'Please enter a valid email.',
                },
                'password1': {
                    'required': 'Please enter a password.',
                },
                'password2': {
                    'required': 'Please confirm your password.',
                    'mismatch': 'The passwords do not match.',
                },
            }
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password1 or not password2:
                raise ValidationError(self.Meta.error_messages['password2']['required'])
        # will not proceed
        if password1 and password2 and password1 != password2:
            raise ValidationError(self.Meta.error_messages['password2']['mismatch'])
        password_regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'

        # If password does not match the criteria, raise a ValidationError
        if not re.match(password_regex, password1):
            raise ValidationError(
                'Password must be at least 8 characters long and must contain:\n- at least one digit\n- at least one uppercase letter\n- at least one special character.'
            )

        return password2   
