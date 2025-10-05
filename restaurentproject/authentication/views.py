from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "in nam sabt shode ast!")
            return redirect('register')
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        messages.success(request, f"خوش آمدی، {username}!") 
        return redirect('index') 
    return render(request, 'authentication/register.html') 
    

def login_view(request):
    if request.method == 'POST': 
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'اطلاعات ورود نادرست است.')
    return render(request, 'authentication/login.html')


def logout_view(request):
    logout(request)
    return redirect('index') 