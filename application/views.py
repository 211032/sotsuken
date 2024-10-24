from django.shortcuts import render, redirect
from .models import Student, teacher  # データベースのStudentモデルをインポート
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from .models import Attendance
import asyncio
from . import ble_utils


# Create your views here.
def index(request):
    return render(request, 'index.html')  # トップページを表示

def login_student(request):  # ログインページのビュー
    error_message = None

    if request.method == "POST":
        email = request.POST.get('email')  # フォームからメールアドレスを取得
        password = request.POST.get('password')  # フォームからパスワードを取得

        # バリデーション: フィールドが空でないか確認
        if email and password:
            try:
                student = Student.objects.get(email=email)
                if student.password == password:
                    # セッションにメールアドレスを保存
                    request.session['student_email'] = student.email
                    return redirect('home')  # ホーム画面にリダイレクト
                else:
                    error_message = "パスワードが違います"  # パスワードが一致しない場合のエラーメッセージ
            except Student.DoesNotExist:
                error_message = "メールアドレスが存在しません"  # メールアドレスが見つからない場合のエラーメッセージ
        else:
            error_message = "メールアドレスとパスワードを入力してください"  # フィールドが空の場合のエラーメッセージ

    return render(request, 'login.html', {'error_message': error_message})

def home(request):
    # セッションからメールアドレスを取得
    student_email = request.session.get('student_email')
    if student_email:
        try:
            student = Student.objects.get(email=student_email)
            return render(request, 'home.html', {'student': student})
        except Student.DoesNotExist:
            return redirect('login')  # 学生が存在しない場合はログイン画面にリダイレクト
    else:
        return redirect('login')  # ログインしていない場合はログイン画面にリダイレクト

def logout(request):
    return render(request, 'login.html')  # トップページを表示

def login_teacher(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            Teacher = teacher.objects.get(teacher_id=username, password=password)
            request.session['teacher_id'] = Teacher.id # idをセッションに保持
            if Teacher.roll == 0:
                return redirect(request,'adomin_teacher_home.html')
            elif Teacher.roll == 1:
                return redirect(request,'teacher_home.html')
        except teacher.DoesNotExist:
            error_message = "ユーザーが見つかりませんでした。"
            return render(request, '/', {'error_message': error_message})

    return render(request, 'login.html')# ログアウト時の画面へのURLを指定
def teacher_home(request):
    return render(request, 'teacher_home.html')

def adomin_teacher_home(request):
    return render(request, 'adomin_teacher_home.html')




def register_view(request):

    return render(request, 'accountReg.html')

def register_comp(request):
    if request.method == 'POST':
        name = request.POST.get('student_name')
        email = request.POST.get('student_mail')
        class_name = request.POST.get('student_class')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # パスワード確認
        if password != confirm_password:
            messages.error(request, "パスワードが一致しません。")
            return render(request, 'accountReg.html', {'messages': messages.get_messages(request)})

        # メールアドレスの重複チェック
        if Student.objects.filter(email=email).exists():
            messages.error(request, "このメールアドレスはすでに使用されています。")
            return render(request, 'accountReg.html', {'messages': messages.get_messages(request)})

        # 学生データの作成
        student = Student(
            email=email,
            name=name,
            class_name=class_name,
            password=password  # パスワードをハッシュ化
        )
        student.save()  # データベースに保存

        messages.success(request, "アカウントが正常に登録されました。")
        return render(request, 'RegComplete.html')
    return render(request, 'accountReg.html')

async def beacon_connect(request):
    return render(request, 'beacon_connect.html')

def attendance_confirmation(request):

    attendances = Attendance.objects.filter(student_id=request.user.id)
    return render(request, 'attendance_confirmation.html', {'attendances': attendances})

def teacher_submit(request):
    return render(request, 'teacher_submit.html')

async def beacon_scan(request):
    devices = await ble_utils.scan_beacons()  # 特定のUUIDに一致するデバイスをスキャン
    return JsonResponse({'devices': devices})  # デバイス情報を返す



