from tkinter.font import names

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('register_student/', views.register_student, name='register_student'),
    # path('beacon_connect/', views.beacon_connect, name='beacon_connect'),
    # path('beacon_scan/', views.scan_beacon, name='beacon_scan'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),
    path('login/', views.login_student, name='login'),  # login_studentに変更
    path('login_android/', views.login_android, name='login_android'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('login_teacher/', views.login_teacher, name='login_teacher'),  # login_studentに変更
    path('teacher_home/', views.teacher_home, name='teacher_home'),
    path('adomin_teacher_home/', views.adomin_teacher_home, name='adomin_teacher_home'),
    path('attendance_confirmation/', views.attendance_confirmation, name='attendance_confirmation'),
    path('register-teacher/', views.register_teacher, name='register_teacher'),
    path('teacher-registration-success/', views.registration_success, name='teacher_registration_success'),
    path('teacher_list/', views.teacher_list, name='teacher_list'),  # 教師一覧ページ
    path('time_table/', views.time_table, name='time_table'), #時間割登録機能にとぶ
    path('subject_registration/', views.subject_registration, name='course_registration'), #科目登録機能にとぶ
    path('student_course_registration/', views.student_course_registration, name='student_course_registration'),
    path('register_admin_teacher_course/', views.register_admin_teacher_course, name='register_admin_teacher_course'),
    path('student_course_subject_registration/', views.student_course_subject_registration, name='student_course_subject_registration'),
    path('student_course_comp_registration/', views.student_course_comp_registration, name='student_course_comp_registration'),
    path('student_course_ok/', views.student_course_ok, name='student_course_ok'),
    path('student_search/', views.student_search, name='student_search'),
    path('register_beacon/', views.register_beacon, name='register_beacon'),  # ビーコン登録ページへのパス
    path('course_registration_comp/', views.subject_registration_comp, name='course_registration_comp'),
    path('monthly_schedule/', views.monthly_schedule, name='monthly_schedule'),
    path('monthly_schedule_teacher/', views.monthly_schedule_teacher,name='monthly_schedule_teacher'),
    path('api/',views.api, name='api'),
    path('student_attendance_confirmation/', views.student_attendance_confirmation, name='student_attendance_confirmation')

]
