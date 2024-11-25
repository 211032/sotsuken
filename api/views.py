from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from application.models import Attendance, Equipment, Classroom
import json

@csrf_exempt
def register_beacon(request):
    """ビーコン情報をサーバーに登録するAPI"""
    if request.method == "POST":
        try:
            # JSONデータを読み取る
            data = json.loads(request.body)
            minor = data.get('minor')  # minor値
            location = data.get('location')  # 教室名

            if not (minor and location):
                return JsonResponse({"error": "データが不足しています"}, status=400)

            # 教室が存在するか確認
            classroom = Classroom.objects.filter(classroom_name=location).first()
            if not classroom:
                return JsonResponse({"error": "教室が見つかりません"}, status=404)

            # Equipmentテーブルにビーコンデータを登録または更新
            beacon, created = Equipment.objects.update_or_create(
                minor=minor,
                defaults={"location": classroom}
            )

            status = "新規作成" if created else "更新"
            return JsonResponse({"message": f"ビーコン情報を{status}しました"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON形式が正しくありません"}, status=400)

    return JsonResponse({"error": "POSTメソッドのみ対応しています"}, status=405)

def get_attendance_status(request, student_email):
    """特定の生徒の出席データを取得するAPI"""
    if request.method == "GET":
        try:
            # Attendanceモデルから生徒の出席データを取得
            student_attendances = Attendance.objects.filter(student__email=student_email)
            data = [
                {
                    "attendance_id": att.attendance_id,
                    "status": att.attendance_status,
                    "classroom": att.classroom.classroom_name,
                    "time": att.attendance_time,
                }
                for att in student_attendances
            ]
            return JsonResponse({"attendances": data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "GETメソッドのみ対応しています"}, status=405)

def get_beacons(request):
    """
    登録済みのビーコン情報を取得するAPI
    """
    try:
        # クエリパラメータの取得
        minor = request.GET.get('minor')  # GETパラメータ "minor"
        location_id = request.GET.get('location_id')  # GETパラメータ "location_id"

        # 条件に応じてフィルタリング
        if minor and location_id:
            beacons = Equipment.objects.filter(minor=minor, location__id=location_id)
        elif minor:
            beacons = Equipment.objects.filter(minor=minor)
        elif location_id:
            beacons = Equipment.objects.filter(location__id=location_id)
        else:
            beacons = Equipment.objects.all()  # すべてのビーコンを取得

        # データをシリアライズしてJSON形式で返す
        data = [
            {
                "device_id": beacon.id,
                "minor": beacon.minor,
                "location_id": beacon.location.id,
                "location_name": beacon.location.classroom_name
            }
            for beacon in beacons
        ]
        return JsonResponse({"beacons": data}, status=200)

    except Exception as e:
        # エラーハンドリング
        return JsonResponse({"error": str(e)}, status=500)

