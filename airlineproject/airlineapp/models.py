from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Flight(models.Model):
    flight_number = models.CharField(max_length=10, unique=True)
    airline_name = models.CharField(max_length=100)
    departure_city = models.CharField(max_length=50)
    arrival_city = models.CharField(max_length=50)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.airline_name} - {self.flight_number}"


class Seat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=5)
    is_available = models.BooleanField(default=True)

    def clean(self):
        if not self.is_available and Reservation.objects.filter(flight=self.flight, seat_number=self.seat_number).exists():
            raise ValidationError(f'Seat number {self.seat_number} already exists for this flight.')

    def save(self, *args, **kwargs):
        # Only call clean on booking, not during cancellation
        if not self.is_available:
            self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Seat {self.seat_number} - {('Available' if self.is_available else 'Booked')}"
    

class Passenger(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Reservation(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seat_number = models.ManyToManyField(Seat)  
    booking_date = models.DateTimeField(auto_now_add=True)
    cancellation_deadline = models.DateTimeField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        for seat in self.seat_number.all():
            # Check for existing reservations for the same seat that are not canceled
            if Reservation.objects.filter(flight=self.flight, seat_number=seat, is_cancelled=False).exists():
                raise ValidationError(f'Seat number {seat.seat_number} already exists for this flight.')

    def save(self, *args, **kwargs):
        if not self.cancellation_deadline:
            self.cancellation_deadline = self.flight.departure_time - timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation for {self.passenger} on {self.flight}"

   
    