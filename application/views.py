from django.shortcuts import render
from django.http import  HttpResponse

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def beacon_connect(request):
    return render(request, 'beacon_connect.html')

def attendance_confirmation(request):
    return render(request, 'attendance_confirmation.html')

def teacher_submit(request):
    return render(request, 'teacher_submit.html')