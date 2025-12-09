# utils/layout.py
import streamlit as st

def configurar_pagina(titulo="Página", layout="wide"):
    st.set_page_config(page_title=titulo, layout=layout)

def verificar_acceso():
    if "usuario" not in st.session_state:
        st.error("Debes iniciar sesión primero.")
        st.stop()

def sidebar_personalizado():
    usuario = st.session_state.get("usuario", "")
    rol = st.session_state.get("rol", "")

    # ocultar nav streamlit
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # sidebar
    with st.sidebar:
        st.image("assets/logo.png", width=350)
        st.write("---")
        st.page_link("pages/inicio.py", label="🏠 Inicio")
        st.page_link("pages/dashboard.py", label="📊 Dashboard")
        st.page_link("pages/inventarios.py", label="📥 Inventarios")
        st.page_link("pages/productos.py", label="📦 Productos")
        if rol == "administrador":
            st.page_link("pages/usuarios.py", label="👤 Gestión de Usuarios")
        st.write("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.clear()
            st.switch_page("login.py")

