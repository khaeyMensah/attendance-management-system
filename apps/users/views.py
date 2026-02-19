from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from apps.users.forms import LoginForm, RegisterForm

# Create your views here.
def home(request):
    return render(request, 'users/dashboard.html')
    # return render(request, 'base.html')
    # return render(request, 'authentication/registration_pending.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm(request)
    return render(request, 'users/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

def student_dashboard_view(request):
    return render(request, 'users/dashboard.html')

def lecturer_dashboard_view(request):
    return render(request, 'users/dashboard.html')