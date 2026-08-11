from django.test import TestCase
from rest_framework.test import APITestCase
from accounts.models import User
from .models import *
from rest_framework import status
import io
from django.core.files.base import ContentFile
import secrets
from unittest.mock import patch, Mock
from django.utils import timezone

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

class DeleteEventTest(APITestCase):
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

    def test_delete_event(self):
        
        headers = {
            'Authorization': f'Bearer {self.login.data["access"]}'
        }
        response = self.client.delete('/api/delete-event/1/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ------------------------------------------------------
    def test_non_owner_cannot_delete_event(self):
    
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
            headers = {
                'Authorization': f'Bearer {login.data["access"]}'
            }
    
    
            response = self.client.delete(
                '/api/delete-event/1/',
                headers=headers
            )
    
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND
            )
    
class ViewTicketsTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='macho',
            email='macho@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='TestPassword123!'
        )
        
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

    def test_authenticated_user_can_view_tickets(self):
        self.client.force_authenticate(user=self.user)
        token = secrets.token_urlsafe(32) 
        buffer = io.BytesIO()

        Ticket.objects.create(
            event = self.event,
            owner = self.user,
            qr_token = token
        )

        response = self.client.get('/api/view-tickets/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(len(response.data), 1)

    def test_user_only_sees_their_own_tickets(self):
        self.client.force_authenticate(user=self.user)
        token = secrets.token_urlsafe(32)
        token2 = secrets.token_urlsafe(32) 

        buffer = io.BytesIO()

        Ticket.objects.create(
            event = self.event,
            owner = self.user,
            qr_token = token
        )

        Ticket.objects.create(
            event = self.event,
            owner = self.other_user,
            qr_token = token2
        )

        response = self.client.get('/api/view-tickets/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(len(response.data), 1)

        print(response.data[0]['owner'])
        self.assertEqual(
            response.data[0]['owner'],
            self.user.id
        )

    def test_unauthenticated_user_cannot_view_tickets(self):
        response = self.client.get('/api/view-tickets/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_user_with_no_tickets_gets_empty_list(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/view-tickets/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data,
            []
        )

class ViewOneTicketTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='macho',
            email='macho@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='TestPassword123!'
        )
        
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

    def test_authenticated_user_can_view_ticket(self):
        self.client.force_authenticate(user=self.user)
        token = secrets.token_urlsafe(32) 
        buffer = io.BytesIO()

        Ticket.objects.create(
            event = self.event,
            owner = self.user,
            qr_token = token
        )

        response = self.client.get('/api/view-one-ticket/1/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_non_owner_cannot_view_ticket(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get('/api/view-one-ticket/1/')
        
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

class GetAttendeesTest(APITestCase):
    def setUp(self):
            self.user = User.objects.create_user(
                username='macho',
                email='macho@example.com',
                password='TestPassword123!',
                is_event_staff = True
            )
    
            self.other_user = User.objects.create_user(
                username='other',
                email='other@example.com',
                password='TestPassword123!',
                is_event_staff = True

            )
            
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
            token = secrets.token_urlsafe(32) 


            Ticket.objects.create(
                event = self.event,
                owner = self.user,
                qr_token = token
            )
    def test_get_attendees(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/get-attendees/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_get_attendees(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get('/api/get-attendees/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 


class GetAttendeesCSVTest(APITestCase):
    def setUp(self):
            self.user = User.objects.create_user(
                username='macho',
                email='macho@example.com',
                password='TestPassword123!',
                is_event_staff = True
            )
    
            self.other_user = User.objects.create_user(
                username='other',
                email='other@example.com',
                password='TestPassword123!',
                is_event_staff = True

            )
            
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
            token = secrets.token_urlsafe(32) 


            Ticket.objects.create(
                event = self.event,
                owner = self.user,
                qr_token = token
            )
    def test_get_attendees_csv(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/get-attendees-csv/1/')
        self.assertIn('text/csv', response['Content-Type'])
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        

    def test_non_owner_cant_get_attendees_csv(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get('/api/get-attendees-csv/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 

class Checkin(APITestCase):
    def setUp(self):
                self.user = User.objects.create_user(
                    username='macho',
                    email='macho@example.com',
                    password='TestPassword123!',
                    is_event_staff = True
                )
        
                self.other_user = User.objects.create_user(
                    username='other',
                    email='other@example.com',
                    password='TestPassword123!',
                    is_event_staff = True
    
                )
                
                self.event1 = Event.objects.create(
                    title= "Tech Fest 042",
                    description= "The biggest Tech Fest in 042",
                    location= "Enugu",
                    start_at= "2026-08-08T09:00:00Z",
                    end_at= "2026-08-08T15:00:00Z",
                    capacity= 0,
                    created_by = self.other_user,
                    price= 10.00
                )
                
                self.event2 = Event.objects.create(
                    title= "Tech Fest 042",
                    description= "The biggest Tech Fest in 042",
                    location= "Enugu",
                    start_at= timezone.now(),
                    end_at= "2026-08-15T15:00:00Z",
                    capacity= 0,
                    created_by = self.user,
                    price= 10.00
                )
                self.token = secrets.token_urlsafe(32) 
                self.token2 = secrets.token_urlsafe(32) 

    
    
                self.ticket1 = Ticket.objects.create(
                    event = self.event2,
                    owner = self.user,
                    qr_token = self.token,
                    checked_in = False
                )

                self.ticket2 = Ticket.objects.create(
                    event = self.event1,
                    owner = self.other_user,
                    qr_token = self.token2,
                    checked_in = True
                )

    def test_event_ended_and_checked_in(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(f'/api/check-in/{self.token2}/')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_check_in(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/check-in/{self.token}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)