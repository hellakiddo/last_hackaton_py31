from last_hackaton.users.send_email_celery import (
    send_activation_email
)
from last_hackaton.last_hackaton.celery import app

@app.task
def send_confirm_email_task(email, code):
    send_activation_email(email, code)
