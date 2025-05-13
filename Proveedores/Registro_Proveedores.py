import customtkinter as ctk
import pyodbc
from tkinter import messagebox
from tkinter import ttk  # Importar ttk para el Treeview

# Configuración de la apariencia
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# Conexión a SQL Server
def conectar_db():
    try:
        conn_str = (
            r'DRIVER={SQL Server};'
            r'SERVER=LAPTOP-V800EBTP\SQLEXPRESS01;'
            r'DATABASE=Automatizacion;'
            r'Trusted_Connection=yes;'
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0] if ex.args else "N/A"  # Obtener SQLSTATE si está disponible
        messagebox.showerror(
            "Error de Base de Datos",
            f"Error al conectar a la base de datos (SQLSTATE: {sqlstate}): {ex}",
        )
        return None
    except Exception as e:
        messagebox.showerror(
            "Error de Conexión", f"No se pudo establecer la conexión: {e}"
        )
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
            if not conn:
                return  # Si la conexión falla, salimos de la función
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
            cargar_proveedores()  # Recargar datos en el Treeview
        except pyodbc.Error as ex:
            conn.rollback()  # Deshacer cualquier cambio
            conn.close()
            sqlstate = ex.args[0] if ex.args else "N/A"
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al agregar programa (SQLSTATE: {sqlstate}): {ex}",
            )
        except Exception as e:
            conn.rollback()  # Asegurar rollback en otros errores
            if conn:
                conn.close()
            messagebox.showerror("Error Inesperado", f"Error al agregar programa: {e}")

    def limpiar_campos():
        entry_nombre.delete(0, ctk.END)
        entry_identificacion.delete(0, ctk.END)
        entry_cuenta.delete(0, ctk.END)
        tipo_var.set("Proveedor")

    def cargar_proveedores():
        try:
            for row in tree_proveedores.get_children():
                tree_proveedores.delete(row)
            conn = conectar_db()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, identificacion, tipo, cuenta_bancaria FROM proveedores")
            data = cursor.fetchall()
            for row in data:
                tree_proveedores.insert("", "end", values=row)
            conn.close()
        except pyodbc.Error as ex:
            if conn:
                conn.rollback()
                conn.close()
            sqlstate = ex.args[0] if ex.args else "N/A"
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al modificar programa (SQLSTATE: {sqlstate}): {ex}",
            )
            
        except Exception as e:
            if conn:
                conn.rollback()  # Asegurar rollback en otros errores
                conn.close()
            messagebox.showerror("Error Inesperado", f"Error al modificar programa: {e}")

    def seleccionar_proveedor(event):
        selected_item = tree_proveedores.focus()
        if selected_item:
            row = tree_proveedores.item(selected_item)['values']
            entry_nombre.delete(0, ctk.END)
            entry_nombre.insert(0, row[1])  # Nombre
            entry_identificacion.delete(0, ctk.END)
            entry_identificacion.insert(0, row[2])  # Identificacion
            tipo_var.set(row[3])  # Tipo
            entry_cuenta.delete(0, ctk.END)
            entry_cuenta.insert(0, row[4])  # Cuenta bancaria

    def modificar_proveedor():
        selected_item = tree_proveedores.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un proveedor para modificar.")
            return

        try:
            proveedor_id = tree_proveedores.item(selected_item)['values'][0]
            nombre = entry_nombre.get()
            identificacion = entry_identificacion.get()
            tipo = tipo_var.get()
            cuenta = entry_cuenta.get()

            if not nombre or not identificacion or not tipo:
                messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos.")
                return

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE proveedores SET nombre=?, identificacion=?, tipo=?, cuenta_bancaria=?
                WHERE id=?
                """,
                (nombre, identificacion, tipo, cuenta, proveedor_id)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Proveedor modificado.")
            limpiar_campos()
            cargar_proveedores()

        except pyodbc.Error as ex:
            if conn:
                conn.rollback()
                conn.close()
            sqlstate = ex.args[0] if ex.args else "N/A"
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al modificar programa (SQLSTATE: {sqlstate}): {ex}",
            )
            
        except Exception as e:
            if conn:
                conn.rollback()  # Asegurar rollback en otros errores
                conn.close()
            messagebox.showerror("Error Inesperado", f"Error al modificar programa: {e}")

    def eliminar_proveedor():
        selected_item = tree_proveedores.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un proveedor para eliminar.")
            return

        confirm = messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este proveedor?")
        if confirm:
            try:
                proveedor_id = tree_proveedores.item(selected_item)['values'][0]
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM proveedores WHERE id=?", (proveedor_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Proveedor eliminado.")
                limpiar_campos()
                cargar_proveedores()
                
            except pyodbc.Error as ex:
                if conn:
                    conn.rollback()
                    conn.close()
                sqlstate = ex.args[0] if ex.args else "N/A"
                messagebox.showerror(
                    "Error de Base de Datos",
                    f"Error al modificar programa (SQLSTATE: {sqlstate}): {ex}",
                )
                
            except Exception as e:
                if conn:
                    conn.rollback()  # Asegurar rollback en otros errores
                    conn.close()
                messagebox.showerror("Error Inesperado", f"Error al modificar programa: {e}")

    frame = ctk.CTkFrame(master)  # Crear frame dentro del 'master'

    # Widgets
    ctk.CTkLabel(frame, text="Registro de Proveedores", font=("Arial", 20)).pack(pady=20)

    entry_nombre = ctk.CTkEntry(frame, placeholder_text="Nombre completo")
    entry_nombre.pack(pady=10, fill="x", expand=True)  # Modificado

    entry_identificacion = ctk.CTkEntry(frame, placeholder_text="Identificación")
    entry_identificacion.pack(pady=10, fill="x", expand=True)  # Modificado


    tipo_var = ctk.StringVar(value="Proveedor")
    frame_tipo = ctk.CTkFrame(frame)
    frame_tipo.pack(pady=10)
    ctk.CTkLabel(frame_tipo, text="Tipo: ").pack(side="left")
    ctk.CTkRadioButton(frame_tipo, text="Proveedor", variable=tipo_var, value="Proveedor").pack(side="left", padx=10)
    ctk.CTkRadioButton(frame_tipo, text="Funcionario", variable=tipo_var, value="Funcionario").pack(side="left")

    entry_cuenta = ctk.CTkEntry(frame, placeholder_text="Cuenta bancaria (opcional)")
    entry_cuenta.pack(pady=10)

    btn_guardar = ctk.CTkButton(frame, text="Guardar", command=guardar_proveedor)
    btn_guardar.pack(pady=10)

    btn_modificar = ctk.CTkButton(frame, text="Modificar", command=modificar_proveedor)
    btn_modificar.pack(pady=5)

    btn_eliminar = ctk.CTkButton(frame, text="Eliminar", command=eliminar_proveedor)
    btn_eliminar.pack(pady=5)

    btn_limpiar = ctk.CTkButton(frame, text="Limpiar", command=limpiar_campos)
    btn_limpiar.pack(pady=10)

    # Treeview para mostrar los proveedores
    tree_proveedores = ttk.Treeview(
        frame,
        columns=("ID", "Nombre", "Identificación", "Tipo", "Cuenta Bancaria"),
        show="headings",
        height=8
    )
    tree_proveedores.heading("ID", text="ID")
    tree_proveedores.heading("Nombre", text="Nombre")
    tree_proveedores.heading("Identificación", text="Identificación")
    tree_proveedores.heading("Tipo", text="Tipo")
    tree_proveedores.heading("Cuenta Bancaria", text="Cuenta Bancaria")
    tree_proveedores.pack(pady=10, fill="both", expand=True)  # Modificado
    tree_proveedores.bind("<ButtonRelease-1>", seleccionar_proveedor)  # Bindear la selección

    cargar_proveedores()  # Cargar los datos al inicio

    return frame