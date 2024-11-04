from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Flight, Passenger, Reservation, Seat
from django.utils import timezone

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


def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        selected_seats = request.POST.getlist('seat_numbers')

        if not selected_seats:
            messages.error(request, "No seats selected. Please select at least one seat.")
            return redirect('airlineapp:book_ticket', flight_id=flight.id)

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if not first_name or not last_name or not email or not phone_number:
            messages.error(request, "All fields are required.")
            return redirect('airlineapp:book_ticket', flight_id=flight.id)

        if len(phone_number) != 10 or not phone_number.isdigit():
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return redirect('airlineapp:book_ticket', flight_id=flight.id)

        existing_passenger = Passenger.objects.filter(email=email).first()
        if existing_passenger:
            if existing_passenger.first_name == first_name and existing_passenger.last_name == last_name:
                messages.error(request, "This email is already registered with your name.")
                return redirect('airlineapp:book_ticket', flight_id=flight.id) 
            passenger = existing_passenger 
        else:
            passenger = Passenger.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )

        # Check availability of all selected seats
        unavailable_seats = []
        reservation_instances = []
        for seat_number in selected_seats:
            seat = Seat.objects.filter(flight=flight, seat_number=seat_number, is_available=True).first()
            if not seat:
                unavailable_seats.append(seat_number)

        if unavailable_seats:
            messages.error(request, f"The following seats are already booked: {', '.join(unavailable_seats)}")
            return redirect('airlineapp:book_ticket', flight_id=flight.id)
        else:
            reservation = Reservation.objects.create(
                flight=flight,
                passenger=passenger
            )
            for seat_number in selected_seats:
                seat = Seat.objects.get(flight=flight, seat_number=seat_number)
                seat.is_available = False
                seat.save()

                reservation.seat_number.add(seat) 
            request.session['reservation_id'] = reservation.id
            return redirect('airlineapp:print_ticket', reservation_id=reservation.id)

    available_seats = Seat.objects.filter(flight=flight, is_available=True)
    return render(request, 'book_ticket.html', {'flight': flight, 'available_seats': available_seats})


def print_ticket(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    flight = reservation.flight
    passenger = reservation.passenger

    seat_numbers = reservation.seat_number.all()  
    selected_seat_numbers = [str(seat.seat_number) for seat in seat_numbers] 

    price_per_seat = flight.price
    total_price = price_per_seat * len(seat_numbers)

    context = {
        'reservation': reservation,
        'passenger': passenger,
        'flight': flight,
        'seat_numbers': selected_seat_numbers,
        'total_price': total_price,
    }
    return render(request, 'print_ticket.html', context)


def cancel_booking(request, reservation_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to cancel a booking.")
        return redirect('airlineapp:login')  

    reservation = get_object_or_404(Reservation, id=reservation_id)
    if reservation.passenger.email != request.user.email:
        messages.error(request, "You do not have permission to cancel this reservation.")
        return redirect('airlineapp:print_ticket', reservation_id=reservation.id)  

    # Check if the cancellation deadline has passed
    if reservation.cancellation_deadline < timezone.now():
        messages.error(request, "The cancellation deadline has passed.")
    else:
        for seat in reservation.seat_number.all():
            seat.is_available = True
            seat.save()

        reservation.is_cancelled = True
        reservation.save()  

        messages.success(request, "Your reservation and all selected seats have been successfully canceled.")
    return redirect('airlineapp:print_ticket', reservation_id=reservation.id)


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


