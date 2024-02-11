from .send_email import send_confirmation_email, send_password_reset_email
from last_hackaton.celery import app

@app.task
def send_confirm_email_task(email, code):
    send_confirmation_email(email, code)

@app.task
def send_password_reset_task(email, user_id):
    send_password_reset_email(email, user_id)