from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_student, name='login_student'),
    path('register/', views.register_view, name='register'),
    path('registercomp/', views.registercomp, name='registercomp'),
    path('beacon_connect/', views.beacon_connect, name='beacon_connect'),
    path('beacon_scan/', views.beacon_scan, name='beacon_scan'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),
    path('login/', views.login_student, name='login'),  # login_studentに変更
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),

]
