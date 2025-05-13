import customtkinter as ctk
import pyodbc
from tkinter import messagebox


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


def limpiar_campos():
    for entry in [entry_codigo, entry_desc, entry_monto, entry_programa, entry_fuente]:
        entry.delete(0, ctk.END)


# Contiene la parte visual
def crear_frame_partidas(master):  # 'master' es el frame del Dashboard
    def guardar_partida():
        codigo = entry_codigo.get()
        descripcion = entry_desc.get()
        monto = entry_monto.get()
        programa = entry_programa.get()
        fuente = entry_fuente.get()

        try:
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Monto asignado debe ser un número.")
            return

        if not codigo or monto <= 0:
            messagebox.showwarning(
                "Campos vacíos", "Código y monto asignado son obligatorios."
            )
            return

        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO partidas_presupuestarias
                (codigo_partida, descripcion, monto_asignado, monto_disponible, programa, fuente_financiamiento)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (codigo, descripcion, monto, monto, programa, fuente),
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo(
                "Éxito", "Partida presupuestaria registrada correctamente."
            )
            limpiar_campos()
        except pyodbc.Error as err:
            messagebox.showerror("Error", f"Error al guardar: {err}")

    frame = ctk.CTkFrame(master)  # Crear frame dentro del 'master'

    # Interfaz
    # app = ctk.CTk()  # ELIMINAR
    # app.title("Registro de Partidas Presupuestarias")  # ELIMINAR
    # app.geometry("500x500")  # ELIMINAR

    # ctk.CTkLabel(app, text="Registro de Partidas", font=("Arial", 20)).pack(pady=15)  # MODIFICAR
    ctk.CTkLabel(frame, text="Registro de Partidas", font=("Arial", 20)).pack(pady=15)

    entry_codigo = ctk.CTkEntry(
        frame, placeholder_text="Código de partida (ej. 1.01.02.03)"
    )  # MODIFICAR
    entry_codigo.pack(pady=5)

    entry_desc = ctk.CTkEntry(
        frame, placeholder_text="Descripción de la partida"
    )  # MODIFICAR
    entry_desc.pack(pady=5)

    entry_monto = ctk.CTkEntry(frame, placeholder_text="Monto asignado")  # MODIFICAR
    entry_monto.pack(pady=5)

    entry_programa = ctk.CTkEntry(frame, placeholder_text="Programa")  # MODIFICAR
    entry_programa.pack(pady=5)

    entry_fuente = ctk.CTkEntry(
        frame, placeholder_text="Fuente de financiamiento"
    )  # MODIFICAR
    entry_fuente.pack(pady=5)

    ctk.CTkButton(frame, text="Guardar Partida", command=guardar_partida).pack(
        pady=15
    )  # MODIFICAR
    ctk.CTkButton(
        frame, text="Limpiar Campos", command=limpiar_campos
    ).pack()  # MODIFICAR

    return frame
    # app.mainloop()  # ELIMINAR
