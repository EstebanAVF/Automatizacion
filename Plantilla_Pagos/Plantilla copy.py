import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import pyodbc

partidas_agregadas = []
total_pago = tk.DoubleVar(value=0.0)


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


# BOTON PARA AÑADIR PARTIDA
def agregar_partida():
    codigo = combo_nueva_partida.get()
    monto_str = entry_monto_agregar.get()

    if not codigo or not monto_str:
        messagebox.showerror("Error", "Completa código y monto.")
        return

    try:
        monto = float(monto_str)
        if monto <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Monto inválido.")
        return

    # Agregar al Treeview
    tree_partidas.insert("", "end", values=(codigo, f"₡{monto:,.2f}"))
    partidas_agregadas.append((codigo, monto))
    total_pago.set(total_pago.get() + monto)
    entry_monto_agregar.delete(0, tk.END)
    label_total_pago.config(text=f"Total: ₡{total_pago.get():,.2f}")


# ACtulaizacion saldo
def actualizar_saldo(event=None):
    partida_nombre = combo_partida.get()
    if partida_nombre in partidas_dict:
        partida_id = partidas_dict[partida_nombre]
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT monto_disponible FROM partidas_presupuestarias WHERE id = ?", partida_id)
        saldo = cursor.fetchone()[0]
        conn.close()
        label_saldo.configure(text=f"Saldo disponible: ₡{saldo:,.2f}")
    else:
        label_saldo.configure(text="Saldo disponible: ₡0.00")


# Para visualizar historial
def ver_historial():
    ventana_historial = ctk.CTkToplevel(app)
    ventana_historial.title("Historial de Pagos")
    ventana_historial.geometry("950x400")

    tree_historial = ttk.Treeview(ventana_historial, columns=("id", "proveedor", "partida", "factura", "descripcion", "monto", "fecha"), show="headings")
    tree_historial.pack(fill="both", expand=True)

    for col in tree_historial["columns"]:
        tree_historial.heading(col, text=col.upper())
        tree_historial.column(col, anchor="center")

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
        tree_historial.insert("", "end", values=row)


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
    monto_str = entry_monto.get()

    if not proveedor_nombre or not partida_codigo or not monto_str:
        messagebox.showwarning("Faltan datos", "Debe completar todos los campos.")
        return

    try:
        monto = float(monto_str)
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
    combo_proveedor.set("Seleccionar proveedor")
    combo_partida.set("Seleccionar partida presupuestaria")
    entry_monto_agregar.delete(0, tk.END)
    combo_nueva_partida.set("Seleccionar partida")
    tree_partidas.delete(*tree_partidas.get_children())
    partidas_agregadas.clear()
    total_pago.set(0.0)
    label_total_pago.config(text="Total: ₡0.00")


# Registar pago Boton
def registrar_pago():
    if not partidas_agregadas:
        messagebox.showerror("Error", "Agrega al menos una partida.")
        return

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=LAPTOP-V800EBTP\\SQLEXPRESS01;DATABASE=Automatizacion;Trusted_Connection=yes')
        cursor = conn.cursor()

        proveedor_nombre = combo_proveedor.get()
        proveedor_id = proveedores_dict.get(proveedor_nombre)
        factura = entry_factura.get()
        descripcion = entry_desc.get()

        if proveedor_id is None:
            messagebox.showerror("Error", "Proveedor no seleccionado.")
            return

        # Insertar en pagos
        cursor.execute("INSERT INTO pagos (proveedor_id, factura, descripcion, total) VALUES (?, ?, ?, ?)",
                       proveedor_id, factura, descripcion, total_pago.get())
        conn.commit()
        cursor.execute("SELECT @@IDENTITY")
        pago_id = cursor.fetchone()[0]

        # Insertar detalle por partida
        for codigo, monto in partidas_agregadas:
            cursor.execute("SELECT id, monto_disponible FROM partidas_presupuestarias WHERE codigo_partida LIKE ?", f"%{codigo}%")
            resultado_partida = cursor.fetchone()
            if resultado_partida:
                id_partida, saldo_actual = resultado_partida
                if monto > saldo_actual:
                    messagebox.showerror("Error", f"Saldo insuficiente en {codigo}")
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    return
                nuevo_saldo = saldo_actual - monto

                # Actualizar saldo
                cursor.execute("UPDATE partidas_presupuestarias SET monto_disponible = ? WHERE id = ?",
                               nuevo_saldo, id_partida)

                # Insertar en detalle
                cursor.execute("INSERT INTO detalle_pago_partidas (id_pago, id_partida, monto_asignado, saldo_antes, saldo_despues) VALUES (?, ?, ?, ?, ?)",
                               pago_id, id_partida, monto, saldo_actual, nuevo_saldo)
            else:
                messagebox.showerror("Error", f"No se encontró la partida con código: {codigo}")
                conn.rollback()
                cursor.close()
                conn.close()
                return

        # Registrar en libro de bancos
        cursor.execute("INSERT INTO libro_bancos (fecha, concepto, monto, tipo_movimiento, referencia, proveedor_id) VALUES (GETDATE(), ?, ?, 'egreso', ?, ?)",
                       f"Pago Factura #{factura}", total_pago.get(), factura, proveedor_id)

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Éxito", "Pago registrado correctamente.")
        # Limpiar datos
        tree_partidas.delete(*tree_partidas.get_children())
        partidas_agregadas.clear()
        total_pago.set(0.0)
        limpiar_campos()

    except pyodbc.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error de base de datos: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error general: {e}")


# Interfaz
app = ctk.CTk()
app.title("Registro de Planilla de Pago")
app.geometry("650x750")  # Aumenté un poco la altura

ctk.CTkLabel(app, text="Planilla de Pago", font=("Arial", 22)).pack(pady=15)

# Sección para datos del pago principal
frame_pago = ctk.CTkFrame(app)
frame_pago.pack(pady=10, padx=10, fill="x")

proveedores_dict = cargar_proveedores()
partidas_dict = cargar_partidas()

ctk.CTkLabel(frame_pago, text="Proveedor:", anchor="w").pack(fill="x")
combo_proveedor = ctk.CTkComboBox(frame_pago, values=list(proveedores_dict.keys()))
combo_proveedor.pack(pady=5, fill="x")
combo_proveedor.set("Seleccionar proveedor")

ctk.CTkLabel(frame_pago, text="Partida Presupuestaria Principal:", anchor="w").pack(fill="x")
combo_partida = ctk.CTkComboBox(frame_pago, values=list(partidas_dict.keys()))
combo_partida.pack(pady=5, fill="x")
combo_partida.set("Seleccionar partida presupuestaria")
combo_partida.bind("<<ComboboxSelected>>", actualizar_saldo)
label_saldo = ctk.CTkLabel(frame_pago, text="Saldo disponible: ₡0.00", font=("Arial", 16))
label_saldo.pack(pady=5, fill="x")

ctk.CTkLabel(frame_pago, text="Descripción del pago:", anchor="w").pack(fill="x")
entry_desc = ctk.CTkEntry(frame_pago, placeholder_text="Descripción del pago")
entry_desc.pack(pady=5, fill="x")

ctk.CTkLabel(frame_pago, text="Número de factura:", anchor="w").pack(fill="x")
entry_factura = ctk.CTkEntry(frame_pago, placeholder_text="Número de factura")
entry_factura.pack(pady=5, fill="x")

# Sección para agregar partidas individuales
frame_agregar_partida = ctk.CTkFrame(app)
frame_agregar_partida.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(frame_agregar_partida, text="Agregar Partida Individual", font=("Arial", 16)).pack(pady=5)

ctk.CTkLabel(frame_agregar_partida, text="Partida:", anchor="w").pack(fill="x")
combo_nueva_partida = ttk.Combobox(frame_agregar_partida, values=list(partidas_dict.keys()))
combo_nueva_partida.pack(pady=5, fill="x")
combo_nueva_partida.set("Seleccionar partida")

ctk.CTkLabel(frame_agregar_partida, text="Monto:", anchor="w").pack(fill="x")
entry_monto_agregar = ctk.CTkEntry(frame_agregar_partida, placeholder_text="Monto")
entry_monto_agregar.pack(pady=5, fill="x")

ctk.CTkButton(frame_agregar_partida, text="Añadir Partida", command=agregar_partida).pack(pady=10)

# Sección para mostrar partidas añadidas
frame_partidas_agregadas = ctk.CTkFrame(app)
frame_partidas_agregadas.pack(pady=10, padx=10, fill="x", expand=True)
ctk.CTkLabel(frame_partidas_agregadas, text="Partidas Añadidas", font=("Arial", 16)).pack(pady=5)

tree_partidas = ttk.Treeview(frame_partidas_agregadas, columns=("Partida", "Monto"), show="headings", height=5)
tree_partidas.heading("Partida", text="Código Partida")
tree_partidas.heading("Monto", text="Monto Asignado")
tree_partidas.pack(fill="both", expand=True)

label_total_pago = ctk.CTkLabel(frame_partidas_agregadas, textvariable=total_pago, font=("Arial", 14, "bold"))
label_total_pago.pack(pady=5, anchor="e")

# Botones finales
frame_botones = ctk.CTkFrame(app)
frame_botones.pack(pady=15, padx=10, fill="x")
ctk.CTkButton(frame_botones, text="Registrar Pago", command=registrar_pago).pack(pady=5, fill="x")
ctk.CTkButton(frame_botones, text="Limpiar", command=limpiar_campos).pack(pady=5, fill="x")
ctk
