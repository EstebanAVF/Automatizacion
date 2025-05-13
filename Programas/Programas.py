import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Conexión a la base de datos
def conectar_db():
    try:
        conn = pyodbc.connect(
            r'DRIVER={SQL Server};'
            r'SERVER=LAPTOP-V800EBTP\SQLEXPRESS01;'
            r'DATABASE=Automatizacion;'
            r'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
        return None

# Contiene todas las funciones en su interior
def crear_frame_programas(master):

    # se coloca aca ya que contiene variables que estan dentro de esta funcion, y al estarlo ya no son globales
    def cargar_programas():
        try:
            # Limpiar el Treeview
            for row in tree_programas.get_children():
                tree_programas.delete(row)
            # Conectar a la base de datos
            conn = conectar_db()
            if not conn:  # Verificar si la conexión fue exitosa
                return  # Si la conexión falla, salimos de la función
            cursor = conn.cursor()
            # Ejecutar la consulta SQL
            cursor.execute("SELECT id, nombre FROM programas")
            # Fetchall() recupera todos los resultados de la consulta
            data = cursor.fetchall()  # ¡Aquí es donde asignamos el valor a 'data'!
            # Insertar los datos en el Treeview
            for id, nombre in data:
                tree_programas.insert("", "end", values=(id, nombre))

            # Cerrar la conexión
            conn.close()

        except pyodbc.Error as db_err:
            print("Error de base de datos al cargar programas:", db_err)
            messagebox.showerror(
                "Error de Base de Datos",
                "Error al cargar programas desde la base de datos.",
            )

        except Exception as e:
            print("Error inesperado al cargar programas:", e)
            messagebox.showerror("Error Inesperado", f"Error al cargar programas: {e}")

    def agregar_programa():
        nombre = entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror(
                "Error", "El nombre del programa no puede estar vacío."
            )
            return
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO programas (nombre) VALUES (?)", nombre)
        conn.commit()
        conn.close()
        entry_nombre.delete(0, tk.END)
        cargar_programas()
        messagebox.showinfo("Éxito", "Programa agregado correctamente.")

    def seleccionar_programa(event):
        selected = tree_programas.focus()
        if selected:
            valores = tree_programas.item(selected, "values")
            entry_nombre.delete(0, tk.END)
            entry_nombre.insert(0, valores[1])

    def modificar_programa():
        try:
            item = tree_programas.selection()[0]
            valores = tree_programas.item(item, "values")
            id_programa = int(valores[0])  # Convertir correctamente a entero
            nuevo_nombre = entry_nombre.get()

            if not nuevo_nombre:
                messagebox.showerror("Error", "Debe ingresar un nuevo nombre.")
                return

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE programas SET nombre = ? WHERE id = ?",
                nuevo_nombre,
                id_programa,
            )
            conn.commit()
            conn.close()

            cargar_programas()
            entry_nombre.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar: {e}")

    def eliminar_programa():
        try:
            item = tree_programas.selection()[0]
            valores = tree_programas.item(item, "values")
            id_programa = int(valores[0])  # Convertir correctamente a entero

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM programas WHERE id = ?", id_programa)
            conn.commit()
            conn.close()

            cargar_programas()
            entry_nombre.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    frame = ctk.CTkFrame(master)  # Crear el frame dentro del 'master'
    # Interfaz
    # app = ctk.CTk()  # ELIMINAR ESTA LÍNEA
    # app.title("Gestión de Programas") # ELIMINAR ESTA LÍNEA
    # app.geometry("500x500") # ELIMINAR ESTA LÍNEA

    # frame = ctk.CTkFrame(app) # MODIFICAR: frame = ctk.CTkFrame(master)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Nombre del Programa").pack(anchor="w")
    entry_nombre = ctk.CTkEntry(
        frame, placeholder_text="Ingrese el nombre del programa"
    )
    entry_nombre.pack(fill="x", pady=5, expand=True)  # Modificado

    ctk.CTkButton(frame, text="Agregar", command=agregar_programa).pack(pady=5)
    ctk.CTkButton(frame, text="Modificar", command=modificar_programa).pack(pady=5)
    ctk.CTkButton(frame, text="Eliminar", command=eliminar_programa).pack(pady=5)

    tree_programas = ttk.Treeview(
        frame, columns=("ID", "Nombre"), show="headings", height=10
    )
    tree_programas.heading("ID", text="ID")
    tree_programas.heading("Nombre", text="Nombre")
    tree_programas.pack(fill="both", expand=True, pady=10)  # Modificado
    tree_programas.bind("<ButtonRelease-1>", seleccionar_programa)

    cargar_programas()

    return frame
