from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .forms import LoginForm, ClientProfileForm
from .models import ClientProfile

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Check if user is redirected from another page
                next_url = request.GET.get('next', 'dashboard:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    """Display and update user profile"""
    try:
        profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        profile = ClientProfile(user=request.user)
        profile.save()
    
    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ClientProfileForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {'form': form})

# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """API endpoint to get user profile info"""
    try:
        profile = request.user.client_profile
        data = {
            'username': request.user.username,
            'email': request.user.email,
            'company_name': profile.company_name,
            'contact_email': profile.contact_email,
            'contact_phone': profile.contact_phone,
        }
        return Response(data)
    except ClientProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)