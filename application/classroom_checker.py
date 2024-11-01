from .models import Equipment
from asgiref.sync import sync_to_async

@sync_to_async
def get_classroom_name(minor):
    equipment = Equipment.objects.get(minor=minor)

    return equipment.location