from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ramo, Carrera, Evaluacion

class DashboardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.carrera = Carrera.objects.create(nombre="Ingeniería Civil Informática", codigo="ICI")
        self.ramo = Ramo.objects.create(nombre="Programación Avanzada", codigo="PA101", carrera=self.carrera, usuario=self.user)
        self.evaluacion = Evaluacion.objects.create(nombre='Test Eval', ponderacion=20, nota=5.0, ramo=self.ramo)

    def test_dashboard_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Programación Avanzada")
        self.assertContains(response, "Promedio Actual")
        self.assertContains(response, '5.0')
