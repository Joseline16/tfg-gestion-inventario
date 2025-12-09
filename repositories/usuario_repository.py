# repositories/usuario_repository.py

from database.connection import get_connection
from models.usuario import Usuario


class UsuarioRepository:

    #Login: obtener usuario por email
    def obtener_por_email(self, email):
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_usuario, nombre_usuario, email, password, rol
                FROM usuarios
                WHERE email = %s
                LIMIT 1;
            """, (email,))
            row = cur.fetchone()

        conn.close()

        if row:
            return {
                "id_usuario": row[0],
                "nombre_usuario": row[1],
                "email": row[2],
                "password": row[3],
                "rol": row[4],
            }
        return None

    #Lista de usuarios
    def obtener(self, offset, limit, filtro_campo, filtro_valor, orden):
        if filtro_campo not in ["nombre_usuario", "email", "rol", "telefono"]:
            filtro_campo = "nombre_usuario"

        conn = get_connection()
        with conn.cursor() as cur:

            query = """
                SELECT id_usuario, nombre_usuario, email, rol,
                       id_telegram, telefono, password, fecha_registro
                FROM usuarios
            """

            params = []

            if filtro_valor:
                query += f" WHERE {filtro_campo} ILIKE %s"
                params.append(f"%{filtro_valor}%")

            query += f" ORDER BY {filtro_campo} {orden}"
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cur.execute(query, params)
            rows = cur.fetchall()

        conn.close()
        return [Usuario(*row) for row in rows]

    #Validar si existe email
    def existe_email(self, email):
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM usuarios WHERE email = %s LIMIT 1;
            """, (email,))
            exists = cur.fetchone() is not None
        conn.close()
        return exists

    #Insertar nuevo usuario
    def insertar(self, usuario: Usuario):
        if self.existe_email(usuario.email):
            return "email_duplicado"

        conn = get_connection()
        try:
            with conn, conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO usuarios
                    (nombre_usuario, email, rol, id_telegram, telefono, password)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_usuario;
                """, (
                    usuario.nombre,
                    usuario.email,
                    usuario.rol,
                    usuario.telegram,
                    usuario.telefono,
                    usuario.password
                ))
                return cur.fetchone()[0]
        except Exception:
            conn.rollback()
            return None

    #Actualizar usuario existente   
    def actualizar(self, usuario: Usuario):
        conn = get_connection()
        try:
            with conn, conn.cursor() as cur:
                cur.execute("""
                    UPDATE usuarios
                    SET nombre_usuario = %s,
                        email = %s,
                        rol = %s,
                        id_telegram = %s,
                        telefono = %s,
                        password = %s
                    WHERE id_usuario = %s;
                """, (
                    usuario.nombre,
                    usuario.email,
                    usuario.rol,
                    usuario.telegram,
                    usuario.telefono,
                    usuario.password,
                    usuario.id
                ))
            return True
        except Exception:
            conn.rollback()
            return False
