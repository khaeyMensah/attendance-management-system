from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from apps.attendance.models import Session
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
