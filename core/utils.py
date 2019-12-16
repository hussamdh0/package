from django.core.mail           import send_mail
from django.conf                import settings
import random, string

def reset_user_password_by_email(user):
    user.reset_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    user.save()
    send_mail(
        f'Reset password for package app.',
        f'new password for package app for user with email: {user.email} '
        f'is: {user.reset_token}',
        settings.EMAIL_SENDER,
        [user.email],
        fail_silently=False,
    )