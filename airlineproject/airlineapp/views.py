from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Flight, Passenger, Reservation, Seat

# Create your views here.
def index(request):
    flights = None  
    search_attempted = False 
    if request.method == 'POST':
        departure_city = request.POST.get('departure_city')
        arrival_city = request.POST.get('arrival_city')
        travel_date = request.POST.get('travel_date')

        # Search for flights based on form inputs
        flights = Flight.objects.filter(
            departure_city__icontains=departure_city,
            arrival_city__icontains=arrival_city,
            departure_time__date=travel_date
        )
        search_attempted = True  
    return render(request, 'index.html', {'flights': flights,'search_attempted': search_attempted,})


def flight_detail(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    seats = Seat.objects.filter(flight=flight)
    # Sort seats by seat_number in ascending numeric order
    seats = sorted(seats, key=lambda seat: int(seat.seat_number))
    return render(request, 'flight_detail.html', {'flight': flight, 'seats': seats})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Flight, Seat, Passenger, Reservation
from django.contrib import messages

def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        selected_seats = request.POST.getlist('seat_numbers')  # Get list of selected seat numbers

        # Check availability of all selected seats
        unavailable_seats = []
        for seat_number in selected_seats:
            seat = Seat.objects.filter(flight=flight, seat_number=seat_number, is_available=True).first()
            if not seat:
                unavailable_seats.append(seat_number)

        if unavailable_seats:
            messages.error(request, f"The following seats are already booked: {', '.join(unavailable_seats)}.")
        else:
            passenger = Passenger.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )

            for seat_number in selected_seats:
                seat = Seat.objects.get(flight=flight, seat_number=seat_number)
                seat.is_available = False
                seat.save()
                
                reservation = Reservation.objects.create(
                    flight=flight,
                    passenger=passenger,
                    seat_number=seat_number
                )

            messages.success(request, "Tickets booked successfully!")
            return redirect('airlineapp:index')

    # Get available seats for the flight
    available_seats = Seat.objects.filter(flight=flight, is_available=True)
    return render(request, 'book_ticket.html', {'flight': flight, 'available_seats': available_seats})



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        
        errors = {}
        if User.objects.filter(username=username).exists():
            errors['username_error'] = 'Username already exists. Please choose another one.'
        if User.objects.filter(email=email).exists():
            errors['email_error'] = 'Email already registered. Please use another email.'
        if len(password) < 8:
            errors['password_length_error'] = 'Password must be at least 8 characters long.'
        if password != cpassword:
            errors['password_mismatch'] = 'Passwords do not match.'
        if errors:
            return render(request, 'register.html', errors)

        # Create a new user with hashed password
        user = User(username=username, email=email, password=make_password(password))
        user.save()
        return redirect('airlineapp:login')  
    return render(request, 'register.html')


def login(request):
    user = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        errors = {}
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            errors['email_error'] = 'Email not found. Please try again.'
        if user and not authenticate(username=user.username, password=password):
            errors['password_error'] = 'Incorrect password. Please try again.'
        if errors:
            return render(request, 'login.html', {'errors': errors})
        
        auth_login(request, user)
        return redirect('airlineapp:index')  
    return render(request, 'login.html')


def logout_view(request):
    logout(request) 
    messages.success(request, 'You have been logged out successfully.') 
    return redirect('airlineapp:login') 


def change_password(request):
    errors = {}  
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = User.objects.get(email=email)
            if new_password != confirm_password:
                errors['confirm_password_error'] = "Passwords do not match."
            elif len(new_password) < 8:
                errors['new_password_error'] = "Password must be at least 8 characters long."
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been successfully updated!")
                return redirect('airlineapp:login')  
        except User.DoesNotExist:
            errors['email_error'] = "Email not found. Please try again."
    return render(request, 'change_password.html', {'errors': errors})


def print_ticket(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    return render(request, 'print_ticket.html', {'reservation': reservation})

def cancel_ticket(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    seat = Seat.objects.get(flight=reservation.flight, seat_number=reservation.seat_number)
    seat.is_available = True
    seat.save()
    reservation.delete()
    messages.success(request, "Reservation canceled successfully.")
    return redirect('airlineapp:index')





