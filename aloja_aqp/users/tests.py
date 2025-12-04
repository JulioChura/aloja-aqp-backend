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
        print("\n" + "="*80)
        print("TEST: PU001-1 - REGISTRO EXITOSO DE ESTUDIANTE")
        print("="*80)
        
        # --- 1. PREPARACIÓN (ARRANGE) ---
        print("\n[MÓDULO] User Registration")
        print("[ENTRADA]")
        url = reverse('user-register')  
        payload = {
            'email': 'juan@estudiante.com',
            'password': 'password123',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'phone_number': '',
            'campuses': [] 
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Email: {payload['email']}")
        print(f"  Nombre: {payload['first_name']} {payload['last_name']}")
        
        print("\n[ESPERADO]")
        print("  Status: 201 CREATED")
        print("  Efecto: Usuario creado en BD")

        # --- 2. EJECUCIÓN (ACT) ---
        print("\n[EJECUCIÓN]")
        resp = self.client.post(url, payload, format='json')
        
        # --- 3. VERIFICACIÓN (ASSERT) ---
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 201, "El código de estado debería ser 201 CREATED")
        print("  ✓ Status correcto")
        
        # Verificamos persistencia en Base de Datos
        user_exists = User.objects.filter(email='juan@estudiante.com').exists()
        print(f"  Usuario en BD: {user_exists}")
        self.assertTrue(user_exists, "El usuario debería existir en la BD")
        print("  ✓ Usuario creado en Base de Datos")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO")
        print("="*80)

    def test_register_owner_with_valid_dni(self):
        """
        PU001-2: Registro exitoso de propietario con DNI válido.
        Prerrequisito: Usuario base ya creado y autenticado.
        Simulación: API de RENIEC retorna datos válidos.
        """
        print("\n" + "="*80)
        print("TEST: PU001-2 - REGISTRO EXITOSO PROPIETARIO CON DNI VÁLIDO")
        print("="*80)
        
        # --- 1. PREPARACIÓN ---
        print("\n[MÓDULO] Owner Registration (con validación RENIEC)")
        print("[ENTRADA]")
        # Crear usuario base y loguearlo
        user = User.objects.create_user(email='maria@propietario.com', password='password123')
        self.client.force_authenticate(user=user)
        print(f"  Usuario base: {user.email}")

        url = reverse('owner-register') 
        payload = {
            'first_name': 'María',
            'last_name': 'García',
            'dni': '12345678',
            'phone_number': '999888777',
            'contact_address': 'Av. Ejército 123'
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Datos: DNI={payload['dni']}, Nombre={payload['first_name']} {payload['last_name']}")
        
        print("\n[ESPERADO]")
        print("  Status: 201 CREATED")
        print("  Validación RENIEC: ✓ DNI encontrado")
        print("  Efecto: OwnerProfile creado en BD")

        # --- 2. EJECUCIÓN CON MOCK (ACT) ---
        print("\n[EJECUCIÓN]")
        print("  Simulando respuesta de RENIEC...")
        # Simulamos que RENIEC encuentra a la persona
        with patch('users.serializers.verificar_dni') as mock_verificar:
            mock_verificar.return_value = {
                'first_name': 'María',
                'last_name_1': 'García',
                'last_name_2': ''
            }
            resp = self.client.post(url, payload, format='json')

        # --- 3. VERIFICACIÓN ---
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 201)
        print("  ✓ Status correcto (201 CREATED)")
        
        # Verificar que se creó el perfil de propietario asociado al DNI
        owner_profile_exists = OwnerProfile.objects.filter(user=user, dni='12345678').exists()
        print(f"  OwnerProfile en BD: {owner_profile_exists}")
        self.assertTrue(owner_profile_exists)
        print("  ✓ OwnerProfile creado correctamente")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO")
        print("="*80)

    def test_register_owner_with_invalid_dni(self):
        """
        PU001-3: Registro propietario con DNI inválido.
        Simulación: API de RENIEC no encuentra el DNI.
        Resultado esperado: Error 400 y NO creación del perfil.
        """
        print("\n" + "="*80)
        print("TEST: PU001-3 - REGISTRO PROPIETARIO CON DNI INVÁLIDO")
        print("="*80)
        
        # --- 1. PREPARACIÓN ---
        print("\n[MÓDULO] Owner Registration (validación RENIEC fallida)")
        print("[ENTRADA]")
        user = User.objects.create_user(email='carlos@propietario.com', password='password123')
        self.client.force_authenticate(user=user)
        print(f"  Usuario base: {user.email}")

        url = reverse('owner-register')
        payload = {
            'first_name': 'Carlos',
            'last_name': 'López',
            'dni': '99999999',
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Datos: DNI={payload['dni']} (INVÁLIDO)")
        
        print("\n[ESPERADO]")
        print("  Status: 400 BAD REQUEST")
        print("  Validación RENIEC: ✗ DNI no encontrado")
        print("  Efecto: NO se crea OwnerProfile")

        # --- 2. EJECUCIÓN CON MOCK ---
        print("\n[EJECUCIÓN]")
        print("  Simulando DNI no encontrado en RENIEC...")
        # Simulamos que RENIEC devuelve None (no encontrado)
        with patch('users.serializers.verificar_dni') as mock_verificar:
            mock_verificar.return_value = None
            resp = self.client.post(url, payload, format='json')

        # --- 3. VERIFICACIÓN ---
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 400, "Debería fallar si el DNI no es válido")
        print("  ✓ Status correcto (400 BAD REQUEST)")
        
        # Aseguramos que la base de datos sigue limpia
        owner_profile_exists = OwnerProfile.objects.filter(user=user).exists()
        print(f"  OwnerProfile en BD: {owner_profile_exists}")
        self.assertFalse(owner_profile_exists, "No se debió crear el perfil")
        print("  ✓ OwnerProfile NO fue creado (validación rechazada)")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO - VALIDACIÓN CORRECTA")
        print("="*80)

    def test_register_student_existing_email(self):
        """
        PU001-4: Registro con correo ya existente.
        Resultado esperado: Error 400 (Bad Request).
        """
        print("\n" + "="*80)
        print("TEST: PU001-4 - REGISTRO CON EMAIL DUPLICADO")
        print("="*80)
        
        # --- 1. PREPARACIÓN ---
        print("\n[MÓDULO] User Registration (email único)")
        print("[ENTRADA]")
        # Insertamos manualmente un usuario para generar el conflicto
        User.objects.create_user(email='juan@estudiante.com', password='password123')
        print("  Usuario 1 pre-existente: juan@estudiante.com")

        url = reverse('user-register')
        payload = {
            'email': 'juan@estudiante.com', # Intentamos registrar el mismo email
            'password': 'password456',
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Intento de Email: {payload['email']} (ya existe)")
        
        print("\n[ESPERADO]")
        print("  Status: 400 BAD REQUEST")
        print("  Error: Email duplicado")

        # --- 2. EJECUCIÓN ---
        print("\n[EJECUCIÓN]")
        resp = self.client.post(url, payload, format='json')

        # --- 3. VERIFICACIÓN ---
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 400, "No se deben permitir emails duplicados")
        print("  ✓ Status correcto (400 BAD REQUEST)")
        print("  ✓ Email duplicado fue rechazado")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO - VALIDACIÓN DE UNICIDAD")
        print("="*80)


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
        print("\n" + "="*80)
        print("TEST: PU002-1 - LOGIN EXITOSO ESTUDIANTE")
        print("="*80)
        
        # --- 1. PREPARACIÓN ---
        print("\n[MÓDULO] User Authentication (JWT Tokens)")
        print("[ENTRADA]")
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'juan@estudiante.com',
            'password': 'password123'
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Email: {payload['email']}")
        
        print("\n[ESPERADO]")
        print("  Status: 200 OK")
        print("  Response: access token + refresh token")

        # --- 2. EJECUCIÓN ---
        print("\n[EJECUCIÓN]")
        resp = self.client.post(url, payload, format='json')
        
        # --- 3. VERIFICACIÓN ---
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 200)
        print("  ✓ Status correcto (200 OK)")
        
        has_access = 'access' in resp.data
        has_refresh = 'refresh' in resp.data
        print(f"  Access token: {has_access}")
        print(f"  Refresh token: {has_refresh}")
        self.assertIn('access', resp.data, "Falta el token de acceso")
        self.assertIn('refresh', resp.data, "Falta el token de refresco")
        print("  ✓ Tokens JWT generados correctamente")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO")
        print("="*80)

    def test_login_owner_success(self):
        """
        PU002-2: Login exitoso propietario.
        Resultado esperado: Acceso correcto (código 200).
        """
        print("\n" + "="*80)
        print("TEST: PU002-2 - LOGIN EXITOSO PROPIETARIO")
        print("="*80)
        
        print("\n[MÓDULO] User Authentication (Owner role)")
        print("[ENTRADA]")
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'maria@propietario.com',
            'password': 'password123'
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Email: {payload['email']} (role: Owner)")
        
        print("\n[ESPERADO]")
        print("  Status: 200 OK")
        print("  Response: access token")
        
        print("\n[EJECUCIÓN]")
        resp = self.client.post(url, payload, format='json')
        
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 200)
        print("  ✓ Status correcto (200 OK)")
        self.assertIn('access', resp.data)
        print("  ✓ Access token generado")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO")
        print("="*80)

    def test_login_invalid_credentials(self):
        """
        PU002-3: Login con credenciales incorrectas.
        Resultado esperado: Error 400 (Bad Request).
        """
        print("\n" + "="*80)
        print("TEST: PU002-3 - LOGIN CON CREDENCIALES INCORRECTAS")
        print("="*80)
        
        print("\n[MÓDULO] User Authentication (invalid credentials)")
        print("[ENTRADA]")
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'juan@estudiante.com',
            'password': 'passwordINCORRECTO'
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Email: {payload['email']}")
        print(f"  Password: {payload['password']} (INCORRECTO)")
        
        print("\n[ESPERADO]")
        print("  Status: 400 BAD REQUEST")
        print("  Error: Credenciales inválidas")
        
        print("\n[EJECUCIÓN]")
        resp = self.client.post(url, payload, format='json')
        
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 400)
        print("  ✓ Status correcto (400 BAD REQUEST)")
        print("  ✓ Credenciales rechazadas correctamente")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO - VALIDACIÓN CORRECTA")
        print("="*80)

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
        print("\n" + "="*80)
        print("TEST: PU002-5 - LOGIN CON USUARIO NO REGISTRADO")
        print("="*80)
        
        print("\n[MÓDULO] User Authentication (non-existent user)")
        print("[ENTRADA]")
        url = reverse('token_obtain_pair')
        payload = {
            'email': 'noexiste@correo.com',
            'password': 'password123'
        }
        print(f"  Endpoint: POST {url}")
        print(f"  Email: {payload['email']} (NO EXISTE)")
        
        print("\n[ESPERADO]")
        print("  Status: 400 BAD REQUEST")
        print("  Error: Usuario no encontrado")
        
        print("\n[EJECUCIÓN]")
        resp = self.client.post(url, payload, format='json')
        
        print("\n[RESULTADO]")
        print(f"  Status obtenido: {resp.status_code}")
        self.assertEqual(resp.status_code, 400)
        print("  ✓ Status correcto (400 BAD REQUEST)")
        print("  ✓ Usuario inexistente rechazado")
        print("\n" + "="*80)
        print("✓ TEST EXITOSO - VALIDACIÓN CORRECTA")
        print("="*80)
