from django.test import TestCase
from ninja_extra.testing import TestClient
from .controller import AuthController
import json
from django.contrib.auth.models import User
from ninja_jwt.tokens import RefreshToken

class TestAuth(TestCase):
    def setUp(self):
        self.client = TestClient(AuthController)
        self.client.post("/register", data=json.dumps({
            "phone_number": "08123456789",
            "first_name": "Omar",
            "last_name": "Khalif",
            "password": "AkuAnakEmo"
        }))


    def test_register(self):
        response = self.client.post(
            "/register",
            data=json.dumps({
                "phone_number": "1234567890",
                "first_name": "John",
                "last_name": "Doe",
                "password": "password"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Akun berhasil dibuat")
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())


    def test_register_existing(self):
        response = self.client.post("/register", data=json.dumps({
            "phone_number": "08123456789",
            "first_name": "Rafif",
            "last_name": "Aulia",
            "password": "admin1234"
        }))

        self.assertEqual(response.status_code, 400)


    def test_register_invalid_phone_number(self):
        response = self.client.post("/register", data=json.dumps({
            "phone_number": "12345",
            "first_name": "John",
            "last_name": "Doe",
            "password": "password"
        }))
        self.assertEqual(response.status_code, 400)

        response2 = self.client.post("/register", data=json.dumps({
            "phone_number": "12345a",
            "first_name": "John",
            "last_name": "Doe",
            "password": "password"
        }))
        self.assertEqual(response2.status_code, 400)

        response3 = self.client.post("/register", data=json.dumps({
            "phone_number": "123456789012345",
            "first_name": "John",
            "last_name": "Doe",
            "password": "password"
        }))
        self.assertEqual(response3.status_code, 400)


    def test_login(self):
        response = self.client.post("/login", data=json.dumps({
            "phone_number": "08123456789",
            "password": "AkuAnakEmo"
        }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Login berhasil")
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())


    def test_login_password_invalid(self):
        response = self.client.post("/login", data=json.dumps({
            "phone_number": "08123456789",
            "password": "wrongpassword"
        }))
        self.assertEqual(response.status_code, 404)


    def test_login_user_not_found(self):
        response = self.client.post("/login", data=json.dumps({
            "phone_number": "1234567890",
            "password": "password"
        }))
        self.assertEqual(response.status_code, 404)


    def test_refresh(self):
        login_res = self.client.post("/login", data=json.dumps({
            "phone_number": "08123456789",
            "password": "AkuAnakEmo"
        }))
        tokens = login_res.json()
        refresh = tokens["refresh"]

        response = self.client.post("/refresh", data=json.dumps({
            "refresh": refresh
        }))
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())


    def test_refresh_invalid(self):
        response = self.client.post("/refresh", data=json.dumps({
            "refresh": "invalidtoken"
        }))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Token invalid atau telah kadaluarsa")


    def test_refresh_with_deleted_user(self):
        user = User.objects.create_user(username="testuser", password="password123")
        refresh_token = RefreshToken.for_user(user)
    
        user.delete()
    
        response = self.client.post("/refresh", data=json.dumps({"refresh": str(refresh_token)}))
    
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Pengguna tidak ditemukan atau token tidak valid")


    def test_me(self):
        login_res = self.client.post("/login", data=json.dumps({
            "phone_number": "08123456789",
            "password": "AkuAnakEmo"
        }))
        tokens = login_res.json()
        access = tokens["access"]

        response = self.client.get("/me", headers={"Authorization": f"Bearer {access}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["phone_number"], "08123456789")
        self.assertEqual(response.json()["first_name"], "Omar")
        self.assertEqual(response.json()["last_name"], "Khalif")


    def test_me_invalid(self):
        response = self.client.get("/me", headers={"Authorization ": "Bearer invalidtoken"})
        self.assertEqual(response.status_code, 401)

    
    def test_validate_token(self):
        login_res = self.client.post("/login", data=json.dumps({
            "phone_number": "08123456789",
            "password": "AkuAnakEmo"
        }), content_type='application/json')
        tokens = login_res.json()
        access = tokens["access"]

        response = self.client.post("/validate", headers={"Authorization": f"Bearer {access}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Token valid")


    def test_validate_invalid(self):
        response = self.client.post("/validate", headers={"Authorization": "Bearer invalidtoken"})
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("message", response.json())


    def test_validate_wrong_method(self):
        response = self.client.get("/validate", headers={"Authorization": "Bearer invalidtoken"})
        self.assertEqual(response.status_code, 405)
