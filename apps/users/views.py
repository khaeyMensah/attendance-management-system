from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from apps.users.forms import LoginForm, RegisterForm


# Create your views here.
def home(request):
    return render(request, 'users/dashboard.html')
    # return render(request, 'base.html')
    # return render(request, 'authentication/registration_pending.html')


def register_options(request):
    """Present role selection before registration."""
    return render(request, 'accounts/register_options.html')


def register_view(request):
    # allow role to be preselected via query param or POST
    role = request.GET.get('role') or request.POST.get('role')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        # if role provided, initialize the form with that role
        if role:
            form = RegisterForm(initial={'role': role})
        else:
            form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': role})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def student_dashboard_view(request):
    return render(request, 'users/dashboard.html')


@login_required
def lecturer_dashboard_view(request):
    return render(request, 'users/dashboard.html')