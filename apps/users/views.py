from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging
from apps.users.decorators import role_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction, IntegrityError, DataError
from django.db.models import Count, Q
from django.urls import reverse
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from django.utils import timezone

from apps.users.forms import LoginForm, RegisterForm
from apps.users.tokens import account_activation_token
from apps.users.models import User
from apps.courses.models import Course, Enrollment
from apps.attendance.models import AttendanceRecord, Session

logger = logging.getLogger(__name__)
ADMIN_INVITE_SALT = 'users.admin_invite'
ADMIN_INVITE_MAX_AGE = getattr(settings, 'ADMIN_INVITE_MAX_AGE', 60 * 60 * 24 * 7)


def _send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your ClassMark account.'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    activation_url = f"{'https' if request.is_secure() else 'http'}://{current_site.domain}"
    activation_url += reverse('users:activate', kwargs={'uidb64': uid, 'token': token})
    context = {
        'user': user,
        'domain': current_site.domain,
        'protocol': 'https' if request.is_secure() else 'http',
        'uid': uid,
        'token': token,
        'activation_url': activation_url,
    }
    text_message = render_to_string('authentication/acc_active_email.txt', context)
    html_message = render_to_string('authentication/acc_active_email.html', context)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
    email = EmailMultiAlternatives(mail_subject, text_message, from_email, [user.email])
    email.attach_alternative(html_message, 'text/html')
    email.send(fail_silently=False)


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
            return redirect('users:admin_dashboard')
    # Unauthenticated users see the public landing (base template default hero)
    return render(request, 'base.html')
    # return render(request, 'authentication/registration_pending.html')


def register_options(request):
    """Present role selection before registration."""
    return render(request, 'accounts/register_options.html')


def _prepare_admin_register_form(form, invited_email=None):
    form.fields['role'].choices = [('admin', 'Admin')]
    form.fields['role'].initial = 'admin'
    if invited_email:
        form.fields['email'].initial = invited_email
        form.fields['email'].widget.attrs['readonly'] = True
    return form


def registration_pending(request):
    pending_email = request.session.get('pending_activation_email')
    return render(
        request,
        'authentication/registration_pending.html',
        {'pending_email': pending_email},
    )


def register_view(request):
    # allow role to be preselected via query param or POST
    role = request.GET.get('role') or request.POST.get('role')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()
            except (IntegrityError, DataError) as exc:
                error_text = str(exc)
                if 'users_user_username_key' in error_text:
                    form.add_error('username', 'This username is already taken.')
                elif 'users_user_email_key' in error_text:
                    form.add_error('email', 'This email is already registered.')
                elif 'users_user_student_id_key' in error_text:
                    form.add_error('identification', 'This student ID is already registered.')
                elif 'users_user_staff_id_key' in error_text:
                    form.add_error('identification', 'This staff ID is already registered.')
                elif 'value too long' in error_text.lower():
                    form.add_error('identification', 'The ID entered is too long for the selected role.')
                else:
                    form.add_error(None, 'A duplicate record was detected. Please use different details.')
            except Exception as exc:
                logger.exception('Registration email send failed for %s', form.cleaned_data.get('email'))
                messages.error(
                    request,
                    f'We could not send your verification email right now: {exc}',
                )
            else:
                request.session['pending_activation_email'] = user.email
                try:
                    _send_activation_email(request, user)
                except Exception:
                    logger.exception('Activation email send failed after registration for %s', user.email)
                    messages.warning(
                        request,
                        'Account created, but we could not send the activation email. Use resend.',
                    )
                else:
                    messages.info(request, 'Activation email sent. Please check your inbox.')
                return redirect('users:registration_pending')
    else:
        # if role provided, initialize the form with that role
        if role:
            form = RegisterForm(initial={'role': role})
        else:
            form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': role})


def admin_register_view(request, token):
    try:
        payload = signing.loads(token, salt=ADMIN_INVITE_SALT, max_age=ADMIN_INVITE_MAX_AGE)
    except (BadSignature, SignatureExpired):
        messages.error(request, 'This admin invite link is invalid or expired.')
        return redirect('users:register_options')

    invited_email = (payload.get('email') or '').strip().lower() or None

    if request.method == 'POST':
        form = _prepare_admin_register_form(RegisterForm(request.POST), invited_email=invited_email)
        if form.is_valid():
            if invited_email and form.cleaned_data['email'].strip().lower() != invited_email:
                form.add_error('email', 'This invite is restricted to a specific email address.')
            else:
                try:
                    with transaction.atomic():
                        user = form.save(commit=False)
                        user.role = 'admin'
                        user.is_active = False
                        user.save()
                except IntegrityError as exc:
                    error_text = str(exc)
                    if 'users_user_username_key' in error_text:
                        form.add_error('username', 'This username is already taken.')
                    elif 'users_user_email_key' in error_text:
                        form.add_error('email', 'This email is already registered.')
                    else:
                        form.add_error(None, 'A duplicate record was detected. Please use different details.')
                except Exception as exc:
                    logger.exception('Admin registration email send failed for %s', form.cleaned_data.get('email'))
                    messages.error(
                        request,
                        f'We could not send your verification email right now: {exc}',
                    )
                else:
                    request.session['pending_activation_email'] = user.email
                    try:
                        _send_activation_email(request, user)
                    except Exception:
                        logger.exception('Activation email send failed after admin registration for %s', user.email)
                        messages.warning(
                            request,
                            'Admin account created, but we could not send the activation email. Use resend.',
                        )
                    else:
                        messages.info(request, 'Activation email sent. Please check your inbox.')
                    return redirect('users:registration_pending')
    else:
        initial = {'role': 'admin'}
        if invited_email:
            initial['email'] = invited_email
        form = _prepare_admin_register_form(RegisterForm(initial=initial), invited_email=invited_email)
    return render(request, 'accounts/register.html', {'form': form, 'role': 'admin'})


def resend_activation_email(request):
    if request.method != 'POST':
        return redirect('users:registration_pending')

    email = (request.POST.get('email') or request.session.get('pending_activation_email') or '').strip()
    if not email:
        messages.error(request, 'No pending email found. Enter your email to resend.')
        return redirect('users:registration_pending')

    user = User.objects.filter(email=email, is_active=False).first()
    if user:
        try:
            _send_activation_email(request, user)
            request.session['pending_activation_email'] = user.email
        except Exception:
            logger.exception('Resend activation failed for %s', email)
            messages.error(request, 'We could not send the activation email right now. Please try again.')
            return redirect('users:registration_pending')

    messages.success(
        request,
        'If an inactive account exists for that email, an activation link has been sent.',
    )
    return redirect('users:registration_pending')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your email has been verified. Please log in to continue.')
        return redirect('users:login')
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
            if user.role == 'admin':
                return redirect('users:admin_dashboard')
            return redirect('home')
        login_value = (request.POST.get('username') or '').strip()
        raw_password = request.POST.get('password') or ''
        inactive_user = User.objects.filter(
            Q(username=login_value) | Q(email=login_value),
            is_active=False,
        ).first()
        if inactive_user and raw_password and inactive_user.check_password(raw_password):
            request.session['pending_activation_email'] = inactive_user.email
            try:
                _send_activation_email(request, inactive_user)
            except Exception:
                logger.exception('Activation email send failed during inactive login for %s', inactive_user.email)
                messages.warning(
                    request,
                    'Your account is not verified. We could not send an email; use resend.',
                )
            else:
                messages.info(request, 'Your account is not verified. A new activation email has been sent.')
            return redirect('users:registration_pending')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
@role_required('student')
def student_dashboard_view(request):
    attendance_qs = AttendanceRecord.objects.filter(
        student=request.user
    ).select_related('session__course').order_by('-check_in_time')
    context = {
        'enrolled_courses_count': Enrollment.objects.filter(student=request.user).count(),
        'present_count': attendance_qs.filter(status='present').count(),
        'absent_count': attendance_qs.filter(status='absent').count(),
        'recent_attendance': attendance_qs[:8],
    }
    return render(request, 'users/student_dashboard.html', context)


@login_required
@role_required('lecturer')
def lecturer_dashboard_view(request):
    courses_qs = Course.objects.filter(lecturer=request.user).order_by('code')
    all_sessions_qs = Session.objects.filter(
        course__lecturer=request.user
    ).select_related('course').annotate(
        present_count=Count('attendance_records', filter=Q(attendance_records__status='present')),
        absent_count=Count('attendance_records', filter=Q(attendance_records__status='absent')),
    ).order_by('-start_time')

    marked_attendance_total = AttendanceRecord.objects.filter(
        session__course__lecturer=request.user,
        status__in=['present', 'absent'],
    ).count()
    present_attendance_total = AttendanceRecord.objects.filter(
        session__course__lecturer=request.user,
        status='present',
    ).count()
    attendance_rate = None
    if marked_attendance_total:
        attendance_rate = round((present_attendance_total / marked_attendance_total) * 100, 1)

    context = {
        'courses': courses_qs,
        'total_courses': courses_qs.count(),
        'todays_sessions': all_sessions_qs.filter(start_time__date=timezone.localdate()).count(),
        'attendance_rate': attendance_rate,
        'recent_sessions': all_sessions_qs[:8],
    }
    return render(request, 'users/lecturer_dashboard.html', context)


@login_required
@role_required('admin')
def admin_dashboard_view(request):
    return render(request, 'users/admin_dashboard.html')
