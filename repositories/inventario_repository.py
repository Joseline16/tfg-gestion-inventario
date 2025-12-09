from psycopg2.extras import RealDictCursor
from database.connection import get_connection


class InventarioRepository:

    @staticmethod
    def lista_productos():
        sql = """
            SELECT id_producto, nombre_producto, categoria, marca,
                   stock_actual, stock_minimo, precio_unitario, estado
            FROM productos
            ORDER BY nombre_producto;
        """
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    @staticmethod
    def get_producto_by_id(id_producto):
        sql = """
            SELECT id_producto, nombre_producto, categoria, marca,
                   stock_actual, stock_minimo, precio_unitario, estado
            FROM productos
            WHERE id_producto = %s;
        """
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (id_producto,))
                return cur.fetchone()

    @staticmethod
    def insertar_transaccion(conn, codigo_mov, id_usuario, fecha_mov, referencia, metodo_registro="manual"):
        """
        Inserta una transacción usando una conexión existente.
        Devuelve (id_transaccion, fecha_mov).
        """
        sql = """
            INSERT INTO transacciones
            (codigo_mov, id_usuario, fecha_mov, referencia, metodo_registro)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_transaccion, fecha_mov;
        """
        with conn.cursor() as cur:
            cur.execute(sql, (codigo_mov, id_usuario, fecha_mov, referencia, metodo_registro))
            return cur.fetchone()

    @staticmethod
    def insertar_mov_inventario(conn, codigo_mov, id_producto, cantidad, tipo_movimiento):
        """
        Inserta un movimiento de inventario usando una conexión existente.
        Devuelve (id_mov,).
        """
        sql = """
            INSERT INTO mov_inventario
            (codigo_mov, id_producto, cantidad, tipo_movimiento)
            VALUES (%s, %s, %s, %s)
            RETURNING id_mov;
        """
        with conn.cursor() as cur:
            cur.execute(sql, (codigo_mov, id_producto, cantidad, tipo_movimiento))
            return cur.fetchone()

    @staticmethod
    def existe_transaccion(codigo_mov: str) -> bool:
        """
        Verifica si existe una transacción con ese código.
        Esto garantiza que no se creen movimientos huérfanos.
        """
        sql = """
            SELECT 1
            FROM transacciones
            WHERE codigo_mov = %s
            LIMIT 1;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (codigo_mov,))
                return cur.fetchone() is not None

    @staticmethod
    def ultimos_movimientos(limit: int = 20):
        """
        Devuelve los últimos movimientos de inventario ya unidos a productos.
        """
        sql = """
            SELECT m.codigo_mov,
                   p.nombre_producto,
                   m.cantidad,
                   m.fecha,
                   m.tipo_movimiento
            FROM mov_inventario m
            LEFT JOIN productos p ON p.id_producto = m.id_producto
            ORDER BY m.fecha DESC
            LIMIT %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (limit,))
                rows = cur.fetchall()
        return rows
