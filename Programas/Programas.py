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

# Crear frame de programas
def crear_frame_programas(master):

    def cargar_fuentes():
        conn = conectar_db()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM fuentes_financiamiento")
        fuentes = cursor.fetchall()
        conn.close()

        opciones = [f"{id} - {nombre}" for id, nombre in fuentes]
        combo_fuentes.configure(values=opciones)
        if opciones:
            combo_fuentes.set(opciones[0])  # Seleccionar primera por defecto

    def cargar_programas():
        for row in tree_programas.get_children():
            tree_programas.delete(row)

        conn = conectar_db()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, f.nombre
            FROM programas p
            LEFT JOIN fuentes_financiamiento f ON p.fuente_id = f.id
        """)
        data = cursor.fetchall()
        conn.close()

        for i, (id, nombre, fuente) in enumerate(data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree_programas.insert("", "end", values=(id, nombre, fuente if fuente else "No asignada"), tags=(tag,))

    def agregar_programa():
        nombre = entry_nombre.get().strip()
        fuente_seleccionada = fuente_var.get()

        if not nombre:
            messagebox.showerror("Error", "El nombre del programa no puede estar vacío.")
            return

        if "-" not in fuente_seleccionada:
            messagebox.showerror("Error", "Seleccione una fuente válida.")
            return

        fuente_id = int(fuente_seleccionada.split(" - ")[0])

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO programas (nombre, fuente_id) VALUES (?, ?)", nombre, fuente_id)
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

            # Seleccionar fuente correspondiente
            fuente_actual = valores[2]
            for opcion in combo_fuentes.cget("values"):
                if fuente_actual in opcion:
                    combo_fuentes.set(opcion)
                    break

    def modificar_programa():
        try:
            item = tree_programas.selection()[0]
            valores = tree_programas.item(item, "values")
            id_programa = int(valores[0])
            nuevo_nombre = entry_nombre.get().strip()
            fuente_seleccionada = fuente_var.get()

            if not nuevo_nombre or "-" not in fuente_seleccionada:
                messagebox.showerror("Error", "Datos incompletos.")
                return

            fuente_id = int(fuente_seleccionada.split(" - ")[0])

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE programas SET nombre = ?, fuente_id = ? WHERE id = ?",
                nuevo_nombre, fuente_id, id_programa
            )
            conn.commit()
            conn.close()

            cargar_programas()
            entry_nombre.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar: {e}")

    def eliminar_programa():
        selected = tree_programas.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un programa para eliminar.")
            return

        item = selected[0]
        valores = tree_programas.item(item, "values")
        id_programa = int(valores[0])

        confirm = messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este programa?")
        if not confirm:
            return

        conn = conectar_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM programas WHERE id = ?", id_programa)
            conn.commit()
            conn.close()

            cargar_programas()
            entry_nombre.delete(0, tk.END)
        except pyodbc.Error as e:  # Captura la excepción específica de pyodbc
            sqlstate = e.args[0]
            if sqlstate == '23000':  # Código de error para violación de restricción (puede variar)
                mensaje_error = "No se pudo eliminar el programa porque existen pagos de partidas asociados a él. Por favor, elimina primero los pagos asociados."
                messagebox.showerror("Error", mensaje_error)
            else:
                messagebox.showerror("Error", f"Ocurrió un error al intentar eliminar el programa: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    # Frame principal
    frame = ctk.CTkFrame(master)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Nombre del Programa").pack(anchor="w", padx=5, pady=(5, 0))
    entry_nombre = ctk.CTkEntry(frame, placeholder_text="Ingrese el nombre del programa")
    entry_nombre.pack(fill="x", padx=5, pady=(0, 5))

    ctk.CTkLabel(frame, text="Fuente de Financiamiento").pack(anchor="w", padx=5, pady=(5, 0))
    fuente_var = tk.StringVar()
    combo_fuentes = ctk.CTkComboBox(frame, width=450, variable=fuente_var, values=[])
    combo_fuentes.pack(fill="x", padx=5, pady=(0, 5))

    ctk.CTkButton(frame, text="Agregar", command=agregar_programa).pack(pady=5)
    ctk.CTkButton(frame, text="Modificar", command=modificar_programa).pack(pady=5)
    ctk.CTkButton(frame, text="Eliminar", command=eliminar_programa).pack(pady=5)

    # Estilo para el Treeview
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
                    background="#f0f0f0",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#f0f0f0",
                    bordercolor="#cccccc",
                    borderwidth=1)
    style.map('Treeview', background=[('selected', '#007acc')])
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    tree_programas = ttk.Treeview(
        frame, columns=("ID", "Nombre", "Fuente"), show="headings", height=10
    )
    tree_programas.heading("ID", text="ID", anchor="center")
    tree_programas.heading("Nombre", text="Nombre", anchor="center")
    tree_programas.heading("Fuente", text="Fuente de Financiamiento", anchor="center")
    tree_programas.pack(fill="both", expand=True, pady=10)
    tree_programas.bind("<ButtonRelease-1>", seleccionar_programa)

    tree_programas.tag_configure('evenrow', background="#d3d3d3")
    tree_programas.tag_configure('oddrow', background="#ffffff")

    cargar_fuentes()
    cargar_programas()

    return frame