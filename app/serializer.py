from rest_framework import serializers
from .models import *

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['owner', 'checked_in']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'