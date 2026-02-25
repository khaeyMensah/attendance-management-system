from datetime import timedelta
import secrets
import string
from urllib.parse import quote_plus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.attendance.forms import AccessCodeForm, StartSessionForm
from apps.attendance.models import AttendanceRecord, Session
from apps.courses.models import Course, Enrollment
from apps.users.decorators import role_required


def _generate_unique_qr_token():
    while True:
        token = secrets.token_urlsafe(24)
        if not Session.objects.filter(qr_token=token).exists():
            return token


def _generate_unique_access_code(length=6):
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not Session.objects.filter(access_code=code).exists():
            return code


def _redirect_to_dashboard(user):
    if user.role == 'student':
        return redirect('users:student_dashboard')
    if user.role == 'lecturer':
        return redirect('users:lecturer_dashboard')
    if user.role == 'admin':
        return redirect('users:admin_dashboard')
    return redirect('home')


@login_required
@role_required('lecturer')
def start_session_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id, lecturer=request.user)

    if request.method == 'POST':
        form = StartSessionForm(request.POST)
        if form.is_valid():
            start_time = timezone.now()
            end_time = start_time + timedelta(minutes=form.cleaned_data['duration_minutes'])
            session = Session(
                course=course,
                start_time=start_time,
                end_time=end_time,
                qr_token=_generate_unique_qr_token(),
                access_code=_generate_unique_access_code(),
                is_active=True,
            )
            try:
                session.full_clean()
                session.save()
            except ValidationError as exc:
                messages.error(request, '; '.join(exc.messages))
            else:
                messages.success(request, f'Session started for {course.code}. QR is ready.')
                return redirect('attendance:session_qr', session_id=session.pk)
    else:
        form = StartSessionForm()

    return render(
        request,
        'attendance/start_session.html',
        {
            'course': course,
            'form': form,
        },
    )


@login_required
@role_required('lecturer')
def session_qr_view(request, session_id):
    session = get_object_or_404(
        Session.objects.select_related('course'),
        pk=session_id,
        course__lecturer=request.user,
    )
    if session.is_active and session.end_time < timezone.now():
        session.is_active = False
        session.save(update_fields=['is_active'])

    scan_url = request.build_absolute_uri(
        reverse('attendance:scan_qr', kwargs={'qr_token': session.qr_token})
    )
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote_plus(scan_url)}"
    return render(
        request,
        'attendance/session_qr.html',
        {
            'session': session,
            'scan_url': scan_url,
            'qr_image_url': qr_image_url,
        },
    )


def scan_qr_view(request, qr_token):
    session = get_object_or_404(
        Session.objects.select_related('course', 'course__lecturer'),
        qr_token=qr_token,
    )
    if request.user.is_anonymous:
        return redirect(f"{reverse('users:login')}?next={request.path}")

    if request.user.role != 'student':
        messages.error(request, 'Only students can submit attendance with this page.')
        return _redirect_to_dashboard(request.user)

    if session.is_active and session.end_time < timezone.now():
        session.is_active = False
        session.save(update_fields=['is_active'])

    existing_record = AttendanceRecord.objects.filter(
        student=request.user,
        session=session,
    ).first()
    enrolled = Enrollment.objects.filter(
        student=request.user,
        course=session.course,
    ).exists()

    if request.method == 'POST':
        if existing_record:
            messages.info(request, 'Attendance already recorded for this session.')
        elif not enrolled:
            messages.error(request, 'You are not enrolled in this course.')
        else:
            attendance = AttendanceRecord(student=request.user, session=session, status='present')
            try:
                attendance.full_clean()
                attendance.save()
            except ValidationError as exc:
                messages.error(request, '; '.join(exc.messages))
            except IntegrityError:
                messages.info(request, 'Attendance already recorded for this session.')
            else:
                messages.success(request, 'Attendance logged successfully.')
        return redirect('attendance:scan_qr', qr_token=session.qr_token)

    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])

    return render(
        request,
        'attendance/scan_session.html',
        {
            'session': session,
            'existing_record': existing_record,
            'enrolled': enrolled,
            'is_open': session.is_open(),
        },
    )


@login_required
@role_required('student')
def enter_code_view(request):
    if request.method == 'POST':
        form = AccessCodeForm(request.POST)
        if form.is_valid():
            session = Session.objects.select_related('course').filter(
                access_code=form.cleaned_data['access_code'],
                is_active=True,
                end_time__gte=timezone.now(),
            ).order_by('-start_time').first()
            if session:
                return redirect('attendance:scan_qr', qr_token=session.qr_token)
            form.add_error('access_code', 'Invalid or expired code.')
    else:
        form = AccessCodeForm()
    return render(request, 'attendance/enter_code.html', {'form': form})


@login_required
@role_required('student')
def my_attendance_view(request):
    records = AttendanceRecord.objects.filter(student=request.user).select_related(
        'session',
        'session__course',
    ).order_by('-check_in_time')
    return render(
        request,
        'attendance/my_attendance.html',
        {'records': records},
    )


@login_required
@role_required('lecturer')
def session_records_view(request, session_id):
    session = get_object_or_404(
        Session.objects.select_related('course'),
        pk=session_id,
        course__lecturer=request.user,
    )
    records = AttendanceRecord.objects.filter(session=session).select_related('student').order_by(
        '-check_in_time'
    )
    enrolled_count = Enrollment.objects.filter(course=session.course).count()
    present_count = records.filter(status='present').count()
    absent_count = records.filter(status='absent').count()
    return render(
        request,
        'attendance/session_records.html',
        {
            'session': session,
            'records': records,
            'enrolled_count': enrolled_count,
            'present_count': present_count,
            'absent_count': absent_count,
        },
    )


@login_required
@role_required('lecturer')
def close_session_view(request, session_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    session = get_object_or_404(
        Session,
        pk=session_id,
        course__lecturer=request.user,
    )
    if session.is_active:
        session.is_active = False
        session.save(update_fields=['is_active'])
        messages.success(request, 'Session closed.')
    else:
        messages.info(request, 'Session is already closed.')
    return redirect('attendance:session_records', session_id=session.pk)
