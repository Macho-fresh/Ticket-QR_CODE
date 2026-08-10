from django.test import TestCase
from rest_framework.test import APITestCase
from accounts.models import User
from .models import *
from rest_framework import status
import io
from django.core.files.base import ContentFile
import secrets
from unittest.mock import patch, Mock

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

        self.reference = "test_reference_123"
        Payment.objects.create(
            reference=self.reference,
            user=self.user,
            amount = 10.00,
            event=self.event,
            status="pending"
        )
        
        self.login = self.client.post('/api/auth/login/', data)

        self.assertEqual(self.login.status_code, status.HTTP_200_OK)

    @patch("app.views.requests.get")    
    def test_ticket(self, mock_get):
        mock_response = Mock()

        mock_response.json.return_value = {
            "status": True,
            "data": {
                "status": "success",
                "reference": self.reference
            }
        }

        mock_get.return_value = mock_response
        token = secrets.token_urlsafe(32) 
        buffer = io.BytesIO()
        headers = {
                    'Authorization': f'Bearer {self.login.data["access"]}'
                }
        response = self.client.get(f'/api/create-ticket/?reference={self.reference}',headers=headers)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

# test event ended
class EventEndTest(APITestCase):
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
            start_at= "2026-08-08T09:00:00Z",
            end_at= "2026-08-08T15:00:00Z",
            capacity= 0,
            created_by = self.user,
            price= 10.00
        )
        
        self.login = self.client.post('/api/auth/login/', data)

        self.assertEqual(self.login.status_code, status.HTTP_200_OK)

    def test_end_event(self):
        headers = {
            'Authorization': f'Bearer {self.login.data["access"]}'
        }
        response = self.client.post('/api/payment/', {"event_id": 1}, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ViewEvents(APITestCase):
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
    def test_view_event(self):
        headers = {
                    'Authorization': f'Bearer {self.login.data["access"]}'
                }
        response = self.client.get('/api/view-events/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EditEventTest(APITestCase):
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

    def test_edit_event(self):
        data = {
            "title": "Tech Fest 042",
            "description": "The biggest Tech Fest in 042",
            "location": "Enugu",
            "start_at": "2026-08-15T09:00:00Z",
            "end_at": "2026-08-15T15:00:00Z",
            "capacity": 0,
            "price": 10.00
        } 
        headers = {
            'Authorization': f'Bearer {self.login.data["access"]}'
        }
        response = self.client.patch('/api/edit-events/1/', data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    # -----------------------------------------------------------------------
    def test_non_owner_cannot_edit_event(self):

        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='OtherPassword123!',
            is_event_staff = True
        )

        login = self.client.post(
            '/api/auth/login/',
            {
                'username': 'otheruser',
                'password': 'OtherPassword123!'
            }
        )
        # print(login.data)
        headers = {
            'Authorization': f'Bearer {login.data["access"]}'
        }

        data = {
            "title": "Hacked Event",
            "description": "Trying to modify someone else's event",
            "location": "Lagos",
            "start_at": "2026-08-15T09:00:00Z",
            "end_at": "2026-08-15T15:00:00Z",
            "capacity": 0,
            "price": 10.00
        }

        response = self.client.patch(
            '/api/edit-events/1/',
            data,
            headers=headers
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )