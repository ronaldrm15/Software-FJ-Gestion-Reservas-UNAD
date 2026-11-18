# -*- coding: utf-8 -*-
"""
Punto de entrada del Sistema Integral Software FJ.
Por defecto abre la interfaz gráfica (Tkinter), desde la cual se gestionan clientes,
servicios y reservas, se consulta el log y se ejecuta la simulación de 14 operaciones.
Proyecto: Fase 4 - Programación (213023) - UNAD.

Uso:
    python main.py            -> abre la interfaz gráfica
    python main.py --consola  -> ejecuta la simulación por consola (sin ventana)
"""

import sys  # Permite leer los argumentos de la línea de comandos.


def iniciar() -> None:
    """Abre la interfaz gráfica o, si se pide, ejecuta la simulación en consola."""
    # Modo consola: útil en equipos sin entorno gráfico.
    if "--consola" in sys.argv:
        from simulacion import ejecutar_simulacion
        ejecutar_simulacion()
        return

    try:
        # Importa la interfaz solo cuando se necesita (requiere Tkinter instalado).
        from interfaz_grafica import AppSoftwareFJ
    except ImportError:
        # Tkinter no está disponible en este equipo: informa cómo continuar sin cerrarse con un traceback.
        print("No se encontró Tkinter. En Windows y macOS viene con Python;")
        print("en Linux instálelo con: sudo apt install python3-tk")
        print("Mientras tanto puede usar: python main.py --consola")
        return

    # Crea la ventana principal y arranca el ciclo de eventos de Tkinter.
    AppSoftwareFJ().mainloop()


if __name__ == "__main__":
    iniciar()
