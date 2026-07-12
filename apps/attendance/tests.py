from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.attendance.models import AttendanceRecord, Session
from apps.courses.models import Course, Enrollment
from apps.users.models import User


class AttendanceMVPTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student',
            password='test-pass-123',
            email='student@example.com',
            full_name='Student One',
            role='student',
            student_id='ST001',
        )
        self.absent_student = User.objects.create_user(
            username='absent-student',
            password='test-pass-123',
            email='absent@example.com',
            full_name='Absent Student',
            role='student',
            student_id='ST002',
        )
        self.unenrolled_student = User.objects.create_user(
            username='unenrolled-student',
            password='test-pass-123',
            email='unenrolled@example.com',
            full_name='Unenrolled Student',
            role='student',
            student_id='ST003',
        )
        self.lecturer = User.objects.create_user(
            username='lecturer',
            password='test-pass-123',
            email='lecturer@example.com',
            full_name='Lecturer One',
            role='lecturer',
            staff_id='LC001',
        )
        self.course = Course.objects.create(
            code='CSC101',
            title='Intro to Computing',
            lecturer=self.lecturer,
        )
        Enrollment.objects.create(student=self.student, course=self.course)
        Enrollment.objects.create(student=self.absent_student, course=self.course)
        now = timezone.now()
        self.session = Session.objects.create(
            course=self.course,
            start_time=now - timedelta(minutes=5),
            end_time=now + timedelta(minutes=55),
            qr_token='test-token',
            access_code='ABC123',
            is_active=True,
        )

    def test_qr_page_uses_local_svg_data_uri(self):
        self.client.force_login(self.lecturer)

        response = self.client.get(reverse('attendance:session_qr', args=[self.session.pk]))

        self.assertContains(response, 'data:image/svg+xml;base64,')
        self.assertNotContains(response, 'api.qrserver.com')

    def test_login_next_preserves_scanned_attendance_url(self):
        scan_url = reverse('attendance:scan_qr', args=[self.session.qr_token])

        response = self.client.post(
            f"{reverse('users:login')}?next={scan_url}",
            {'username': self.student.username, 'password': 'test-pass-123', 'next': scan_url},
        )

        self.assertRedirects(response, scan_url, fetch_redirect_response=False)

    def test_student_can_confirm_attendance_from_scan_page(self):
        self.client.force_login(self.student)

        response = self.client.post(reverse('attendance:scan_qr', args=[self.session.qr_token]))

        self.assertRedirects(
            response,
            reverse('attendance:scan_qr', args=[self.session.qr_token]),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            AttendanceRecord.objects.filter(
                student=self.student,
                session=self.session,
                status='present',
            ).exists()
        )

    def test_unenrolled_student_cannot_confirm_attendance(self):
        self.client.force_login(self.unenrolled_student)

        response = self.client.post(reverse('attendance:scan_qr', args=[self.session.qr_token]))

        self.assertRedirects(
            response,
            reverse('attendance:scan_qr', args=[self.session.qr_token]),
            fetch_redirect_response=False,
        )
        self.assertFalse(
            AttendanceRecord.objects.filter(
                student=self.unenrolled_student,
                session=self.session,
            ).exists()
        )

    def test_expired_session_does_not_accept_attendance(self):
        now = timezone.now()
        self.session.start_time = now - timedelta(hours=2)
        self.session.end_time = now - timedelta(hours=1)
        self.session.save(update_fields=['start_time', 'end_time'])
        self.client.force_login(self.student)

        response = self.client.post(reverse('attendance:scan_qr', args=[self.session.qr_token]))

        self.assertRedirects(
            response,
            reverse('attendance:scan_qr', args=[self.session.qr_token]),
            fetch_redirect_response=False,
        )
        self.assertFalse(
            AttendanceRecord.objects.filter(
                student=self.student,
                session=self.session,
            ).exists()
        )

    def test_duplicate_scan_keeps_one_attendance_record(self):
        self.client.force_login(self.student)
        scan_url = reverse('attendance:scan_qr', args=[self.session.qr_token])

        self.client.post(scan_url)
        self.client.post(scan_url)

        self.assertEqual(
            AttendanceRecord.objects.filter(student=self.student, session=self.session).count(),
            1,
        )

    def test_lecturer_cannot_submit_attendance(self):
        self.client.force_login(self.lecturer)

        response = self.client.post(reverse('attendance:scan_qr', args=[self.session.qr_token]))

        self.assertRedirects(response, reverse('users:lecturer_dashboard'), fetch_redirect_response=False)
        self.assertFalse(AttendanceRecord.objects.filter(session=self.session).exists())

    def test_close_session_marks_unchecked_enrolled_students_absent(self):
        self.client.force_login(self.student)
        self.client.post(reverse('attendance:scan_qr', args=[self.session.qr_token]))
        self.client.force_login(self.lecturer)

        response = self.client.post(reverse('attendance:close_session', args=[self.session.pk]))

        self.assertRedirects(
            response,
            reverse('attendance:session_records', args=[self.session.pk]),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            AttendanceRecord.objects.filter(
                student=self.student,
                session=self.session,
                status='present',
            ).exists()
        )
        self.assertTrue(
            AttendanceRecord.objects.filter(
                student=self.absent_student,
                session=self.session,
                status='absent',
            ).exists()
        )
