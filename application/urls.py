from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('register_comp/', views.register_comp, name='register_comp'),
    path('beacon_connect/', views.beacon_connect, name='beacon_connect'),
    path('beacon_scan/', views.beacon_scan, name='beacon_scan'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),
    path('login/', views.login_student, name='login'),  # login_studentに変更
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('login_teacher/', views.login_teacher, name='login_teacher'),  # login_studentに変更
    path('teacher_home/', views.teacher_home, name='teacher_home'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),

]
