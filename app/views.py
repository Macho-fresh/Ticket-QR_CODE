from django.shortcuts import render
from .models import *
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import secrets
from .serializer import *
import qrcode
from django.utils import timezone

from accounts.views import IsStaff
from dotenv import load_dotenv
import requests
from django.db import transaction
from django.core.mail import send_mail
import os
from django.conf import settings
import io
from django.core.files.base import ContentFile
import csv
from django.http import HttpResponse
from .tasks import *

load_dotenv()

class CreateEvent(APIView):
    permission_classes = [IsStaff]
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        location = request.data.get('location')
        start_at = request.data.get('start_at')
        end_at = request.data.get('end_at')
        capacity = request.data.get('capacity')
        price = request.data.get('price')

        with transaction.atomic():
            Event.objects.create(
                title =title,
                description = description,
                location = location,
                start_at = start_at,
                end_at = end_at,
                capacity = capacity,
                created_by = request.user,
                price = price
            )
            print(request.user.email)  
            print(settings.EMAIL_HOST_PASSWORD)
            sendmail.delay(title, request.user.email)

            return Response({
                'message': 'Event Created Successfully'
            }, status=status.HTTP_201_CREATED)

# send email to owner after creation
# add celery workers

class PaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer
    def post (self, request):
        event_id = request.data.get('event_id')
        # owner_id = request.data.get('owner')
        event = Event.objects.get(id=event_id)
        owner = request.user
        now = timezone.now()
        if now >= event.end_at:
            return Response({
                'error': 'Event Ended'
            }, status = status.HTTP_403_FORBIDDEN) 
        url = 'https://api.paystack.co/transaction/initialize'
        
        headers = {
            "Authorization": f"Bearer {os.getenv('SECRET_KEY')}",
            "Content-Type": "application/json"
        }

        amount = (event.price * 100) 

        payload = {
        "email": owner.email,
        "amount": f'{amount}',
        "callback_url": f"http://127.0.0.1:8000/api/create-ticket/"
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        print(data)
        reference = data['data']['reference']
        Payment.objects.create(
            reference=reference,
            user=request.user,
            amount = amount,
            event=event,
            status="pending"
        )
        return Response({
            'payment_url': data['data']['authorization_url']
        }, status = status.HTTP_200_OK)

class CreateTicket(generics.GenericAPIView):
    permission_classes = []
    serializer_class = TicketSerializer

    def get(self, request):
        # event_id = request.GET.get('event_id')
        reference = request.GET.get('reference')
        # owner_id = request.data.get('owner')
        # event = Event.objects.get(id=event_id)
        owner = Payment.objects.get(reference=reference).user
        event = Payment.objects.get(reference=reference).event
        token = secrets.token_urlsafe(32)   
        qr = qrcode.make(f'http://127.0.0.1:8000/api/check-in/{token}')
        buffer = io.BytesIO()
        qr.save(buffer, format = "PNG")

        now = timezone.now()
        if now >= event.end_at:
            return Response({
                'error': 'Event Ended'
            }, status = status.HTTP_403_FORBIDDEN) 
        # integrate paystack
        headers = {
        "Authorization": f"Bearer {os.getenv('SECRET_KEY')}"
        }

        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers
        )

        data = response.json()
        print(data)

        if data['data']['status'] == 'success':
       
            if Ticket.objects.filter(event = event).count() < event.capacity:

                ticket = Ticket.objects.create(
                    event = event,
                    owner = owner,
                    qr_token = token
                )
                ticket.qr_code.save(
                    f'{token}.png',
                    ContentFile(buffer.getvalue()),
                    save = False
                ) 
                ticket.save()
                qr_url = request.build_absolute_uri(ticket.qr_code.url)
                serializer = TicketSerializer(ticket)
                ticketmail.delay(qr_url, owner.email)

                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response({
                'error': 'capacity is full'
            }, status = status.HTTP_503_SERVICE_UNAVAILABLE)

# integrate paystack in createticket so after purchase ticket is automatically created

class ViewEvents(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)

        return Response(serializer.data,status = status.HTTP_200_OK)

class EditEvents(generics.GenericAPIView):
    permission_classes = [IsStaff]
    serializer_class = EventSerializer

    def patch(self, request, id):
        title = request.data.get('title')
        description = request.data.get('description')
        location = request.data.get('location')
        start_at = request.data.get('start_at')
        end_at = request.data.get('end_at')
        capacity = request.data.get('capacity')

        try:
            event = Event.objects.get(
                id=id,
                created_by=request.user
            )
        except Event.DoesNotExist:
            return Response(
                {
                    'error': 'You are not the owner of this event'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        event.title = title
        event.description = description
        event.location = location
        event.start_at = start_at
        event.end_at = end_at
        event.capacity = capacity
        event.created_by = request.user
        event.save()

        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class DeleteEvent(generics.GenericAPIView):
    permission_classes = [IsStaff]
    serializer_class = EventSerializer
    def delete(self, request, id):
        event = Event.objects.get(id=id, created_by=request.user)
        if event:
            event.delete()
            return Response({
                'message': 'Event Deleted'
            }, status=status.HTTP_200_OK)

class ViewTickets(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get(self, request):
        tickets = Ticket.objects.filter(owner=request.user)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ViewOneTicket(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get(self, request, id):
        ticket = Ticket.objects.get(id=id)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data,status=status.HTTP_200_OK)

class GetAttendees(generics.GenericAPIView):
    permission_classes = [IsStaff]
    serializer_class = AttendeeSerializer

    def get(self, request, id):
        event = Event.objects.get(id=id)
        ticket = Ticket.objects.filter(event=event)
        serializer = AttendeeSerializer(ticket, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)   

class GetAttendeesCSV(generics.GenericAPIView):
    permission_classes = [IsStaff]
    serializer_class = AttendeeSerializer

    def get(self, request, id):
        event = Event.objects.get(id=id)
        tickets = Ticket.objects.filter(event=event)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendeess.csv"'
        writer = csv.writer(response)
        writer.writerow(['Owner', 'Checked-in'])
        for ticket in tickets:
            writer.writerow([ticket.owner, ticket.checked_in])
        return response  

class CheckIn(generics.GenericAPIView):
    permission_classes = [IsStaff]
    def post (self, request, token):
        ticket = Ticket.objects.get(qr_token=token)
        if timezone.now() < ticket.event.start_at or timezone.now() >= ticket.event.end_at:
            return Response({
                'error': 'cannot check-in before or after the event'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        if ticket.checked_in == False:
            ticket.checked_in = True
            ticket.checked_in_at = timezone.now()
            ticket.save()
            return Response({
                'message': 'Checked_in: True'
            }, status = status.HTTP_202_ACCEPTED)
        return Response({
            'error': 'ticket already checked in'
        }, status=status.HTTP_409_CONFLICT)
        
# check in endpoint ----- done
# export to csv