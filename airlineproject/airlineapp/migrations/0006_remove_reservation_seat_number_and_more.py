# Generated by Django 4.2.16 on 2024-11-04 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlineapp', '0005_reservation_cancellation_deadline_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='seat_number',
        ),
        migrations.AddField(
            model_name='reservation',
            name='seat_number',
            field=models.ManyToManyField(to='airlineapp.seat'),
        ),
    ]
