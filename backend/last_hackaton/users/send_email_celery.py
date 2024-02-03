from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_activation_email(user_email, activation_code):
    subject = 'Активируйте свой аккаунт'
    message = f'Ваш код: {activation_code}'
    from_email = 'ams800v@gmail.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)

