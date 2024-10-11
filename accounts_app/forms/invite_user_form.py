from django import forms
from django.core.exceptions import ValidationError
from accounts_app.models import User


class InviteUserForm(forms.Form):
    email = forms.EmailField(max_length=65, required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        if User.objects.filter(email=email):
            raise ValidationError("Email already exists as a user.")
