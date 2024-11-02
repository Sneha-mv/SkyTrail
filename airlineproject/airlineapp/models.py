from django.db import models
from django.core.exceptions import ValidationError

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
        # Check for duplicates within the same flight
        if Seat.objects.filter(flight=self.flight, seat_number=self.seat_number).exists():
            raise ValidationError(f"Seat number {self.seat_number} already exists for this flight.")

    def save(self, *args, **kwargs):
        self.clean()  # Call clean to ensure validation
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
    seat_number = models.CharField(max_length=5)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation for {self.passenger} on {self.flight}"


    

