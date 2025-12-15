#!/usr/bin/env python
"""
Script para ejecutar tests en orden específico con salida detallada.
Orden: users → accommodations → core
"""

import subprocess
import sys

def run_test(app_name, description):
    """Ejecuta los tests de una app específica."""
    print("\n" + "="*90)
    print(f"EJECUTANDO TESTS: {description}")
    print("="*90 + "\n")
    
    cmd = [sys.executable, "manage.py", "test", app_name, "-v", "2"]
    result = subprocess.run(cmd, cwd=".")
    
    return result.returncode == 0

def main():
    """Ejecuta los tests en orden."""
    print("\n" + "="*90)
    print("EJECUCIÓN DE TESTS EN ORDEN")
    print("="*90)
    
    tests = [
        ("users", "APP: USERS (Autenticación y Registro)"),
        ("accommodations", "APP: ACCOMMODATIONS (Gestión de Anuncios)"),
        ("core", "APP: CORE (Pruebas de Integración)")
    ]
    
    results = {}
    
    for app_name, description in tests:
        success = run_test(app_name, description)
        results[app_name] = "✓ EXITOSO" if success else "✗ FALLÓ"
    
    # Resumen final
    print("\n" + "="*90)
    print("RESUMEN DE RESULTADOS")
    print("="*90)
    
    for app_name, description in tests:
        status = results[app_name]
        print(f"{description}: {status}")
    
    print("="*90 + "\n")
    
    # Verificar si todos pasaron
    all_passed = all(status == "✓ EXITOSO" for status in results.values())
    
    if all_passed:
        print("✓ TODOS LOS TESTS PASARON EXITOSAMENTE\n")
        return 0
    else:
        print("✗ ALGUNOS TESTS FALLARON\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())