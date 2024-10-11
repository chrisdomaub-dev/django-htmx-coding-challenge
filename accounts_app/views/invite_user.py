from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext as _

from accounts_app.forms import EditUserForm, InviteUserForm
from accounts_app.models import UserInvitation

from datetime import timedelta


class InviteUserView(LoginRequiredMixin, View):

    # Added "accept-invite" view and url to group same process/intents instead and removed the GET here
    # def get(self, request, *args, **kwargs):
    #     ...

    def post(self, request, *args, **kwargs):
        user_form = EditUserForm(instance=request.user)
        invite_user_form = InviteUserForm(request.POST)

        if invite_user_form.is_valid():
            # 1. I added USER_INVITE_INTERVAL_MINUTES to avoid re-invitation spamming (15 minutes),
            # e.g. can only re-invite every 15 minutes
            # 2. Only use the UserInvitation.expires_at in the [GET] view only to restrict invalid invitations and not
            # on the [POST] since having 7 days (USER_INVITE_EXPIRATION_DAYS) lag before being able to re-invite
            # would be too long, and not having any would be disastrous.
            # 3. Assuming that the invited email address becomes a user, I restricted inviting email that
            # is already a user.
            # 4. In the future it would be best for UserInvite to have a Boolean sent_success flag to be able to
            # strategically re-invite users who are marked sent_success=False.

            time_threshold = timezone.now() - timedelta(minutes=settings.USER_INVITE_INTERVAL_MINUTES)

            existing_invitations = UserInvitation.objects.filter(email=invite_user_form.cleaned_data["email"])

            if existing_invitations:
                if existing_invitations.filter(created_at__gt=time_threshold):
                    messages.error(request, _(
                        f"Can only re-invite user every {settings.USER_INVITE_INTERVAL_MINUTES} minutes to avoid spamming."
                    ))
                    return render(request, "accounts_app/profile.html", {"form": user_form, "invite_user_form": invite_user_form})
                else:
                    existing_invitations.delete()

            invitation = UserInvitation(email=invite_user_form.cleaned_data["email"], invited_by=request.user)
            invitation.save()

            invitation.send_invitation_email()

            messages.success(request, _(
                f"Email sent to {invitation.email}."
            ))
            return render(request, "accounts_app/profile.html", {"form": user_form, "invite_user_form": invite_user_form, "invited": True})
        else:
            for field, errors in invite_user_form.errors.items():
                for error in errors:
                    messages.error(request, _(error))

            return render(request, "accounts_app/profile.html", {"form": user_form, "invite_user_form": invite_user_form})
