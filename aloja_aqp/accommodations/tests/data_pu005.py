"""
Datos de prueba específicos para el módulo PU005 - Filtrado de alojamientos.

Este archivo contiene métodos para crear escenarios de datos completos para cada prueba.
Alineado con el plan de pruebas:
1. Búsqueda con filtro precio [200, 500]
2. Filtro por universidad cercana (UNSA, radio 3km)
3. Búsqueda con lenguaje natural ("Departamento cerca a la Unsa")
4. Búsqueda con múltiples filtros (precio, universidad, servicios)
5. Búsqueda sin resultados [1000, 5000]
"""
from decimal import Decimal


class PU005DataMixin:
    """Mixin con métodos para crear datos específicos de pruebas PU005"""

    def crear_alojamientos_rango_precio(self):
        """
        PU005-1: Crea alojamientos para probar filtro de precio [200, 500].
        
        Returns:
            dict: Diccionario con alojamientos dentro y fuera del rango
        """
        # Alojamientos FUERA del rango [200, 500]
        fuera_rango = [
            self.create_accommodation('Muy económico', '150.00', address='Calle Barata 1'),
            self.create_accommodation('Caro', '550.00', rooms=2, address='Calle Cara 2'),
            self.create_accommodation('Muy caro', '650.00', rooms=3, address='Calle Lujosa 3'),
        ]

        # Alojamientos DENTRO del rango [200, 500]
        dentro_rango = [
            self.create_accommodation('Límite inferior', '200.00', address='Calle Min'),
            self.create_accommodation('Económico en rango', '250.00', address='Calle Media'),
            self.create_accommodation('Moderado', '350.00', rooms=2, address='Calle Normal'),
            self.create_accommodation('Estándar alto', '450.00', rooms=2, address='Calle Buena'),
            self.create_accommodation('Límite superior', '500.00', rooms=3, address='Calle Max'),
        ]

        return {
            'fuera_rango': fuera_rango,
            'dentro_rango': dentro_rango
        }

    def crear_alojamientos_proximidad_unsa(self):
        """
        PU005-2: Crea alojamientos a diferentes distancias de UNSA (dentro de 3km).
        
        Returns:
            list: Lista de alojamientos ordenados por distancia
        """
        alojamientos = [
            self.create_accommodation_with_distance(
                title='Al lado de UNSA',
                price='450.00',
                campus=self.campus_unsa,
                distance_km='0.5',
                walk_time=5,
                bus_time=2,
                rooms=2,
                address='Av. Independencia 100',
                latitude=-16.4010,
                longitude=-71.5376
            ),
            self.create_accommodation_with_distance(
                title='Cerca a UNSA',
                price='400.00',
                campus=self.campus_unsa,
                distance_km='1.5',
                walk_time=15,
                bus_time=5,
                rooms=2,
                address='Av. Venezuela 200',
                latitude=-16.4050,
                longitude=-71.5400
            ),
            self.create_accommodation_with_distance(
                title='En el límite de UNSA',
                price='350.00',
                campus=self.campus_unsa,
                distance_km='2.8',
                walk_time=30,
                bus_time=10,
                rooms=1,
                address='Av. Dolores 300',
                latitude=-16.4100,
                longitude=-71.5450
            ),
        ]

        return alojamientos

    def crear_alojamientos_lenguaje_natural(self):
        """
        PU005-3: Crea departamentos cerca de UNSA para búsqueda por lenguaje natural.
        
        Returns:
            list: Lista de departamentos cerca de UNSA
        """
        # Tipo "Departamento" ya está creado en setUp de fixtures
        alojamientos = [
            self.create_accommodation_with_distance(
                title='Departamento moderno UNSA',
                price='400.00',
                accommodation_type=self.tipo_departamento,
                campus=self.campus_unsa,
                distance_km='0.8',
                walk_time=10,
                bus_time=5,
                rooms=2,
                address='Av. Independencia 150'
            ),
            self.create_accommodation_with_distance(
                title='Departamento amplio cerca UNSA',
                price='500.00',
                accommodation_type=self.tipo_departamento,
                campus=self.campus_unsa,
                distance_km='1.2',
                walk_time=15,
                bus_time=7,
                rooms=3,
                address='Av. Parra 200'
            ),
            # Un cuarto para verificar que NO se incluye
            self.create_accommodation(
                title='Cuarto económico',
                price='250.00',
                accommodation_type=self.tipo_cuarto,
                rooms=1,
                address='Calle Lejos 500'
            ),
        ]

        return alojamientos

    def crear_alojamientos_multiples_filtros(self):
        """
        PU005-4: Crea alojamientos para probar filtros combinados.
        Precio [300, 600] + Universidad UNSA + Servicios (WiFi, Agua)
        
        Returns:
            dict: Diccionario con alojamientos que cumplen/no cumplen criterios
        """
        # Alojamientos que CUMPLEN todos los criterios
        cumplen = []
        
        alo1 = self.create_accommodation_with_distance(
            title='Depto con todo',
            price='350.00',
            campus=self.campus_unsa,
            distance_km='1.0',
            walk_time=12,
            bus_time=6,
            rooms=2,
            address='Calle Completa 1'
        )
        self.add_service_to_accommodation(alo1, self.servicio_wifi)
        self.add_service_to_accommodation(alo1, self.servicio_agua)
        cumplen.append(alo1)

        alo2 = self.create_accommodation_with_distance(
            title='Casa equipada UNSA',
            price='500.00',
            campus=self.campus_unsa,
            distance_km='1.5',
            walk_time=18,
            bus_time=8,
            rooms=3,
            address='Calle Completa 2'
        )
        self.add_service_to_accommodation(alo2, self.servicio_wifi)
        self.add_service_to_accommodation(alo2, self.servicio_agua)
        cumplen.append(alo2)

        # Alojamientos que NO CUMPLEN (precio fuera de rango)
        alo3 = self.create_accommodation_with_distance(
            title='Muy caro UNSA',
            price='700.00',  # Fuera del rango [300, 600]
            campus=self.campus_unsa,
            distance_km='0.8',
            walk_time=10,
            bus_time=5,
            rooms=2,
            address='Calle Cara 1'
        )
        self.add_service_to_accommodation(alo3, self.servicio_wifi)
        self.add_service_to_accommodation(alo3, self.servicio_agua)

        # Alojamiento sin servicios
        alo4 = self.create_accommodation_with_distance(
            title='Sin servicios UNSA',
            price='400.00',
            campus=self.campus_unsa,
            distance_km='1.2',
            walk_time=15,
            bus_time=7,
            rooms=2,
            address='Calle Incompleta 1'
        )
        # No tiene WiFi ni Agua

        return {
            'cumplen_criterios': cumplen,
            'precio_fuera_rango': [alo3],
            'sin_servicios': [alo4]
        }

    def crear_alojamientos_sin_resultados(self):
        """
        PU005-5: Crea alojamientos con precios moderados para probar búsqueda sin resultados.
        
        Returns:
            list: Lista de alojamientos con precios fuera del rango [1000, 5000]
        """
        alojamientos = [
            self.create_accommodation('Moderado 1', '500.00', rooms=2, address='Calle A'),
            self.create_accommodation('Moderado 2', '600.00', rooms=2, address='Calle B'),
            self.create_accommodation('Económico', '300.00', rooms=1, address='Calle C'),
        ]

        return alojamientos

