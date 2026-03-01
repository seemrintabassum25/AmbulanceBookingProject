from django.contrib import admin
from .models import UserProfile, Ambulance, Booking, EmergencyContact

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    search_fields = ['user__username', 'phone_number']

@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'ambulance_type', 'driver_name', 'status']
    list_filter = ['status', 'ambulance_type']
    search_fields = ['vehicle_number', 'driver_name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'user', 'status', 'booking_time']
    list_filter = ['status']
    search_fields = ['patient_name', 'user__username']
    date_hierarchy = 'booking_time'

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'phone_number', 'relationship']
    search_fields = ['name', 'user__username']
