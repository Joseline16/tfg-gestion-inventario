import streamlit as st
import pandas as pd
from database.connection import get_connection
from services.inventario_service import InventarioService
from utils.formato import configurar_pagina, verificar_acceso, sidebar_personalizado

service = InventarioService()

# Configuración
configurar_pagina("Inventarios - Sistema de Inventario")
verificar_acceso()
sidebar_personalizado()

# Usuario activo
usuario = st.session_state["usuario"]
nombre = usuario.get("nombre_usuario", "Usuario")
rol = st.session_state.get("rol", "")
id_usuario = usuario.get("id_usuario", usuario.get("id", 0))

# Estado inicial , crea almacenamiento temporal a nivel de sesión de usuario que ha hecho login
if "ultimo_codigo_mov" not in st.session_state:
    st.session_state.ultimo_codigo_mov = ""
if "productos_temp" not in st.session_state:
    st.session_state.productos_temp = []
if "confirmar_productos" not in st.session_state:
    st.session_state.confirmar_productos = False
if "tipo_movimiento_temp" not in st.session_state:
    st.session_state.tipo_movimiento_temp = "venta"

#Caja de regirtro de inventarios
tab1, tab2 = st.tabs(["📝 Registrar Transacción", "📦 Registrar Movimientos de Inventario"])

#Transacciones 
with tab1:
    st.subheader("Registrar Nueva Transacción")

    with st.form("form_transaccion"):
        col1, col2 = st.columns(2)

        with col1:
            codigo_mov = st.text_input("Código de Movimiento*", placeholder="Ej: VTA0001")
            fecha_mov = st.date_input("Fecha*")
        with col2:
            referencia = st.text_input("Referencia", placeholder="Opcional")

        st.info(f"👤 Usuario: {nombre} (ID: {id_usuario})")

        btn_guardar_trans = st.form_submit_button(
            "💾 Guardar Transacción", type="primary", use_container_width=True
        )

        if btn_guardar_trans:
            if not codigo_mov:
                st.error("❌ El código de movimiento es obligatorio")
            else:
                conn = None
                try:
                    conn = get_connection()
                    conn.autocommit = False

                    trans = service.repo.insertar_transaccion(
                        conn, codigo_mov, id_usuario, fecha_mov, referencia or None, "manual"
                    )

                    conn.commit()

                    # Se guarda el código en el estado de sesión para usarlo en la siguiente pestaña
                    st.session_state.ultimo_codigo_mov = codigo_mov

                    st.success("✅ Transacción registrada correctamente.")
                    st.info(f"📦 Código: **{codigo_mov}** | ID: **{trans[0]}**")
                    st.info(
                        "➡️ Ahora ve a la pestaña 'Registrar Movimientos de Inventario' para agregar productos."
                    )
                    st.balloons()

                except Exception as e:
                    if conn:
                        conn.rollback()
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    if conn:
                        conn.close()

# Movimientos de inventario
with tab2:
    st.subheader("Registrar Movimientos de Inventario")

    # Mostrar código de la última transacción
    if st.session_state.ultimo_codigo_mov:
        st.success(f"✅ Usando código de transacción: **{st.session_state.ultimo_codigo_mov}**")
    else:
        st.warning("Primero registra una transacción en la pestaña anterior.")

    # formulario de añadir productos
    if not st.session_state.confirmar_productos:

        # Si ya hay productos agregados, los mostramos
        if st.session_state.productos_temp:
            st.write("### 📦 Productos agregados:")

            for idx, prod in enumerate(st.session_state.productos_temp):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1.2, 0.8, 0.5])
                with col1:
                    st.write(f"**{prod['nombre_producto']}**")
                with col2:
                    st.write(f"*{prod['marca_producto']}*")
                with col3:
                    st.write(f"Cant: **{prod['cantidad']}**")
                with col4:
                    st.write(f"ID: {prod['id_producto']}")
                with col5:
                    if st.button("🗑️", key=f"del_prod_{idx}"):
                        st.session_state.productos_temp.pop(idx)
                        st.rerun()

            st.divider()

        with st.form("form_movimiento"):
            col1, col2 = st.columns(2)

            with col1:
                codigo_mov_inv = st.text_input(
                    "Código de Movimiento*",
                    value=st.session_state.ultimo_codigo_mov,
                    placeholder="Debe existir en transacciones",
                )
                id_producto = st.number_input("ID Producto*", min_value=1, step=1)

            with col2:
                cantidad = st.number_input(
                    "Cantidad*", min_value=0.1, value=1.0, step=1.0, format="%.1f"
                )
                tipo_movimiento = st.selectbox(
                    "Tipo de Movimiento*",
                    ["venta", "compra", "ajuste"],
                    index=["venta", "compra", "ajuste"].index(
                        st.session_state.tipo_movimiento_temp
                    ),
                )

            col1b, col2b, col3b = st.columns(3)
            with col1b:
                btn_agregar = st.form_submit_button("➕ Agregar Producto", use_container_width=True)
            with col2b:
                btn_finalizar = st.form_submit_button(
                    "✅ Revisar y Guardar", type="primary", use_container_width=True
                )
            with col3b:
                btn_cancelar = st.form_submit_button(
                    "❌ Cancelar Todo", use_container_width=True
                )

            # Agregar producto a la lista temporal
            if btn_agregar:
                if not codigo_mov_inv:
                    st.error("❌ El código de movimiento es obligatorio")
                elif not service.repo.existe_transaccion(codigo_mov_inv):
                    st.error(
                        "❌ El código de movimiento no existe. "
                        "Primero registra la transacción en la pestaña anterior."
                    )
                elif cantidad <= 0:
                    st.error("❌ La cantidad debe ser mayor a 0")
                else:
                    try:
                        producto = service.repo.get_producto_by_id(int(id_producto))
                        if not producto:
                            st.error("❌ El producto no existe")
                            st.stop()

                        # Evitar duplicados
                        if any(
                            p["id_producto"] == int(id_producto)
                            for p in st.session_state.productos_temp
                        ):
                            st.error("❌ Este producto ya fue agregado")
                            st.stop()

                        # Validar stock en venta
                        if tipo_movimiento == "venta":
                            stock_actual = producto.get("stock_actual", 0)
                            if stock_actual < cantidad:
                                st.error(
                                    f"❌ Stock insuficiente. Disponible: {stock_actual}"
                                )
                                st.stop()

                        # Agregar a la lista temporal
                        st.session_state.productos_temp.append(
                            {
                                "id_producto": int(id_producto),
                                "cantidad": float(cantidad),
                                "nombre_producto": producto.get(
                                    "nombre_producto", "Desconocido"
                                ),
                                "marca_producto": producto.get("marca", "Sin marca"),
                                "stock_actual": producto.get("stock_actual", 0),
                            }
                        )

                        st.session_state.ultimo_codigo_mov = codigo_mov_inv
                        st.session_state.tipo_movimiento_temp = tipo_movimiento

                        st.success(f"✅ {producto.get('nombre_producto')} agregado")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # modo: finalizar y revisar
            if btn_finalizar:
                if not st.session_state.productos_temp:
                    st.error("❌ Debes agregar al menos un producto")
                elif not codigo_mov_inv:
                    st.error("❌ El código de movimiento es obligatorio")
                elif not service.repo.existe_transaccion(codigo_mov_inv):
                    st.error(
                        "❌ El código de movimiento no existe. "
                        "Primero registra la transacción en la pestaña anterior."
                    )
                else:
                    st.session_state.ultimo_codigo_mov = codigo_mov_inv
                    st.session_state.tipo_movimiento_temp = tipo_movimiento
                    st.session_state.confirmar_productos = True
                    st.rerun()

            # Cancelar todo
            if btn_cancelar:
                st.session_state.productos_temp = []
                st.session_state.confirmar_productos = False
                st.rerun()

    # Resumen y confirmación de movimientos
    else:
        st.subheader("📋 Resumen de Productos a Registrar")

        st.info(
            f"📦 Código de Movimiento: **{st.session_state.ultimo_codigo_mov}** "
            f"| Tipo: **{st.session_state.tipo_movimiento_temp.upper()}**"
        )

        tabla_productos = [
            {
                "ID": p["id_producto"],
                "Producto": p["nombre_producto"],
                "Marca": p["marca_producto"],
                "Cantidad": p["cantidad"],
                "Stock Actual": p["stock_actual"],
            }
            for p in st.session_state.productos_temp
        ]

        df_productos = pd.DataFrame(tabla_productos)
        st.dataframe(df_productos, use_container_width=True, hide_index=True)

        st.write(f"**Total de productos:** {len(st.session_state.productos_temp)}")

        col1c, col2c = st.columns(2)

        # Confirmar y guardar movimientos
        with col1c:
            if st.button("✅ Confirmar y Guardar Todo", type="primary", use_container_width=True):
                conn = None
                try:
                    # Validación extra: la transacción debe existir
                    if not service.repo.existe_transaccion(
                        st.session_state.ultimo_codigo_mov
                    ):
                        st.error(
                            "❌ La transacción asociada no existe. "
                            "Vuelve a registrar la transacción."
                        )
                        st.stop()

                    conn = get_connection()
                    conn.autocommit = False

                    movimientos_guardados = []

                    for prod in st.session_state.productos_temp:
                        mov = service.repo.insertar_mov_inventario(
                            conn,
                            st.session_state.ultimo_codigo_mov,
                            prod["id_producto"],
                            prod["cantidad"],
                            st.session_state.tipo_movimiento_temp,
                        )
                        movimientos_guardados.append(
                            {
                                "id_mov": mov[0],
                                "producto": prod["nombre_producto"],
                                "cantidad": prod["cantidad"],
                            }
                        )

                    conn.commit()

                    st.success(
                        f"✅ {len(movimientos_guardados)} movimiento(s) registrado(s) correctamente."
                    )

                    with st.expander("Ver detalles", expanded=True):
                        for mov in movimientos_guardados:
                            st.info(
                                f"✓ {mov['producto']} - Cantidad: {mov['cantidad']} "
                                f"(ID movimiento: {mov['id_mov']})"
                            )

                    # Limpiar estados
                    st.session_state.productos_temp = []
                    st.session_state.confirmar_productos = False
                    st.balloons()

                except Exception as e:
                    if conn:
                        conn.rollback()
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    if conn:
                        conn.close()

        # Volver a editar
        with col2c:
            if st.button("⬅️ Volver a Editar", use_container_width=True):
                st.session_state.confirmar_productos = False
                st.rerun()

# Mostrar últimos movimientos registrados
st.markdown("---")
st.subheader("📊 Últimos Movimientos")

rows = service.repo.ultimos_movimientos(limit=20)

if rows:
    df = pd.DataFrame(
        rows,
        columns=["Código", "Producto", "Cantidad", "Fecha", "Tipo"],
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No hay movimientos registrados aún.")
