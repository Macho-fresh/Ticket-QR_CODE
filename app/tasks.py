from celery import shared_task
import os
from django.conf import settings
from django.core.mail import send_mail
from dotenv import load_dotenv
load_dotenv()

@shared_task
def sendmail(title, email):
    send_mail(
                    "Event created successfully",
                    f"{title} Event has been created",
                    os.getenv('EMAIL_HOST_USER'),
                    [email],
                    fail_silently=False,
                )

@shared_task
def ticketmail(qr_url, email):
    send_mail(
                "Ticket purchase successfull",
                f"here is the qr code: {qr_url}",
                os.getenv('EMAIL_HOST_USER'),
                [email],
                fail_silently=False,
            )