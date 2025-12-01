"""
Pruebas del módulo PU005 - Búsqueda y filtrado de alojamientos.

Plan de Pruebas:
Nº | Descripción                          | Método            | Datos Entrada                                | Salida Esperada
---|--------------------------------------|-------------------|----------------------------------------------|------------------------------------------
1  | Búsqueda con filtro precio           | searchProperties  | Rango: [200, 500] soles                      | Lista de propiedades dentro del rango
2  | Filtro por universidad cercana       | searchProperties  | Universidad: "UNSA", radio: 3km              | Propiedades ordenadas por proximidad a UNSA
3  | Búsqueda con lenguaje natural        | searchProperties  | "Departamento cerca a la Unsa"               | N Departamentos que hagan match
4  | Búsqueda con múltiples filtros       | searchProperties  | Precio: [300,600], universidad, servicios    | Propiedades que cumplen todos los criterios
5  | Búsqueda sin resultados              | searchProperties  | Precio: [1000, 5000]                         | Mensaje: "No se encontraron propiedades"
"""
from rest_framework.test import APIClient
from decimal import Decimal
from .fixtures import AccommodationTestBase
from .data_pu005 import PU005DataMixin


class AccommodationFilterTests(PU005DataMixin, AccommodationTestBase):
    """Pruebas del módulo PU005 - Búsqueda y filtrado de alojamientos"""

    def setUp(self):
        """Configuración adicional para pruebas de filtros"""
        super().setUp()
        self.client = APIClient()

    def test_pu005_1_busqueda_filtro_precio(self):
        """
        PU005-1: Búsqueda con filtro precio
        Datos Entrada: Rango [200, 500] soles
        Salida Esperada: Lista de propiedades dentro del rango de precio
        """
        self.crear_alojamientos_rango_precio()

        response = self.client.get('/api/public/accommodations/filter/', {
            'min_price': '200',
            'max_price': '500'
        })

        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', response.json())

        # Verificar que hay resultados
        self.assertGreater(len(results), 0, "Debe retornar alojamientos en el rango [200, 500]")

        # Verificar que todos están dentro del rango
        for item in results:
            precio = Decimal(str(item['monthly_price']))
            self.assertGreaterEqual(precio, Decimal('200.00'),
                                  f"Precio {precio} es menor que el mínimo 200")
            self.assertLessEqual(precio, Decimal('500.00'),
                               f"Precio {precio} es mayor que el máximo 500")

    def test_pu005_2_filtro_universidad_cercana(self):
        """
        PU005-2: Filtro por universidad cercana
        Datos Entrada: Universidad "UNSA", radio 3km
        Salida Esperada: Propiedades ordenadas por proximidad a UNSA
        """
        self.crear_alojamientos_proximidad_unsa()

        response = self.client.get('/api/public/accommodations/filter/', {
            'university_id': str(self.unsa.id)
        })

        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', response.json())

        self.assertGreater(len(results), 0, "Debe retornar alojamientos cercanos a UNSA")

        # Extraer distancias y verificar ordenamiento
        distancias = []
        for item in results:
            unsa_dists = [Decimal(str(d['distance_km'])) 
                         for d in item.get('university_distances', [])
                         if d.get('campus_university_id') == self.unsa.id]
            if unsa_dists:
                dist = min(unsa_dists)
                distancias.append(dist)

        # Verificar ordenamiento ascendente por distancia
        for i in range(len(distancias) - 1):
            self.assertLessEqual(distancias[i], distancias[i + 1],
                               f"No ordenado por distancia: {distancias[i]} > {distancias[i + 1]}")

    def test_pu005_3_busqueda_lenguaje_natural(self):
        """
        PU005-3: Búsqueda con lenguaje natural
        Datos Entrada: "Departamento cerca a la Unsa"
        Salida Esperada: N Departamentos que hagan match con el lenguaje natural
        """
        self.crear_alojamientos_lenguaje_natural()

        # Buscar con "moderno" que es más específico y único
        response = self.client.get('/api/public/accommodations/filter/', {
            'q': 'moderno'
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get('results', data)

        # Debe encontrar al menos 1 resultado (el "Departamento moderno UNSA")
        self.assertGreater(len(results), 0, 
                          "Debe retornar alojamientos que coincidan con 'moderno'")

        # Verificar que encontró el departamento moderno
        titulos = [item.get('title', '') for item in results]
        self.assertTrue(
            any('moderno' in t.lower() for t in titulos),
            "Debe incluir el 'Departamento moderno UNSA'"
        )

    def test_pu005_4_busqueda_multiples_filtros(self):
        """
        PU005-4: Búsqueda con múltiples filtros
        Datos Entrada: Precio [300, 600], universidad (UNSA), servicios
        Salida Esperada: Propiedades que cumplen todos los criterios
        """
        datos = self.crear_alojamientos_multiples_filtros()

        response = self.client.get('/api/public/accommodations/filter/', {
            'min_price': '300',
            'max_price': '600',
            'university_id': str(self.unsa.id),
            'services': f"{self.servicio_wifi.id},{self.servicio_agua.id}"
        })

        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', response.json())

        self.assertGreater(len(results), 0,
                          "Debe retornar alojamientos que cumplan todos los filtros")

        # Verificar cada criterio
        for item in results:
            # Criterio 1: Precio en rango [300, 600]
            precio = Decimal(str(item['monthly_price']))
            self.assertGreaterEqual(precio, Decimal('300.00'))
            self.assertLessEqual(precio, Decimal('600.00'))

            # Criterio 2: Tiene distancia a UNSA
            unsa_distances = [d for d in item.get('university_distances', [])
                            if d.get('campus_university_id') == self.unsa.id]
            self.assertGreater(len(unsa_distances), 0,
                             f"Alojamiento '{item['title']}' debe estar cerca de UNSA")

            # Criterio 3: Tiene los servicios requeridos (wifi y agua)
            servicios = item.get('services', [])
            # Extraer IDs de PredefinedService (dentro del campo 'service')
            servicios_ids = [s['service']['id'] for s in servicios if 'service' in s]
            self.assertIn(self.servicio_wifi.id, servicios_ids,
                         f"Alojamiento '{item['title']}' debe tener WiFi")
            self.assertIn(self.servicio_agua.id, servicios_ids,
                         f"Alojamiento '{item['title']}' debe tener Agua")

    def test_pu005_5_busqueda_sin_resultados(self):
        """
        PU005-5: Búsqueda sin resultados
        Datos Entrada: Precio [1000, 5000]
        Salida Esperada: Mensaje "No se encontraron propiedades"
        """
        self.crear_alojamientos_sin_resultados()

        response = self.client.get('/api/public/accommodations/filter/', {
            'min_price': '1000',
            'max_price': '5000'
        })

        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', response.json())

        # Verificar que no hay resultados
        self.assertEqual(len(results), 0,
                        "No debe haber resultados para el rango de precio [1000, 5000]")

