from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, BloodStock, BloodRequest, Donation
from django.contrib.auth.models import User
from django.db.models import Sum

def home(request):
    return render(request, 'blood_bank/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get('role', 'DONOR')
            profile = user.profile
            profile.role = role
            profile.blood_group = request.POST.get('blood_group')
            profile.location = request.POST.get('location')
            profile.contact = request.POST.get('contact')
            profile.save()
            login(request, user)
            messages.success(request, f"Account created for {user.username}!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'blood_bank/register.html', {'form': form})

@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == 'ADMIN' or request.user.is_superuser:
        total_donors = Profile.objects.filter(role='DONOR').count()
        total_units = BloodStock.objects.aggregate(Sum('units'))['units__sum'] or 0
        pending_requests = BloodRequest.objects.filter(status='PENDING').count()
        stock = BloodStock.objects.all()
        return render(request, 'blood_bank/admin_dashboard.html', {
            'total_donors': total_donors,
            'total_units': total_units,
            'pending_requests': pending_requests,
            'stock': stock,
            'requests': BloodRequest.objects.all().order_by('-request_date')[:10],
            'donations': Donation.objects.all().order_by('-donation_date')[:10]
        })
    else:
        user_requests = BloodRequest.objects.filter(requester=request.user).order_by('-request_date')
        user_donations = Donation.objects.filter(donor=request.user).order_by('-donation_date')
        return render(request, 'blood_bank/user_dashboard.html', {
            'profile': profile,
            'user_requests': user_requests,
            'user_donations': user_donations
        })


@login_required
def request_blood(request):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units = int(request.POST.get('units'))
        reason = request.POST.get('reason')
        
        BloodRequest.objects.create(
            requester=request.user,
            blood_group=blood_group,
            units=units,
            reason=reason
        )
        messages.success(request, "Blood request submitted successfully!")
        return redirect('dashboard')
    
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return render(request, 'blood_bank/request_blood.html', {'blood_groups': blood_groups})

@login_required
def search_donors(request):
    blood_group = request.GET.get('blood_group')
    location = request.GET.get('location')
    donors = Profile.objects.filter(role='DONOR')
    
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if location:
        donors = donors.filter(location__icontains=location)
        
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return render(request, 'blood_bank/search.html', {
        'donors': donors,
        'blood_groups': blood_groups
    })

@login_required
def manage_request(request, request_id, action):
    # Permission Check
    is_admin = request.user.is_superuser
    if not is_admin:
        try:
            if request.user.profile.role != 'ADMIN':
                messages.error(request, "Permission denied.")
                return redirect('dashboard')
        except Exception:
            messages.error(request, "Admin profile not found.")
            return redirect('dashboard')

    # Get Request
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    
    if action == 'approve':
        # Get or Create stock to avoid 404/errors
        stock, created = BloodStock.objects.get_or_create(blood_group=blood_request.blood_group)
        
        if stock.units >= blood_request.units:
            stock.units -= blood_request.units
            stock.save()
            blood_request.status = 'APPROVED'
            blood_request.save()
            messages.success(request, f"Approved {blood_request.units} units of {blood_request.blood_group}.")
        else:
            messages.error(request, f"Insufficient stock! Available: {stock.units}")
            
    elif action == 'reject':
        blood_request.status = 'REJECTED'
        blood_request.save()
        messages.info(request, "Request rejected.")
        
    return redirect('dashboard')



@login_required
def donate_blood(request):
    if not request.user.profile.blood_group:
        messages.error(request, "Please update your blood group in your profile before donating.")
        return redirect('dashboard')

    if request.method == 'POST':
        units = int(request.POST.get('units'))
        Donation.objects.create(
            donor=request.user,
            blood_group=request.user.profile.blood_group,
            units=units
        )
        messages.success(request, "Donation submitted! Awaiting admin approval.")
        return redirect('dashboard')
    return render(request, 'blood_bank/donate_blood.html')


@login_required
def manage_donation(request, donation_id, action):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')):
        return redirect('dashboard')
        
    donation = get_object_or_404(Donation, id=donation_id)
    if action == 'approve':
        stock, created = BloodStock.objects.get_or_create(blood_group=donation.blood_group)
        stock.units += donation.units
        stock.save()
        donation.status = 'APPROVED'
        donation.save()
        messages.success(request, f"Donation approved! {donation.units} units added to {donation.blood_group}.")
    elif action == 'reject':
        donation.status = 'REJECTED'
        donation.save()
        messages.info(request, "Donation rejected.")
    return redirect('dashboard')


@login_required
def update_stock(request):

    if not (request.user.profile.role == 'ADMIN' or request.user.is_superuser):
        return redirect('dashboard')
        
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units = int(request.POST.get('units'))
        stock = BloodStock.objects.get(blood_group=blood_group)
        stock.units += units
        stock.save()
        messages.success(request, f"Added {units} units to {blood_group} stock.")
        return redirect('dashboard')
