from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Ambulance(models.Model):
    AMBULANCE_TYPES = [
        ('basic', 'Basic Ambulance'),
        ('advanced', 'Advanced Ambulance'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('maintenance', 'Maintenance'),
    ]

    vehicle_number = models.CharField(max_length=20, unique=True)
    ambulance_type = models.CharField(max_length=20, choices=AMBULANCE_TYPES)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    current_location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle_number} - {self.get_ambulance_type_display()}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('en_route', 'En Route'),
        ('arrived', 'Arrived'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    ambulance = models.ForeignKey(Ambulance, on_delete=models.SET_NULL, null=True, blank=True)

    # Patient details
    patient_name = models.CharField(max_length=100)
    patient_age = models.IntegerField(null=True, blank=True)
    emergency_details = models.TextField()

    # Location details
    pickup_location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=200, blank=True, null=True)

    # Booking details
    booking_time = models.DateTimeField(default=timezone.now)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Tracking
    current_location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.patient_name}"


class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
