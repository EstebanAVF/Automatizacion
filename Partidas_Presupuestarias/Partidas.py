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
         programa_nombre = combo_programa.get()
         programa_id = programa_dict.get(programa_nombre)
         if not programa_id:
             messagebox.showerror("Error", "Debe seleccionar un programa válido.")
             return

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
                 (codigo_partida, descripcion, monto_asignado, monto_disponible, programa_id)
                 VALUES (?, ?, ?, ?, ?)
                 """,
                 (codigo, descripcion, monto, monto, programa_id),
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
         combo_programa.set("Seleccione un programa")

     def cargar_partidas():
         # (Tu función cargar_partidas aquí - con mejoras visuales)
         try:
             for row in tree_partidas.get_children():
                 tree_partidas.delete(row)
             conn = conectar_db()
             if not conn:
                 return
             cursor = conn.cursor()
             cursor.execute(
                 """
                 SELECT p.id, p.codigo_partida, p.descripcion, p.monto_asignado,
                     prog.nombre AS nombre_programa, f.nombre AS fuente_financiamiento
                 FROM partidas_presupuestarias p
                 LEFT JOIN programas prog ON p.programa_id = prog.id
                 LEFT JOIN fuentes_financiamiento f ON prog.fuente_id = f.id
                 """
             )
             data = cursor.fetchall()
             for i, row in enumerate(data):
                 # Formatear el monto como cadena
                 monto_formateado = (
                     f"{row[3]:.2f}"
                     if isinstance(row[3], (int, float))
                     else str(row[3])
                 )
                 tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                 tree_partidas.insert(
                     "",
                     "end",
                     values=(row[0], row[1], row[2], monto_formateado, row[4], row[5]),
                     tags=(tag,),
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
                 combo_programa.set(partida[4])

         except IndexError:
             pass  # No hay nada seleccionado

     def modificar_partida():
         # Nueva función para modificar la partida seleccionada
         codigo = entry_codigo.get()
         descripcion = entry_desc.get()
         monto_str = entry_monto.get()
         programa_nombre = combo_programa.get()
         programa_id = programa_dict.get(programa_nombre)
         if not programa_id:
             messagebox.showerror("Error", "Debe seleccionar un programa válido.")
             return

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
                 SET codigo_partida = ?, descripcion = ?, monto_asignado = ?, monto_disponible = ?, programa_id = ?
                 WHERE id = ?
                 """,
                 (codigo, descripcion, monto, monto, programa_id, partida_id),
             )

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

     def obtener_programas():
         try:
             conn = conectar_db()
             if not conn:
                 return []
             cursor = conn.cursor()
             cursor.execute("SELECT id, nombre FROM Programas")
             programas = cursor.fetchall()
             conn.close()
             return programas  # Lista de tuplas (id, nombre)
         except Exception as e:
             messagebox.showerror("Error", f"No se pudieron cargar los programas: {e}")
             return []

     def eliminar_partida():
         selected = tree_partidas.selection()
         if not selected:
             messagebox.showerror("Error", "Seleccione una partida para eliminar.")
             return

         item = selected[0]
         valores = tree_partidas.item(item, "values")
         id_partida = int(valores[0])

         confirm = messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar esta partida?")
         if not confirm:
             return

         conn = conectar_db()
         if not conn:
             return
         try:
             cursor = conn.cursor()
             cursor.execute("DELETE FROM partidas_presupuestarias WHERE id = ?", id_partida)
             conn.commit()
             conn.close()

             cargar_partidas()
             limpiar_campos()
         except pyodbc.Error as e:  # Captura la excepción específica de pyodbc
             sqlstate = e.args[0]
             if sqlstate == '23000':  # Código de error para violación de restricción (puede variar)
                 mensaje_error = "No se pudo eliminar la partida porque existen registros asociados a ella. Por favor, elimina primero los registros asociados."
                 messagebox.showerror("Error", mensaje_error)
             else:
                 messagebox.showerror("Error", f"Ocurrió un error al intentar eliminar la partida: {e}")
         except Exception as e:
             messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

     frame = ctk.CTkFrame(master)  # Crear frame dentro del 'master'
     frame.pack(padx=10, pady=10, fill="both", expand=True)  # Añadido para redimensionar

     # Nombre del programa
     ctk.CTkLabel(frame, text="Código de partida (ej. 1.01.02.03)").pack(anchor="w", padx=5, pady=(5, 0))
     entry_codigo = ctk.CTkEntry(frame, placeholder_text="Ingrese el código de la partida")
     entry_codigo.pack(fill="x", padx=5, pady=(0, 5))

     # Fuente de Financiamiento
     ctk.CTkLabel(frame, text="Descripción de la partida").pack(anchor="w", padx=5, pady=(5, 0))
     entry_desc = ctk.CTkEntry(frame, placeholder_text="Ingrese la descripción de la partida")
     entry_desc.pack(fill="x", padx=5, pady=(0, 5))

     ctk.CTkLabel(frame, text="Monto asignado").pack(anchor="w", padx=5, pady=(5, 0))
     entry_monto = ctk.CTkEntry(frame, placeholder_text="Ingrese el monto asignado")
     entry_monto.pack(fill="x", padx=5, pady=(0, 5))

     ctk.CTkLabel(frame, text="Programa").pack(anchor="w", padx=5, pady=(5, 0))
     programas = obtener_programas()
     programa_dict = {nombre: id_ for id_, nombre in programas}  # Para mapear nombre → id
     combo_programa = ctk.CTkComboBox(frame, width=450, values=list(programa_dict.keys()))
     combo_programa.pack(fill="x", padx=5, pady=(0, 5))

     ctk.CTkButton(frame, text="Agregar", command=guardar_partida).pack(pady=5)
     ctk.CTkButton(frame, text="Modificar", command=modificar_partida).pack(pady=5)
     ctk.CTkButton(frame, text="Eliminar", command=eliminar_partida).pack(pady=5)

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
     style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background="#e0e0e0", foreground="black")  # Estilo para los encabezados

     tree_partidas = ttk.Treeview(
         frame,
         columns=("ID", "Código", "Descripción", "Monto", "Programa", "Fuente"),
         show="headings",
         height=8,
         style="Treeview"  # Aplicar el estilo
     )
     tree_partidas.heading("ID", text="ID", anchor="center")
     tree_partidas.heading("Código", text="Código", anchor="center")
     tree_partidas.heading("Descripción", text="Descripción", anchor="center")
     tree_partidas.heading("Monto", text="Monto", anchor="center")
     tree_partidas.heading("Programa", text="Programa", anchor="center")
     tree_partidas.heading("Fuente", text="Fuente", anchor="center")
     tree_partidas.pack(pady=10, fill="both", expand=True, padx=5)  # Añadido padx

     tree_partidas.bind(
         "<ButtonRelease-1>", seleccionar_partida
     )  # Vincular clic del mouse

     tree_partidas.tag_configure('evenrow', background="#d3d3d3")
     tree_partidas.tag_configure('oddrow', background="#ffffff")
     tree_partidas.tag_configure('selected', background="#007acc", foreground="white")  # Estilo para la selección

     cargar_partidas()  # Cargar los datos al inicio

     return frame
