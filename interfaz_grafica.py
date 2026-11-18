# -*- coding: utf-8 -*-
"""
Módulo 6: Interfaz gráfica (Tkinter) del Sistema Integral Software FJ.
Reutiliza los módulos 1 a 5 sin modificarlos: la ventana solo llama al
GestorSoftwareFJ, de modo que todas las validaciones, excepciones y registros
en el archivo de logs siguen funcionando igual que en consola.
Proyecto: Fase 4 - Programación (213023_2204) - UNAD.
Ejecución: python main.py  (o directamente: python interfaz_grafica.py)
"""

import contextlib  # Permite redirigir temporalmente lo que imprime la simulación.
import io  # Proporciona un búfer de texto en memoria para capturar esa salida.
import os  # Permite comprobar si el archivo de logs ya existe.
import tkinter as tk  # Biblioteca estándar de interfaces gráficas.
from tkinter import ttk, messagebox  # Widgets con estilo y cuadros de mensaje.

# Importa las excepciones, el modelo de cliente, los servicios y el gestor del proyecto.
from excepciones_logs import SoftwareFJError, ServicioNoDisponibleError, ReservaInvalidaError
from modelos_base import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import GestorSoftwareFJ
import simulacion  # Reutiliza la simulación de 14 operaciones del módulo 5.

ARCHIVO_LOG = "sistema_software_fj.log"  # Nombre del archivo de auditoría.

# ==============================================================================
# PALETA DE COLORES Y FUENTES
# ==============================================================================
C = {
    "header": "#1F3A5F",    # Azul oscuro del encabezado.
    "accent": "#F5A623",    # Naranja de acento (pestaña activa, foco).
    "fondo": "#F4F6FA",     # Gris muy claro del fondo general.
    "panel": "#FFFFFF",     # Blanco de los paneles y formularios.
    "borde": "#C9D1E0",     # Gris azulado de los bordes.
    "texto": "#1B2430",     # Texto principal.
    "ok": "#2E7D32",        # Verde de éxito.
    "error": "#C62828",     # Rojo de error.
    "info": "#1565C0",      # Azul informativo.
    "gris": "#5F6B7A",      # Gris de botones secundarios.
    "log_bg": "#1E1E2E",    # Fondo oscuro del visor de logs.
}
# Color de cada botón y su versión más oscura para el efecto hover.
HOVER = {C["info"]: "#0D47A1", C["ok"]: "#1B5E20", C["error"]: "#8E0000",
         C["gris"]: "#3E4853", C["accent"]: "#D98A0B"}
FUENTE = ("Segoe UI", 10)
FUENTE_B = ("Segoe UI", 10, "bold")


class AppSoftwareFJ(tk.Tk):
    """Ventana principal con pestañas para clientes, servicios, reservas, logs y simulación."""

    def __init__(self):
        super().__init__()
        self.title("Software FJ - Gestión de Clientes, Servicios y Reservas")
        self.geometry("1120x720")
        self.minsize(980, 640)
        self.configure(bg=C["fondo"])

        # Gestor central: mantiene las listas en memoria y escribe el log.
        self.gestor = GestorSoftwareFJ(ARCHIVO_LOG)

        self._configurar_estilos()
        self._crear_encabezado()

        # Barra de estado inferior (se crea antes que las pestañas para poder usarla).
        self.estado = tk.Label(self, text="Listo.", anchor="w", padx=12, pady=6,
                               bg=C["info"], fg="white", font=FUENTE_B)
        self.estado.pack(side="bottom", fill="x")

        # Contenedor de pestañas.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=10)
        self._crear_tab_clientes()
        self._crear_tab_servicios()
        self._crear_tab_reservas()
        self._crear_tab_logs()
        self._crear_tab_simulacion()
        # Al cambiar de pestaña se actualizan los datos mostrados.
        self.notebook.bind("<<NotebookTabChanged>>", lambda _e: self._refrescar_todo())
        self._refrescar_todo()

    # ==========================================================================
    # ESTILOS Y COMPONENTES REUTILIZABLES
    # ==========================================================================
    def _configurar_estilos(self):
        """Define el tema ttk: pestañas, tablas y listas desplegables."""
        est = ttk.Style(self)
        est.theme_use("clam")
        est.configure("TNotebook", background=C["fondo"], borderwidth=0)
        est.configure("TNotebook.Tab", padding=(18, 8), font=FUENTE_B,
                      background=C["borde"], foreground=C["texto"])
        est.map("TNotebook.Tab", background=[("selected", C["accent"])],
                foreground=[("selected", "white")])
        est.configure("Treeview", rowheight=26, font=FUENTE, background=C["panel"],
                      fieldbackground=C["panel"], foreground=C["texto"])
        est.configure("Treeview.Heading", font=FUENTE_B, background=C["header"],
                      foreground="white", relief="flat")
        est.map("Treeview.Heading", background=[("active", C["info"])])
        est.map("Treeview", background=[("selected", C["info"])],
                foreground=[("selected", "white")])
        est.configure("TCombobox", padding=4)

    def _crear_encabezado(self):
        """Franja superior con el nombre del sistema."""
        marco = tk.Frame(self, bg=C["header"])
        marco.pack(fill="x")
        tk.Label(marco, text="SOFTWARE FJ", bg=C["header"], fg=C["accent"],
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=(18, 8), pady=12)
        tk.Label(marco, text="Sistema Integral de Gestión de Clientes, Servicios y Reservas",
                 bg=C["header"], fg="white", font=("Segoe UI", 12)).pack(side="left", pady=12)

    def _boton(self, padre, texto, comando, color):
        """Crea un botón de color con efecto hover (cambia al pasar el cursor)."""
        b = tk.Button(padre, text=texto, command=comando, bg=color, fg="white",
                      activebackground=HOVER[color], activeforeground="white",
                      font=FUENTE_B, relief="flat", cursor="hand2", padx=14, pady=6, bd=0)
        b.bind("<Enter>", lambda _e: b.config(bg=HOVER[color]))
        b.bind("<Leave>", lambda _e: b.config(bg=color))
        return b

    def _entrada(self, padre, ancho=24):
        """Crea un campo de texto con borde que se resalta al recibir el foco."""
        return tk.Entry(padre, width=ancho, font=FUENTE, relief="flat", bg="white",
                        highlightthickness=1, highlightbackground=C["borde"],
                        highlightcolor=C["accent"])

    def _panel(self, padre, titulo):
        """Crea un panel blanco con título para agrupar un formulario."""
        return tk.LabelFrame(padre, text=f"  {titulo}  ", bg=C["panel"], fg=C["header"],
                             font=FUENTE_B, padx=14, pady=12, bd=1, relief="solid")

    def _tabla(self, padre, columnas, anchos):
        """Crea un Treeview con barra de desplazamiento y filas alternadas."""
        marco = tk.Frame(padre, bg=C["fondo"])
        marco.pack(fill="both", expand=True, pady=(10, 0))
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=8)
        for col, ancho in zip(columnas, anchos):
            tabla.heading(col, text=col)
            tabla.column(col, width=ancho, anchor="w")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        # Colores de fila: alternadas y por estado de reserva.
        tabla.tag_configure("par", background="#FFFFFF")
        tabla.tag_configure("impar", background="#EEF2FA")
        tabla.tag_configure("PENDIENTE", background="#FFF4CC")
        tabla.tag_configure("CONFIRMADA", background="#DDF3E0")
        tabla.tag_configure("PROCESADA", background="#D6E8FA")
        tabla.tag_configure("CANCELADA", background="#F9D9D9")
        return tabla

    def _exito(self, mensaje):
        """Muestra un mensaje de éxito en la barra de estado (verde)."""
        self.estado.config(text=f"✔ {mensaje}", bg=C["ok"])

    def _error(self, mensaje):
        """Muestra un error en un cuadro de diálogo y en la barra de estado (rojo)."""
        self.estado.config(text=f"✖ {mensaje}", bg=C["error"])
        messagebox.showerror("Error controlado", mensaje)

    def _ultimo_error_log(self):
        """Devuelve el mensaje del último ERROR escrito en el log (o un texto genérico)."""
        try:
            with open(ARCHIVO_LOG, encoding="utf-8", errors="replace") as f:
                for linea in reversed(f.readlines()):
                    if "| ERROR" in linea:
                        partes = linea.strip().split(" | ", 2)
                        return partes[2] if len(partes) == 3 else linea.strip()
        except OSError:
            pass
        return "La operación no se pudo completar. Revise el archivo de logs."

    # ==========================================================================
    # PESTAÑA 1: CLIENTES
    # ==========================================================================
    def _crear_tab_clientes(self):
        tab = tk.Frame(self.notebook, bg=C["fondo"], padx=14, pady=14)
        self.notebook.add(tab, text="  Clientes  ")
        panel = self._panel(tab, "Registrar cliente")
        panel.pack(fill="x")

        etiquetas = [("id", "ID (ej. CLI-01)"), ("documento", "Documento"), ("nombre", "Nombre completo"),
                     ("correo", "Correo"), ("telefono", "Teléfono")]
        self.e_cli = {}
        for i, (clave, texto) in enumerate(etiquetas):
            fila, col = divmod(i, 3)
            tk.Label(panel, text=texto, bg=C["panel"], fg=C["texto"], font=FUENTE).grid(
                row=fila * 2, column=col, sticky="w", padx=8)
            self.e_cli[clave] = self._entrada(panel)
            self.e_cli[clave].grid(row=fila * 2 + 1, column=col, padx=8, pady=(0, 8), sticky="we")

        botones = tk.Frame(panel, bg=C["panel"])
        botones.grid(row=4, column=0, columnspan=3, sticky="w", padx=8, pady=(4, 0))
        self._boton(botones, "Registrar cliente", self._registrar_cliente, C["ok"]).pack(side="left", padx=(0, 8))
        self._boton(botones, "Limpiar", self._limpiar_cliente, C["gris"]).pack(side="left")

        self.t_cli = self._tabla(tab, ("ID", "Documento", "Nombre", "Correo", "Teléfono", "Estado"),
                                 (90, 120, 240, 260, 120, 90))

    def _registrar_cliente(self):
        """Crea el Cliente (con validaciones) y lo registra; los errores se capturan y se registran."""
        v = {k: e.get() for k, e in self.e_cli.items()}
        try:
            cliente = Cliente(v["id"], v["documento"], v["nombre"], v["correo"], v["telefono"])
            if self.gestor.registrar_cliente(cliente):
                self._exito(f"Cliente {cliente.id_entidad} registrado correctamente.")
                self._limpiar_cliente()
            else:
                self._error("No se registró: ya existe un cliente con ese ID o documento.")
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_RegistroCliente")
            self._error(str(err))
        self._refrescar_todo()

    def _limpiar_cliente(self):
        for e in self.e_cli.values():
            e.delete(0, "end")

    # ==========================================================================
    # PESTAÑA 2: SERVICIOS
    # ==========================================================================
    def _crear_tab_servicios(self):
        tab = tk.Frame(self.notebook, bg=C["fondo"], padx=14, pady=14)
        self.notebook.add(tab, text="  Servicios  ")
        panel = self._panel(tab, "Crear servicio")
        panel.pack(fill="x")

        tk.Label(panel, text="Tipo de servicio", bg=C["panel"], font=FUENTE).grid(row=0, column=0, sticky="w", padx=8)
        self.cb_tipo = ttk.Combobox(panel, values=["Sala", "Equipo", "Asesoría"], state="readonly", width=22)
        self.cb_tipo.current(0)
        self.cb_tipo.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="we")
        self.cb_tipo.bind("<<ComboboxSelected>>", lambda _e: self._actualizar_extras())

        self.e_srv = {}
        for i, (clave, texto) in enumerate([("id", "ID (ej. SRV-01)"), ("nombre", "Nombre del servicio"),
                                            ("tarifa", "Tarifa por hora")], start=1):
            tk.Label(panel, text=texto, bg=C["panel"], font=FUENTE).grid(row=0, column=i, sticky="w", padx=8)
            self.e_srv[clave] = self._entrada(panel)
            self.e_srv[clave].grid(row=1, column=i, padx=8, pady=(0, 8), sticky="we")

        # Campos específicos: sus etiquetas cambian según el tipo de servicio elegido.
        self.var_x1, self.var_x2 = tk.StringVar(), tk.StringVar()
        self.l_x1 = tk.Label(panel, textvariable=self.var_x1, bg=C["panel"], font=FUENTE)
        self.l_x2 = tk.Label(panel, textvariable=self.var_x2, bg=C["panel"], font=FUENTE)
        self.e_x1, self.e_x2 = self._entrada(panel), self._entrada(panel)
        self.l_x1.grid(row=2, column=0, sticky="w", padx=8)
        self.e_x1.grid(row=3, column=0, padx=8, pady=(0, 8), sticky="we")
        self.l_x2.grid(row=2, column=1, sticky="w", padx=8)
        self.e_x2.grid(row=3, column=1, padx=8, pady=(0, 8), sticky="we")

        botones = tk.Frame(panel, bg=C["panel"])
        botones.grid(row=4, column=0, columnspan=4, sticky="w", padx=8, pady=(4, 0))
        self._boton(botones, "Crear servicio", self._crear_servicio, C["ok"]).pack(side="left", padx=(0, 8))
        self._boton(botones, "Limpiar", self._limpiar_servicio, C["gris"]).pack(side="left")
        self._actualizar_extras()

        self.t_srv = self._tabla(tab, ("ID", "Tipo", "Nombre", "Tarifa/hora", "Estado"),
                                 (90, 120, 330, 140, 200))

    def _actualizar_extras(self):
        """Cambia las etiquetas de los campos específicos según el tipo de servicio."""
        tipo = self.cb_tipo.get()
        if tipo == "Sala":
            self.var_x1.set("Capacidad máxima (personas)")
            self.l_x2.grid_remove()
            self.e_x2.grid_remove()
        elif tipo == "Equipo":
            self.var_x1.set("Stock disponible (unidades)")
            self.var_x2.set("Seguro por hora")
            self.l_x2.grid()
            self.e_x2.grid()
        else:
            self.var_x1.set("Especialidad")
            self.var_x2.set("Consultor asignado")
            self.l_x2.grid()
            self.e_x2.grid()

    def _crear_servicio(self):
        """Convierte los datos, crea el servicio del tipo elegido y lo registra en el catálogo."""
        tipo = self.cb_tipo.get()
        id_s, nombre = self.e_srv["id"].get(), self.e_srv["nombre"].get()
        try:
            try:
                tarifa = float(self.e_srv["tarifa"].get().replace(",", "."))
                if tipo == "Sala":
                    servicio = ReservaSala(id_s, nombre, tarifa, int(self.e_x1.get()))
                elif tipo == "Equipo":
                    servicio = AlquilerEquipo(id_s, nombre, tarifa, int(self.e_x1.get()),
                                              float(self.e_x2.get().replace(",", ".")))
                else:
                    servicio = AsesoriaEspecializada(id_s, nombre, tarifa, self.e_x1.get(), self.e_x2.get())
            except ValueError as err_tecnico:
                # Encadenamiento: el error de conversión numérica se relanza como error de dominio.
                raise ServicioNoDisponibleError(
                    f"Datos numéricos inválidos para el servicio '{nombre}': {err_tecnico}"
                ) from err_tecnico
            if self.gestor.registrar_servicio(servicio):
                self._exito(f"Servicio {servicio.id_entidad} creado correctamente.")
                self._limpiar_servicio()
            else:
                self._error("No se registró: ya existe un servicio con ese ID.")
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_CreacionServicio")
            self._error(str(err))
        self._refrescar_todo()

    def _limpiar_servicio(self):
        for e in list(self.e_srv.values()) + [self.e_x1, self.e_x2]:
            e.delete(0, "end")

    # ==========================================================================
    # PESTAÑA 3: RESERVAS
    # ==========================================================================
    def _crear_tab_reservas(self):
        tab = tk.Frame(self.notebook, bg=C["fondo"], padx=14, pady=14)
        self.notebook.add(tab, text="  Reservas  ")
        panel = self._panel(tab, "Crear y confirmar reserva")
        panel.pack(fill="x")

        tk.Label(panel, text="Cliente", bg=C["panel"], font=FUENTE).grid(row=0, column=0, sticky="w", padx=8)
        self.cb_cli = ttk.Combobox(panel, state="readonly", width=30)
        self.cb_cli.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="we")
        tk.Label(panel, text="Servicio", bg=C["panel"], font=FUENTE).grid(row=0, column=1, sticky="w", padx=8)
        self.cb_srv = ttk.Combobox(panel, state="readonly", width=34)
        self.cb_srv.grid(row=1, column=1, padx=8, pady=(0, 8), sticky="we")

        self.e_res = {}
        campos = [("id", "ID reserva (ej. RES-01)", ""), ("horas", "Duración (horas)", ""),
                  ("cantidad", "Cantidad / asistentes", "1"), ("descuento", "Descuento (0 a 0.99)", "0")]
        for i, (clave, texto, defecto) in enumerate(campos):
            fila, col = divmod(i, 2)
            tk.Label(panel, text=texto, bg=C["panel"], font=FUENTE).grid(
                row=2 + fila * 2, column=col, sticky="w", padx=8)
            self.e_res[clave] = self._entrada(panel)
            self.e_res[clave].insert(0, defecto)
            self.e_res[clave].grid(row=3 + fila * 2, column=col, padx=8, pady=(0, 8), sticky="we")

        botones = tk.Frame(panel, bg=C["panel"])
        botones.grid(row=6, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 0))
        self._boton(botones, "Crear y confirmar", self._crear_reserva, C["ok"]).pack(side="left", padx=(0, 8))
        self._boton(botones, "Procesar seleccionada", self._procesar_reserva, C["info"]).pack(side="left", padx=(0, 8))
        self._boton(botones, "Cancelar seleccionada", self._cancelar_reserva, C["error"]).pack(side="left")

        self.t_res = self._tabla(tab, ("ID", "Cliente", "Servicio", "Horas", "Cant.", "Total c/IVA", "Estado"),
                                 (80, 190, 240, 70, 70, 140, 110))

    def _crear_reserva(self):
        """Valida los datos de la pantalla y delega la creación al gestor (que registra errores en el log)."""
        try:
            if not self.cb_cli.get() or not self.cb_srv.get():
                raise ReservaInvalidaError("Seleccione un cliente y un servicio para la reserva.")
            try:
                horas = int(self.e_res["horas"].get())
                cantidad = int(self.e_res["cantidad"].get())
                descuento = float(self.e_res["descuento"].get().replace(",", "."))
            except ValueError as err_tecnico:
                raise ReservaInvalidaError(
                    f"Duración, cantidad o descuento con formato inválido: {err_tecnico}"
                ) from err_tecnico
            reserva = self.gestor.crear_y_confirmar_reserva(
                self.e_res["id"].get().strip(), self.cb_cli.get().split(" - ")[0],
                self.cb_srv.get().split(" - ")[0], horas, cantidad, descuento)
            if reserva is None:
                self._error(self._ultimo_error_log())
            else:
                self._exito(f"Reserva {reserva.id_entidad} confirmada. Total: ${reserva.costo_total:,.2f}")
                self.e_res["id"].delete(0, "end")
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_CreacionReserva")
            self._error(str(err))
        self._refrescar_todo()

    def _reserva_seleccionada(self):
        """Devuelve el objeto Reserva de la fila seleccionada o None si no hay selección."""
        seleccion = self.t_res.selection()
        if not seleccion:
            messagebox.showinfo("Seleccione una reserva", "Haga clic en una reserva de la tabla primero.")
            return None
        id_res = self.t_res.item(seleccion[0], "values")[0]
        return next((r for r in self.gestor.reservas if r.id_entidad == id_res), None)

    def _procesar_reserva(self):
        reserva = self._reserva_seleccionada()
        if reserva is None:
            return
        try:
            total = reserva.procesar()
            self.gestor.logs.registrar_info(f"Reserva {reserva.id_entidad} procesada desde la GUI por ${total:,.2f}")
            self._exito(f"Reserva {reserva.id_entidad} procesada. Total facturado: ${total:,.2f}")
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_ProcesarReserva")
            self._error(str(err))
        self._refrescar_todo()

    def _cancelar_reserva(self):
        reserva = self._reserva_seleccionada()
        if reserva is None:
            return
        try:
            reserva.cancelar("Cancelación solicitada desde la interfaz gráfica")
            self.gestor.logs.registrar_info(f"Reserva {reserva.id_entidad} cancelada desde la GUI.")
            self._exito(f"Reserva {reserva.id_entidad} cancelada.")
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_CancelarReserva")
            self._error(str(err))
        self._refrescar_todo()

    # ==========================================================================
    # PESTAÑA 4: VISOR DE LOGS
    # ==========================================================================
    def _crear_tab_logs(self):
        tab = tk.Frame(self.notebook, bg=C["fondo"], padx=14, pady=14)
        self.notebook.add(tab, text="  Logs  ")
        barra = tk.Frame(tab, bg=C["fondo"])
        barra.pack(fill="x", pady=(0, 8))
        self._boton(barra, "Actualizar log", self._cargar_log, C["info"]).pack(side="left")
        tk.Label(barra, text="  Rojo = ERROR   Verde = INFO   Amarillo = WARNING", bg=C["fondo"],
                 fg=C["gris"], font=FUENTE).pack(side="left", padx=12)
        marco = tk.Frame(tab)
        marco.pack(fill="both", expand=True)
        self.txt_log = tk.Text(marco, bg=C["log_bg"], fg="#D8DEE9", font=("Consolas", 10),
                               wrap="none", state="disabled", relief="flat")
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.txt_log.yview)
        sx = ttk.Scrollbar(tab, orient="horizontal", command=self.txt_log.xview)
        self.txt_log.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.txt_log.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")
        sx.pack(fill="x")
        self.txt_log.tag_configure("ERROR", foreground="#FF6B6B")
        self.txt_log.tag_configure("INFO", foreground="#7EE787")
        self.txt_log.tag_configure("WARNING", foreground="#F2CC60")

    def _cargar_log(self):
        """Lee el archivo de logs y lo muestra coloreado según el nivel de cada línea."""
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", "end")
        if os.path.exists(ARCHIVO_LOG):
            with open(ARCHIVO_LOG, encoding="utf-8", errors="replace") as f:
                for linea in f:
                    nivel = "ERROR" if "| ERROR" in linea else "WARNING" if "| WARNING" in linea else "INFO"
                    self.txt_log.insert("end", linea, nivel)
        else:
            self.txt_log.insert("end", "Aún no existe el archivo de logs.")
        self.txt_log.config(state="disabled")
        self.txt_log.see("end")

    # ==========================================================================
    # PESTAÑA 5: SIMULACIÓN
    # ==========================================================================
    def _crear_tab_simulacion(self):
        tab = tk.Frame(self.notebook, bg=C["fondo"], padx=14, pady=14)
        self.notebook.add(tab, text="  Simulación  ")
        barra = tk.Frame(tab, bg=C["fondo"])
        barra.pack(fill="x", pady=(0, 8))
        self._boton(barra, "Ejecutar simulación de 14 operaciones", self._ejecutar_simulacion,
                    C["accent"]).pack(side="left")
        tk.Label(barra, text="  Carga los datos de ejemplo en las pestañas Clientes, Servicios y Reservas.",
                 bg=C["fondo"], fg=C["gris"], font=FUENTE).pack(side="left", padx=12)
        marco = tk.Frame(tab)
        marco.pack(fill="both", expand=True)
        self.txt_sim = tk.Text(marco, bg="white", fg=C["texto"], font=("Consolas", 10),
                               wrap="word", relief="flat", state="disabled")
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.txt_sim.yview)
        self.txt_sim.configure(yscrollcommand=sy.set)
        self.txt_sim.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")
        self.txt_sim.tag_configure("titulo", foreground=C["info"], font=("Consolas", 10, "bold"))
        self.txt_sim.tag_configure("error", foreground=C["error"])
        self.txt_sim.tag_configure("ok", foreground=C["ok"])

    def _ejecutar_simulacion(self):
        """Carga los datos de la simulación en el gestor de la ventana y muestra su salida."""
        # Si ya hay datos ingresados a mano, pide confirmación antes de reemplazarlos.
        hay_datos = self.gestor.clientes or self.gestor.servicios or self.gestor.reservas
        if hay_datos:
            if not messagebox.askyesno("Reemplazar datos",
                                       "La simulación reemplazará los clientes, servicios y reservas actuales. ¿Continuar?"):
                return
            self.gestor.clientes.clear()
            self.gestor.servicios.clear()
            self.gestor.reservas.clear()

        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                simulacion.ejecutar_simulacion(self.gestor)
        except Exception as err:  # Última barrera: la ventana nunca debe cerrarse por un fallo.
            buffer.write(f"\nERROR INESPERADO: {err}\n")
        self.txt_sim.config(state="normal")
        self.txt_sim.delete("1.0", "end")
        for linea in buffer.getvalue().splitlines():
            if linea.startswith("[Simulación") or linea.startswith("="):
                etiqueta = "titulo"
            elif "Error" in linea or "bloqueada" in linea or "detectado" in linea or "controlada" in linea:
                etiqueta = "error"
            elif "->" in linea:
                etiqueta = "ok"
            else:
                etiqueta = ""
            self.txt_sim.insert("end", linea + "\n", etiqueta)
        self.txt_sim.config(state="disabled")
        self._exito("Simulación finalizada. Los datos quedaron cargados en las demás pestañas.")
        self._refrescar_todo()

    # ==========================================================================
    # ACTUALIZACIÓN DE TABLAS Y LISTAS
    # ==========================================================================
    def _refrescar_todo(self):
        """Vuelve a llenar las tablas, las listas desplegables y el visor de logs."""
        for fila in self.t_cli.get_children():
            self.t_cli.delete(fila)
        for i, c in enumerate(self.gestor.clientes):
            self.t_cli.insert("", "end", tags=("par" if i % 2 == 0 else "impar",),
                              values=(c.id_entidad, c.documento, c.nombre, c.correo, c.telefono,
                                      "Activo" if c.activo else "Inactivo"))

        for fila in self.t_srv.get_children():
            self.t_srv.delete(fila)
        for i, s in enumerate(self.gestor.servicios):
            if isinstance(s, ReservaSala):
                tipo, est = "Sala", ("Ocupada" if s.ocupada else "Disponible")
            elif isinstance(s, AlquilerEquipo):
                tipo, est = "Equipo", f"Stock: {s.stock_disponible} unid."
            else:
                tipo, est = "Asesoría", "Activa"
            self.t_srv.insert("", "end", tags=("par" if i % 2 == 0 else "impar",),
                              values=(s.id_entidad, tipo, s.nombre_servicio, f"${s.tarifa_hora:,.2f}", est))

        for fila in self.t_res.get_children():
            self.t_res.delete(fila)
        for r in self.gestor.reservas:
            self.t_res.insert("", "end", tags=(r.estado,),
                              values=(r.id_entidad, r.cliente.nombre, r.servicio.nombre_servicio,
                                      r.duracion_horas, r.cantidad, f"${r.costo_total:,.2f}", r.estado))

        self.cb_cli["values"] = [f"{c.id_entidad} - {c.nombre}" for c in self.gestor.clientes]
        self.cb_srv["values"] = [f"{s.id_entidad} - {s.nombre_servicio}" for s in self.gestor.servicios]
        self._cargar_log()


if __name__ == "__main__":
    AppSoftwareFJ().mainloop()
