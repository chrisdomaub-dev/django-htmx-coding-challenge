from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext as _

from accounts_app.forms import EditUserForm, InviteUserForm, AcceptInviteForm
from accounts_app.models import UserInvitation

from datetime import timedelta


class AcceptInviteView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        try:
            # Attempt to retrieve the UserInvitation
            user_invite = UserInvitation.objects.get(id=request.GET["invite_id"])

            if user_invite.expires_at < timezone.now():
                user_invite.delete()
                return render(request, "accounts_app/invitation.html", {"invite_state": "expired"})

            return render(request, "accounts_app/invitation.html", {
                "invite_state": "valid",
                "invite": user_invite,
            })

        except UserInvitation.DoesNotExist:
            return render(request, "accounts_app/invitation.html", {"invite_state": "invalid"})

    def post(self, request, *args, **kwargs):
        form = AcceptInviteForm(request.POST)
        user_invite = UserInvitation.objects.get(id=request.POST["invite_id"])

        if form.is_valid():
            form.save()
            messages.success(request, _(f"Successfully created user."))

            return redirect("home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(error))

            return render(request, "accounts_app/invitation.html", {"form": form, "invite": user_invite})
