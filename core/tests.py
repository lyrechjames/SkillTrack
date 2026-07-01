from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationRoutesTests(TestCase):
    def test_password_reset_confirm_route_exists(self):
        url = reverse('password_reset_confirm', kwargs={'uidb64': 'test', 'token': 'token'})
        self.assertEqual(url, '/password-reset-confirm/test/token/')

    def test_password_reset_complete_route_exists(self):
        url = reverse('password_reset_complete')
        self.assertEqual(url, '/password-reset-complete/')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=/dashboard/', response['Location'])

    def test_register_persists_new_user_to_database(self):
        response = self.client.post(
            reverse('register'),
            {
                'full_name': 'Jane Doe',
                'email': 'jane@example.com',
                'password': 'StrongPass!123',
                'confirm_password': 'StrongPass!123',
                'terms': 'on',
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        User = get_user_model()
        self.assertTrue(User.objects.filter(username='jane@example.com').exists())

        user = User.objects.get(username='jane@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(user.check_password('StrongPass!123'))
