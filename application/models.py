from tkinter.constants import CASCADE

from django.db import models

class Student(models.Model):
    email = models.EmailField(primary_key=True)  # メールアドレス
    class_name = models.CharField(max_length=100)  # クラス名
    name = models.CharField(max_length=100)  # 学生の名前
    password = models.CharField(max_length=128)  # パスワード

class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)  # 講師ID（自動で増加する）
    name = models.CharField(max_length=100)  # 講師の名前
    password = models.CharField(max_length=128)  # ハッシュ化されたパスワードを保存
    romanized_last_name = models.CharField(max_length=100)  # 講師のローマ字の姓
    roll = models.IntegerField()  # 役割



class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)  # 科目ID
    subject_name = models.CharField(max_length=100)  # 科目名


class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)  # 履修ID
    instructor_id = models.ForeignKey('Teacher',on_delete=models.CASCADE)  # 講師ID（外部キーとして講師モデルを追加するのが望ましい）
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)  # 科目ID（外部キー）
    class_identifier = models.CharField(max_length=50)  # クラス識別

class Classroom(models.Model):
    classroom_id = models.CharField(max_length=50,primary_key=True)
    classroom_name = models.CharField(max_length=10, unique=True)


class Attendance(models.Model):
    attendance_id = models.CharField(max_length=50, primary_key=True)  # 出欠IDを文字列型の主キーに設定
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE)  # 履修ID（外部キー）
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE)  # 教室ID（外部キー）
    student = models.ForeignKey('Student', on_delete=models.CASCADE)  # 学籍番号（メールアドレスの外部キー）
    period = models.IntegerField()  # 何限
    start_time = models.TimeField()  # 授業開始時間
    end_time = models.TimeField()  # 授業終了時間
    attendance_time = models.TimeField(null=True, blank=True)  # 出席時間（生徒）
    exit_time = models.TimeField(null=True, blank=True)  # 退出時間（生徒）
    attendance_status = models.CharField(max_length=20, choices=[
        ('present', '出席'),
        ('absent', '欠席'),
        ('late', '遅刻'),
        ('leave_early', '早退'),
        ('not_attended', '退席'),
    ])

class Timetable(models.Model):
    email = models.EmailField(primary_key=True)  # メールアドレス
    date = models.DateField()  # 日にち
    period1 = models.ForeignKey('Attendance', related_name='timetable_period1', on_delete=models.SET_NULL, null=True, blank=True)  # 1コマ目
    period2 = models.ForeignKey('Attendance', related_name='timetable_period2', on_delete=models.SET_NULL, null=True, blank=True)  # 2コマ目
    period3 = models.ForeignKey('Attendance', related_name='timetable_period3', on_delete=models.SET_NULL, null=True, blank=True)  # 3コマ目
    period4 = models.ForeignKey('Attendance', related_name='timetable_period4', on_delete=models.SET_NULL, null=True, blank=True)  # 4コマ目
    is_special_class = models.BooleanField(default=False)

    class Meta:
        unique_together = (('email', 'date'),)  # emailとdateの複合キー設定


class Equipment(models.Model):
    device_id = models.CharField(max_length=10,primary_key=True)  # 機器IDを主キーに設定
    location = models.ForeignKey('Classroom',on_delete=models.CASCADE)  # 場所
    minor = models.IntegerField()

