# -*- coding: utf-8 -*-
"""
Módulo 1: Excepciones Personalizadas y Sistema de Logging.
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Curso: Programación (213023) - UNAD.
"""

import logging  # Librería estándar de Python para registro de eventos y errores en archivos.
from datetime import datetime  # Permite sellar con fecha y hora exacta cada excepción.


# ==============================================================================
# 1. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ==============================================================================

class SoftwareFJError(Exception):
    """
    Excepción base personalizada para todo el sistema de Software FJ.
    Hereda de Exception para poder capturar cualquier error propio del dominio.
    """

    def __init__(self, mensaje: str, codigo_error: str = "ERR-GENERAL"):
        # Llama al constructor de la clase padre con el mensaje descriptivo.
        super().__init__(mensaje)
        # Almacena el mensaje legible del error.
        self.mensaje = mensaje
        # Código identificador del error para rastrearlo en los logs.
        self.codigo_error = codigo_error
        # Instante exacto en que se originó la excepción.
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        # Representación con código, hora y detalle del fallo.
        return f"[{self.codigo_error}] ({self.timestamp}) -> {self.mensaje}"


class ValidacionClienteError(SoftwareFJError):
    """Datos personales del cliente inválidos (documento, correo, nombre, teléfono)."""

    def __init__(self, mensaje: str):
        # Código específico de validación de cliente.
        super().__init__(mensaje, codigo_error="ERR-CLIENTE-001")


class ServicioNoDisponibleError(SoftwareFJError):
    """Servicio inactivo, sin cupos o inventario, o con parámetros inválidos."""

    def __init__(self, mensaje: str):
        # Código específico de disponibilidad de servicio.
        super().__init__(mensaje, codigo_error="ERR-SERVICIO-002")


class ReservaInvalidaError(SoftwareFJError):
    """Operaciones no permitidas en reservas: duración inválida, cliente inexistente, estados ilegales."""

    def __init__(self, mensaje: str):
        # Código específico de gestión de reservas.
        super().__init__(mensaje, codigo_error="ERR-RESERVA-003")


class CalculoCostoError(SoftwareFJError):
    """Inconsistencias o parámetros fuera de rango en el cálculo de tarifas, impuestos o descuentos."""

    def __init__(self, mensaje: str):
        # Código específico de errores de cálculo.
        super().__init__(mensaje, codigo_error="ERR-CALCULO-004")


# ==============================================================================
# 2. GESTOR DE LOGS EN ARCHIVO (SIN BASE DE DATOS)
# ==============================================================================

class GestorLogs:
    """
    Administra el registro persistente de eventos, advertencias y errores en un
    archivo plano (.log), evitando duplicar manejadores de escritura.
    """

    def __init__(self, nombre_archivo: str = "sistema_software_fj.log"):
        # Guarda el nombre del archivo donde se almacenarán los registros.
        self.nombre_archivo = nombre_archivo
        # Obtiene una instancia nombrada del logger del sistema.
        self.logger = logging.getLogger("SoftwareFJ_Logger")
        # Nivel mínimo de captura: INFO (captura INFO, WARNING, ERROR y CRITICAL).
        self.logger.setLevel(logging.INFO)

        # Solo agrega el manejador si el logger aún no tiene uno (evita logs duplicados).
        if not self.logger.handlers:
            # Manejador de archivo UTF-8 para soportar tildes y caracteres en español.
            file_handler = logging.FileHandler(self.nombre_archivo, mode="a", encoding="utf-8")
            # Formato: Fecha/Hora | Nivel | Mensaje.
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            # Asocia el formato al manejador.
            file_handler.setFormatter(formatter)
            # Agrega el manejador al logger.
            self.logger.addHandler(file_handler)

    def registrar_info(self, mensaje: str) -> None:
        """Registra una operación exitosa o evento normal."""
        # Escribe una línea de nivel INFO.
        self.logger.info(mensaje)

    def registrar_advertencia(self, mensaje: str) -> None:
        """Registra una alerta que no detiene el flujo pero requiere atención."""
        # Escribe una línea de nivel WARNING.
        self.logger.warning(mensaje)

    def registrar_error(self, excepcion: Exception, contexto: str = "") -> None:
        """Registra una excepción capturada, incluyendo su causa encadenada (__cause__) si existe."""
        # Prefijo de contexto si fue proporcionado.
        prefijo = f"[{contexto}] " if contexto else ""
        # Si hubo encadenamiento (raise ... from ...), documenta también la causa original.
        if excepcion.__cause__ is not None:
            detalle = (
                f"{prefijo}{type(excepcion).__name__}: {excepcion} | "
                f"Causa original ({type(excepcion.__cause__).__name__}): {excepcion.__cause__}"
            )
        else:
            # Documenta solo la excepción principal.
            detalle = f"{prefijo}{type(excepcion).__name__}: {excepcion}"
        # Escribe el error completo con nivel ERROR.
        self.logger.error(detalle)
