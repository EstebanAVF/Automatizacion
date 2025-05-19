import customtkinter as ctk
from Programas.Programas import crear_frame_programas
from Proveedores.Registro_Proveedores import crear_frame_proveedores
from Partidas_Presupuestarias.Partidas import crear_frame_partidas
from Plantilla_Pagos.planilla_con_distribucion import crear_frame_planilla
from Fuentes_Financiamiento.Fuentes import crear_frame_fuentes


def cargar_modulo(modulo_func):
    # Limpiar el scroll_frame antes de cargar el nuevo módulo
    for widget in scroll_frame.winfo_children():
        widget.destroy()
    
    # Cargar el nuevo contenido dentro del scroll_frame
    modulo_func(scroll_frame).pack(fill="both", expand=True)


def cambiar_tema():
    if switch_tema.get() == 1:
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")


# Configuración inicial
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Sistema de Automatización Contable")
app.geometry("1000x600")
app.resizable(True, True)

# Menú lateral
menu_frame = ctk.CTkFrame(app, width=200)
menu_frame.pack(side="left", fill="y")

ctk.CTkLabel(menu_frame, text="Módulos", font=("Arial", 16)).pack(pady=10)

ctk.CTkButton(
    menu_frame, text="Programas", command=lambda: cargar_modulo(crear_frame_programas)
).pack(pady=8, fill="x")
ctk.CTkButton(
    menu_frame,
    text="Proveedores",
    command=lambda: cargar_modulo(crear_frame_proveedores),
).pack(pady=8, fill="x")
ctk.CTkButton(
    menu_frame, text="Partidas", command=lambda: cargar_modulo(crear_frame_partidas)
).pack(pady=8, fill="x")
ctk.CTkButton(
    menu_frame, text="Planilla", command=lambda: cargar_modulo(crear_frame_planilla)
).pack(pady=8, fill="x")
ctk.CTkButton(
    menu_frame, text="Fuentes", command=lambda: cargar_modulo(crear_frame_fuentes)
).pack(pady=8, fill="x")

# Espaciador
ctk.CTkLabel(menu_frame, text="").pack(expand=True)

# Interruptor de tema
switch_tema = ctk.CTkSwitch(
    menu_frame,
    text="Tema",
    command=cambiar_tema
    
)
switch_tema.select()  # Por defecto en modo oscuro
switch_tema.pack(pady=(0, 20), padx=10, anchor="w")

# Área principal con scroll
scroll_frame = ctk.CTkScrollableFrame(app)
scroll_frame.pack(side="right", fill="both", expand=True)

# Mostrar un módulo por defecto
cargar_modulo(crear_frame_programas)

app.mainloop()

