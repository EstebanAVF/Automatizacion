
import customtkinter as ctk
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Variables globales
partidas_agregadas = []
total_pago = tk.DoubleVar(value=0.0)

# Conexion a base de datos
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
        print("Error al conectar:", e)
        return None

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

# Agregar partida a distribución
def agregar_partida():
    codigo = combo_partida.get()
    monto_str = entry_monto.get()

    if not codigo or not monto_str:
        messagebox.showerror("Error", "Debe seleccionar una partida y un monto.")
        return

    try:
        monto = float(monto_str)
        if monto <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Monto inválido.")
        return

    tree_partidas.insert("", "end", values=(codigo, f"₡{monto:,.2f}"))
    partidas_agregadas.append((codigo, monto))
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
        cursor.execute("INSERT INTO pagos (proveedor_id, factura, descripcion, total) VALUES (?, ?, ?, ?)",
                       proveedor_id, factura, descripcion, total_pago.get())
        conn.commit()
        cursor.execute("SELECT SCOPE_IDENTITY()")
        pago_id = cursor.fetchone()[0]

        # Insertar detalle por partida
        for codigo, monto in partidas_agregadas:
            cursor.execute("SELECT id, monto_disponible FROM partidas_presupuestarias WHERE codigo_partida LIKE ?", f"%{codigo.split(' ')[0]}%")
            resultado = cursor.fetchone()
            if resultado:
                partida_id, saldo_actual = resultado
                if monto > saldo_actual:
                    messagebox.showerror("Error", f"Saldo insuficiente en {codigo}")
                    conn.rollback()
                    return
                nuevo_saldo = saldo_actual - monto

                cursor.execute("UPDATE partidas_presupuestarias SET monto_disponible = ? WHERE id = ?", nuevo_saldo, partida_id)
                cursor.execute("INSERT INTO detalle_pago_partidas (id_pago, id_partida, monto_asignado, saldo_antes, saldo_despues) VALUES (?, ?, ?, ?, ?)",
                               pago_id, partida_id, monto, saldo_actual, nuevo_saldo)
            else:
                messagebox.showerror("Error", f"No se encontró la partida {codigo}")
                conn.rollback()
                return

        # Libro de bancos
        cursor.execute("INSERT INTO libro_bancos (fecha, concepto, monto, tipo_movimiento, referencia, proveedor_id) VALUES (GETDATE(), ?, ?, 'egreso', ?, ?)",
                       f"Pago Factura #{factura}", total_pago.get(), factura, proveedor_id)

        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Pago registrado correctamente.")
        limpiar_campos()
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al registrar pago: {e}")

def limpiar_campos():
    entry_desc.delete(0, ctk.END)
    entry_factura.delete(0, ctk.END)
    combo_proveedor.set("Seleccionar proveedor")
    combo_partida.set("Seleccionar partida")
    entry_monto.delete(0, ctk.END)
    tree_partidas.delete(*tree_partidas.get_children())
    partidas_agregadas.clear()
    total_pago.set(0.0)

# Interfaz
app = ctk.CTk()
app.title("Planilla de Pago con Distribución del Gasto")
app.geometry("700x700")

# Cargar datos iniciales
proveedores_dict = cargar_proveedores()
partidas_dict = cargar_partidas()

# Formulario
frame = ctk.CTkFrame(app)
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

ctk.CTkLabel(frame, text="Monto").pack(anchor="w")
entry_monto = ctk.CTkEntry(frame, placeholder_text="Monto")
entry_monto.pack(fill="x")

ctk.CTkButton(frame, text="Agregar a distribución", command=agregar_partida).pack(pady=10)

tree_partidas = ttk.Treeview(frame, columns=("Partida", "Monto"), show="headings", height=5)
tree_partidas.heading("Partida", text="Código Partida")
tree_partidas.heading("Monto", text="Monto Asignado")
tree_partidas.pack(fill="both", expand=True, pady=5)

ctk.CTkLabel(frame, textvariable=total_pago, font=("Arial", 14)).pack(anchor="e", pady=5)

ctk.CTkButton(frame, text="Registrar Pago Distribuido", command=registrar_pago).pack(pady=10)

app.mainloop()
