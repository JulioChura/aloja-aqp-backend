# Tests de Accommodations

Estructura modular de pruebas para el módulo de alojamientos.

## Estructura

```
accommodations/
├── tests/
│   ├── __init__.py           # Exporta las clases de prueba
│   ├── fixtures.py           # Clase base y helpers para crear datos de prueba
│   └── test_pu005_filters.py # Pruebas del módulo PU005
└── tests.py                  # Punto de entrada (importa desde tests/)
```

## Archivos

### `fixtures.py`
Contiene la clase base `AccommodationTestBase` con:
- **setUp()**: Crea estados, tipos, propietario, universidades y servicios
- **Helpers para crear datos**:
  - `create_owner_profile()`: Crear propietarios
  - `create_university()`: Crear universidades
  - `create_campus()`: Crear campus universitarios
  - `create_accommodation()`: Crear alojamientos con parámetros personalizables
  - `create_university_distance()`: Crear distancias a universidades
  - `create_accommodation_with_distance()`: Crear alojamiento + distancia en un solo paso
  - `add_service_to_accommodation()`: Agregar servicios a alojamientos

### `test_pu005_filters.py`
Pruebas del módulo **PU005 - Búsqueda y filtrado de alojamientos**:
- **PU005-1**: Filtro de precio en rango [200, 500]
- **PU005-2**: Filtro solo con precio mínimo
- **PU005-3**: Filtro solo con precio máximo
- **PU005-4**: Verificar límites inclusivos
- **PU005-5**: Filtro por universidad con ordenamiento
- **PU005-6**: Filtro combinado (universidad + precio)
- **PU005-7**: Búsqueda sin resultados
- **PU005-8**: Filtro por campus específico

## Uso

### Ejecutar todas las pruebas de accommodations
```bash
python manage.py test accommodations
```

### Ejecutar solo las pruebas de filtros (PU005)
```bash
python manage.py test accommodations.tests.AccommodationFilterTests
```

### Ejecutar una prueba específica
```bash
python manage.py test accommodations.tests.AccommodationFilterTests.test_pu005_1_filtro_precio_rango_200_500
```

### Con verbose para más detalles
```bash
python manage.py test accommodations -v 2
```

## Agregar nuevas pruebas

### 1. Para un nuevo módulo (ej: PU006)

Crear archivo `test_pu006_nombre.py`:

```python
from .fixtures import AccommodationTestBase

class NuevoModuloTests(AccommodationTestBase):
    def setUp(self):
        super().setUp()
        # Configuración adicional si es necesario
    
    def test_pu006_1_descripcion(self):
        # Usar helpers de fixtures.py
        acc = self.create_accommodation('Test', '300.00')
        # ... resto de la prueba
```

Luego agregar en `__init__.py`:
```python
from .test_pu006_nombre import NuevoModuloTests
__all__ = [..., 'NuevoModuloTests']
```

### 2. Para agregar helpers en fixtures.py

```python
def create_mi_nuevo_helper(self, param1, param2):
    """Helper para crear algo específico"""
    # lógica
    return objeto_creado
```

## Ventajas de esta estructura

✅ **Separación de responsabilidades**: Datos de prueba vs lógica de prueba  
✅ **Reutilización**: Helpers compartidos entre todas las pruebas  
✅ **Mantenibilidad**: Fácil agregar nuevos módulos de prueba  
✅ **Legibilidad**: Código de prueba más limpio y conciso  
✅ **Organización**: Un archivo por módulo de prueba (PU005, PU006, etc.)
