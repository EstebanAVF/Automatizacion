# Dashboard.py
import customtkinter as ctk
from Programas.Programas import crear_frame_programas
from Proveedores.Registro_Proveedores import crear_frame_proveedores
from Partidas_Presupuestarias.Partidas import crear_frame_partidas
from Plantilla_Pagos.planilla_con_distribucion import crear_frame_planilla

def cargar_modulo(modulo_func):
    for widget in contenido_frame.winfo_children():
        widget.destroy()
    modulo_func(contenido_frame).pack(fill="both", expand=True)

# Configuración general
app = ctk.CTk()
app.title("Sistema de Automatización Contable")
app.geometry("1000x600")

# Menú lateral
menu_frame = ctk.CTkFrame(app, width=200)
menu_frame.pack(side="left", fill="y")

ctk.CTkLabel(menu_frame, text="Módulos", font=("Arial", 16)).pack(pady=10)

ctk.CTkButton(menu_frame, text="Programas", command=lambda: cargar_modulo(crear_frame_programas)).pack(pady=5, fill="x")
ctk.CTkButton(menu_frame, text="Proveedores", command=lambda: cargar_modulo(crear_frame_proveedores)).pack(pady=5, fill="x")
ctk.CTkButton(menu_frame, text="Partidas", command=lambda: cargar_modulo(crear_frame_partidas)).pack(pady=5, fill="x")
ctk.CTkButton(menu_frame, text="Planilla", command=lambda: cargar_modulo(crear_frame_planilla)).pack(pady=5, fill="x")

# Área principal
contenido_frame = ctk.CTkFrame(app)
contenido_frame.pack(side="right", fill="both", expand=True)

# Mostrar un módulo por defecto
cargar_modulo(crear_frame_programas)

app.mainloop()
