from django.db import models
from accounts.models import User
from django.conf import settings


class Event(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=250)
    location = models.CharField(max_length=50)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    capacity = models.PositiveIntegerField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    price = models.DecimalField(max_digits=4, decimal_places=2)




class Ticket(models.Model):
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    qr_token = models.CharField(
        max_length=255,
        unique=True
    )

    qr_code = models.ImageField(upload_to='qr_code/')

    checked_in = models.BooleanField(
        default=False
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    checked_in_at = models.DateTimeField(
        null=True,
        blank=True
    )


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)