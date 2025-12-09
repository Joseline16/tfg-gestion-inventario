# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from services.dashboard_service import DashboardService 
service = DashboardService()
from utils.formato import configurar_pagina, verificar_acceso, sidebar_personalizado

# Configuración
configurar_pagina("dashboard - Sistema de Inventario")
verificar_acceso()
sidebar_personalizado()

# Obtener usuario activo
usuario = st.session_state["usuario"]
nombre = usuario["nombre_usuario"]
rol = st.session_state.get("rol", "")

st.title("📊 Dashboard de Ventas")

resumen = service.obtener_resumen_mes()

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

# Ventas por día
with col_grafico:
    st.subheader("📈 Ventas por día del mes")
    df_ventas_mes = service.obtener_ventas_mes_actual()

    if df_ventas_mes.empty:
        st.info("No hay ventas registradas este mes.")
    else:
        df_plot = df_ventas_mes.rename(columns={"dia": "Día", "total_dia": "Ventas"})
        df_plot = df_plot.sort_values("Día")
        fig_line = px.line(df_plot, x="Día", y="Ventas", title="Ventas por día", markers=True)
        fig_line.update_layout(height=ALTO_GRAFICOS, margin=dict(t=50, b=20))
        fig_line.update_traces(line=dict(color="#1f77b4"))
        st.plotly_chart(fig_line, use_container_width=True)

# Ventas por categoría
with col_torta:
    st.subheader("🍰 Ventas por categoría (mes actual)")
    df_categorias = service.ventas_por_categoria_mes()
    if df_categorias.empty:
        st.info("No hay ventas por categoría este mes.")
    else:
        fig_pie = px.pie(
            df_categorias,
            names="categoria",
            values="total_categoria",
            title="Distribución por categoría",
            hole=0.35,
        )
        fig_pie.update_layout(height=ALTO_GRAFICOS)
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
col_ranking, col_ultimas = st.columns([1, 1])

with col_ranking:
    st.subheader("🥇 Productos más vendidos")
    ranking = service.obtener_ranking_productos_vendidos()
    if ranking.empty:
        st.info("No hay datos suficientes para mostrar.")
    else:
        ranking = ranking.reset_index(drop=True)
        ranking = ranking.rename(columns={"nombre_producto": "Producto", "total_vendido": "Unidades vendidas"})
        st.dataframe(ranking.style.hide(axis="index"), use_container_width=True)

with col_ultimas:
    st.subheader("🧾 Últimas ventas registradas")
    ult = service.ultimas_ventas()
    if ult.empty:
        st.info("Todavía no hay ventas registradas.")
    else:
        ult = ult.reset_index(drop=True)
        ult = ult.rename(
            columns={
                "codigo_mov": "Código Movimiento",
                "nombre_producto": "Producto",
                "cantidad": "Cantidad",
                "precio_unitario": "Precio unitario",
                "precio_total": "Precio total",
                "fecha_mov": "Fecha de movimiento",
            }
        )
        st.dataframe(
            ult.style.format({"Precio unitario": "{:.2f}", "Precio total": "{:.2f}"}).hide(axis="index"),
            use_container_width=True,
        )


#bajo stock de productos 
st.markdown("---")
st.subheader("📉 Productos con menor stock")

df_stock = service.productos_bajo_stock() 

if df_stock.empty:
    st.info("No hay productos con stock por debajo del mínimo.")
else:
   
    df_temp = df_stock.copy()
    df_temp["diferencia"] = df_temp["stock_actual"] - df_temp["stock_minimo"]

    df_temp = df_temp.rename(columns={
        "id_producto": "ID",
        "nombre_producto": "Producto",
        "stock_actual": "Stock actual",
        "stock_minimo": "Stock mínimo",
        "diferencia": "Dif. (act - mín)"
    })

    # Mostramos solo las columnas importantes
    st.dataframe(
        df_temp[["ID", "Producto", "Stock actual", "Stock mínimo"]],
        use_container_width=True,
        hide_index=True
    )
