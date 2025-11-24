from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch
from .models import User, OwnerProfile


class UserRegistrationTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_register_student_success(self):
		"""PU001-1: Registro exitoso de estudiante"""
		url = reverse('user-register')  # /api/register-student/
		payload = {
			'email': 'juan@estudiante.com',
			'password': 'password123',
			'first_name': 'Juan',
			'last_name': 'Pérez',
			'phone_number': '',
			'campuses': []
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, 201)
		self.assertIn('message', resp.data)
		self.assertEqual(resp.data['message'], 'Usuario registrado exitosamente')
		# user created
		self.assertTrue(User.objects.filter(email='juan@estudiante.com').exists())

	def test_register_owner_with_valid_dni(self):
		"""PU001-2: Registro exitoso de propietario con DNI válido"""
		# crear usuario y autenticar
		user = User.objects.create_user(email='maria@propietario.com', password='password123')
		self.client.force_authenticate(user=user)

		url = reverse('owner-register')  # /api/register-owner/
		payload = {
			'first_name': 'María',
			'last_name': 'García',
			'dni': '12345678',
			'phone_number': '',
			'contact_address': ''
		}

		# parchear la llamada a RENIEC para devolver nombres coincidentes
		with patch('users.serializers.verificar_dni') as mock_verificar:
			mock_verificar.return_value = {
				'first_name': 'María',
				'last_name_1': 'García',
				'last_name_2': ''
			}
			resp = self.client.post(url, payload, format='json')

		self.assertEqual(resp.status_code, 201)
		self.assertIn('message', resp.data)
		self.assertEqual(resp.data['message'], 'Perfil de propietario creado exitosamente')
		# OwnerProfile created and linked
		self.assertTrue(OwnerProfile.objects.filter(user__email='maria@propietario.com', dni='12345678').exists())

	def test_register_owner_with_invalid_dni(self):
		"""PU001-3: Registro propietario con DNI inválido"""
		user = User.objects.create_user(email='carlos@propietario.com', password='password123')
		self.client.force_authenticate(user=user)

		url = reverse('owner-register')
		payload = {
			'first_name': 'Carlos',
			'last_name': 'López',
			'dni': '99999999',
			'phone_number': '',
			'contact_address': ''
		}

		with patch('users.serializers.verificar_dni') as mock_verificar:
			# Simular que RENIEC no encuentra el DNI
			mock_verificar.return_value = None
			resp = self.client.post(url, payload, format='json')

		self.assertEqual(resp.status_code, 400)
		# Mensaje esperado definido en serializer: "DNI no encontrado en RENIEC." 
		self.assertTrue(any('DNI' in str(v) for v in resp.data.values()))

	def test_register_student_existing_email(self):
		"""PU001-4: Registro con correo ya existente"""
		# crear previamente un usuario con el email
		User.objects.create_user(email='juan@estudiante.com', password='password123')

		url = reverse('user-register')
		payload = {
			'email': 'juan@estudiante.com',
			'password': 'password456',
			'first_name': 'Ana',
			'last_name': 'Ruiz',
			'phone_number': '',
			'campuses': []
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, 400)
		# Debe indicar que el email ya está registrado
		self.assertIn('email', resp.data)
