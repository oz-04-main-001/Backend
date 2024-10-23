from datetime import datetime, time

from django.db import migrations, models
from django.utils import timezone


def convert_time_to_datetime(apps, schema_editor):
    Room = apps.get_model("rooms", "Room")
    for room in Room.objects.all():
        if room.check_in_time:
            room.check_in_time = timezone.make_aware(datetime.combine(timezone.now().date(), room.check_in_time))
        if room.check_out_time:
            room.check_out_time = timezone.make_aware(datetime.combine(timezone.now().date(), room.check_out_time))
        room.save()


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="check_in_time_temp",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="room",
            name="check_out_time_temp",
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(convert_time_to_datetime),
        migrations.RemoveField(
            model_name="room",
            name="check_in_time",
        ),
        migrations.RemoveField(
            model_name="room",
            name="check_out_time",
        ),
        migrations.RenameField(
            model_name="room",
            old_name="check_in_time_temp",
            new_name="check_in_time",
        ),
        migrations.RenameField(
            model_name="room",
            old_name="check_out_time_temp",
            new_name="check_out_time",
        ),
    ]
