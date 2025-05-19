import customtkinter as ctk
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
import datetime  # Asegurarse que datetime está importado
from decimal import Decimal, InvalidOperation

# Variables globales (como en tu código original)
partidas_agregadas = []
programa_nombre = ""  # Inicializar programa_nombre


# Conexion a base de datos
def conectar_db():
    try:
        conn = pyodbc.connect(
            r'DRIVER={SQL Server};'
            r'SERVER=LAPTOP-V800EBTP\SQLEXPRESS01;'  # Revisa tu nombre de servidor
            r'DATABASE=Automatizacion;'
            r'Trusted_Connection=yes;'
        )
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


# Contiene todas las funciones
def crear_frame_planilla(master):
    # --- Definición de los frames principales del módulo ---
    # Frame principal que contendrá todo lo de este módulo
    frame_principal_modulo = ctk.CTkFrame(master, fg_color="transparent")  # Usar fg_color para que no tenga su propio fondo si no se desea

    # Frame para el formulario de ingreso de un nuevo pago
    formulario_frame = ctk.CTkFrame(frame_principal_modulo)

    # Frame para el historial de pagos
    registro_frame = ctk.CTkFrame(frame_principal_modulo)

    # --- Variables y Listas Específicas para una instancia de este frame ---
    # Usar una lista local para las partidas del pago actual, en lugar de la global `partidas_agregadas`
    # para evitar interferencias si este frame se recreara o si hubiera múltiples instancias (aunque no es el caso aquí).
    partidas_para_pago_actual = []

    # --- Widgets del formulario_frame ---
    ctk.CTkLabel(formulario_frame, text="Proveedor").pack(anchor="w", padx=10, pady=(5, 0))
    combo_proveedor = ctk.CTkComboBox(formulario_frame, width=350, values=[])  # Ancho ajustado
    combo_proveedor.pack(fill="x", padx=10, pady=(0, 5))

    ctk.CTkLabel(formulario_frame, text="Descripción del pago").pack(anchor="w", padx=10, pady=(5, 0))
    entry_desc = ctk.CTkEntry(formulario_frame, placeholder_text="Descripción", width=350)
    entry_desc.pack(fill="x", padx=10, pady=(0, 5))

    ctk.CTkLabel(formulario_frame, text="Número de Factura").pack(anchor="w", padx=10, pady=(5, 0))
    entry_factura = ctk.CTkEntry(formulario_frame, placeholder_text="Factura (NO Opcional)", width=350)
    entry_factura.pack(fill="x", padx=10, pady=(0, 10))

    ctk.CTkLabel(formulario_frame, text="Número de Transferencia").pack(anchor="w", padx=10, pady=(5, 0))
    entry_transferencia = ctk.CTkEntry(formulario_frame, placeholder_text="Transferencia (NO Opcional)", width=350)
    entry_transferencia.pack(fill="x", padx=10, pady=(0, 10))


    #PARA FUNCIONMIENTO DE LAS RETENCIONES
    tipo_var = ctk.StringVar(value="Con retención")
    retencion_var = ctk.StringVar(value="2")  # Valor real del entry
    def actualizar_entry_retencion():
        if tipo_var.get() == "Con retención":
            retencion_var.set("2")
            entry_valor_retencion.configure(state="normal")
        else:
            retencion_var.set("")
            entry_valor_retencion.configure(state="disabled")
    # Frame y radio buttons
    frame_tipo = ctk.CTkFrame(formulario_frame)
    frame_tipo.pack(pady=20, padx=20, anchor="w")
    ctk.CTkLabel(frame_tipo, text="   ").pack(side="left")
    ctk.CTkRadioButton(
        frame_tipo, text="Con retención", variable=tipo_var, value="Con retención",
        command=actualizar_entry_retencion
    ).pack(side="left", padx=10)
    ctk.CTkRadioButton(
        frame_tipo, text="Sin retención", variable=tipo_var, value="Sin retención",
        command=actualizar_entry_retencion
    ).pack(side="left")
    # Label y Entry de porcentaje
    ctk.CTkLabel(formulario_frame, text="Porcentaje de retención").pack(anchor="w", padx=10, pady=(5, 0))
    entry_valor_retencion = ctk.CTkEntry(formulario_frame, textvariable=retencion_var, width=40)
    entry_valor_retencion.pack(anchor="w", padx=10, pady=(0, 10))
    # Llamar una vez para aplicar el estado inicial
    actualizar_entry_retencion()



    # Sección de Distribución
    distribucion_subframe = ctk.CTkFrame(formulario_frame)
    distribucion_subframe.pack(fill="both", expand=True, padx=10, pady=5)

    ctk.CTkLabel(distribucion_subframe, text="Fuente de financiamiento").pack(anchor="w", padx=5, pady=(5, 0))
    combo_fuente = ctk.CTkComboBox(distribucion_subframe, width=450, values=[])  # Ancho ajustado
    combo_fuente.pack(fill="x", padx=5, pady=(0, 5))

    ctk.CTkLabel(distribucion_subframe, text="Programa (Asociado a Fuentes de financiamiento)").pack(anchor="w", padx=5,
                                                                                                 pady=(5, 0))
    combo_programa = ctk.CTkComboBox(distribucion_subframe, width=450, values=[])  # Este combo se poblará basado en la partida o será solo informativo
    combo_programa.pack(fill="x", padx=5, pady=(0, 5))

    ctk.CTkLabel(distribucion_subframe, text="Partida Presupuestaria").pack(anchor="w", padx=5, pady=(5, 0))
    combo_partida = ctk.CTkComboBox(distribucion_subframe, width=450, values=[])  # Ancho ajustado
    combo_partida.pack(fill="x", padx=5, pady=(0, 5))

    # Nota: La lógica original para combo_programa y la variable global programa_nombre era un poco confusa.
    # Se simplificará para que el programa se derive de la partida.

    ctk.CTkLabel(distribucion_subframe, text="Monto").pack(anchor="w", padx=5, pady=(5, 0))
    entry_monto = ctk.CTkEntry(distribucion_subframe, placeholder_text="Monto a afectar", width=150)
    entry_monto.pack(fill="x", padx=5, pady=(0, 10), side="left", expand=False)  # No expandir para que el botón quede al lado

    tree_partidas = ttk.Treeview(  # Treeview para la distribución del pago actual
        distribucion_subframe, columns=("Partida", "Monto", "Programa Ref."), show="headings", height=5,
    )
    tree_partidas.heading("Partida", text="Código Partida");
    tree_partidas.column("Partida", width=200)
    tree_partidas.heading("Monto", text="Monto Asignado");
    tree_partidas.column("Monto", width=100, anchor="e")
    tree_partidas.heading("Programa Ref.", text="Programa");
    tree_partidas.column("Programa Ref.", width=150)
    tree_partidas.pack(fill="both", expand=True, side="bottom", padx=5,
                      pady=5)  # Abajo de los controles de agregar

    total_pago = tk.DoubleVar(value=0.0)
    ctk.CTkLabel(formulario_frame, textvariable=total_pago, font=("Arial", 14, "bold")).pack(anchor="e", pady=5, padx=10)

    # --- Widgets del registro_frame (Historial de Pagos) ---
    ctk.CTkLabel(registro_frame, text="Historial de Pagos Registrados", font=("Arial", 18, "bold")).pack(pady=10)
    tree_registro_pagos = ttk.Treeview(
        registro_frame, columns=("ID", "Fecha", "Proveedor", "Factura", "Descripción", "Total"), show="headings",
        height=18
    )
    col_widths_hist = {"ID": 40, "Fecha": 90, "Proveedor": 200, "Factura": 100, "Descripción": 250, "Total": 100}
    col_anchors_hist = {"ID": "center", "Fecha": "center", "Proveedor": "w", "Factura": "center", "Descripción": "w",
                       "Total": "e"}
    for col_name_h in col_widths_hist:
        tree_registro_pagos.heading(col_name_h, text=col_name_h)
        tree_registro_pagos.column(col_name_h, width=col_widths_hist[col_name_h], anchor=col_anchors_hist[col_name_h],
                                  minwidth=40)
    tree_registro_pagos.pack(fill="both", expand=True, padx=10, pady=5)

    # --- Funciones Anidadas (Lógica del Módulo) ---
    def cargar_combos_formulario():
        conn_cb = None
        try:
            conn_cb = conectar_db()
            if not conn_cb:
                return

            # Cargar Proveedores
            cursor_prov = conn_cb.cursor()
            cursor_prov.execute("SELECT id, nombre FROM proveedores ORDER BY nombre")
            proveedores = cursor_prov.fetchall()
            proveedor_values = [f"{p[1]} (ID: {p[0]})" for p in proveedores]
            combo_proveedor.configure(values=proveedor_values)
            if proveedor_values:
                combo_proveedor.set(proveedor_values[0])
            else:
                combo_proveedor.set("No hay proveedores")

            # Cargar Fuentes de Financiamiento
            cursor_fuente = conn_cb.cursor()
            cursor_fuente.execute(
                "SELECT id, nombre, descripcion FROM fuentes_financiamiento ORDER BY nombre")
            fuentes_data = cursor_fuente.fetchall()  # Cambiado nombre para evitar conflicto
            # Formatear valores como: "nombre - descripcion (ID: X)"
            fuente_values = [f"{f[1]} - {f[2]} (ID: {f[0]})" for f in fuentes_data]
            combo_fuente.configure(values=fuente_values)
            if fuente_values:
                combo_fuente.set(fuente_values[0])
            else:
                combo_fuente.set("No hay fuentes registradas")

            # Cargar Programas (para el combo_programa)
            cursor_prog = conn_cb.cursor()
            cursor_prog.execute("SELECT id, nombre FROM programas ORDER BY nombre")
            programas_data = cursor_prog.fetchall()  # Cambiado nombre para evitar conflicto
            nonlocal programas_dict  # Para modificar la variable del alcance de crear_frame_planilla
            programas_dict = {f"{prog[1]} (ID: {prog[0]})": prog[0] for prog in
                              programas_data}  # Este es el programas_dict que usabas.
            programa_values_combo = list(programas_dict.keys())
            # combo_programa.configure(values=programa_values_combo) # Se llena dinámicamente
            if programa_values_combo:
                combo_programa.set(programa_values_combo[0])
            else:
                combo_programa.set("No hay programas")

            # Cargar Partidas (incluyendo la referencia al programa de la partida)
            cursor_part = conn_cb.cursor()
            cursor_part.execute(
                "SELECT pp.id, pp.codigo_partida, pp.descripcion, pr.nombre AS programa, ff.nombre AS fuente_financiamiento "
                "FROM partidas_presupuestarias pp "
                "JOIN programas pr ON pp.programa_id = pr.id "
                "JOIN fuentes_financiamiento ff ON pr.fuente_id = ff.id "  # Unir a través de pr.fuente_id
                "WHERE ISNULL(pp.monto_disponible,0) > 0 "
                "ORDER BY pp.codigo_partida"
            )
            partidas_data = cursor_part.fetchall()  # Cambiado nombre para evitar conflicto
            # El string del combo ahora guarda la ref. del programa de la partida directamente.
            # Incluir también la fuente en el string para filtrar
            partida_values = [
                f"{p[1]} - {p[2]} (Prog: {p[3] if p[3] else 'N/A'}, Fuente: {p[4] if p[4] else 'N/A'}, ID: {p[0]})"
                for p in partidas_data]
            #combo_partida.configure(values=partida_values) # Se llena dinámicamente
            if partida_values:
                combo_partida.set(partida_values[0])
            else:
                combo_partida.set("No hay partidas disponibles")

            # Guardar datos en diccionarios para acceso rápido
            nonlocal fuentes_dict
            fuentes_dict = {f"{f[1]} - {f[2]} (ID: {f[0]})": f[0] for f in fuentes_data}
            nonlocal partidas_dict
            partidas_dict = {
                f"{p[1]} - {p[2]} (Prog: {p[3] if p[3] else 'N/A'}, Fuente: {p[4] if p[4] else 'N/A'}, ID: {p[0]})": p[0]
                for p in partidas_data}

        except Exception as e_combos:
            messagebox.showerror("Error de Carga", f"No se pudieron cargar datos para combos: {e_combos}")
            print(f"Error cargando combos: {e_combos}")
        finally:
            if conn_cb:
                conn_cb.close()

    # Definir diccionarios en el alcance de crear_frame_planilla para que sea accesible
    programas_dict = {}
    proveedores_dict = {}  # Se poblará en cargar_combos_formulario y se usará en registrar_pago
    partidas_dict = {}
    fuentes_dict = {}

    def actualizar_programas(fuente_seleccionada):
        """Actualiza las opciones del combobox de Programas según la Fuente seleccionada."""
        programas_filtrados = []
        if fuente_seleccionada and fuente_seleccionada in fuentes_dict:
            fuente_id = fuentes_dict[fuente_seleccionada]
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT pr.nombre FROM partidas_presupuestarias pp "
                    "JOIN programas pr ON pp.programa_id = pr.id "
                    "WHERE pr.fuente_id = ?",  # <--  CORREGIDO:  Usar pr.fuente_id
                    fuente_id
                )
                programas_filtrados = [row[0] for row in cursor.fetchall()]
                conn.close()

        combo_programa.configure(values=programas_filtrados)
        combo_programa.set("Seleccione un Programa")
        actualizar_partidas(None)  # Limpiar partidas también

    def actualizar_partidas(programa_seleccionado):
        """Actualiza las opciones del combobox de Partidas según el Programa seleccionado."""
        partidas_filtradas = []
        if programa_seleccionado:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT pp.id, pp.codigo_partida, pp.descripcion, pr.nombre AS programa, ff.nombre AS fuente_financiamiento "
                    "FROM partidas_presupuestarias pp "
                    "JOIN programas pr ON pp.programa_id = pr.id "
                    "JOIN fuentes_financiamiento ff ON pr.fuente_id = ff.id "  # Corregido: Unir a través de pr.fuente_id
                    "WHERE pr.nombre = ? AND ISNULL(pp.monto_disponible,0) > 0",
                    programa_seleccionado
                )
                partidas_data = cursor.fetchall()
                partidas_filtradas = [
                    f"{p[1]} - {p[2]} (Prog: {p[3] if p[3] else 'N/A'}, Fuente: {p[4] if p[4] else 'N/A'}, ID: {p[0]})"
                    for p in partidas_data]
                conn.close()
        combo_partida.configure(values=partidas_filtradas)
        combo_partida.set("Seleccione una Partida")

    def agregar_partida_accion():  # Renombrado para evitar conflicto con variable global 'partidas_agregadas'
        nonlocal partidas_para_pago_actual  # Para modificar la lista local

        partida_sel_str = combo_partida.get()
        monto_str = entry_monto.get()
        # El programa ahora se infiere de la partida seleccionada, no del combo_programa independiente

        if not partida_sel_str or "ID: " not in partida_sel_str or "No hay partidas" in partida_sel_str:
            messagebox.showerror("Error", "Seleccione una partida válida.")
            return
        try:
            monto = Decimal(monto_str)
            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")
        except (ValueError, InvalidOperation) as e_val:
            messagebox.showerror("Error", f"Monto inválido: {e_val}")
            return

        try:
            partida_id = int(partida_sel_str.split("ID: ")[1].replace(")", ""))
            codigo_partida_mostrar = partida_sel_str.split(" (Prog:")[0]  # Para mostrar en treeview
            programa_ref_de_partida = partida_sel_str.split("Prog: ")[1].split(", Fuente:")[0].strip()
            fuente_ref_de_partida = partida_sel_str.split("Fuente: ")[1].split(", ID:")[0].strip()
        except (IndexError, ValueError):
            messagebox.showerror("Error", "No se pudo extraer información de la partida seleccionada.")
            return

        if not programa_ref_de_partida or programa_ref_de_partida == 'N/A' or not fuente_ref_de_partida or fuente_ref_de_partida == 'N/A':
            messagebox.showerror("Error de Datos",
                               f"La partida '{codigo_partida_mostrar}' no tiene una referencia de programa o fuente válida.")
            return

        # Verificar si la partida ya fue agregada
        #for item in partidas_para_pago_actual:
            #if item["id_partida"] == partida_id:
                #messagebox.showwarning("Advertencia", "Esta partida ya ha sido agregada a la distribución.")
                #return

        partidas_para_pago_actual.append({
            "id_partida": partida_id,
            "codigo_mostrar": codigo_partida_mostrar,
            "monto": monto,
            "programa_ref": programa_ref_de_partida,  # Esta es la referencia textual del programa de la partida
            "fuente_ref": fuente_ref_de_partida  # Referencia textual de la fuente
        })

        # Actualizar treeview de distribución y total
        for i in tree_partidas.get_children():
            tree_partidas.delete(i)
        current_total = Decimal("0.00")
        for item in partidas_para_pago_actual:
            tree_partidas.insert("", "end",
                              values=(item["codigo_mostrar"], f"₡{item['monto']:,.2f}", item["programa_ref"]))
            current_total += item['monto']
        total_pago.set(float(current_total))
        entry_monto.delete(0, tk.END)

    def registrar_pago_accion():  # Renombrado
        nonlocal partidas_para_pago_actual  # Acceder a la lista local
        nonlocal proveedores_dict  # Acceder al diccionario de proveedores

        if not partidas_para_pago_actual:
            messagebox.showerror("Error", "Debe agregar al menos una partida a la distribución.")
            return

        proveedor_sel_str = combo_proveedor.get()
        factura = entry_factura.get()
        descripcion = entry_desc.get()

        if not proveedor_sel_str or "Seleccionar" in proveedor_sel_str or "No hay proveedores" in proveedor_sel_str:
            messagebox.showerror("Error", "Seleccione un proveedor válido.")
            return
        if not descripcion.strip():  # La descripción es obligatoria
            messagebox.showerror("Error", "La descripción del pago es obligatoria.")
            return

        # Extraer ID del proveedor
        try:
            # Asumiendo que proveedores_dict se llenó correctamente en cargar_combos_formulario
            # Si no, necesitas una forma más robusta de obtener el ID del proveedor_sel_str
            proveedor_id = None
            for k, v in proveedores_dict.items():  # Reconstruir proveedores_dict si es necesario o buscar en el string
                if k == proveedor_sel_str:
                    proveedor_id = v
                    break
            if proveedor_id is None:  # Fallback si no se encuentra en el dict (debería estar)
                proveedor_id = int(proveedor_sel_str.split("ID: ")[1].replace(")", ""))

        except (IndexError, ValueError, AttributeError):
            messagebox.showerror("Error", "No se pudo obtener el ID del proveedor.")
            return

        conn_reg = None
        try:
            conn_reg = conectar_db()
            if not conn_reg:
                return
            cursor_reg = conn_reg.cursor()

            monto_total_pago_actual = Decimal(str(total_pago.get()))

            cursor_reg.execute(
                "INSERT INTO pagos (proveedor_id, factura, descripcion, total, fecha_pago) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, GETDATE())",
                proveedor_id, factura.strip() if factura.strip() else None, descripcion, monto_total_pago_actual
            )
            id_pago_nuevo = cursor_reg.fetchone()[0]

            for detalle in partidas_para_pago_actual:
                programa_ref_textual = detalle["programa_ref"]  # ej. 'FR' o 'Programa Comedor'
                fuente_ref_textual = detalle["fuente_ref"]

                # Buscar el ID numérico del programa en la tabla Programas
                cursor_reg.execute("SELECT id FROM Programas WHERE nombre = ?", programa_ref_textual)
                id_programa_tuple = cursor_reg.fetchone()

                if not id_programa_tuple:
                    messagebox.showerror("Error Crítico de Datos",
                                        f"El programa '{programa_ref_textual}' (referenciado por la partida) no existe en la tabla 'Programas'. Verifique la consistencia de datos.")
                    if conn_reg:
                        conn_reg.rollback()
                    return
                id_programa_numerico = id_programa_tuple[0]

                # Buscar el ID numérico de la fuente en la tabla Fuentes de Financiamiento
                cursor_reg.execute("SELECT id FROM fuentes_financiamiento WHERE nombre = ?", fuente_ref_textual)
                id_fuente_tuple = cursor_reg.fetchone()

                if not id_fuente_tuple:
                    messagebox.showerror("Error Crítico de Datos",
                                        f"La fuente '{fuente_ref_textual}' (referenciada por la partida) no existe en la tabla 'fuentes_financiamiento'. Verifique la consistencia de datos.")
                    if conn_reg:
                        conn_reg.rollback()
                    return
                id_fuente_numerico = id_fuente_tuple[0]

                cursor_reg.execute("SELECT monto_disponible FROM partidas_presupuestarias WHERE id = ?",
                                 detalle['id_partida'])
                saldo_partida_tuple = cursor_reg.fetchone()
                if not saldo_partida_tuple or saldo_partida_tuple[0] is None or detalle['monto'] > \
                        saldo_partida_tuple[0]:
                    messagebox.showerror("Error de Presupuesto",
                                        f"Saldo insuficiente en partida {detalle['codigo_mostrar']}.")
                    if conn_reg:
                        conn_reg.rollback()
                    return

                saldo_actual_decimal = saldo_partida_tuple[0]
                nuevo_saldo_decimal = saldo_actual_decimal - detalle['monto']


                # ACA SE REALIZA LA INSERCION PARA DETALLE DE PAGO
                # --- Obtener estado de retención y porcentaje ---
                con_retencion = tipo_var.get() == "Con retención"
                try:
                    porcentaje_retencion = Decimal(entry_valor_retencion.get()) if con_retencion else Decimal("0")
                except:
                    porcentaje_retencion = Decimal("0")  # Si el usuario escribe mal el valor

                try:
                    numero_transferencia = int(entry_transferencia.get().strip())
                except:
                    messagebox.showerror("Error", "Debe ingresar un número de transferencia válido.")
                    if conn_reg:
                        conn_reg.rollback()
                    return

                # Obtener saldo actual
                cursor_reg.execute("SELECT monto_disponible FROM partidas_presupuestarias WHERE id = ?",
                                detalle['id_partida'])
                saldo_partida_tuple = cursor_reg.fetchone()
                if not saldo_partida_tuple or saldo_partida_tuple[0] is None or detalle['monto'] > saldo_partida_tuple[0]:
                    messagebox.showerror("Error de Presupuesto",
                                        f"Saldo insuficiente en partida {detalle['codigo_mostrar']}.")
                    if conn_reg:
                        conn_reg.rollback()
                    return

                saldo_actual_decimal = saldo_partida_tuple[0]
                presupuesto_actual = saldo_actual_decimal  # Para guardar en columna
                valor_retencion = Decimal("0")

                if con_retencion:
                    valor_retencion = (detalle['monto'] * porcentaje_retencion) / Decimal("100")
                    saldo_antes = saldo_actual_decimal - valor_retencion
                else:
                    saldo_antes = saldo_actual_decimal

                nuevo_saldo_decimal = saldo_antes - detalle['monto']

                # Actualizar partida
                cursor_reg.execute(
                    "UPDATE partidas_presupuestarias SET monto_disponible = ? WHERE id = ?",
                    nuevo_saldo_decimal, detalle['id_partida']
                )

                # Insertar en detalle_pago_partidas
                cursor_reg.execute("""
                    INSERT INTO detalle_pago_partidas (
                        id_pago, id_partida, monto_asignado,
                        saldo_antes, saldo_despues, id_programa,
                        retencion, valor_retencion, numero_factura,
                        id_proveedor, descripcion, numero_transferencia,
                        presupuesto_actual
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_pago_nuevo,
                    detalle['id_partida'],
                    detalle['monto'],
                    saldo_antes,
                    nuevo_saldo_decimal,
                    id_programa_numerico,
                    int(con_retencion),
                    valor_retencion,
                    factura.strip() if factura.strip() else None,
                    proveedor_id,
                    descripcion.strip(),
                    numero_transferencia,
                    presupuesto_actual
                ))


            # Libro de bancos
            #cursor_reg.execute(
             #   "INSERT INTO libro_bancos (fecha, descripcion, monto, proveedor_id, numero_documento, monto_mas) VALUES (GETDATE(), ?, ?, ?, ?, '1')",
              #  f"Pago Factura #{factura}", monto_total_pago_actual,
               # factura.strip() if factura.strip() else None, proveedor_id
            #)

            conn_reg.commit()
            messagebox.showinfo("Éxito", f"Pago ID: {id_pago_nuevo} registrado correctamente.")
            limpiar_formulario_actual()  # Limpiar el formulario
        except pyodbc.Error as db_err:
            if conn_reg:
                conn_reg.rollback()
            messagebox.showerror("Error de Base de Datos", f"Error al registrar pago: {db_err}")
        except Exception as e:
            if conn_reg:
                conn_reg.rollback()
            messagebox.showerror("Error Inesperado", f"Fallo al registrar pago: {e}")
        finally:
            if conn_reg:
                conn_reg.close()

    def limpiar_formulario_actual():  # Renombrado para claridad
        nonlocal partidas_para_pago_actual
        entry_desc.delete(0, ctk.END)
        entry_factura.delete(0, ctk.END)
        entry_monto.delete(0, ctk.END)
        entry_transferencia.delete(0, ctk.END)
        for i in tree_partidas.get_children():
            tree_partidas.delete(i)
        partidas_para_pago_actual.clear()
        total_pago.set(0.0)
        cargar_combos_formulario()  # Recargar y resetear combos

    def mostrar_vista_historial_pagos():  # Renombrado para claridad
        formulario_frame.pack_forget()
        registro_frame.pack(fill="both", expand=True, padx=10, pady=5)  # Asegurar que se empaqueta
        cargar_historial_de_pagos()  # Llamar a la función de carga

    def cargar_historial_de_pagos():  # Renombrado para claridad
        try:
            for item in tree_registro_pagos.get_children():
                tree_registro_pagos.delete(item)

            conn = conectar_db()
            if not conn:
                return

            cursor = conn.cursor()
            query_historial = """
                SELECT p.id, p.fecha_pago, pr.nombre, p.factura, p.descripcion, p.total
                FROM pagos p JOIN proveedores pr ON p.proveedor_id = pr.id
                ORDER BY p.fecha_pago DESC, p.id DESC;
            """
            cursor.execute(query_historial)
            data = cursor.fetchall()
            conn.close()  # Cerrar conexión después de fetchall

            if not data:
                print("No hay pagos en el historial.")

            for row_data in data:
                fecha_db = row_data[1]
                fecha_formateada = "N/A"
                if fecha_db:
                    if isinstance(fecha_db, (datetime.datetime, datetime.date)):
                        fecha_formateada = fecha_db.strftime("%Y-%m-%d")
                    elif isinstance(fecha_db, str):
                        try:
                            fecha_formateada = datetime.datetime.strptime(fecha_db.split(" ")[0],
                                                                        "%Y-%m-%d").strftime("%Y-%m-%d")
                        except ValueError:
                            fecha_formateada = fecha_db
                    else:
                        fecha_formateada = str(fecha_db)

                monto_val = row_data[5]
                monto_formateado = f"₡{Decimal(monto_val if monto_val is not None else 0):,.2f}"
                tree_registro_pagos.insert("", "end",
                                          values=(row_data[0], fecha_formateada, row_data[2], row_data[3], row_data[4],
                                                  monto_formateado))

        except pyodbc.Error as db_err:
            messagebox.showerror("Error BD (Historial)", f"Error cargando historial: {db_err}")
            print(f"Error DB (Historial): {db_err}")
        except Exception as e:
            messagebox.showerror("Error (Historial)", f"Error inesperado cargando historial: {e}")
            print(f"Error inesperado (Historial): {e}")

    def mostrar_vista_formulario_pago():  # Renombrado para claridad
        registro_frame.pack_forget()
        formulario_frame.pack(padx=10, pady=10, fill="both", expand=True)
        # No es necesario llamar a limpiar_campos_pago_actual aquí si se hace al inicio o al registrar
        # Pero sí es bueno recargar los combos por si los datos cambiaron
        cargar_combos_formulario()

    # --- Botones y Lógica de Navegación ---
    # Botones del formulario
    ctk.CTkButton(distribucion_subframe, text="Agregar Partida a Distribución", command=agregar_partida_accion).pack(
        side="left", padx=(10, 5), pady=(0, 10))  # Mover al lado del monto
    ctk.CTkButton(formulario_frame, text="Registrar Pago", command=registrar_pago_accion, fg_color="green").pack(pady=10)
    ctk.CTkButton(formulario_frame, text="Ver Historial de Pagos", command=mostrar_vista_historial_pagos).pack(pady=5)

    # Botón en el frame de historial para volver
    ctk.CTkButton(registro_frame, text="Volver a Registrar Pago", command=mostrar_vista_formulario_pago).pack(pady=10)

    # --- Inicialización ---
    cargar_combos_formulario()  # Cargar datos en los combos al crear el frame
    # La variable global `partidas_agregadas` se limpia en `limpiar_formulario_actual`
    # La variable global `programa_nombre` se actualiza en `agregar_partida_accion`

    # Configurar los comandos de los comboboxes para la lógica en cascada
    combo_fuente.configure(command=actualizar_programas)
    combo_programa.configure(command=actualizar_partidas)

    mostrar_vista_formulario_pago()  # Mostrar el formulario de pago por defecto

    return frame_principal_modulo