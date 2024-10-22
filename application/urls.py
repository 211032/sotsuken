from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('beconconect/', views.beacon_connect, name='beacon_connect'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),
]
