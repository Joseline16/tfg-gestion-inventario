import streamlit as st
from repositories.usuario_repository import UsuarioRepository
from services.auth_service import AuthService

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Si ya está logueado, redirigir a inicio
if st.session_state.get("logueado", False):
    st.switch_page("pages/inicio.py")

# Login form
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    with st.form("login_form"):
        st.title("StockFox")
        st.subheader("Iniciar Sesión")

        # <- Cambios: añadimos keys para que Streamlit persista los valores entre reruns
        email = st.text_input("Email", key="email_input")
        password = st.text_input("Password", type="password", key="password_input")

        btn = st.form_submit_button("Sign In")

# Revisa login
if btn:
    if not st.session_state["email_input"] or not st.session_state["password_input"]:
        st.error("Por favor ingresa email y contraseña.")
    else:
        repo = UsuarioRepository()
        auth = AuthService(repo)

        # usamos los valores persistidos en session_state para mayor fiabilidad
        usuario, error = auth.login(st.session_state["email_input"], st.session_state["password_input"])

        if usuario:
            st.session_state["usuario"] = usuario
            st.session_state["logueado"] = True
            st.session_state["rol"] = usuario["rol"]  # ← NECESARIO

            st.success(f"Bienvenido, {usuario['nombre_usuario']}!")
            st.switch_page("pages/inicio.py")
        else:
            # <-- IMPORTANT: NO limpiar st.session_state["password_input"]
            # Simplemente mostramos el error; el input seguirá mostrando la contraseña
            st.error(error)

# Extras 
load_css("style.css")

# Ocultar sidebar si NO está logueado
if not st.session_state.get("logueado", False):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .block-container {padding-left: 2rem !important;}
    </style>
    """, unsafe_allow_html=True)

# Inputs blancos
st.markdown(""" 
<style>
.stTextInput > div > div > input {
    background-color: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)
