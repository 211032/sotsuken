from .models import Equipment, Classroom
from asgiref.sync import sync_to_async

@sync_to_async
def get_classroom_name(minor):
    equipment = Equipment.objects.get(minor=minor)
    classroom_name = Classroom.objects.get(classroom_id=equipment.location_id).classroom_name

    return classroom_name