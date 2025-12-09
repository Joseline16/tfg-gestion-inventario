# services/usuario_service.py

from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository


class UsuarioService:
    def __init__(self):
        self.repo = UsuarioRepository()

    # Login 
    def obtener_usuario_por_email(self, email):
        return self.repo.obtener_por_email(email)

    # Crear nuevo usuario
    def crear_usuario(self, nombre, email, rol, telefono, password, telegram=None):

        if not nombre:
            raise Exception("El nombre no puede estar vacío")

        if "@" not in email:
            raise Exception("El email no es válido")

        nuevo_usuario = Usuario(
            id_usuario=None,
            nombre_usuario=nombre,
            email=email,
            rol=rol,
            id_telegram=telegram,
            telefono=telefono,
            password=password,
            fecha_registro=None
        )

        resultado = self.repo.insertar(nuevo_usuario)

        if resultado == "email_duplicado":
            raise Exception("El email ya está registrado")

        return resultado

    # Listar usuarios
    def obtener_usuarios(self, offset, limit, filtro_campo, filtro_valor, orden):
        return self.repo.obtener(offset, limit, filtro_campo, filtro_valor, orden)

    # Actualizar usuario existente
    def actualizar_usuario(self, id_usuario, nombre, email, rol, telefono, password, telegram=None):

        usuario = Usuario(
            id_usuario=id_usuario,
            nombre_usuario=nombre,
            email=email,
            rol=rol,
            id_telegram=telegram,
            telefono=telefono,
            password=password,
            fecha_registro=None
        )

        return self.repo.actualizar(usuario)
