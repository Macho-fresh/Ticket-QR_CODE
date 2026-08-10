from .views import *
from django.urls import path

urlpatterns = [
    path('create-event/', CreateEvent.as_view()),
    path('create-ticket/', CreateTicket.as_view()),
    path('view-events/', ViewEvents.as_view()),
    path('edit-events/<int:id>/', EditEvents.as_view()),
    path('delete-event/<int:id>/', DeleteEvent.as_view()),
    path('view-tickets/', ViewTickets.as_view()),
    path('view-one-ticket/<int:id>/', ViewOneTicket.as_view()),
    path('get-attendees/<int:id>/', GetAttendees.as_view()),
    path('get-attendees-csv/<int:id>/', GetAttendeesCSV.as_view()),
    path('check-in/<str:token>/', CheckIn.as_view()),
    path('payment/', PaymentView.as_view())
]
