# pages/usuarios.py

import streamlit as st
import pandas as pd
from services.usuario_service import UsuarioService
from utils.formato import configurar_pagina, verificar_acceso, sidebar_personalizado

service = UsuarioService()

# Configuración
configurar_pagina("Gestión de Usuarios - Sistema de Inventario")
verificar_acceso()
sidebar_personalizado()

# Usuario activo
usuario = st.session_state["usuario"]
nombre = usuario.get("nombre_usuario", "Usuario")
rol = st.session_state.get("rol", "")

st.title("Gestión de Usuarios")

# Seguridad: solo administradores
if rol != "administrador":
    st.error("No tienes permiso para acceder a esta sección.")
    st.stop()


#"""Devuelve el primer atributo existente en `u` entre names, o ''."""
def a(u, *names):
    for n in names:
        # dict-like
        if isinstance(u, dict) and n in u:
            return u[n]
        # objeto con atributo
        if hasattr(u, n):
            return getattr(u, n)
    return ""


def usuario_to_row(u):
    return {
        "id_usuario": a(u, "id_usuario", "id"),
        "nombre_usuario": a(u, "nombre_usuario", "nombre"),
        "email": a(u, "email"),
        "rol": a(u, "rol"),
        "telefono": a(u, "telefono"),
        "id_telegram": a(u, "id_telegram", "telegram"),
        "password": a(u, "password"), 
        "fecha_registro": a(u, "fecha_registro", "fecha"),
    }


def obtener_todos_usuarios():
    try:
        return service.obtener_usuarios(0, 1000000, "nombre_usuario", None, "ASC")
    except Exception as e:
        st.error(f"Error obteniendo usuarios: {e}")
        return []

def crear_usuario_ui(nombre, email, rol_u, telefono, telegram, password):
    return service.crear_usuario(nombre, email, rol_u, telefono, password, telegram)


def actualizar_usuario_ui(id_usuario, nombre, email, rol_u, telefono, password, telegram):
    return service.actualizar_usuario(id_usuario, nombre, email, rol_u, telefono, password, telegram)


#Dialogos
@st.dialog("Registrar nuevo usuario")
def modal_nuevo_usuario():
    st.write("Complete la información del nuevo usuario:")

    nombre = st.text_input("Nombre del usuario")
    email = st.text_input("Email")
    telefono = st.text_input("Teléfono")
    telegram = st.text_input("ID Telegram")
    password = st.text_input("Contraseña", type="password")
    rol_sel = st.selectbox("Rol", ["administrador", "empleado"])

    if st.button("Guardar"):
        if not nombre or not email or "@" not in email:
            st.error("Nombre y email válidos son obligatorios.")
            return
        if not password:
            st.error("La contraseña no puede estar vacía.")
            return

        try:
            r = crear_usuario_ui(nombre, email, rol_sel, telefono, telegram, password)
            if r:
                st.success("Usuario registrado correctamente.")
                st.rerun()
            else:
                st.error("Error al registrar usuario.")
        except Exception as e:
            st.error(str(e))


@st.dialog("Modificar usuario")
def modal_modificar_usuario(row: dict):
    st.write("Actualizar información del usuario:")

    nombre = st.text_input("Nombre", row.get("nombre_usuario", ""))
    email = st.text_input("Email", row.get("email", ""))
    telefono = st.text_input("Teléfono", row.get("telefono", ""))
    telegram = st.text_input("ID Telegram", row.get("id_telegram", ""))

    rol_sel = st.selectbox(
        "Rol",
        ["administrador", "empleado"],
        index=0 if row.get("rol") == "administrador" else 1
    )

    password = st.text_input(
        "Contraseña",
        value=row.get("password", ""),

    )

    if st.button("Actualizar"):
        if not nombre or not email or "@" not in email:
            st.error("Nombre y email válidos son obligatorios.")
            return
        if not password:
            st.error("La contraseña no puede estar vacía.")
            return

        try:
            r = actualizar_usuario_ui(
                row["id_usuario"], nombre, email, rol_sel, telefono, password, telegram
            )
            if r:
                st.success("Usuario actualizado correctamente.")
                st.rerun()
            else:
                st.error("Error al actualizar usuario.")
        except Exception as e:
            st.error(str(e))


#Principal
def main():
    # Filtros superiores
    col1, col2 = st.columns(2)

    with col1:
        campo = st.selectbox("Buscar por:", ["nombre_usuario", "email", "rol", "telefono"])
    with col2:
        valor = st.text_input("Valor")

    opciones = {
        "Nombre A-Z": ("nombre_usuario", True),
        "Nombre Z-A": ("nombre_usuario", False),
        "Email A-Z": ("email", True),
        "Email Z-A": ("email", False),
    }

    col3, col4 = st.columns(2)
    with col3:
        orden_sel = st.selectbox("Ordenar por:", list(opciones.keys()))

    campo_orden, asc = opciones[orden_sel]

    with col4:
        mostrar = st.selectbox("Mostrar:", [5, 10, 20, 50])

    st.markdown("---")

    # Obtener usuarios
    usuarios = obtener_todos_usuarios()
    rows = [usuario_to_row(u) for u in usuarios]
    df = pd.DataFrame(rows)

    # Filtro por campo/valor
    if valor and valor.strip():
        df = df[df[campo].astype(str).str.contains(valor, case=False, na=False)]

    # Orden
    df = df.sort_values(by=campo_orden, ascending=asc)

    # Paginación
    total = len(df)
    paginas = (total - 1) // mostrar + 1 if total > 0 else 1

    if "pagina_usr" not in st.session_state:
        st.session_state.pagina_usr = 1

    colA, colB, colC = st.columns([1, 2, 1])

    with colA:
        if st.button("⟵ Anterior", disabled=st.session_state.pagina_usr == 1):
            st.session_state.pagina_usr -= 1
            st.rerun()

    with colC:
        if st.button("Siguiente ⟶", disabled=st.session_state.pagina_usr == paginas):
            st.session_state.pagina_usr += 1
            st.rerun()

    with colB:
        st.markdown(
            f"<h5 style='text-align:center;'>Página {st.session_state.pagina_usr} / {paginas}</h5>",
            unsafe_allow_html=True,
        )

    ini = (st.session_state.pagina_usr - 1) * mostrar
    fin = ini + mostrar
    df_page = df.iloc[ini:fin].reset_index(drop=True)

    # Dataframe para mostrar (ocultamos password)
    df_display = df_page.drop(columns=["password"], errors="ignore")

    st.subheader("Usuarios")
    selected = st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
    )

    # Selección de fila
    row = None
    try:
        if selected and "selection" in selected and selected["selection"]["rows"]:
            row_index = selected["selection"]["rows"][0]
            # Usamos df_page (que sí contiene password)
            row = df_page.iloc[row_index].to_dict()
    except Exception:
        row = None

    # Botones CRUD
    st.divider()
    col_add, col_edit = st.columns(2)

    with col_add:
        if st.button("➕ Añadir usuario"):
            modal_nuevo_usuario()

    with col_edit:
        if st.button("✏️ Modificar", disabled=row is None):
            if row is not None:
                modal_modificar_usuario(row)


if __name__ == "__main__":
    main()
