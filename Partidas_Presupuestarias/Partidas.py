import customtkinter as ctk
import pyodbc
from tkinter import messagebox
from tkinter import ttk  # Importar ttk

def conectar_db():
    # (Tu función conectar_db aquí - sin cambios)
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
        sqlstate = ex.args[0] if ex.args else "N/A"
        print(f"Error al conectar a la base de datos: {sqlstate}")
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
def crear_frame_partidas(master):  # 'master' ahora es el frame del Dashboard
    def guardar_partida():
        # (Tu función guardar_partida aquí - sin cambios importantes)
        codigo = entry_codigo.get()
        descripcion = entry_desc.get()
        monto_str = entry_monto.get()  # Obtener como string
        programa = entry_programa.get()
        fuente = entry_fuente.get()

        try:
            monto = float(monto_str)  # Convertir a float
        except ValueError:
            messagebox.showerror("Error", "Monto debe ser un número.")
            return

        if not codigo or monto <= 0:
            messagebox.showwarning(
                "Campos vacíos", "Código y monto asignado son obligatorios."
            )
            return

        try:
            conn = conectar_db()
            if not conn:
                return  # Si la conexión falla, salimos de la función
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
            conn.close()
            messagebox.showinfo(
                "Éxito", "Partida presupuestaria registrada correctamente."
            )
            limpiar_campos()
            cargar_partidas()  # Recargar datos en el Treeview
        except pyodbc.Error as db_err:
            if conn:
                conn.rollback()
                conn.close()
            sqlstate = db_err.args[0] if db_err.args else "N/A"
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al guardar partida (SQLSTATE: {sqlstate}): {db_err}",
            )
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            messagebox.showerror("Error Inesperado", f"Error al guardar partida: {e}")

    def limpiar_campos():
        # (Tu función limpiar_campos aquí - sin cambios)
        entry_codigo.delete(0, ctk.END)
        entry_desc.delete(0, ctk.END)
        entry_monto.delete(0, ctk.END)
        entry_programa.delete(0, ctk.END)
        entry_fuente.delete(0, ctk.END)

    def cargar_partidas():
        # (Tu función cargar_partidas aquí - sin cambios importantes)
        try:
            for row in tree_partidas.get_children():
                tree_partidas.delete(row)
            conn = conectar_db()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, codigo_partida, descripcion, monto_asignado, programa, fuente_financiamiento FROM partidas_presupuestarias"
            )
            data = cursor.fetchall()
            for row in data:
                # Formatear el monto como cadena
                monto_formateado = (
                    f"{row[3]:.2f}"
                    if isinstance(row[3], (int, float))
                    else str(row[3])
                )
                tree_partidas.insert(
                    "",
                    "end",
                    values=(row[0], row[1], row[2], monto_formateado, row[4], row[5]),
                )
            conn.close()
        except pyodbc.Error as db_err:
            print("Error de base de datos al cargar partidas:", db_err)
            messagebox.showerror(
                "Error de Base de Datos",
                "Error al cargar partidas desde la base de datos.",
            )
        except Exception as e:
            print("Error inesperado al cargar partidas:", e)
            messagebox.showerror("Error Inesperado", f"Error al cargar partidas: {e}")

    def seleccionar_partida(event):
        # Nueva función para seleccionar una partida del Treeview
        try:
            item = tree_partidas.selection()[0]
            partida = tree_partidas.item(item, "values")
            if partida:
                entry_codigo.delete(0, ctk.END)
                entry_codigo.insert(0, partida[1])
                entry_desc.delete(0, ctk.END)
                entry_desc.insert(0, partida[2])
                entry_monto.delete(0, ctk.END)
                entry_monto.insert(0, str(partida[3]))  # Convertir monto a string
                entry_programa.delete(0, ctk.END)
                entry_programa.insert(0, partida[4])
                entry_fuente.delete(0, ctk.END)
                entry_fuente.insert(0, partida[5])
        except IndexError:
            pass  # No hay nada seleccionado

    def modificar_partida():
        # Nueva función para modificar la partida seleccionada
        codigo = entry_codigo.get()
        descripcion = entry_desc.get()
        monto_str = entry_monto.get()
        programa = entry_programa.get()
        fuente = entry_fuente.get()

        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showerror("Error", "Monto debe ser un número.")
            return

        if not codigo or monto <= 0:
            messagebox.showwarning(
                "Campos vacíos", "Código y monto asignado son obligatorios."
            )
            return

        try:
            conn = conectar_db()
            if not conn:
                return
            cursor = conn.cursor()
            item = tree_partidas.selection()[0]
            partida_id = tree_partidas.item(item, "values")[0]  # Obtener el ID

            cursor.execute(
                """
                UPDATE partidas_presupuestarias
                SET codigo_partida = ?, descripcion = ?, monto_asignado = ?, monto_disponible = ?, programa = ?, fuente_financiamiento = ?
                WHERE id = ?
            """,
                (codigo, descripcion, monto, monto, programa, fuente, partida_id),
            )  # Usar partida_id en la cláusula WHERE
            conn.commit()
            conn.close()
            messagebox.showinfo(
                "Éxito", "Partida presupuestaria modificada correctamente."
            )
            limpiar_campos()
            cargar_partidas()
        except pyodbc.Error as db_err:
            if conn:
                conn.rollback()
                conn.close()
            sqlstate = db_err.args[0] if db_err.args else "N/A"
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al modificar partida (SQLSTATE: {sqlstate}): {db_err}",
            )
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            messagebox.showerror("Error Inesperado", f"Error al modificar partida: {e}")

    frame = ctk.CTkFrame(master)  # Crear frame dentro del 'master'
    frame.pack(padx=10, pady=10, fill="both", expand=True)  # Añadido para redimensionar

    # Interfaz
    ctk.CTkLabel(frame, text="Registro de Partidas", font=("Arial", 20)).pack(
        pady=15
    )

    entry_codigo = ctk.CTkEntry(
        frame, placeholder_text="Código de partida (ej. 1.01.02.03)"
    )
    entry_codigo.pack(pady=5, fill="x")  # Añadido fill="x"
    entry_desc = ctk.CTkEntry(frame, placeholder_text="Descripción de la partida")
    entry_desc.pack(pady=5, fill="x")  # Añadido fill="x"
    entry_monto = ctk.CTkEntry(frame, placeholder_text="Monto asignado")
    entry_monto.pack(pady=5, fill="x")  # Añadido fill="x"
    entry_programa = ctk.CTkEntry(frame, placeholder_text="Programa")
    entry_programa.pack(pady=5, fill="x")  # Añadido fill="x"
    entry_fuente = ctk.CTkEntry(frame, placeholder_text="Fuente de financiamiento")
    entry_fuente.pack(pady=5, fill="x")  # Añadido fill="x"

    ctk.CTkButton(frame, text="Guardar Partida", command=guardar_partida).pack(
        pady=5
    )
    ctk.CTkButton(frame, text="Modificar Partida", command=modificar_partida).pack(
        pady=5
    )  # Botón "Modificar"
    ctk.CTkButton(frame, text="Limpiar Campos", command=limpiar_campos).pack(pady=5)

    # Treeview para mostrar las partidas
    tree_partidas = ttk.Treeview(
        frame,
        columns=("ID", "Código", "Descripción", "Monto", "Programa", "Fuente"),
        show="headings",
        height=8,
    )
    tree_partidas.heading("ID", text="ID")
    tree_partidas.heading("Código", text="Código")
    tree_partidas.heading("Descripción", text="Descripción")
    tree_partidas.heading("Monto", text="Monto")
    tree_partidas.heading("Programa", text="Programa")
    tree_partidas.heading("Fuente", text="Fuente")
    tree_partidas.pack(pady=10, fill="both", expand=True)  # Añadido fill y expand

    tree_partidas.bind(
        "<ButtonRelease-1>", seleccionar_partida
    )  # Vincular clic del mouse

    cargar_partidas()  # Cargar los datos al inicio

    return frame