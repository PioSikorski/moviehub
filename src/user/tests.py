from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("start")
        self.index_url = reverse("index")

    def test_get_start_view(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start.html")
        self.assertIn("signup_form", response.context)
        self.assertIn("login_form", response.context)

    def test_signup(self):
        response = self.client.post(
            self.signup_url,
            {
                "signup": True,
                "username": "newuser",
                "password1": "newpass123",
                "password2": "newpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.index_url)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        response = self.client.post(
            self.signup_url,
            {"login": True, "username": "testuser", "password": "testpass"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.index_url)
