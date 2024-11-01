from django.shortcuts import render, redirect
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from .ble_utils import scan_beacons
from .models import Attendance,Student,Teacher #modelsはDB
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
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Teacher モデルの取得
            teacher = Teacher.objects.get(teacher_id=username)

            # 入力されたパスワードと保存されている平文のパスワードを直接比較
            if teacher.password == password:
                # teacher_idをセッションに保持
                request.session['teacher_id'] = teacher.teacher_id

                # ロールに応じてリダイレクト
                if teacher.roll == 0:  # 管理者ロールの場合
                    return redirect('adomin_teacher_home')
                elif teacher.roll == 1:  # 教師ロールの場合
                    return redirect('teacher_home')
            else:
                error_message = "パスワードが違います"  # パスワードが一致しない場合
        except Teacher.DoesNotExist:
            error_message = "ユーザーが見つかりませんでした"  # ユーザーが存在しない場合

    return render(request, 'login_teacher.html', {'error_message': error_message})


def teacher_home(request):
    # Retrieve teacher_id from session
    teacher_id = request.session.get('teacher_id')
    teacher = None

    if teacher_id:
        try:
            # Fetch the teacher object using the teacher_id from the session
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            return render(request, 'teacher_home.html', {'teacher': teacher})
        except teacher.DoesNotExist:
            # If teacher is not found, redirect to the login page
            return redirect('login_teacher')
    else:
        # If no teacher_id in session, redirect to the login page
        return redirect('login_teacher')


def adomin_teacher_home(request):
    # Retrieve teacher_id from session
    teacher_id = request.session.get('teacher_id')
    teacher = None

    if teacher_id:
        try:
            # Fetch the teacher object using the teacher_id from the session
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            return render(request, 'adomin_teacher_home.html', {'teacher': teacher})
        except teacher.DoesNotExist:
            # If teacher is not found, redirect to the login page
            return redirect('login_teacher')
    else:
        # If no teacher_id in session, redirect to the login page
        return redirect('login_teacher')

def register_view(request):
    return render(request, 'accountReg.html')

def register_teacher(request):
    if request.method == 'POST':
        # フォームデータを取得
        teacher_id = request.POST.get('teacher_id')
        name = request.POST.get('name')
        romanized_last_name = request.POST.get('romanized_last_name')
        roll = request.POST.get('roll')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 必須フィールドのバリデーション
        if not all([teacher_id, name, romanized_last_name, roll, password, confirm_password]):
            messages.error(request, "すべてのフィールドを入力してください。")
            return render(request, 'register_teacher.html')

        # `teacher_id`の重複チェック
        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            messages.error(request, "この教師IDは既に使用されています。")
            return render(request, 'register_teacher.html')

        # パスワードの確認
        if password != confirm_password:
            messages.error(request, "パスワードが一致しません。")
            return render(request, 'register_teacher.html')

        # 教師の登録処理（パスワードをハッシュ化）
        Teacher.objects.create(
            teacher_id=teacher_id,
            name=name,
            romanized_last_name=romanized_last_name,
            roll=int(roll),
            password=make_password(password)
        )

        messages.success(request, "教師が正常に登録されました！")
        return redirect('teacher_registration_success')  # 登録成功ページにリダイレクト

    return render(request, 'register_teacher.html')

def registration_success(request):
    return render(request, 'registration_success.html')

def register_student(request):
    if request.method == 'POST':
        name = request.POST.get('student_name')
        email = request.POST.get('student_mail')
        class_name = request.POST.get('student_class')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # パスワード確認
        if password != confirm_password:
            messages.error(request, "パスワードが一致しません。")
            return render(request, 'register_student.html', {'messages': messages.get_messages(request)})

        # メールアドレスの重複チェック
        if Student.objects.filter(email=email).exists():
            messages.error(request, "このメールアドレスはすでに使用されています。")
            return render(request, 'register_student.html', {'messages': messages.get_messages(request)})

        # 学生データの作成
        student = Student(
            email=email,
            name=name,
            class_name=class_name,
            password=password  # パスワードをハッシュ化
        )
        student.save()  # データベースに保存

        messages.success(request, "生徒が正常に登録されました。")
        return render(request, 'register_student.html')
    return render(request, 'register_student.html')

async def beacon_connect(request):
    return render(request, 'beacon_connect.html')


async def async_scan():
    return await scan_beacons()

def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'teacher_list.html', {'teachers': teachers})


def scan_beacon(request):
    # 非同期でBLEビーコンをスキャン
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    devices = loop.run_until_complete(async_scan())

    # 期待するJSON形式でデバイス情報を返す
    response_data = {'devices': devices}
    return JsonResponse(response_data)
def attendance_confirmation(request):

    attendances = Attendance.objects.filter(student_id=request.user.id)
    return render(request, 'attendance_confirmation.html', {'attendances': attendances})

def teacher_submit(request):
    return render(request, 'teacher_submit.html')





