# Generated by Django 5.1.2 on 2024-10-23 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0003_booking_guests_count_alter_booking_total_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="booker_name",
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="booking",
            name="booker_phone_number",
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="booking",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("confirmed", "Confirmed"),
                    ("paid", "Paid"),
                    ("partially_paid", "Partially Paid"),
                    ("check_in", "Checked In"),
                    ("check_out", "Checked Out"),
                    ("cancelled_by_guest", "Cancelled by Guest"),
                    ("cancelled_by_host", "Cancelled by Host"),
                    ("no_show", "No Show"),
                    ("refunded", "Refunded"),
                    ("completed", "Completed"),
                ],
                default="pending",
                max_length=30,
            ),
        ),
    ]
