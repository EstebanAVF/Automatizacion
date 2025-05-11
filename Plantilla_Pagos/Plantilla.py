import customtkinter as ctk

import pyodbc

import tkinter as tk

from customtkinter import *

from tkinter import ttk, messagebox

from datetime import datetime

from tkinter import Toplevel, ttk


# FUNCIONES

# Conexion base de datos 
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
        sqlstate = ex.args[0]
        print(f"Error al conectar a la base de datos: {sqlstate}")
        return None



# ACtulaizacion saldo
def actualizar_saldo(event=None):
    partida_nombre = combo_partida.get()
    
    print(f"Valor seleccionado en el combo (automático): '{partida_nombre}'")
    print(f"Claves en partidas_dict: {partidas_dict.keys()}")
    if partida_nombre in partidas_dict:
        try:
            partida_id = int(partidas_dict[partida_nombre])
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT monto_disponible FROM partidas_presupuestarias WHERE id = ?", (partida_id,))
            saldo = cursor.fetchone()[0] # Accedemos al primer (y único) elemento
            
            label_saldo.configure(text=f"Saldo disponible: ₡{saldo:,.2f}")
        except (ValueError, TypeError, IndexError):
            label_saldo.configure(text="Saldo disponible: ₡error") # Manejar posibles errores
    else:
        label_saldo.configure(text="Saldo disponible: ₡0.00")


# Para visualizar historial
def ver_historial():
    ventana = Toplevel(app)
    ventana.title("Historial de Pagos")
    ventana.geometry("950x400")

    tree = ttk.Treeview(ventana, columns=("id", "proveedor", "partida", "factura", "descripcion", "monto", "fecha"), show="headings")
    tree.pack(fill="both", expand=True)

    for col in tree["columns"]:
        tree.heading(col, text=col.upper())
        tree.column(col, anchor="center")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, pr.nombre, pp.codigo_partida, p.numero_factura, p.descripcion_pago, p.monto_pago, p.fecha_pago
        FROM planillas_pago p
        JOIN proveedores pr ON pr.id = p.proveedor_id
        JOIN partidas_presupuestarias pp ON pp.id = p.partida_id
        ORDER BY p.fecha_pago DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", "end", values=row)


# Cargar proveedores
def cargar_proveedores():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM proveedores")
    proveedores = cursor.fetchall()
    conn.close()
    return {f"{nombre} (ID: {id})": id for id, nombre in proveedores}


# Cargar partidas
def cargar_partidas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo_partida FROM partidas_presupuestarias")
    partidas = cursor.fetchall()
    conn.close()
    return {f"{codigo} (ID: {id})": id for id, codigo in partidas}


# Guardar pago
def guardar_pago():
    proveedor_nombre = combo_proveedor.get()
    partida_codigo = combo_partida.get()
    factura = entry_factura.get()
    descripcion = entry_desc.get()
    monto = entry_monto.get()

    if not proveedor_nombre or not partida_codigo or not monto:
        messagebox.showwarning("Faltan datos", "Debe completar todos los campos.")
        return

    try:
        monto = float(monto)
    except ValueError:
        messagebox.showerror("Error", "Monto inválido.")
        return

    proveedor_id = proveedores_dict[proveedor_nombre]
    partida_id = partidas_dict[partida_codigo]

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Validar saldo
        cursor.execute("SELECT monto_disponible FROM partidas_presupuestarias WHERE id = ?", partida_id)
        saldo_actual = cursor.fetchone()[0]

        if monto > saldo_actual:
            messagebox.showerror("Error", "Fondos insuficientes en la partida.")
            return

        # Insertar en planillas_pago
        cursor.execute("""
            INSERT INTO planillas_pago (proveedor_id, partida_id, descripcion_pago, numero_factura, monto_pago)
            VALUES (?, ?, ?, ?, ?)
        """, (proveedor_id, partida_id, descripcion, factura, monto))

        # Actualizar partida
        cursor.execute("""
            UPDATE partidas_presupuestarias
            SET monto_disponible = monto_disponible - ?
            WHERE id = ?
        """, (monto, partida_id))

        # Insertar en libro_bancos
        cursor.execute("""
            INSERT INTO libro_bancos (descripcion, monto, tipo_movimiento, referencia)
            VALUES (?, ?, 'egreso', ?)
        """, (descripcion, monto, factura))

        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Éxito", "Pago registrado correctamente.")
        limpiar_campos()

    except pyodbc.Error as err:
        messagebox.showerror("Error", f"Error al registrar el pago: {err}")


# Limpiar los campso
def limpiar_campos():
    entry_desc.delete(0, ctk.END)
    entry_factura.delete(0, ctk.END)
    entry_monto.delete(0, ctk.END)
    combo_proveedor.set("")
    combo_partida.set("")




# Interfaz
app = ctk.CTk()
app.title("Registro de Planilla de Pago")
app.geometry("550x600")

ctk.CTkLabel(app, text="Planilla de Pago", font=("Arial", 22)).pack(pady=15)

proveedores_dict = cargar_proveedores()
partidas_dict = cargar_partidas()

combo_proveedor = ctk.CTkComboBox(app, values=list(proveedores_dict.keys()), width=400)
combo_proveedor.pack(pady=5)
combo_proveedor.set("Seleccionar proveedor")

combo_partida = ctk.CTkComboBox(app, values=list(partidas_dict.keys()), width=400)
combo_partida.pack(pady=5)
combo_partida.set("Seleccionar partida presupuestaria")

combo_partida.bind("<<ComboboxSelected>>", actualizar_saldo)
label_saldo = ctk.CTkLabel(app, text="Saldo disponible: ₡0.00", font=("Arial", 16))
label_saldo.pack(pady=5)


entry_desc = ctk.CTkEntry(app, placeholder_text="Descripción del pago", width=400)
entry_desc.pack(pady=5)

entry_factura = ctk.CTkEntry(app, placeholder_text="Número de factura", width=400)
entry_factura.pack(pady=5)

entry_monto = ctk.CTkEntry(app, placeholder_text="Monto a pagar", width=400)
entry_monto.pack(pady=5)

ctk.CTkButton(app, text="Registrar Pago", command=guardar_pago).pack(pady=15)
ctk.CTkButton(app, text="Limpiar", command=limpiar_campos).pack()

ctk.CTkButton(app, text="Ver Historial de Pagos", command=ver_historial).pack(pady=5)


app.mainloop()
