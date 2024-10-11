from django import forms

from accounts_app.models import User, UserInvitation
from django.core.exceptions import ValidationError
from django.utils import timezone


class AcceptInviteForm(forms.Form):

    invite_id = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=65, required=True)
    first_name = forms.CharField(max_length=65, required=True)
    last_name = forms.CharField(max_length=65, required=True)
    occupation = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        invite_id = cleaned_data.get("invite_id")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        invite = UserInvitation.objects.get(id=invite_id)

        if invite.expires_at < timezone.now():
            invite.delete()
            raise ValidationError("Invitation has expired.")

    def save(self):
        UserInvitation.objects.filter(email=self.cleaned_data['email']).delete()

        user = User(
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            occupation=self.cleaned_data['occupation'],
        )
        user.set_password(self.cleaned_data['password'])
        user.save()

        return user
