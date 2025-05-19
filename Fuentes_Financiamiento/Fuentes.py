import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Conexión a la base de datos
def conectar_db():
    try:
        conn_str = (
            r'DRIVER={SQL Server};'
            r'SERVER=LAPTOP-V800EBTP\SQLEXPRESS01;'
            r'DATABASE=Automatizacion;'
            r'Trusted_Connection=yes;'
        )
        return pyodbc.connect(conn_str)
    except pyodbc.Error as ex:
        sqlstate = ex.args[0] if ex.args else "N/A"
        messagebox.showerror("Error de Base de Datos", f"Error al conectar (SQLSTATE: {sqlstate}): {ex}")
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo establecer la conexión: {e}")
    return None

def crear_frame_fuentes(master):
    def cargar_fuentes():
        for row in tree_fuentes.get_children():
            tree_fuentes.delete(row)
        conn = conectar_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, descripcion FROM fuentes_financiamiento")
            data = cursor.fetchall()
            for id_, nombre, descripcion in data:
                tree_fuentes.insert("", "end", values=(id_, nombre, descripcion))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fuentes: {e}")
            conn.close()

    def agregar_fuente():
        nombre = entry_nombre.get().strip()
        descripcion = entry_desc.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        conn = conectar_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO fuentes_financiamiento (nombre, descripcion) VALUES (?, ?)", nombre, descripcion)
            conn.commit()
            conn.close()
            entry_nombre.delete(0, tk.END)
            entry_desc.delete(0, tk.END)
            cargar_fuentes()
            messagebox.showinfo("Éxito", "Fuente de financiamiento agregada.")
        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Error", f"No se pudo agregar la fuente: {e}")

    def seleccionar_fuente(event):
        selected = tree_fuentes.focus()
        if selected:
            valores = tree_fuentes.item(selected, "values")
            entry_nombre.delete(0, tk.END)
            entry_desc.delete(0, tk.END)
            entry_nombre.insert(0, valores[1])
            entry_desc.insert(0, valores[2])

    def modificar_fuente():
        selected = tree_fuentes.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione una fuente para modificar.")
            return
        valores = tree_fuentes.item(selected, "values")
        id_fuente = valores[0]
        nuevo_nombre = entry_nombre.get().strip()
        nueva_desc = entry_desc.get().strip()
        if not nuevo_nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return
        conn = conectar_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE fuentes_financiamiento SET nombre = ?, descripcion = ? WHERE id = ?",
                nuevo_nombre, nueva_desc, id_fuente
            )
            conn.commit()
            conn.close()
            entry_nombre.delete(0, tk.END)
            entry_desc.delete(0, tk.END)
            cargar_fuentes()
            messagebox.showinfo("Éxito", "Fuente modificada correctamente.")
        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Error", f"No se pudo modificar: {e}")

    def eliminar_fuente():
        selected = tree_fuentes.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione una fuente para eliminar.")
            return
        valores = tree_fuentes.item(selected, "values")
        id_fuente = valores[0]
        confirm = messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar esta fuente?")
        if not confirm:
            return
        conn = conectar_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fuentes_financiamiento WHERE id = ?", id_fuente)
            conn.commit()
            conn.close()
            entry_nombre.delete(0, tk.END)
            entry_desc.delete(0, tk.END)
            cargar_fuentes()
            messagebox.showinfo("Éxito", "Fuente eliminada correctamente.")
        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    # INTERFAZ
    frame = ctk.CTkFrame(master)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Nombre de la Fuente").pack(anchor="w")
    entry_nombre = ctk.CTkEntry(frame, placeholder_text="Nombre")
    entry_nombre.pack(fill="x", pady=5)

    ctk.CTkLabel(frame, text="Descripción").pack(anchor="w")
    entry_desc = ctk.CTkEntry(frame, placeholder_text="Descripción")
    entry_desc.pack(fill="x", pady=5)

    ctk.CTkButton(frame, text="Agregar", command=agregar_fuente).pack(pady=3)
    ctk.CTkButton(frame, text="Modificar", command=modificar_fuente).pack(pady=3)
    ctk.CTkButton(frame, text="Eliminar", command=eliminar_fuente).pack(pady=3)

    tree_fuentes = ttk.Treeview(frame, columns=("ID", "Nombre", "Descripción"), show="headings", height=10)
    tree_fuentes.heading("ID", text="ID")
    tree_fuentes.heading("Nombre", text="Nombre")
    tree_fuentes.heading("Descripción", text="Descripción")
    tree_fuentes.pack(fill="both", expand=True, pady=10)
    tree_fuentes.bind("<ButtonRelease-1>", seleccionar_fuente)

    cargar_fuentes()
    return frame
