import json

from asgiref.sync import sync_to_async
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from .ble_utils import scan_beacons
from .models import Attendance, Student, Teacher, Classroom, Equipment, StudentClass, Subject  # modelsはDB
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
            alphabet_last_name=romanized_last_name,
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

        studentClass = StudentClass.objects.get(class_name=class_name)


        # 学生データの作成
        student = Student(
            email=email,
            name=name,
            class_name=studentClass,
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

#時間割登録機能に遷移する
def time_table(request):
    return render(request, 'time_table.html')

def subject_registration(request):
    return render(request, 'subject_registration.html')

def subject_registration_comp(request):
    if request.method == 'POST':
        subjectName = request.POST.get('subjectName')

        subject = Subject(subject_name=subjectName)
        subject.save()

        return render(request, 'subject_registration.html', {'message': '登録が完了しました!'})



# beacon登録
def register_beacon(request):
    # POSTリクエストでビーコンデータを登録
    if request.method == 'POST':
        location_id = request.POST.get('location')
        minor = request.POST.get('minor')

        # `minor` の重複チェック
        if Equipment.objects.filter(minor=minor).exists():
            messages.error(request, "このビーコンのminorはすでに登録されています。")
            # `redirect` ではなく `render` でエラーメッセージを表示
            classrooms = Classroom.objects.all()
            return render(request, 'register_beacon.html', {'classrooms': classrooms})

        # 教室の確認
        try:
            classroom = Classroom.objects.get(classroom_id=location_id)
        except Classroom.DoesNotExist:
            messages.error(request, "指定された教室が見つかりませんでした。")
            classrooms = Classroom.objects.all()
            return render(request, 'register_beacon.html', {'classrooms': classrooms})

        # ビーコンデータを保存
        Equipment.objects.create(
            location=classroom,
            minor=minor
        )

        classrooms = Classroom.objects.all()

        context = {
            'classrooms' : classrooms,
            'success_message' : 'beacon登録成功！'
        }

        return render(request, 'register_beacon.html', context)

    # GETリクエスト時は教室一覧を表示する
    classrooms = Classroom.objects.all()
    return render(request, 'register_beacon.html', {'classrooms': classrooms})


def student_course_registration(request):
    students = []
    student_classes = StudentClass.objects.all()
    if request.method == 'GET':
        number = 0
        student_all = Student.objects.all()
        for student in student_all:
            number += 1
            show_student = {
                'number': number,
                'email': student.email,
                'name': student.name,
                'class_name': StudentClass.objects.get(class_id=student.class_name_id).class_name
            }
            students.append(show_student)
        return render(request, 'student_course_registration.html',
                  {'students': students, 'student_classes': student_classes})
    if request.method== 'POST':
        student_email = request.POST.getlist('select_student')

        students = Student.objects.only('email','name').filter(email__in=student_email)
        subjects = Subject.objects.all()
        classrooms = Classroom.objects.all()

        return render(request, 'student_course_subject_registration.html',
                      {'students': students, 'subjects': subjects, 'classrooms': classrooms})

def student_course_subject_registration(request):
    if request.method == 'GET':
        return render(request, 'student_course_subject_registration.html')
    if request.method== 'POST':
        students = request.POST.getlist('students')
        subject = request.POST.getlist('subjects')
        subject_classroom = request.POST.getlist('subject_classroom')

        return  render(request, 'student_course_subject_registration.html')

def student_search(request):
    students = []
    student_classes = StudentClass.objects.all()
    if request.method == 'GET':
        student_all = Student.objects.all()
        for student in student_all:
            show_student = {
                'email': student.email,
                'name': student.name,
                'class_name': StudentClass.objects.get(class_id=student.class_name_id).class_name
            }
            students.append(show_student)
    return render(request, 'student_search.html',
                  {'students': students, 'student_classes': student_classes})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Equipment, Classroom
import json

@csrf_exempt
def api(request):
    if request.method == "POST":
        try:
            # クライアントから送信されたデータを取得
            body = json.loads(request.body)
            minor = body.get("minor")

            # デバイス情報を取得
            equipment = Equipment.objects.get(minor=minor)
            classroom = Classroom.objects.get(classroom_id=equipment.location_id)

            # レスポンスを作成
            return JsonResponse({
                "message": "Data processed successfully",
                "classroom_name": classroom.classroom_name,
                "equipment_location": equipment.location_id,
            })
        except Equipment.DoesNotExist:
            return JsonResponse({"error": "Equipment not found"}, status=404)
        except Classroom.DoesNotExist:
            return JsonResponse({"error": "Classroom not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
