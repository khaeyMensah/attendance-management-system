from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.attendance.models import Session
from apps.courses.forms import CourseEnrollmentForm
from apps.courses.models import Course, Enrollment
from apps.users.decorators import role_required


@login_required
@role_required('lecturer')
def lecturer_course_detail_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id, lecturer=request.user)
    sessions = Session.objects.filter(course=course).annotate(
        present_count=Count('attendance_records', filter=Q(attendance_records__status='present')),
        absent_count=Count('attendance_records', filter=Q(attendance_records__status='absent')),
    ).order_by('-start_time')
    return render(
        request,
        'courses/lecturer_course_detail.html',
        {
            'course': course,
            'enrolled_students_count': Enrollment.objects.filter(course=course).count(),
            'sessions': sessions,
        },
    )


@login_required
@role_required('lecturer')
def manage_course_students_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id, lecturer=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'enroll':
            form = CourseEnrollmentForm(request.POST, course=course)
            if form.is_valid():
                students = form.cleaned_data['students']
                created_count = 0
                for student in students:
                    _, created = Enrollment.objects.get_or_create(student=student, course=course)
                    if created:
                        created_count += 1
                if created_count:
                    messages.success(request, f'{created_count} student(s) enrolled.')
                else:
                    messages.info(request, 'No new students selected.')
                return redirect('courses:manage_course_students', course_id=course.pk)
        elif action == 'remove':
            enrollment = get_object_or_404(
                Enrollment,
                pk=request.POST.get('enrollment_id'),
                course=course,
            )
            student_name = enrollment.student.full_name or enrollment.student.username
            enrollment.delete()
            messages.success(request, f'{student_name} removed from {course.code}.')
            return redirect('courses:manage_course_students', course_id=course.pk)
        else:
            form = CourseEnrollmentForm(course=course)
            messages.error(request, 'Unknown student management action.')
    else:
        form = CourseEnrollmentForm(course=course)

    enrollments = Enrollment.objects.filter(course=course).select_related('student').order_by(
        'student__full_name',
        'student__username',
    )
    return render(
        request,
        'courses/manage_students.html',
        {
            'course': course,
            'form': form,
            'enrollments': enrollments,
        },
    )
