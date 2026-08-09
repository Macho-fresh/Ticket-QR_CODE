from django.test import TestCase
from rest_framework.test import APITestCase
from .models import User
from rest_framework import status

class RegisterTest(APITestCase):
    def test_register(self):
        data = {
            "username": 'macho',
            "email": 'nonsonnabugwu911@gmail.com',
            "password": 'Macholina911#'
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(username='macho').exists()
        )

class LoginTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(
            username =  'macho',
            email =  'nonsonnabugwu911@gmail.com',
            password =  'Macholina911#'
        )

        data = {
                    "username": 'macho',
                    "email": 'nonsonnabugwu911@gmail.com',
                    "password": 'Macholina911#'
                }

        self.login = self.client.post('/api/auth/login/', data)   
        # print(self.login.data)

    def test_login(self):
        self.assertEqual(self.login.status_code, status.HTTP_200_OK)
        self.assertIn('access', self.login.data)
        self.assertIn('refresh', self.login.data)

     