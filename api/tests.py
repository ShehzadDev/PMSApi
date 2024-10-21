from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import User, Profile
import io
from PIL import Image
from .enums import UserRole


class UserAuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user", password="password", email="user@sample.com"
        )
        self.profile = Profile.objects.create(
            user=self.user, role=UserRole.MANAGER.value
        )

    def test_register_user(self):
        url = reverse("register")

        image = Image.new("RGB", (100, 100), color="red")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.name = "test_image.jpg"
        image_file.seek(0)

        mock_image = SimpleUploadedFile(
            "test_image.jpg",
            image_file.getvalue(),
            content_type="image/jpeg",
        )

        data = {
            "username": "new_user",
            "password": "password",
            "email": "user@example.com",
            "profile_picture": mock_image,
            "role": UserRole.MANAGER.value,
            "contact_number": "1234567890",
        }
        response = self.client.post(url, data, format="multipart")
        print("Register Test")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_user(self):
        url = reverse("login")
        data = {
            "username": "user",
            "password": "password",
        }
        response = self.client.post(url, data, format="json")
        print("Login Test")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_get_user_profile(self):
        url = reverse("user-profile")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        print("Get Profile Test")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)
