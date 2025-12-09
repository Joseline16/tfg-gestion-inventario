# repositories/dashboard_repository.py
from database.connection import get_connection
from datetime import datetime
import pandas as pd
import logging
from typing import Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DashboardRepository:
    """
    Repositorio para métricas del dashboard usando las tablas:
      - mov_inventario (id_mov, codigo_mov, id_producto, cantidad, fecha, tipo_movimiento)
      - transacciones (id_transaccion, codigo_mov, id_usuario, fecha_mov, referencia, metodo_registro)
      - productos (id_producto, nombre_producto, categoria, marca, stock_actual, stock_minimo, precio_unitario, estado, fecha_creacion)
      - stock_seguridad_categoria (categoria, stock_seguridad, fecha)
    """

    def _get_conn(self):
        conn = get_connection()
        if not conn:
            raise ConnectionError("No se pudo obtener conexión a la base de datos.")
        return conn

    def obtener_resumen_mes(self) -> Dict[str, float]:
        ahora = datetime.now()
        mes = ahora.month
        anio = ahora.year
        try:
            conn = self._get_conn()
            with conn.cursor() as cursor:
                # Ventas del mes (contador de movimientos de tipo 'venta')
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM mov_inventario m
                    JOIN transacciones t ON m.codigo_mov = t.codigo_mov
                    WHERE m.tipo_movimiento = 'venta'
                      AND EXTRACT(MONTH FROM t.fecha_mov) = %s
                      AND EXTRACT(YEAR FROM t.fecha_mov) = %s
                    """,
                    (mes, anio),
                )
                ventas_mes = int(cursor.fetchone()[0] or 0)

                # Ingresos del mes (cantidad * precio_unitario)
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(m.cantidad * p.precio_unitario), 0)
                    FROM mov_inventario m
                    JOIN productos p ON m.id_producto = p.id_producto
                    JOIN transacciones t ON m.codigo_mov = t.codigo_mov
                    WHERE m.tipo_movimiento = 'venta'
                      AND EXTRACT(MONTH FROM t.fecha_mov) = %s
                      AND EXTRACT(YEAR FROM t.fecha_mov) = %s
                    """,
                    (mes, anio),
                )
                ingresos_mes = float(cursor.fetchone()[0] or 0.0)

                # Ventas hoy
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM mov_inventario m
                    JOIN transacciones t ON m.codigo_mov = t.codigo_mov
                    WHERE m.tipo_movimiento = 'venta'
                      AND DATE(t.fecha_mov) = CURRENT_DATE
                    """
                )
                ventas_hoy = int(cursor.fetchone()[0] or 0)

                # Productos bajo stock (solo activos)
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM productos
                    WHERE stock_actual < stock_minimo
                      AND estado = 'activo'
                    """
                )
                productos_bajo_stock = int(cursor.fetchone()[0] or 0)

            conn.close()
            return {
                "ventas_mes": ventas_mes,
                "ingresos_mes": round(ingresos_mes, 2),
                "ventas_hoy": ventas_hoy,
                "productos_bajo_stock": productos_bajo_stock,
            }
        except Exception:
            logger.exception("[DashboardRepository][obtener_resumen_mes] Error")
            return {
                "ventas_mes": 0,
                "ingresos_mes": 0.0,
                "ventas_hoy": 0,
                "productos_bajo_stock": 0,
            }

    def obtener_ventas_mes_actual(self) -> pd.DataFrame:
        """
        Devuelve DataFrame con columnas: 'dia' (date) y 'total_dia' (float).
        Usa mov_inventario + transacciones + productos y filtra por tipo_movimiento = 'venta'.
        """
        ahora = datetime.now()
        mes = ahora.month
        anio = ahora.year

        query = """
            SELECT
                DATE(t.fecha_mov) AS dia,
                SUM(m.cantidad * p.precio_unitario) AS total_dia
            FROM mov_inventario m
            JOIN transacciones t ON m.codigo_mov = t.codigo_mov
            JOIN productos p ON m.id_producto = p.id_producto
            WHERE m.tipo_movimiento = 'venta'
              AND EXTRACT(MONTH FROM t.fecha_mov) = %s
              AND EXTRACT(YEAR FROM t.fecha_mov) = %s
            GROUP BY dia
            ORDER BY dia ASC
        """
        try:
            conn = self._get_conn()
            df = pd.read_sql_query(query, conn, params=[mes, anio])
            conn.close()
            if not df.empty:
                df["dia"] = pd.to_datetime(df["dia"]).dt.date
                df["total_dia"] = df["total_dia"].astype(float)
            return df
        except Exception:
            logger.exception("[DashboardRepository][obtener_ventas_mes_actual] Error")
            return pd.DataFrame(columns=["dia", "total_dia"])

    def obtener_ranking_productos_vendidos(self, limit: int = 10) -> pd.DataFrame:
        """
        Top N productos por cantidad vendida (histórico).
        Si quieres top del mes actual, lo adaptamos filtrando por t.fecha_mov.
        """
        query = """
            SELECT
                p.nombre_producto,
                SUM(m.cantidad) AS total_vendido
            FROM mov_inventario m
            JOIN productos p ON m.id_producto = p.id_producto
            WHERE m.tipo_movimiento = 'venta'
            GROUP BY p.nombre_producto
            ORDER BY total_vendido DESC
            LIMIT %s
        """
        try:
            conn = self._get_conn()
            df = pd.read_sql_query(query, conn, params=[limit])
            conn.close()
            if not df.empty:
                df["total_vendido"] = df["total_vendido"].astype(int)
            return df
        except Exception:
            logger.exception("[DashboardRepository][obtener_ranking_productos_vendidos] Error")
            return pd.DataFrame(columns=["nombre_producto", "total_vendido"])

    def ultimas_ventas(self, limite: int = 10) -> pd.DataFrame:
        """
        Últimas N líneas de mov_inventario tipo 'venta' con datos de producto y fecha.
        """
        query = """
            SELECT 
                m.codigo_mov,
                p.nombre_producto,
                m.cantidad,
                p.precio_unitario,
                (p.precio_unitario * m.cantidad) AS precio_total,
                t.fecha_mov
            FROM mov_inventario m
            JOIN transacciones t ON m.codigo_mov = t.codigo_mov
            JOIN productos p ON m.id_producto = p.id_producto
            WHERE m.tipo_movimiento = 'venta'
            ORDER BY t.fecha_mov DESC
            LIMIT %s
        """
        try:
            conn = self._get_conn()
            df = pd.read_sql_query(query, conn, params=[limite])
            conn.close()
            if not df.empty:
                df["fecha_mov"] = pd.to_datetime(df["fecha_mov"])
                df["cantidad"] = df["cantidad"].astype(int)
                df["precio_unitario"] = df["precio_unitario"].astype(float)
                df["precio_total"] = df["precio_total"].astype(float)
            return df
        except Exception:
            logger.exception("[DashboardRepository][ultimas_ventas] Error")
            return pd.DataFrame(
                columns=[
                    "codigo_mov",
                    "nombre_producto",
                    "cantidad",
                    "precio_unitario",
                    "precio_total",
                    "fecha_mov",
                ]
            )

    def productos_bajo_stock(self) -> pd.DataFrame:
        """
        Lista productos activos cuyo stock_actual < stock_minimo.
        """
        query = """
            SELECT 
                id_producto,
                nombre_producto,
                stock_actual,
                stock_minimo
            FROM productos
            WHERE stock_actual < stock_minimo
              AND estado = 'activo'
            ORDER BY stock_actual ASC
        """
        try:
            conn = self._get_conn()
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception:
            logger.exception("[DashboardRepository][productos_bajo_stock] Error")
            return pd.DataFrame(columns=["id_producto", "nombre_producto", "stock_actual", "stock_minimo"])

    def ventas_por_categoria_mes(self) -> pd.DataFrame:
        """
        Total ventas por categoria en el mes actual (suma de cantidad * precio_unitario).
        """
        ahora = datetime.now()
        mes = ahora.month
        anio = ahora.year

        query = """
            SELECT
                p.categoria,
                SUM(m.cantidad * p.precio_unitario) AS total_categoria
            FROM mov_inventario m
            JOIN productos p ON m.id_producto = p.id_producto
            JOIN transacciones t ON m.codigo_mov = t.codigo_mov
            WHERE m.tipo_movimiento = 'venta'
              AND EXTRACT(MONTH FROM t.fecha_mov) = %s
              AND EXTRACT(YEAR FROM t.fecha_mov) = %s
            GROUP BY p.categoria
            ORDER BY total_categoria DESC
        """
        try:
            conn = self._get_conn()
            df = pd.read_sql_query(query, conn, params=[mes, anio])
            conn.close()
            if not df.empty:
                df["total_categoria"] = df["total_categoria"].astype(float)
            return df
        except Exception:
            logger.exception("[DashboardRepository][ventas_por_categoria_mes] Error")
            return pd.DataFrame(columns=["categoria", "total_categoria"])
