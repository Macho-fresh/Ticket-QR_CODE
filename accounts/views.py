from django.shortcuts import render
from .models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        User.objects.create_user(
            username = username,
            email = email,
            password = password
        )
        return Response({
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_event_staff == True