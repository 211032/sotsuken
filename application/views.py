import asyncio
import re
from calendar import monthrange
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import render, redirect

from .ble_utils import scan_beacons
from .models import Student, Teacher, StudentClass, Subject, Enrollment  # modelsはDB


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


def login_android(request):
    error_message = None  # エラーメッセージ初期化

    if request.method == "POST":
        try:
            # POSTデータを取得
            body = json.loads(request.body.decode('utf-8'))
            email = body.get('email')
            password = body.get('password')

            # バリデーション: フィールドが空でないか確認
            if email and password:
                try:
                    student = Student.objects.get(email=email)
                    if student.password == password:
                        # セッションにメールアドレスを保存
                        request.session['student_email'] = student.email
                        request.session.modified = True
                        request.session.save()

                        print(f"Session Key (after creation): {request.session.session_key}")
                        print(f"Request Cookies: {request.COOKIES}")

                        return JsonResponse({
                            "message": "login successfully",
                            "success": True
                        })
                    else:
                        error_message = "パスワードが違います"  # パスワードが一致しない場合のエラーメッセージ
                except Student.DoesNotExist:
                    error_message = "メールアドレスが存在しません"  # メールアドレスが見つからない場合のエラーメッセージ
            else:
                error_message = "メールアドレスとパスワードを入力してください"  # フィールドが空の場合のエラーメッセージ
        except json.JSONDecodeError:
            error_message = "不正なリクエスト形式です"

    # セッション情報のデバッグ

    print(f"Session Key (after creation): {request.session.session_key}")
    print(f"Request Cookies: {request.COOKIES}")

    return JsonResponse({
        "message": error_message,
        "success": False
    })

def home(request):
    # セッションからメールアドレスを取得
    student_email = request.session.get('student_email')
    if student_email:
        try:
            student = Student.objects.get(email=student_email)
            student_class = StudentClass.objects.get(class_id=student.class_name_id)
            return render(request, 'home.html', {'student': student, 'student_class': student_class})
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

                request.session['roll'] = teacher.roll

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
            if teacher.roll == 0:  # 管理者ロールの場合
                return render(request, 'adomin_teacher_home.html', {'teacher': teacher})
            elif teacher.roll == 1:  # 教師ロールの場合
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
        alphabet_last_name = request.POST.get('alphabet_last_name')
        roll = request.POST.get('roll')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 必須フィールドのバリデーション
        if not all([teacher_id, name, alphabet_last_name, roll, password, confirm_password]):
            messages.error(request, "すべてのフィールドを入力してください。")
            return render(request, 'register_teacher.html')

        # `teacher_id`の重複チェック
        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            messages.error(request, "この講師IDは既に使用されています。")
            return render(request, 'register_teacher.html')

        if not re.match("[a-zA-Z\s.,]+", alphabet_last_name):
            messages.error(request, "ローマ字の姓にはローマ字を入力してください。")
            return render(request, 'register_teacher.html')

        # パスワードの確認
        if password != confirm_password:
            messages.error(request, "パスワードが一致しません。")
            return render(request, 'register_teacher.html')

        # 教師の登録処理（パスワードをハッシュ化）
        Teacher.objects.create(
            teacher_id=teacher_id,
            name=name,
            alphabet_last_name=alphabet_last_name,
            roll=int(roll),
            password=make_password(password)
        )
        messages.success(request, "講師が正常に登録されました。")
        return render(request, 'register_teacher.html')  # 登録成功ページ

    return render(request, 'register_teacher.html')


def register_student(request):
    teacherroll = request.session.get('roll')
    print(f"Roll value: {teacherroll}")
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
        return render(request, 'register_student.html', {'student_classes': StudentClass.objects.all()})
    return render(request, 'register_student.html', {'student_classes': StudentClass.objects.all()})

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


# 時間割登録機能に遷移する
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
            'classrooms': classrooms,
            'success_message': 'beacon登録成功！'
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
    if request.method == 'POST':
        student_email = request.POST.getlist('select_student')
        students = Student.objects.only('email', 'name').filter(email__in=student_email)

        if student_email is None or student_email == []:
            student_emails = request.POST.getlist('student')
            students = list(
                Student.objects.filter(email__in=student_emails).only('email', 'name').values('email', 'name'))

        enrollments = Enrollment.objects.only('subject_id').filter(
            instructor_id_id=request.session.get('teacher_id'))

        subjects = Subject.objects.filter(subject_id__in=enrollments.values('subject_id'))
        classrooms = Classroom.objects.all()

        if not (subjects.exists()):
            teachers = Teacher.objects.all()
            subjects = Subject.objects.all()
            student_class = StudentClass.objects.all()
            context = {
                'teachers': teachers,
                'subjects': subjects,
                'studentClass': student_class,
                'message': 'この教員に割り当てられている教科がありません。'
            }
            # リクエスト先をEnrollmentの登録ページに変える
            return render(request, 'register_admin_teacher_course.html', context)
        another = request.POST.get('another')
        if another == '教科の選択に戻る':
            selected_subjects_data = request.POST.get("selected_subjects")

            # JSON文字列をPythonのリストに変換
            try:
                selected_subjects = json.loads(selected_subjects_data)
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return render(request, 'error.html', {'message': 'Invalid subject data.'})

            another_subjects = []
            for subject in selected_subjects:
                print("Processing subject:", subject)
                print(subject['schedule'])
                subject_custom = {
                    'subject_id': subject['subject_id'],
                    'subject_name': Subject.objects.get(subject_id=subject['subject_id']).subject_name,
                    'classroom_id': subject['classroom_id'],
                    'classroom_name': Classroom.objects.get(classroom_id=subject['classroom_id']).classroom_name,
                    'date_first': subject['date_first'],
                    'date_last': subject['date_last'],
                    'schedule': json.dumps(subject['schedule']),  # JSON文字列に変換
                }
                another_subjects.append(subject_custom)

            return render(request, 'student_course_subject_registration.html',
                          {'students': students, 'subjects': subjects, 'classrooms': classrooms,
                           'another_subjects': another_subjects})

        return render(request, 'student_course_subject_registration.html',
                      {'students': students, 'subjects': subjects, 'classrooms': classrooms})


def student_course_subject_registration(request):
    if request.method == 'GET':
        return render(request, 'student_course_subject_registration.html')
    if request.method == 'POST':
        # POSTデータから生徒情報を取得
        student_emails = request.POST.getlist('student')

        students = list(Student.objects.filter(email__in=student_emails).only('email', 'name').values('email', 'name'))

        # POSTデータから選択された科目を取得
        selected_subjects_data = request.POST.get("selected_subjects")

        # JSON文字列をPythonのリストに変換
        try:
            selected_subjects = json.loads(selected_subjects_data)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return render(request, 'error.html', {'message': 'Invalid subject data.'})

        subjects = []
        for subject in selected_subjects:
            print("Processing subject:", subject)
            print(subject['schedule'])
            subject_custom = {
                'subject_id': subject['subject_id'],
                'subject_name': Subject.objects.get(subject_id=subject['subject_id']).subject_name,
                'classroom_id': subject['classroom_id'],
                'classroom_name': Classroom.objects.get(classroom_id=subject['classroom_id']).classroom_name,
                'date_first': subject['date_first'],
                'date_last': subject['date_last'],
                'schedule': json.dumps(subject['schedule']),  # JSON文字列に変換
            }
            subjects.append(subject_custom)

        # レンダリングするテンプレートにデータを渡す
        return render(request, 'student_course_comp_registration.html', {
            'students': students,
            'subjects': subjects
        })


def register_admin_teacher_course(request):
    if request.method == 'GET':
        teachers = Teacher.objects.all()
        subjects = Subject.objects.all()
        studentClass = StudentClass.objects.all()
        context = {
            'teachers': teachers,
            'subjects': subjects,
            'studentClass': studentClass
        }
        return render(request, 'register_admin_teacher_course.html', context)

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        subject_id = request.POST.get('subject')
        student_class_id = request.POST.get('studentClass')
        class_format = request.POST.get('classFormat')

        is_special_class = class_format == '1'

        if Enrollment.objects.filter(instructor_id=teacher_id,subject_id=subject_id).exists():
            return render(request, 'register_admin_teacher_course.html', {'message': 'この講師には既に選択された教科が割り当てられています。'})

        enrollment = Enrollment(
            instructor_id=Teacher.objects.get(teacher_id=teacher_id),
            subject=Subject.objects.get(subject_id=subject_id),
            class_identifier=StudentClass.objects.get(class_id=student_class_id),
            is_special_class=is_special_class
        )

        # 保存
        enrollment.save()

        return render(request, 'register_admin_teacher_course_complete.html')


def student_course_comp_registration(request):
    if request.method == 'GET':
        return render(request, 'student_course_comp_registration.html')

    if request.method == "POST":
        student_emails = request.POST.getlist('student')

        students = list(Student.objects.filter(email__in=student_emails).only('email', 'name').values('email', 'name'))

        selected_subjects_data = request.POST.get("selected_subjects")
        print(selected_subjects_data)

        # JSON文字列をPythonのリストに変換
        try:
            selected_subjects = json.loads(selected_subjects_data)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return render(request, 'error.html', {'message': 'Invalid subject data.'})

        try:
            with transaction.atomic():  # トランザクション処理で一括登録
                subjects = []
                for subject in selected_subjects:
                    print("Processing subject:", subject)
                    # 関連するモデルのインスタンスを取得
                    subject_instance = Subject.objects.get(subject_id=subject['subject_id'])
                    classroom_instance = Classroom.objects.get(classroom_id=subject['classroom_id'])

                    # Enrollmentテーブルに登録
                    # 講師やクラス識別子などを取得
                    enrollment = Enrollment.objects.get(instructor_id=request.session.get('teacher_id'),
                                                        subject_id=subject['subject_id'])

                    # 日数
                    date_first = datetime.strptime(subject['date_first'], '%Y-%m-%d')
                    date_last = datetime.strptime(subject['date_last'], '%Y-%m-%d')
                    distance = int((date_last - date_first).days)

                    # 曜日だけを取り出したリスト
                    days = list(set(item['day'] for item in subject['schedule']))

                    grouped_data = defaultdict(list)
                    for item in subject['schedule']:
                        grouped_data[item['day']].append(item)

                    for student in students:

                        for i in range(0, distance + 1):
                            date = date_first + timedelta(days=i)

                            date_obj = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")

                            weekday_index = date_obj.weekday()

                            # 曜日の名前を取得する (日本語や英語のリストを定義)
                            weekdays = ["月", "火", "水", "木", "金", "土", "日"]
                            weekday_name = weekdays[weekday_index]

                            # dateの曜日を取得しscheduleの曜日と突き合わせる
                            if weekday_name in days:
                                # 曜日が何個あるか数える
                                for day, periods in grouped_data.items():
                                    if day == weekday_name:
                                        day_sames = periods
                                for day_same in day_sames:
                                    # Attendanceテーブルに登録
                                    start_time = None
                                    end_time = None

                                    if enrollment.is_special_class:
                                        if day_same['period'] == '1':
                                            start_time = '9:15:00'
                                            end_time = '11:00:00'
                                        elif day_same['period'] == '2':
                                            start_time = '11:10:00'
                                            end_time = '12:40:00'
                                        elif day_same['period'] == '3':
                                            start_time = '13:30:00'
                                            end_time = '15:00:00'
                                        elif day_same['period'] == '4':
                                            start_time = '15:15:00'
                                            end_time = '16:45:00'
                                    else:

                                        if day_same['period'] == '1':
                                            start_time = '9:15:00'
                                            end_time = '10:45:00'
                                        elif day_same['period'] == '2':
                                            start_time = '11:00:00'
                                            end_time = '12:30:00'
                                        elif day_same['period'] == '3':
                                            start_time = '13:30:00'
                                            end_time = '15:00:00'
                                        elif day_same['period'] ==  '4':
                                            start_time = '15:15:00'
                                            end_time = '16:45:00'

                                    attendance = Attendance.objects.create(
                                        enrollment_id=enrollment.enrollment_id,
                                        classroom_id=subject['classroom_id'],
                                        start_time=start_time,
                                        end_time=end_time
                                    )

                                    # Timetableテーブルに登録または更新
                                    timetable, created = Timetable.objects.get_or_create(
                                        email=student['email'],
                                        date=date
                                    )
                                    # 適切な時限にAttendanceを設定
                                    if day_same['period'] == '1':
                                        timetable.period1_id = attendance.attendance_id
                                    elif day_same['period'] == '2':
                                        timetable.period2_id = attendance.attendance_id
                                    elif day_same['period'] == '3':
                                        timetable.period3_id = attendance.attendance_id
                                    elif day_same['period'] == '4':
                                        timetable.period4_id = attendance.attendance_id
                                    timetable.save()

                    # 表示用データに追加
                    subject_custom = {
                        'subject_id': subject_instance.subject_id,
                        'subject_name': subject_instance.subject_name,
                        'classroom_id': classroom_instance.classroom_id,
                        'classroom_name': classroom_instance.classroom_name,
                        'date_first': subject['date_first'],
                        'date_last': subject['date_last'],
                        'schedule': json.dumps(subject['schedule']),
                    }
                    subjects.append(subject_custom)
                    print(subjects)

                return render(request, 'student_course_ok.html', {'subjects': subjects, 'students': students})

        except Exception as e:
            print("Error saving data:", e)
            return render(request, 'error.html', {'message': e})

def student_course_ok(request):
    if request.method == 'POST':
        student_email = request.POST.getlist('student')

        students = Student.objects.only('email', 'name').filter(email__in=student_email)
        enrollments = Enrollment.objects.only('subject_id').filter(
            instructor_id_id=request.session.get('teacher_id'))

        subjects = Subject.objects.filter(subject_id__in=enrollments.values('subject_id'))
        classrooms = Classroom.objects.all()

        return render(request, 'student_course_subject_registration.html',
                      {'students': students, 'subjects': subjects, 'classrooms': classrooms})

def student_search(request):
    students = []
    student_classes = StudentClass.objects.all()
    if request.method == 'GET':
        student_all = Student.objects.all()
        for student in student_all:
            show_student = {
                'email': student.email,
                'name': student.name,
                'class_name': (StudentClass.objects.get(class_id=student.class_name_id)).class_name
            }
            students.append(show_student)
    return render(request, 'student_search.html',
                  {'students': students, 'student_classes': student_classes})


def student_attendance_confirmation(request):
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

        return render(request, 'student_attendance_confirmation.html',

                      {'students': students, 'student_classes': student_classes})

    if request.method == 'POST':

        email = request.POST.get('email')

        start_date = request.POST.get('start_date')

        end_date = request.POST.get('end_date')

        student = Student.objects.filter(email=email).first()

        # Timetableから条件に一致するデータを取得
        timetables = Timetable.objects.filter(
            email=email,
            date__range=[start_date, end_date]
        )

        # grouped_dataを辞書形式で構築
        grouped_data = defaultdict(dict)
        for timetable in timetables:
            grouped_data[str(timetable.date)] = {
                "period1": get_attendance_and_classroom(timetable.period1_id),
                "period2": get_attendance_and_classroom(timetable.period2_id),
                "period3": get_attendance_and_classroom(timetable.period3_id),
                "period4": get_attendance_and_classroom(timetable.period4_id),
            }

        # grouped_dataを普通の辞書に変換
        grouped_data = dict(grouped_data)

        # コンテキストに渡す
        context = {
            "grouped_data": grouped_data,
            "name": student.name,
            "start_date": start_date,
            "end_date": end_date,
        }
        return render(request, 'timetable_results.html', context)


def get_attendance_and_classroom(period_id):
    """
    指定されたperiod_idからAttendanceレコードと関連するClassroom情報を取得します。
    """
    attendance = Attendance.objects.filter(pk=period_id).first()
    if attendance:
        classroom = Classroom.objects.filter(classroom_id=attendance.classroom_id).first()
        enrollment = Enrollment.objects.filter(enrollment_id=attendance.enrollment_id).first()
        subject = Subject.objects.filter(subject_id=enrollment.subject_id).first()
        return {
            "id": attendance.attendance_id,
            "start_time": attendance.attendance_time,
            "end_time": attendance.exit_time,
            "status": attendance.attendance_status,
            "classroom": classroom.classroom_name if classroom else "未設定",
            "subject": subject.subject_name
        }
    return {

        "message": "空きコマ"
    }


def edit_attendance(request, attendance_id):
    # 出席状況編集のロジックをここに記述します
    request.session['attendance_id'] = attendance_id
    return render(request, 'edit_attendance.html')


def edit_attendance_course(request):
    if request.method == 'POST':
        # フォームデータから選択された出席状況を取得
        new_status = request.POST.get('edit')

        attendance_id = request.session.get('attendance_id', None)

        attendance = Attendance.objects.get(attendance_id=attendance_id)

        # attendance_status を更新
        attendance.attendance_status = new_status
        attendance.save()

        # 更新完了後にリダイレクト
        return redirect('adomin_teacher_home')


def student_change(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        student = request.POST.get('student_email')
        student = Student.objects.get(email=student)
        student_classes = StudentClass.objects.all()
        message = None
        if mode == 'delete':
            student.delete()
            Timetable.objects.filter(email=student.email).delete()
            students = []
            student_all = Student.objects.all()
            for target_student in student_all:
                show_student = {
                    'email': target_student.email,
                    'name': target_student.name,
                    'class_name': StudentClass.objects.get(class_id=target_student.class_name_id).class_name
                }
                students.append(show_student)
            return render(request, 'student_search.html', {'student_classes':student_classes, 'students':students, 'message': student.name+'は削除されました'})
        elif mode == 'change':
            change_mode = request.POST.get('radio')
            text = request.POST.getlist('text')
            if text[0] =='' and text[1] =='':
                message = '変更する値が不正です'
            else:
                if change_mode == 'name':
                    student.name = text[0]
                elif change_mode == 'class':
                    student.class_name_id = text[1]
                elif change_mode == 'password':
                    student.password = text[0]
                student.save()
                message = '正常に変更されました。'
        student = Student.objects.get(email=student.email)
        student = {
            'email': student.email,
            'name': student.name,
            'class_name': StudentClass.objects.get(class_id=student.class_name_id).class_name,
        }

        return render(request, 'student_change.html', {'student': student, 'student_classes':student_classes, 'message': message})



# import locale
#
# # ロケールを日本語に設定
# try:
#     locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
# except locale.Error:
#     locale.setlocale(locale.LC_TIME, "C")  # デフォルトロケール

# 日付を日本語形式にフォーマット
# def format_japanese_date(date):
#     if date:
#         return date.strftime("%Y年%m月%d日 (%a)")  # 例: "2025年01月20日 (月)"
#     return ""

def teacher_change(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        teacher = request.POST.get('teacher_id')
        teacher = Teacher.objects.get(teacher_id=teacher)
        message = None
        if mode == 'delete':
            teacher.delete()
            teachers = Teacher.objects.all()
            return render(request, 'student_search.html', {'teachers':teachers, 'message': teacher.name+'は削除されました'})
        elif mode == 'change':
            change_mode = request.POST.get('radio')
            text = request.POST.getlist('text')
            if text[0] == '' and text[1] == '' and text[2] == '':
                message = '変更に失敗しました。変更する値が空白でした'
            elif change_mode == 'name' and (not text[0] or not re.match("[a-zA-Z\s.,]+", text[1])):
                message = '変更に失敗しました。変更する値が不正です'
            elif change_mode == 'roll' and not text[2]:
                message = '変更に失敗しました。役割の値が空白でした'
            elif change_mode == 'password' and not text[0]:
                message = '変更に失敗しました。パスワードの値が空白でした'
            else:
                if change_mode == 'name':
                    teacher.name = text[0]
                    teacher.alphabet_last_name = text[1]
                elif change_mode == 'roll':
                    teacher.roll = text[2]
                elif change_mode == 'password':
                    teacher.password = text[0]
                teacher.save()
                message = '正常に変更されました。'
        teacher = Teacher.objects.get(teacher_id=teacher.teacher_id)
        return render(request, 'teacher_change.html', {'teacher': teacher, 'message': message})


# 時間を日本語形式にフォーマット
def format_time(time):
    if time:
        return time.strftime("%H:%M")  # e.g., "9:00"
    return ""


def monthly_schedule(request):
    student_email = request.session.get('student_email')
    if not student_email:
        return redirect('login')

    # クエリパラメータの取得
    month_offset = int(request.GET.get('month_offset', 0))  # 月単位でのオフセット
    search_date = request.GET.get('search_date', None)  # 特定の日付での検索
    current_date = datetime.now() + timedelta(days=30 * month_offset)
    current_month = current_date.month
    current_year = current_date.year

    # 月の開始日と終了日を計算
    month_start = datetime(current_year, current_month, 1)
    month_end = datetime(current_year, current_month, monthrange(current_year, current_month)[1])

    # 日付でのフィルタリング
    if search_date:
        try:
            search_date = datetime.strptime(search_date, '%Y-%m-%d').date()  # 入力された日付をパース
            timetables = Timetable.objects.filter(email=student_email, date=search_date).order_by('date')
        except ValueError:
            timetables = []  # 日付が不正な場合は空リストを返す
    else:
        timetables = Timetable.objects.filter(
            email=student_email,
            date__range=(month_start, month_end)
        ).order_by('date')

    # スケジュールデータの生成
    schedule = []
    for timetable in timetables:
        for period, period_field in enumerate(['period1', 'period2', 'period3', 'period4'], start=1):
            attendance = getattr(timetable, period_field, None)
            if attendance:
                subject = attendance.enrollment.subject
                classroom = attendance.classroom
                teacher = attendance.enrollment.instructor_id

                schedule.append({
                    'date': format_japanese_date(timetable.date),
                    'period': period,
                    'subject_name': subject.subject_name,
                    'classroom_name': classroom.classroom_name,
                    'teacher_name': teacher.name,
                    'start_time': format_time(attendance.start_time),
                    'end_time': format_time(attendance.end_time),
                    'attendance_time': format_time(attendance.attendance_time),  # 出席時間を追加
                    'exit_time': format_time(attendance.exit_time),  # 退席時間を追加
                })

    # テンプレートにデータを渡してレンダリング
    return render(request, 'monthly_schedule.html', {
        'schedule': schedule,
        'current_month': current_month,
        'current_year': current_year,
        'month_offset': month_offset,
        'search_date': search_date,  # 入力された日付を再度テンプレートに渡す
    })




def monthly_schedule_teacher(request):
    student_email = request.session.get('student_email')
    if not student_email:
        return redirect('login')

    # クエリパラメータの取得
    month_offset = int(request.GET.get('month_offset', 0))  # 月単位でのオフセット
    search_date = request.GET.get('search_date', None)  # 特定の日付での検索
    current_date = datetime.now() + timedelta(days=30 * month_offset)
    current_month = current_date.month
    current_year = current_date.year

    # 月の開始日と終了日を計算
    month_start = datetime(current_year, current_month, 1)
    month_end = datetime(current_year, current_month, monthrange(current_year, current_month)[1])

    # 日付でのフィルタリング
    if search_date:
        try:
            search_date = datetime.strptime(search_date, '%Y-%m-%d').date()  # 入力された日付をパース
            timetables = Timetable.objects.filter(email=student_email, date=search_date).order_by('date')
        except ValueError:
            timetables = []  # 日付が不正な場合は空リストを返す
    else:
        timetables = Timetable.objects.filter(
            email=student_email,
            date__range=(month_start, month_end)
        ).order_by('date')

    # スケジュールデータの生成
    schedule = []
    for timetable in timetables:
        for period, period_field in enumerate(['period1', 'period2', 'period3', 'period4'], start=1):
            attendance = getattr(timetable, period_field, None)
            if attendance:
                subject = attendance.enrollment.subject
                classroom = attendance.classroom
                teacher = attendance.enrollment.instructor_id

                schedule.append({
                    'date': format_japanese_date(timetable.date),
                    'period': period,
                    'subject_name': subject.subject_name,
                    'classroom_name': classroom.classroom_name,
                    'teacher_name': teacher.name,
                    'start_time': format_time(attendance.start_time),
                    'end_time': format_time(attendance.end_time),
                    'attendance_time': format_time(attendance.attendance_time),  # 出席時間を追加
                })

    # テンプレートにデータを渡してレンダリング
    return render(request, 'monthly_schedule.html', {
        'schedule': schedule,
        'current_month': current_month,
        'current_year': current_year,
        'month_offset': month_offset,
        'search_date': search_date,  # 入力された日付を再度テンプレートに渡す
    })



from .models import Equipment, Classroom, Timetable, Attendance
import json
from datetime import datetime, timedelta

from django.http import JsonResponse

def api(request):
    if request.method == "POST":
        try:
            # クライアントから送信されたデータを取得
            body = json.loads(request.body)
            minor = body.get("minor")
            email = body.get("email")

            if not minor:
                return JsonResponse({"error": "Minor not provided"}, status=400)

            # デバイス情報を取得
            equipment = Equipment.objects.get(minor=minor)
            classroom = Classroom.objects.get(classroom_id=equipment.location_id)

            # 今日の日付を取得
            today = datetime.now().date()

            # Timetableを検索
            timetable = Timetable.objects.filter(date=today, email=email).first()
            if not timetable:
                return JsonResponse({"error": "Timetable not found"}, status=404)

            # Attendanceの時間を更新
            current_time = datetime.now().time()
            attendance_updated = False

            for attendance_obj in [timetable.period1, timetable.period2, timetable.period3, timetable.period4]:
                if attendance_obj:
                    # 出席可能な時間範囲を計算
                    start_time = datetime.combine(today, attendance_obj.start_time)
                    end_time = datetime.combine(today, attendance_obj.end_time)
                    valid_start_time = start_time - timedelta(minutes=10)  # 開始10分前

                    # 現在時刻が有効範囲内であるか確認
                    if valid_start_time.time() <= current_time <= end_time.time():
                        if attendance_obj.attendance_time is not None:
                            print('既に出席登録済み')
                        else:
                            attendance_obj.attendance_time = current_time
                            attendance_obj.save()
                            print("出席時間を登録しました。")
                        attendance_updated = True
                        break
                    else:
                        print(f"時間外です: 現在時刻: {current_time}, 有効範囲: {valid_start_time.time()} - {end_time.time()}")

                    # 退席時間の登録
                    if current_time > end_time.time():
                        if attendance_obj.exit_time is None:
                            # 授業終了時間より遅い退出時間は登録しない
                            if current_time <= end_time.time():
                                attendance_obj.exit_time = current_time
                                attendance_obj.save()
                                print("退席時間を登録しました。")
                            else:
                                print(f"退席時間は授業終了時間を超えています: {current_time} > {end_time.time()}")

            if not attendance_updated:
                return JsonResponse({"error": "出席可能な時間範囲外です"}, status=400)

            student = Student.objects.get(email=email)
            # データを更新
            student.time = datetime.now().time()
            student.room = minor
            student.save()

            # レスポンスを作成
            return JsonResponse({
                "message": "出席登録に成功しました",
                "classroom_name": classroom.classroom_name,
                "equipment_location": equipment.location_id,
                "attendance_time": current_time.strftime("%H:%M:%S"),
            })
        except Equipment.DoesNotExist:
            return JsonResponse({"error": "Equipment not found"}, status=404)
        except Classroom.DoesNotExist:
            return JsonResponse({"error": "Classroom not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)


def attend_check(request):
    if request.method == "POST":
        try:
            # クライアントから送信されたデータを取得
            body = json.loads(request.body)
            minor = body.get("minor")
            email = body.get("email")
            print(email, minor)

            if not minor:
                return JsonResponse({"error": "Minor not provided"}, status=400)

            now = datetime.now()

            student = Student.objects.get(email=email)
            # 学生のtimeをdatetime型に変換（例として、今日の日付を使用）
            if student.time is not None:
                student_datetime = datetime.combine(now.date(), student.time)
                if (now - student_datetime) <= timedelta(seconds=90):
                    if student.room == str(minor):
                        data = {"message": "入室"}
                    else:
                        data = {"message": "入室"}
                else:
                    # 1分半以上通信がなかった場合、退席として登録
                    student.exit_time = now.time()
                    student.save()
                    data = {"message": "退出"}
            else:
                data = {"message": "error"}
            # データを更新
            student.time = datetime.now().time()
            student.room = minor
            student.save()

            # レスポンスを作成
            return JsonResponse(data)
        except Equipment.DoesNotExist:
            return JsonResponse({"error": "Equipment not found"}, status=404)
        except Classroom.DoesNotExist:
            return JsonResponse({"error": "Classroom not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)
