from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Ambulance, Booking, UserProfile
from .forms import UserRegisterForm, BookingForm, EmergencyContactForm


def home(request):
    """Home page view"""
    available_ambulances = Ambulance.objects.filter(status='available').count()
    return render(request, 'core/home.html', {'available_ambulances': available_ambulances})


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data.get('phone_number')
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def book_ambulance(request):
    """Book ambulance view"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user

            # Find available ambulance (simplified logic)
            available_ambulance = Ambulance.objects.filter(status='available').first()

            if available_ambulance:
                booking.ambulance = available_ambulance
                booking.status = 'pending'
                booking.estimated_arrival = timezone.now() + timedelta(minutes=15)
                booking.save()

                # Update ambulance status
                available_ambulance.status = 'on_trip'
                available_ambulance.save()

                messages.success(request, 'Ambulance booked successfully!')
                return redirect('booking_status', booking_id=booking.id)
            else:
                messages.error(request, 'No ambulances available at the moment. Please try again.')
    else:
        form = BookingForm()

    return render(request, 'core/book_ambulance.html', {'form': form})


@login_required
def track_ambulance(request):
    """Track ambulance view"""
    try:
        # Get user's active bookings
        active_bookings = Booking.objects.filter(
            user=request.user,
            status__in=['pending', 'accepted', 'en_route']
        ).order_by('-booking_time')

        # Get all ambulances
        ambulances = Ambulance.objects.all()

        context = {
            'active_bookings': active_bookings,
            'ambulances': ambulances,
        }
        return render(request, 'core/track_ambulance.html', context)
    except Exception as e:
        # If any error occurs, still try to render template with empty context
        return render(request, 'core/track_ambulance.html', {
            'active_bookings': [],
            'ambulances': []
        })

@login_required
def booking_status(request, booking_id):
    """View booking status"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'core/booking_status.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()

        # Free up the ambulance
        if booking.ambulance:
            booking.ambulance.status = 'available'
            booking.ambulance.save()

        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel booking at this stage.')

    return redirect('booking_status', booking_id=booking.id)


@login_required
def dashboard(request):
    """User dashboard"""
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')[:10]
    context = {
        'user_bookings': user_bookings,
        'total_bookings': Booking.objects.filter(user=request.user).count(),
        'pending_bookings': Booking.objects.filter(user=request.user, status='pending').count(),
        'completed_bookings': Booking.objects.filter(user=request.user, status='completed').count(),
    }
    return render(request, 'core/dashboard.html', context)


# Admin views (simplified for beginners)
@login_required
def admin_dashboard(request):
    """Admin dashboard - only accessible by superusers"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')

    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    available_ambulances = Ambulance.objects.filter(status='available').count()

    recent_bookings = Booking.objects.all().order_by('-booking_time')[:10]
    ambulances = Ambulance.objects.all()

    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'available_ambulances': available_ambulances,
        'recent_bookings': recent_bookings,
        'ambulances': ambulances,
    }
    return render(request, 'core/admin_dashboard.html', context)
def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')
