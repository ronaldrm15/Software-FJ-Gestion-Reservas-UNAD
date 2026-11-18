# -*- coding: utf-8 -*-
"""
Módulo 2: Clase Abstracta Base y Modelo de Cliente.
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Curso: Programación (213023) - UNAD.
"""

from abc import ABC, abstractmethod  # Herramientas para clases y métodos abstractos.
from datetime import datetime  # Para registrar la fecha de creación de cada entidad.
import re  # Expresiones regulares para validar el correo electrónico.

# Excepción personalizada del Módulo 1.
from excepciones_logs import ValidacionClienteError


# ==============================================================================
# 1. CLASE ABSTRACTA BASE DEL SISTEMA
# ==============================================================================

class EntidadSistema(ABC):
    """
    Clase abstracta que representa cualquier entidad de Software FJ
    (Clientes, Servicios, Reservas). Obliga a las subclases a implementar
    la validación de datos y el resumen de información.
    """

    def __init__(self, id_entidad: str):
        # Valida que el identificador no sea nulo ni una cadena vacía.
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValueError("El identificador de la entidad debe ser una cadena de texto no vacía.")
        # Almacena el identificador limpio de espacios.
        self._id_entidad = id_entidad.strip()
        # Marca de tiempo de creación del objeto.
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Estado activo por defecto.
        self._activo = True

    @property
    def id_entidad(self) -> str:
        """Propiedad de solo lectura: ID único de la entidad."""
        return self._id_entidad

    @property
    def fecha_creacion(self) -> str:
        """Propiedad de solo lectura: fecha de registro."""
        return self._fecha_creacion

    @property
    def activo(self) -> bool:
        """Indica si la entidad está habilitada operativamente."""
        return self._activo

    @activo.setter
    def activo(self, estado: bool) -> None:
        """Activa o desactiva la entidad verificando que sea booleano."""
        if not isinstance(estado, bool):
            raise TypeError("El estado 'activo' debe ser un valor booleano (True o False).")
        self._activo = estado

    @abstractmethod
    def validar_datos(self) -> bool:
        """Cada subclase debe implementar la verificación de su integridad."""
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Cada subclase debe retornar una descripción legible de la entidad."""
        pass


# ==============================================================================
# 2. CLASE CLIENTE CON ENCAPSULACIÓN Y VALIDACIONES ROBUSTAS
# ==============================================================================

class Cliente(EntidadSistema):
    """
    Cliente de Software FJ. Aplica encapsulación estricta (atributos privados __),
    validaciones de integridad y encadenamiento de excepciones.
    """

    def __init__(self, id_cliente: str, documento: str, nombre: str, correo: str, telefono: str):
        try:
            # Inicializa los atributos heredados de EntidadSistema.
            super().__init__(id_cliente)
            # Asigna mediante los setters para disparar las validaciones.
            self.documento = documento
            self.nombre = nombre
            self.correo = correo
            self.telefono = telefono
            # Validación integral final.
            self.validar_datos()
        except (ValueError, TypeError) as err_tecnico:
            # Encadenamiento de excepciones: conserva la causa técnica original.
            raise ValidacionClienteError(
                f"Fallo al registrar el cliente '{nombre}': {err_tecnico}"
            ) from err_tecnico

    # --- Documento de identidad ---
    @property
    def documento(self) -> str:
        """Número de documento de identidad."""
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        """Valida que sea numérico y tenga entre 6 y 15 dígitos."""
        if not isinstance(valor, str) or not valor.strip().isdigit():
            raise ValueError("El documento de identidad debe contener únicamente dígitos numéricos.")
        doc_limpio = valor.strip()
        if not (6 <= len(doc_limpio) <= 15):
            raise ValueError("El documento de identidad debe tener entre 6 y 15 dígitos.")
        self.__documento = doc_limpio

    # --- Nombre completo ---
    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida que sea una cadena de al menos 3 caracteres."""
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValueError("El nombre del cliente debe tener al menos 3 caracteres válidos.")
        self.__nombre = valor.strip().title()

    # --- Correo electrónico ---
    @property
    def correo(self) -> str:
        """Correo electrónico del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida el formato del correo mediante expresión regular."""
        if not isinstance(valor, str):
            raise TypeError("El correo electrónico debe ser una cadena de texto.")
        correo_limpio = valor.strip().lower()
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron_correo, correo_limpio):
            raise ValueError(f"El formato del correo electrónico '{valor}' no es válido.")
        self.__correo = correo_limpio

    # --- Teléfono de contacto ---
    @property
    def telefono(self) -> str:
        """Número telefónico de contacto."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida que contenga entre 7 y 15 dígitos numéricos."""
        if not isinstance(valor, str) or not valor.strip().isdigit():
            raise ValueError("El teléfono debe contener únicamente números sin espacios ni símbolos.")
        tel_limpio = valor.strip()
        if not (7 <= len(tel_limpio) <= 15):
            raise ValueError("El teléfono debe tener entre 7 y 15 dígitos.")
        self.__telefono = tel_limpio

    # --- Implementación de métodos abstractos ---
    def validar_datos(self) -> bool:
        """Verifica que todos los atributos privados estén poblados."""
        return all([
            bool(self.__documento),
            bool(self.__nombre),
            bool(self.__correo),
            bool(self.__telefono),
            self._activo
        ])

    def obtener_resumen(self) -> str:
        """Ficha resumida del cliente para reportes y logs."""
        estado = "Activo" if self._activo else "Inactivo"
        return (
            f"Cliente [{self.id_entidad}] | Doc: {self.__documento} | "
            f"Nombre: {self.__nombre} | Correo: {self.__correo} | "
            f"Tel: {self.__telefono} | Estado: {estado}"
        )

    def __str__(self) -> str:
        """Representación en cadena del cliente."""
        return self.obtener_resumen()
