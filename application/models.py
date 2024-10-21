from django.db import models

class Student(models.Model):
    email = models.EmailField(primary_key=True)  # メールアドレス
    class_name = models.CharField(max_length=100)  # クラス名
    name = models.CharField(max_length=100)  # 学生の名前
    password = models.CharField(max_length=128)  # パスワード
