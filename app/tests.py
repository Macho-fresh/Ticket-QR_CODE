from django.test import TestCase
from rest_framework.test import APITestCase
from accounts.models import User
from .models import *
from rest_framework import status
import io
from django.core.files.base import ContentFile
import secrets

class CreateEventTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                    username =  'macho',
                    email =  'nonsonnabugwu911@gmail.com',
                    password =  'Macholina911#',
                    is_event_staff = True
                )
        
        data = {
                    "username": 'macho',
                    "email": 'nonsonnabugwu911@gmail.com',
                    "password": 'Macholina911#'
                }
        
        self.login = self.client.post('/api/auth/login/', data)
        self.assertEqual(self.login.status_code, status.HTTP_200_OK)
    def test_event(self):
        data = {
            "title": "Tech Fest 042",
            "description": "The biggest Tech Fest in 042",
            "location": "Enugu",
            "start_at": "2026-08-15T09:00:00Z",
            "end_at": "2026-08-15T15:00:00Z",
            "capacity": 2,
            "price": 10.00
            }
        headers = {
            'Authorization': f'Bearer {self.login.data["access"]}'
        }
        response = self.client.post('/api/create-event/', data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.is_event_staff, True)
        self.assertTrue(Event.objects.filter(title="Tech Fest 042").exists())

class TicketCapacityTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                            username =  'macho',
                            email =  'nonsonnabugwu911@gmail.com',
                            password =  'Macholina911#',
                            is_event_staff = True
                        )
                
        data = {
                    "username": 'macho',
                    "email": 'nonsonnabugwu911@gmail.com',
                    "password": 'Macholina911#'
                }

        self.event = Event.objects.create(
            title= "Tech Fest 042",
            description= "The biggest Tech Fest in 042",
            location= "Enugu",
            start_at= "2026-08-15T09:00:00Z",
            end_at= "2026-08-15T15:00:00Z",
            capacity= 0,
            created_by = self.user,
            price= 10.00
        )
                
        self.login = self.client.post('/api/auth/login/', data)
        self.assertEqual(self.login.status_code, status.HTTP_200_OK)
    def test_ticket(self):
        token = secrets.token_urlsafe(32) 
        buffer = io.BytesIO()
        ticket = Ticket.objects.create(
                            event = self.event,
                            owner = self.user,
                            qr_token = token
                        )
        ticket.qr_code.save(
            f'{token}.png',
            ContentFile(buffer.getvalue()),
            save = False
        ) 
        ticket.save()
        headers = {
                    'Authorization': f'Bearer {self.login.data["access"]}'
                }
        response = self.client.get('/api/create-ticket/',headers=headers)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)