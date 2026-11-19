# Software FJ – Gestión de Clientes, Servicios y Reservas

Sistema Integral de Gestión de Clientes, Servicios y Reservas (POO y manejo avanzado de excepciones).
Proyecto de la **Fase 4 – Prácticas simuladas** del curso **Programación (213023)** de la
**Universidad Nacional Abierta y a Distancia (UNAD)**.

## Descripción

Aplicación orientada a objetos en **Python 3.10 o superior**, sin bases de datos, que administra en memoria
los clientes, servicios y reservas de la empresa Software FJ. Cada error se captura, se registra en el archivo
`sistema_software_fj.log` y el programa continúa funcionando.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `excepciones_logs.py` | Excepciones personalizadas (`SoftwareFJError` y 4 derivadas) y gestor de logs. |
| `modelos_base.py` | Clase abstracta `EntidadSistema` y clase `Cliente` (encapsulación y validaciones). |
| `servicios.py` | Clase abstracta `Servicio` y 3 servicios: `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`. Sobrecarga con `@singledispatchmethod`. |
| `reservas.py` | Clase `Reserva` (estados PENDIENTE, CONFIRMADA, PROCESADA, CANCELADA) y `GestorSoftwareFJ` con `try/except/else/finally`. |
| `main.py` | Punto de entrada: abre la interfaz gráfica (o la simulación por consola con `--consola`). |
| `interfaz_grafica.py` | Interfaz gráfica con Tkinter (clientes, servicios, reservas, visor de logs y simulación). |
| `simulacion.py` | Simulación de 14 operaciones (válidas e inválidas) que usa la pestaña Simulación y la consola. |
| `sistema_software_fj.log` | Archivo de auditoría generado por la simulación. |

## Conceptos aplicados

- **Abstracción y herencia:** `EntidadSistema` → `Cliente`, `Servicio`, `Reserva`; `Servicio` → 3 servicios.
- **Polimorfismo:** `calcular_costo_base()` y `verificar_disponibilidad()` se comportan distinto en cada servicio.
- **Sobrecarga:** `calcular_total()` acepta las horas (`int`) o un diccionario (`dict`).
- **Encapsulación:** atributos privados con `@property` en `Cliente`.
- **Excepciones:** personalizadas, `try/except/else/finally` y encadenamiento con `raise ... from ...`.

## Ejecución

```bash
# Interfaz gráfica (Tkinter viene incluido con Python)
python main.py

# Simulación de 14 operaciones por consola, sin ventana (genera sistema_software_fj.log)
python main.py --consola
```

El log se abre en modo "agregar": borre `sistema_software_fj.log` antes de ejecutar si desea un registro limpio.

## Integrantes

- Ronald Estiven Rodríguez Mora
- David Santiago Ruiz
- Wilian Alejandro Barreto

