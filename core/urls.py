from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book/', views.book_ambulance, name='book_ambulance'),
    path('track/', views.track_ambulance, name='track_ambulance'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('booking/<int:booking_id>/', views.booking_status, name='booking_status'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]