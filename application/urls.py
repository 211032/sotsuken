from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('register_student/', views.register_student, name='register_student'),
    path('beacon_connect/', views.beacon_connect, name='beacon_connect'),
    path('beacon_scan/', views.scan_beacon, name='beacon_scan'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),
    path('login/', views.login_student, name='login'),  # login_studentに変更
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),

    path('login_teacher/', views.login_teacher, name='login_teacher'),  # login_studentに変更
    path('teacher_home/', views.teacher_home, name='teacher_home'),
    path('adomin_teacher_home/', views.adomin_teacher_home, name='adomin_teacher_home'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),
    path('register-teacher/', views.register_teacher, name='register_teacher'),
    path('teacher-registration-success/', views.registration_success, name='teacher_registration_success')

]
