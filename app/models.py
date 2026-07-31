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

    def __str__(self):
        return f"{self.ticket_number} - {self.event.title}"