from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_confirmation_email(email, code):
    activation_url = f'http://158.160.9.246/api/activate/?u={code}'
    context = {'activation_url': activation_url}
    html_message = render_to_string('activation_email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        'Здравствуйте',
        plain_message,
        'ams800v@gmail.com',
        [email],
        html_message=html_message,
        fail_silently=False
    )

def send_password_reset_email(email, user_id):
    password_reset_url = f'http://158.160.9.246/api/password_confirm/{user_id}'
    context = {'password_reset_url': password_reset_url}
    html_message = render_to_string('password_reset_email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        'Здравствуйте',
        plain_message,
        'test@gmail.com',
        [email],
        html_message=html_message,
        fail_silently=False
    )