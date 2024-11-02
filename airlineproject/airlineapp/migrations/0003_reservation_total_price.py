# Generated by Django 4.2.16 on 2024-11-02 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlineapp', '0002_passenger_seat_reservation'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
    ]