from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.attendance.models import Session
from apps.courses.models import Course, Enrollment
from apps.users.models import User


DEMO_PASSWORD = 'ClassMark123!'


class Command(BaseCommand):
    help = 'Create idempotent demo users, courses, enrollments, and one open attendance session.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default=DEMO_PASSWORD,
            help='Password to set for all demo users.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password = options['password']

        admin_user = self._upsert_user(
            username='demo_admin',
            email='demo.admin@example.com',
            full_name='Demo Admin',
            role='admin',
            is_staff=True,
            is_superuser=True,
            password=password,
        )
        lecturer = self._upsert_user(
            username='demo_lecturer',
            email='demo.lecturer@example.com',
            full_name='Demo Lecturer',
            role='lecturer',
            staff_id='STAFF001',
            password=password,
        )
        students = [
            self._upsert_user(
                username='demo_student_1',
                email='demo.student1@example.com',
                full_name='Demo Student One',
                role='student',
                student_id='STU001',
                password=password,
            ),
            self._upsert_user(
                username='demo_student_2',
                email='demo.student2@example.com',
                full_name='Demo Student Two',
                role='student',
                student_id='STU002',
                password=password,
            ),
            self._upsert_user(
                username='demo_student_3',
                email='demo.student3@example.com',
                full_name='Demo Student Three',
                role='student',
                student_id='STU003',
                password=password,
            ),
        ]

        courses = [
            self._upsert_course('CSC101', 'Intro to Computing', lecturer),
            self._upsert_course('MAT120', 'Business Mathematics', lecturer),
        ]

        for course in courses:
            for student in students:
                Enrollment.objects.get_or_create(student=student, course=course)

        now = timezone.now()
        session, created = Session.objects.get_or_create(
            course=courses[0],
            access_code='DEMO01',
            defaults={
                'start_time': now - timedelta(minutes=10),
                'end_time': now + timedelta(minutes=80),
                'qr_token': 'demo-session-token',
                'is_active': True,
            },
        )
        if not created:
            session.start_time = now - timedelta(minutes=10)
            session.end_time = now + timedelta(minutes=80)
            session.qr_token = 'demo-session-token'
            session.is_active = True
            session.save(update_fields=['start_time', 'end_time', 'qr_token', 'is_active'])

        self.stdout.write(self.style.SUCCESS('Demo MVP data is ready.'))
        self.stdout.write(f'Admin:    {admin_user.username} / {password}')
        self.stdout.write(f'Lecturer: {lecturer.username} / {password}')
        for student in students:
            self.stdout.write(f'Student:  {student.username} / {password}')
        self.stdout.write(f'Open session access code: {session.access_code}')

    def _upsert_user(self, username, email, full_name, role, password, **extra_fields):
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'full_name': full_name,
                'role': role,
                'student_id': extra_fields.get('student_id'),
                'staff_id': extra_fields.get('staff_id'),
                'is_active': True,
                'is_staff': extra_fields.get('is_staff', False),
                'is_superuser': extra_fields.get('is_superuser', False),
            },
        )
        user.set_password(password)
        user.save()
        return user

    def _upsert_course(self, code, title, lecturer):
        course, _ = Course.objects.update_or_create(
            code=code,
            defaults={
                'title': title,
                'lecturer': lecturer,
            },
        )
        return course
