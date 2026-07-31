from django.shortcuts import render
from .models import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import secrets

class CreateEvent(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        location = request.data.get('location')
        start_at = request.data.get('start_at')
        end_at = request.data.get('end_at')
        capacity = request.data.get('capacity')

        Event.objects.create(
            title =title,
            description = description,
            location = location,
            start_at = start_at,
            end_at = end_at,
            capacity = capacity,
            created_by = request.user
        )

class CreateTicket(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_id = request.data.get('event')
        owner_id = request.data.get('owner')
        event = Event.objects.get(id=event_id)
        owner = event.owner
        token = secrets.token_urlsafe(32)   

# if eventy is in session no more tickets