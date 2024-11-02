from django.urls import path
from .import views


app_name='airlineapp'

urlpatterns = [
    path('',views.index,name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('book/<int:flight_id>/', views.book_ticket, name='book_ticket'),
    path('print_ticket/<int:reservation_id>/', views.print_ticket, name='print_ticket'),
    path('cancel/<int:reservation_id>/', views.cancel_ticket, name='cancel_ticket'),
]