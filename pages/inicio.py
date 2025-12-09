import streamlit as st
from services.dashboard_service import DashboardService
import pandas as pd
service = DashboardService()  
from datetime import datetime, timedelta
from utils.formato import configurar_pagina, verificar_acceso, sidebar_personalizado
from streamlit_extras.switch_page_button import switch_page

# Configuración
configurar_pagina("Inicio - Sistema de Inventario")
verificar_acceso()
sidebar_personalizado()

# Obtener usuario activo
usuario = st.session_state["usuario"]
nombre = usuario["nombre_usuario"]

#Saludo y bienvenida
st.title(f"📦 Sistema Inteligente de Gestión de Inventario")
st.markdown(f"###  Bienvenido, **{nombre}**")
st.caption("Control y análisis en un solo lugar.")

st.markdown("---")

resumen = service.obtener_resumen_mes()

#Tarjetas KPI
col1, col2, col3, col4 = st.columns(4)

def kpi_card(titulo: str, valor: str, icono: str = ""):
    st.markdown(
        f"""
        <div style="
            background-color: #ffffff;
            border-radius: 14px;
            padding: 18px 12px;
            border: 1px solid #dcdcdc;
            text-align:center;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        ">
            <div style="font-size: 16px; font-weight: 600; color:#555; margin-bottom: 6px;">
                {icono} {titulo}
            </div>
            <div style="font-size: 30px; font-weight: 800; color:#222;">
                {valor}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col1:
    kpi_card("Ventas del mes", resumen.get("ventas_mes", 0), "🛒")

with col2:
    ingresos = resumen.get("ingresos_mes", 0.0)
    kpi_card("Ingresos del mes", f"€ {ingresos:,.2f}", "💵")

with col3:
    kpi_card("Ventas hoy", resumen.get("ventas_hoy", 0), "📅")

with col4:
    kpi_card("Productos bajo stock", resumen.get("productos_bajo_stock", 0), "⚠️")

st.markdown("---")

col_grafico, col_torta = st.columns([2, 1])
ALTO_GRAFICOS = 380


# Ventas últimos 7 días y ultimas ventas
col_left, col_right = st.columns([2, 2])

with col_left:
    st.subheader("📈 Ventas últimos 7 días")

    df_ventas_mes = service.obtener_ventas_mes_actual()

    if df_ventas_mes.empty:
        st.info("No hay datos de ventas para mostrar.")
    else:
        df_temp = df_ventas_mes.copy()

        # Aseguramos tipo fecha
        df_temp["dia"] = pd.to_datetime(df_temp["dia"])

        # Rango de los últimos 7 días (incluyendo hoy)
        hoy = datetime.now().date()
        inicio = hoy - timedelta(days=6)
        rango_fechas = pd.date_range(inicio, hoy)

        # Creamos un dataframe con todos los días del rango
        df_rango = pd.DataFrame({"dia": rango_fechas})

        # Unimos con los datos reales y rellenamos días sin ventas con 0
        df_temp = df_rango.merge(df_temp, on="dia", how="left").fillna(0.0)

        # Formateamos el eje X
        df_temp["dia_str"] = df_temp["dia"].dt.strftime("%d-%m")
        df_temp = df_temp.set_index("dia_str")[["total_dia"]]
        df_temp.rename(columns={"total_dia": "Total (€)"}, inplace=True)

        # Gráfico más compacto
        st.line_chart(df_temp, height=280, use_container_width=True)

with col_right:
    df_ultimas = service.ultimas_ventas(8)

    st.subheader("🧾 Últimas ventas registradas")

    if df_ultimas.empty:
        st.info("No hay ventas registradas.")
    else:
        df_temp = df_ultimas.copy()
        df_temp["fecha_mov"] = df_temp["fecha_mov"].dt.strftime("%d-%m-%Y %H:%M")
        df_temp = df_temp.rename(columns={
            "codigo_mov": "Código",
            "nombre_producto": "Producto",
            "cantidad": "Cantidad",
            "precio_total": "Total (€)",
            "fecha_mov": "Fecha"
    })
    st.dataframe(df_temp[["Código", "Producto", "Cantidad", "Total (€)", "Fecha"]], use_container_width=True)

#Botones de navegación rápida

destino = st.session_state.get("pagina_actual", None)

if destino:
    st.session_state["pagina_actual"] = None
    try:
        st.switch_page(f"pages/{destino}.py")
    except Exception:
        st.warning(f"⚠️ La página '{destino}' no existe en /pages.")

c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("📦 Registro de inventario"):
        st.session_state["pagina_actual"] = "inventarios"

with c2:
    if st.button("🛒 Gestión de productos"):
        st.session_state["pagina_actual"] = "productos"

with c3:
    if st.button("👤 Gestión de usuarios"):
        st.session_state["pagina_actual"] = "usuarios"

with c4:
    if st.button("📊 Dashboard analítico"):
        st.session_state["pagina_actual"] = "dashboard"

st.markdown("---")

# información de telegram IA 
st.subheader("🤖 IA para lectura de facturas")

st.info(
    """
Envía tus facturas por **Telegram** y nuestro sistema las analiza y registra automáticamente.  
Ideal para mantener tu inventario y tus ventas actualizadas sin esfuerzo.
"""
)
