from django.db import models

class Student(models.Model):
    email = models.EmailField(primary_key=True)  # メールアドレス
    class_name = models.CharField(max_length=100)  # クラス名
    name = models.CharField(max_length=100)  # 学生の名前
    password = models.CharField(max_length=128)  # パスワード


class teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)  # 講師ID（自動で増加する）
    name = models.CharField(max_length=100)  # 講師の名前
    password = models.CharField(max_length=128)  # ハッシュ化されたパスワードを保存
    romanized_last_name = models.CharField(max_length=100)  # 講師のローマ字の姓
    roll = models.CharField(max_length=50)  # 役割
