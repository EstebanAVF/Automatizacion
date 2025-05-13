import customtkinter as ctk
import pyodbc
from tkinter import messagebox

# Configuración de la apariencia
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# Conexión a SQL Server
def conectar_db():
    try:
        conn_str = (
            r"DRIVER={SQL Server};"
            r"SERVER=LAPTOP-V800EBTP\SQLEXPRESS01;"
            r"DATABASE=Automatizacion;"
            r"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error al conectar a la base de datos: {sqlstate}")
        return None


# Contiene la parte visual
def crear_frame_proveedores(master):  # 'master' es el frame del Dashboard
    # Función para guardar proveedor
    def guardar_proveedor():
        nombre = entry_nombre.get()
        identificacion = entry_identificacion.get()
        tipo = tipo_var.get()
        cuenta = entry_cuenta.get()

        if not nombre or not identificacion or not tipo:
            messagebox.showwarning(
                "Campos vacíos", "Por favor complete todos los campos obligatorios."
            )
            return

        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO proveedores (nombre, identificacion, tipo, cuenta_bancaria)
                VALUES (?, ?, ?, ?)
            """,
                (nombre, identificacion, tipo, cuenta),
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Éxito", "Proveedor registrado correctamente.")
            limpiar_campos()
        except pyodbc.Error as err:
            messagebox.showerror("Error", f"Error al guardar: {err}")

    def limpiar_campos():
        entry_nombre.delete(0, ctk.END)
        entry_identificacion.delete(0, ctk.END)
        entry_cuenta.delete(0, ctk.END)
        tipo_var.set("Proveedor")

    frame = ctk.CTkFrame(master)  # Crear frame dentro del 'master'

    # Widgets
    # app = ctk.CTk()  # ELIMINAR
    # app.title("Registro de Proveedores - Junta Educativa")  # ELIMINAR
    # app.geometry("500x400")  # ELIMINAR

    ctk.CTkLabel(frame, text="Registro de Proveedores", font=("Arial", 20)).pack(
        pady=20
    )  # MODIFICAR

    entry_nombre = ctk.CTkEntry(frame, placeholder_text="Nombre completo")  # MODIFICAR
    entry_nombre.pack(pady=10)

    entry_identificacion = ctk.CTkEntry(
        frame, placeholder_text="Identificación"
    )  # MODIFICAR
    entry_identificacion.pack(pady=10)

    tipo_var = ctk.StringVar(value="Proveedor")
    frame_tipo = ctk.CTkFrame(frame)  # MODIFICAR
    frame_tipo.pack(pady=10)
    ctk.CTkLabel(frame_tipo, text="Tipo: ").pack(side="left")
    ctk.CTkRadioButton(
        frame_tipo, text="Proveedor", variable=tipo_var, value="Proveedor"
    ).pack(side="left", padx=10)
    ctk.CTkRadioButton(
        frame_tipo, text="Funcionario", variable=tipo_var, value="Funcionario"
    ).pack(side="left")

    entry_cuenta = ctk.CTkEntry(
        frame, placeholder_text="Cuenta bancaria (opcional)"
    )  # MODIFICAR
    entry_cuenta.pack(pady=10)

    btn_guardar = ctk.CTkButton(
        frame, text="Guardar", command=guardar_proveedor
    )  # MODIFICAR
    btn_guardar.pack(pady=10)

    btn_limpiar = ctk.CTkButton(
        frame, text="Limpiar", command=limpiar_campos
    )  # MODIFICAR
    btn_limpiar.pack()

    return frame
    # app.mainloop()  # ELIMINAR
