# pages/productos.py
import streamlit as st
import pandas as pd
from services.producto_service import ProductoService
from utils.formato import configurar_pagina, verificar_acceso, sidebar_personalizado

service = ProductoService()

# Configuración
configurar_pagina("Productos - Sistema de Inventario")
verificar_acceso()
sidebar_personalizado()

# Obtener usuario activo
usuario = st.session_state["usuario"]
nombre = usuario["nombre_usuario"]
rol = st.session_state.get("rol", "")


#Modales

@st.dialog("Registrar nuevo producto")
def modal_nuevo_producto():
    st.write("Complete los datos del producto:")

    nombre = st.text_input("Nombre del producto")
    categoria = st.text_input("Categoría")
    marca = st.text_input("Marca")
    precio_unitario = st.number_input("Precio unitario", min_value=0.0, value=0.0, step=0.01)

    if st.button("Guardar"):
        r = service.crear(nombre, categoria, marca, precio_unitario)
        if r:
            st.success("Producto registrado correctamente.")
            st.rerun()
        else:
            st.error("Error al insertar producto.")


@st.dialog("Modificar producto")
def modal_modificar_producto(row):
    st.write("Actualizar información del producto:")

    nombre = st.text_input("Nombre", row["nombre_producto"])
    categoria = st.text_input("Categoría", row["categoria"])
    marca = st.text_input("Marca", row["marca"])
    precio = st.number_input("Precio unitario", value=float(row["precio_unitario"]))

    estado = st.selectbox("Estado", ["activo", "inactivo"], index=0 if row["estado"] == "activo" else 1)

    if st.button("Actualizar"):
        r = service.actualizar(
            row["id_producto"], nombre, categoria, marca, precio, estado
        )
        if r:
            st.success("Producto actualizado.")
            st.rerun()
        else:
            st.error("Error al actualizar producto.")


# Página principal
def main():

    st.markdown(
        """
        <div style="text-align:center; margin-top: -20px;">
            <h2 style="color:#000000; font-family:Arial;">
                Gestión de Productos
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Filtros
    cola, col1, col2, colb = st.columns([1, 2, 2, 1])
    with col1:
        campo = st.selectbox("Buscar por:", ["nombre_producto", "marca", "categoria"])
    with col2:
        valor = st.text_input("Valor")

    opciones = {
        "Nombre A-Z": ("nombre_producto", True),
        "Nombre Z-A": ("nombre_producto", False),
        "Precio ascendente": ("precio_unitario", True),
        "Precio descendente": ("precio_unitario", False),
    }

    cola, col3, col4, colb = st.columns([1, 2, 2, 1])
    with col3:
        orden_sel = st.selectbox("Ordenar por:", list(opciones.keys()))
    campo_orden, asc = opciones[orden_sel]

    with col4:
        cantidad = st.selectbox("Mostrar:", [5, 10, 20, 50])

    st.markdown("---")

    # Obtener productos
    productos = service.listar(0, 1000000)
    df = pd.DataFrame([p.to_dict() for p in productos])

    # Filtrar
    if valor.strip():
        df = df[df[campo].astype(str).str.contains(valor, case=False, na=False)]

    # Ordenar
    df = df.sort_values(by=campo_orden, ascending=asc)

    # Paginar
    total = len(df)
    paginas = max(1, (total - 1) // cantidad + 1)

    if "pagina_prod" not in st.session_state:
        st.session_state.pagina_prod = 1

    colA, colB, colC = st.columns([1, 2, 1])
    with colA:
        if st.button("⟵ Anterior", disabled=st.session_state.pagina_prod == 1):
            st.session_state.pagina_prod -= 1
            st.rerun()
    with colC:
        if st.button("Siguiente ⟶", disabled=st.session_state.pagina_prod == paginas):
            st.session_state.pagina_prod += 1
            st.rerun()
    with colB:
        st.markdown(
            f"<h5 style='text-align:center;'>Página {st.session_state.pagina_prod} / {paginas}</h5>",
            unsafe_allow_html=True,
        )

    ini = (st.session_state.pagina_prod - 1) * cantidad
    fin = ini + cantidad
    df_page = df.iloc[ini:fin].reset_index(drop=True)

    # Mostrar tabla
    st.subheader("Productos")
    selected = st.dataframe(df_page, use_container_width=True, hide_index=True, on_select="rerun")

    row = None
    try:
        if selected and selected.get("selection") and selected["selection"]["rows"]:
            row_index = selected["selection"]["rows"][0]
            row = df_page.iloc[row_index]
    except Exception:
        row = None

    # Botones CRUD
    st.divider()
    col_add, col_edit, col_del = st.columns(3)

    with col_add:
        if st.button("➕ Añadir producto"):
            modal_nuevo_producto()

    with col_edit:
        if st.button("✏️ Modificar", disabled=row is None):
            modal_modificar_producto(row)

    with col_del:
        if st.button("🗑️ Eliminar", disabled=row is None):
            r = service.eliminar(int(row["id_producto"]))
            if r:
                st.success("Producto eliminado.")
                st.rerun()
            else:
                st.error("Error al eliminar producto.")


if __name__ == "__main__":
    main()
