# Generated by Django 4.2.16 on 2024-10-28 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.CharField(max_length=10, unique=True)),
                ('airline_name', models.CharField(max_length=100)),
                ('departure_city', models.CharField(max_length=50)),
                ('arrival_city', models.CharField(max_length=50)),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('available_seats', models.PositiveIntegerField()),
            ],
        ),
    ]
