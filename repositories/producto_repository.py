# repositories/producto_repository.py
from database.connection import get_connection
from models.producto import Producto


class ProductoRepository:

    def obtener(self, offset, limit, filtro_campo=None, filtro_valor=None, orden_field="id_producto", asc=True):
        try:
            conn = get_connection()
            if not conn:
                return []

            order_dir = "ASC" if asc else "DESC"

            query = """
                SELECT id_producto, nombre_producto, categoria, marca,
                       stock_actual, stock_minimo, precio_unitario, estado, fecha_creacion
                FROM productos
                WHERE estado = 'activo'
            """

            params = []

            if filtro_campo and filtro_valor:
                query += f" AND {filtro_campo} ILIKE %s"
                params.append(f"%{filtro_valor}%")

            query += f" ORDER BY {orden_field} {order_dir}"
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

            productos = [Producto(*row) for row in rows]
            conn.close()
            return productos

        except Exception as e:
            print(f"[ProductoRepository.obtener] Error: {e}")
            return []

    def insertar(self, nombre, categoria, marca, precio_unitario):
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO productos (
                        nombre_producto, categoria, marca,
                        stock_actual, precio_unitario, estado
                    )
                    VALUES (%s, %s, %s, 0, %s, 'activo')
                    RETURNING id_producto
                    """,
                    (nombre, categoria, marca, precio_unitario),
                )
                nuevo_id = cur.fetchone()[0]

            conn.commit()
            conn.close()
            return nuevo_id

        except Exception as e:
            print(f"[ProductoRepository.insertar] Error: {e}")
            return None

    def actualizar(self, id_producto, nombre, categoria, marca, precio_unitario, estado):
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE productos
                    SET nombre_producto = %s,
                        categoria = %s,
                        marca = %s,
                        precio_unitario = %s,
                        estado = %s
                    WHERE id_producto = %s
                    """,
                    (nombre, categoria, marca, precio_unitario, estado, id_producto),
                )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"[ProductoRepository.actualizar] Error: {e}")
            return False

    def eliminar(self, id_producto):
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE productos
                    SET estado = 'inactivo'
                    WHERE id_producto = %s
                    """,
                    (id_producto,),
                )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"[ProductoRepository.eliminar] Error: {e}")
            return False
