from datetime import timedelta

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.attendance.models import Session
from apps.courses.models import Course
from apps.users.models import User


class UserURLFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='old-pass-123',
            email='student@example.com',
            full_name='Student One',
            role='student',
            student_id='ST001',
        )

    def test_password_reset_uses_namespaced_urls(self):
        response = self.client.post(
            reverse('users:password_reset'),
            {'email': self.user.email},
        )

        self.assertRedirects(response, reverse('users:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/reset/', mail.outbox[0].body)

    def test_password_change_uses_namespaced_success_url(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('users:password_change'),
            {
                'old_password': 'old-pass-123',
                'new_password1': 'new-pass-456',
                'new_password2': 'new-pass-456',
            },
        )

        self.assertRedirects(response, reverse('users:password_change_done'))


class LecturerDashboardTests(TestCase):
    def setUp(self):
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

    def test_active_sessions_show_qr_code_and_records_actions(self):
        now = timezone.now()
        session = Session.objects.create(
            course=self.course,
            start_time=now - timedelta(minutes=10),
            end_time=now + timedelta(minutes=50),
            qr_token='active-token',
            access_code='ABC123',
            is_active=True,
        )
        Session.objects.create(
            course=self.course,
            start_time=now - timedelta(hours=3),
            end_time=now - timedelta(hours=2),
            qr_token='expired-token',
            access_code='OLD123',
            is_active=True,
        )
        self.client.force_login(self.lecturer)

        response = self.client.get(reverse('users:lecturer_dashboard'))

        self.assertContains(response, 'Active Sessions')
        self.assertContains(response, session.access_code)
        self.assertContains(response, reverse('attendance:session_qr', args=[session.pk]))
        self.assertContains(response, reverse('attendance:session_records', args=[session.pk]))
        self.assertContains(response, reverse('attendance:close_session', args=[session.pk]))
        self.assertContains(response, 'Show QR')
        self.assertContains(response, 'View Records')
        self.assertContains(response, 'Close & Mark Absentees')
        self.assertNotContains(response, 'OLD123')
