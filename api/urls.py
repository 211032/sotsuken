from django.urls import path
from . import views

urlpatterns = [
    path('register_beacon/', views.register_beacon, name='register_beacon'),
    path('beacons/', views.get_beacons, name='get-beacons'),

]