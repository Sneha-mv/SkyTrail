from django.urls import path
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Flight, Passenger, Reservation, Seat

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'password_display')

    def password_display(self, obj):
        return '********'
    password_display.short_description = 'Password'  

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/change-password/',
                self.admin_site.admin_view(self.change_password),
                name='custom_change_password',
            ),
        ]
        return custom_urls + urls

    def change_password(self, request, user_id):
        user = User.objects.get(pk=user_id)
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            if new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, f"The password for {user.username} has been successfully changed.")
                
    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.is_superuser:
            return ['password']
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if change and 'password' in form.cleaned_data and not obj.is_superuser:
            original_user = User.objects.get(pk=obj.pk)
            obj.password = original_user.password
        super().save_model(request, obj, form, change)

# Unregister and register the custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline_name', 'departure_city', 'arrival_city', 'departure_time', 'arrival_time', 'price', 'available_seats')
    list_filter = ('airline_name', 'departure_city', 'arrival_city', 'departure_time')
    search_fields = ('flight_number', 'airline_name', 'departure_city', 'arrival_city')
    ordering = ('departure_time',)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name',)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('flight', 'seat_number', 'is_available')
    list_filter = ('flight', 'is_available')
    search_fields = ('flight__flight_number', 'seat_number')
    ordering = ('flight', 'seat_number')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('passenger', 'flight', 'display_seat_numbers', 'booking_date', 'is_cancelled')
    list_filter = ('is_cancelled',)
    search_fields = ('passenger__first_name', 'flight__flight_number')
    ordering = ('-booking_date',)

    def display_seat_numbers(self, obj):
        """Display all seat numbers associated with the reservation as a comma-separated list."""
        return ", ".join(seat.seat_number for seat in obj.seat_number.all())
    
    display_seat_numbers.short_description = "Seat Numbers"


