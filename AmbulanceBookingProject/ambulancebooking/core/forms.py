from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Booking, UserProfile, EmergencyContact


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['patient_name', 'patient_age', 'emergency_details',
                 'pickup_location', 'dropoff_location']
        widgets = {
            'patient_name': forms.TextInput(attrs={'id': 'id_patient_name', 'class': 'form-control'}),
            'patient_age': forms.NumberInput(attrs={'id': 'id_patient_age', 'class': 'form-control'}),
            'emergency_details': forms.Textarea(attrs={'id': 'id_emergency_details', 'class': 'form-control', 'rows': 3}),
            'pickup_location': forms.TextInput(attrs={'id': 'id_pickup_location', 'class': 'form-control'}),
            'dropoff_location': forms.TextInput(attrs={'id': 'id_dropoff_location', 'class': 'form-control'}),
        }


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'phone_number', 'relationship']