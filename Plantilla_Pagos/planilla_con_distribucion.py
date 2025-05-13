import customtkinter as ctk
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal


# Variables globales
partidas_agregadas = []
programa_nombre = ""  # Inicializar programa_nombre


# Conexion a base de datos
def conectar_db():
    try:
        conn = pyodbc.connect(
            r"DRIVER={SQL Server};"
            r"SERVER=LAPTOP-V800EBTP\SQLEXPRESS01;"
            r"DATABASE=Automatizacion;"
            r"Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        print("Error al conectar:", e)
        return None


def limpiar_campos():
    entry_desc.delete(0, ctk.END)
    entry_factura.delete(0, ctk.END)
    combo_proveedor.set("Seleccionar proveedor")
    combo_partida.set("Seleccionar partida")
    combo_programa.set("Seleccionar programa")
    entry_monto.delete(0, ctk.END)
    tree_partidas.delete(*tree_partidas.get_children())
    partidas_agregadas.clear()
    total_pago.set(0.0)


# Contiene todas las funciones
def crear_frame_planilla(master):  # 'master' es el frame del Dashboard
    # Cargar datos
    def cargar_proveedores():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM proveedores")
        data = cursor.fetchall()
        conn.close()
        return {f"{nombre} (ID: {id})": id for id, nombre in data}

    def cargar_partidas():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo_partida FROM partidas_presupuestarias")
        data = cursor.fetchall()
        conn.close()
        return {f"{codigo} (ID: {id})": id for id, codigo in data}

    def cargar_programas():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM programas")
        data = cursor.fetchall()
        conn.close()
        return {f"{nombre} (ID: {id})": id for id, nombre in data}

    def agregar_partida():
        global programa_nombre  # Indicar que se usará la variable global
        codigo = combo_partida.get()
        monto_str = entry_monto.get()
        programa_nombre = combo_programa.get()  # Obtener el programa aquí

        if not codigo or not monto_str or not programa_nombre:
            messagebox.showerror(
                "Error", "Debe seleccionar una partida, un monto y un programa."
            )
            return

        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Monto inválido.")
            return

        if programa_nombre not in programas_dict:
            messagebox.showerror("Error", "Debe seleccionar un programa válido.")
            return
        programa_id = programas_dict[programa_nombre]
        partidas_agregadas.append((codigo, monto, programa_id, programa_nombre))

        tree_partidas.insert(
            "", "end", values=(codigo, f"₡{monto:,.2f}", programa_nombre)
        )
        total_pago.set(total_pago.get() + monto)
        entry_monto.delete(0, tk.END)

    # Registrar pago distribuido
    def registrar_pago():
        if not partidas_agregadas:
            messagebox.showerror("Error", "Debe agregar al menos una partida.")
            return

        proveedor_nombre = combo_proveedor.get()
        factura = entry_factura.get()
        descripcion = entry_desc.get()

        if not proveedor_nombre or not factura or not descripcion:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        proveedor_id = proveedores_dict.get(proveedor_nombre)
        if proveedor_id is None:
            messagebox.showerror("Error", "Proveedor no válido.")
            return

        try:
            conn = conectar_db()
            cursor = conn.cursor()

            # Insertar en pagos
            cursor.execute(
                "INSERT INTO pagos (proveedor_id, factura, descripcion, total) VALUES (?, ?, ?, ?)",
                proveedor_id,
                factura,
                descripcion,
                total_pago.get(),
            )
            conn.commit()
            cursor.execute("SELECT SCOPE_IDENTITY()")
            pago_id = cursor.fetchone()[0]

            # Insertar detalle por partida
            for codigo, monto, programa_id, programa_nombre in partidas_agregadas:
                cursor.execute(
                    "SELECT id, monto_disponible FROM partidas_presupuestarias WHERE codigo_partida LIKE ?",
                    f"%{codigo.split(' ')[0]}%",
                )
                resultado = cursor.fetchone()
                if resultado:
                    partida_id, saldo_actual = resultado

                    # Convertir 'monto' a Decimal para que coincida con saldo_actual
                    monto_decimal = Decimal(str(monto))

                    if monto_decimal > saldo_actual:
                        messagebox.showerror("Error", f"Saldo insuficiente en {codigo}")
                        conn.rollback()
                        return

                    nuevo_saldo = saldo_actual - monto_decimal

                    cursor.execute(
                        "UPDATE partidas_presupuestarias SET monto_disponible = ? WHERE id = ?",
                        nuevo_saldo,
                        partida_id,
                    )
                    cursor.execute(
                        "INSERT INTO detalle_pago_partidas (id_pago, id_partida, monto_asignado, saldo_antes, saldo_despues, id_programa) VALUES (?, ?, ?, ?, ?, ?)",
                        pago_id,
                        partida_id,
                        monto_decimal,
                        saldo_actual,
                        nuevo_saldo,
                        programa_id,
                    )

                else:
                    messagebox.showerror("Error", f"No se encontró la partida {codigo}")
                    conn.rollback()
                    return

            # Libro de bancos
            cursor.execute(
                "INSERT INTO libro_bancos (fecha, descripcion, monto, tipo_movimiento, referencia, proveedor_id) VALUES (GETDATE(), ?, ?, 'egreso', ?, ?)",
                f"Pago Factura #{factura}",
                total_pago.get(),
                factura,
                proveedor_id,
            )

            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Pago registrado correctamente.")
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al registrar pago: {e}")

    frame = ctk.CTkFrame(master)  # Crear el frame dentro del 'master'

    # Interfaz
    # app = ctk.CTk()  # ELIMINAR
    # app.title("Planilla de Pago con Distribución del Gasto")  # ELIMINAR
    # app.geometry("700x700")  # ELIMINAR

    total_pago = tk.DoubleVar(value=0.0)

    # Cargar datos iniciales
    proveedores_dict = cargar_proveedores()
    partidas_dict = cargar_partidas()
    programas_dict = cargar_programas()

    # Formulario
    # frame = ctk.CTkFrame(app)  # MODIFICAR
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Proveedor").pack(anchor="w")
    combo_proveedor = ctk.CTkComboBox(frame, values=list(proveedores_dict.keys()))
    combo_proveedor.set("Seleccionar proveedor")
    combo_proveedor.pack(fill="x")

    ctk.CTkLabel(frame, text="Descripción del pago").pack(anchor="w")
    entry_desc = ctk.CTkEntry(frame, placeholder_text="Descripción")
    entry_desc.pack(fill="x")

    ctk.CTkLabel(frame, text="Número de Factura").pack(anchor="w")
    entry_factura = ctk.CTkEntry(frame, placeholder_text="Factura")
    entry_factura.pack(fill="x")

    ctk.CTkLabel(frame, text="Partida Presupuestaria").pack(anchor="w")
    combo_partida = ctk.CTkComboBox(frame, values=list(partidas_dict.keys()))
    combo_partida.set("Seleccionar partida")
    combo_partida.pack(fill="x")

    ctk.CTkLabel(frame, text="Programa").pack(anchor="w")
    combo_programa = ctk.CTkComboBox(frame, values=list(programas_dict.keys()))
    combo_programa.set("Seleccionar programa")
    combo_programa.pack(fill="x")

    ctk.CTkLabel(frame, text="Monto").pack(anchor="w")
    entry_monto = ctk.CTkEntry(frame, placeholder_text="Monto")
    entry_monto.pack(fill="x")

    ctk.CTkButton(frame, text="Agregar a distribución", command=agregar_partida).pack(
        pady=10
    )

    tree_partidas = ttk.Treeview(
        frame, columns=("Partida", "Monto", "Programa"), show="headings", height=5
    )
    tree_partidas.heading("Partida", text="Código Partida")
    tree_partidas.heading("Monto", text="Monto Asignado")
    tree_partidas.heading("Programa", text="Programa")
    tree_partidas.pack(fill="both", expand=True)  # Empaquetar el Treeview

    ctk.CTkLabel(frame, textvariable=total_pago, font=("Arial", 14)).pack(
        anchor="e", pady=5
    )

    ctk.CTkButton(
        frame, text="Registrar Pago Distribuido", command=registrar_pago
    ).pack(pady=10)

    return frame
    # app.mainloop()  # ELIMINAR
