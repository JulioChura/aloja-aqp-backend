from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch
from .models import User, OwnerProfile

class UserRegistrationTests(TestCase):
    """
    PU001: PRUEBAS DE CREACIÓN DE USUARIOS
    --------------------------------------
    Objetivo: 
    Verificar que el registro de roles Estudiante/Propietario
    validación de las restricciones como DNI, email único.
    """

    def setUp(self):
        self.client = APIClient()

    def test_register_student_success(self):
        """
        PU001-1: Registro exitoso de estudiante.
        Resultado esperado: Código 201 y creación del usuario en BD.
        """
        # --- 1. PREPARACIÓN (ARRANGE) ---
        url = reverse('user-register')  
        payload = {
            'email': 'juan@estudiante.com',
            'password': 'password123',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'phone_number': '',
            'campuses': [] 
        }

        # --- 2. EJECUCIÓN (ACT) ---
        resp = self.client.post(url, payload, format='json')
        
        # --- 3. VERIFICACIÓN (ASSERT) ---
        # Verificamos respuesta HTTP
        self.assertEqual(resp.status_code, 201, "El código de estado debería ser 201 CREATED")
        # Verificamos persistencia en Base de Datos
        self.assertTrue(User.objects.filter(email='juan@estudiante.com').exists(), "El usuario debería existir en la BD")

    def test_register_owner_with_valid_dni(self):
        """
        PU001-2: Registro exitoso de propietario con DNI válido.
        Prerrequisito: Usuario base ya creado y autenticado.
        Simulación: API de RENIEC retorna datos válidos.
        """
        # --- 1. PREPARACIÓN ---
        # Crear usuario base y loguearlo
        user = User.objects.create_user(email='maria@propietario.com', password='password123')
        self.client.force_authenticate(user=user)

        url = reverse('owner-register') 
        payload = {
            'first_name': 'María',
            'last_name': 'García',
            'dni': '12345678',
            'phone_number': '999888777',
            'contact_address': 'Av. Ejército 123'
        }

        # --- 2. EJECUCIÓN CON MOCK (ACT) ---
        # Simulamos que RENIEC encuentra a la persona
        with patch('users.serializers.verificar_dni') as mock_verificar:
            mock_verificar.return_value = {
                'first_name': 'María',
                'last_name_1': 'García',
                'last_name_2': ''
            }
            resp = self.client.post(url, payload, format='json')

        # --- 3. VERIFICACIÓN ---
        self.assertEqual(resp.status_code, 201)
        # Verificar que se creó el perfil de propietario asociado al DNI
        self.assertTrue(OwnerProfile.objects.filter(user=user, dni='12345678').exists())

    def test_register_owner_with_invalid_dni(self):
        """
        PU001-3: Registro propietario con DNI inválido.
        Simulación: API de RENIEC no encuentra el DNI.
        Resultado esperado: Error 400 y NO creación del perfil.
        """
        # --- 1. PREPARACIÓN ---
        user = User.objects.create_user(email='carlos@propietario.com', password='password123')
        self.client.force_authenticate(user=user)

        url = reverse('owner-register')
        payload = {
            'first_name': 'Carlos',
            'last_name': 'López',
            'dni': '99999999', # DNI Falso
        }

        # --- 2. EJECUCIÓN CON MOCK ---
        # Simulamos que RENIEC devuelve None (no encontrado)
        with patch('users.serializers.verificar_dni') as mock_verificar:
            mock_verificar.return_value = None
            resp = self.client.post(url, payload, format='json')

        # --- 3. VERIFICACIÓN ---
        self.assertEqual(resp.status_code, 400, "Debería fallar si el DNI no es válido")
        # Aseguramos que la base de datos sigue limpia
        self.assertFalse(OwnerProfile.objects.filter(user=user).exists(), "No se debió crear el perfil")

    def test_register_student_existing_email(self):
        """
        PU001-4: Registro con correo ya existente.
        Resultado esperado: Error 400 (Bad Request).
        """
        # --- 1. PREPARACIÓN ---
        # Insertamos manualmente un usuario para generar el conflicto
        User.objects.create_user(email='juan@estudiante.com', password='password123')

        url = reverse('user-register')
        payload = {
            'email': 'juan@estudiante.com', # Intentamos registrar el mismo email
            'password': 'password456',
        }

        # --- 2. EJECUCIÓN ---
        resp = self.client.post(url, payload, format='json')

        # --- 3. VERIFICACIÓN ---
        self.assertEqual(resp.status_code, 400, "No se deben permitir emails duplicados")


class UserAuthenticationTests(TestCase):
    """
    PU002: PRUEBAS DE AUTENTICACIÓN (LOGIN)
    -------------------------------------------------------------------
    Objetivo: Verificar la correcta emisión de tokens JWT y manejo de errores.
    """
    def setUp(self):
        self.client = APIClient()
        # Creamos usuarios semilla para probar el login
        self.student_user = User.objects.create_user(email='juan@estudiante.com', password='password123')
        self.owner_user = User.objects.create_user(email='maria@propietario.com', password='password123')

    def test_login_student_success(self):
        """
        PU002-1: Login exitoso estudiante.
        Resultado esperado: Tokens 'access' y 'refresh' en la respuesta.
        """
        # --- 1. PREPARACIÓN ---
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'juan@estudiante.com',
            'password': 'password123'
        }

        # --- 2. EJECUCIÓN ---
        resp = self.client.post(url, payload, format='json')
        
        # --- 3. VERIFICACIÓN ---
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data, "Falta el token de acceso")
        self.assertIn('refresh', resp.data, "Falta el token de refresco")

    def test_login_owner_success(self):
        """
        PU002-2: Login exitoso propietario.
        Resultado esperado: Acceso correcto (código 200).
        """
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'maria@propietario.com',
            'password': 'password123'
        }
        
        resp = self.client.post(url, payload, format='json')
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)

    def test_login_invalid_credentials(self):
        """
        PU002-3: Login con credenciales incorrectas.
        Resultado esperado: Error 400 (Bad Request).
        """
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'juan@estudiante.com',
            'password': 'passwordINCORRECTO'
        }
        
        resp = self.client.post(url, payload, format='json')
        
        self.assertEqual(resp.status_code, 400)

    def test_login_google_success(self):
        """
        PU002-4: Login con cuenta Google (Simulado).
        Simulación: Token de Google válido y subida de avatar exitosa.
        Resultado esperado: Creación automática de usuario y retorno de tokens.
        """
        # --- 1. PREPARACIÓN ---
        url = reverse('google-login')
        payload = {'id_token': 'token_falso_de_prueba'}

        # Mock Data: Lo que fingiremos que devuelve Google
        google_mock_data = {
            'email': 'googleuser@test.com',
            'given_name': 'Usuario',
            'family_name': 'Google',
            'sub': '123456789',
            'picture': 'http://foto.falsa/avatar.jpg'
        }

        # --- 2. EJECUCIÓN (CON DOBLE MOCK) ---
        # Mock 1: Evitar llamar a Google
        with patch('users.views.google_auth.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = google_mock_data
            
            # Mock 2: Evitar subir foto a Cloudinary
            with patch('users.views.google_auth.cloudinary.uploader.upload') as mock_upload:
                mock_upload.return_value = {'public_id': 'avatar_falso_id'}

                resp = self.client.post(url, payload, format='json')

        # --- 3. VERIFICACIÓN ---
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        
        # Verificar efecto colateral: El usuario debe existir en BD
        user_created = User.objects.get(email='googleuser@test.com')
        self.assertEqual(user_created.first_name, 'Usuario')
        self.assertTrue(hasattr(user_created, 'student_profile'), "El usuario de Google debe tener perfil de estudiante")

    def test_login_non_existent_user(self):
        """
        PU002-5: Login con usuario no registrado.
        Resultado esperado: Error 400.
        """
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'noexiste@correo.com',
            'password': 'password123'
        }
        
        resp = self.client.post(url, payload, format='json')
        
        self.assertEqual(resp.status_code, 400)
