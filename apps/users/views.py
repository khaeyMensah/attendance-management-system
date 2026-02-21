from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from apps.users.decorators import role_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail

from apps.users.forms import LoginForm, RegisterForm
from apps.users.tokens import account_activation_token
from apps.users.models import User


# Create your views here.
def home(request):
    # If user is authenticated, redirect them to their role dashboard
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', None)
        if role == 'student':
            return redirect('users:student_dashboard')
        if role == 'lecturer':
            return redirect('users:lecturer_dashboard')
        if role == 'admin':
            return redirect('admin:index')
    # Unauthenticated users see the public landing (base template default hero)
    return render(request, 'base.html')
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
            user = form.save(commit=False)
            # mark inactive until email verification
            user.is_active = False
            user.save()
            # send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your ClassMark account.'
            message = render_to_string('authentication/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
            send_mail(mail_subject, message, from_email, [user.email], fail_silently=False)
            return redirect('users:registration_pending')
    else:
        # if role provided, initialize the form with that role
        if role:
            form = RegisterForm(initial={'role': role})
        else:
            form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': role})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # Log the user in after activation and redirect to role dashboard
        login(request, user)
        if user.role == 'student':
            return redirect('users:student_dashboard')
        if user.role == 'lecturer':
            return redirect('users:lecturer_dashboard')
        return redirect('home')
    else:
        return render(request, 'authentication/activation_invalid.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # redirect to role-specific dashboard
            if user.role == 'student':
                return redirect('users:student_dashboard')
            if user.role == 'lecturer':
                return redirect('users:lecturer_dashboard')
            return redirect('home')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
@role_required('student')
def student_dashboard_view(request):
    return render(request, 'users/student_dashboard.html')
    # return render(request, 'users/dashboard.html')


@login_required
@role_required('lecturer')
def lecturer_dashboard_view(request):
    return render(request, 'users/lecturer_dashboard.html')


@login_required
@role_required('admin')
def admin_dashboard_view(request):
    return render(request, 'users/admin_dashboard.html')