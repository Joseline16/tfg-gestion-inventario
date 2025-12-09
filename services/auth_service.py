#Logica del login, lo procesa, hace las comprobaciones
# services/auth_service.py

from repositories.usuario_repository import UsuarioRepository

class AuthService:
    def __init__(self, repo):
        self.repo = repo

    def login(self, email, password):
        usuario = self.repo.obtener_por_email(email)

        if not usuario:
            return None, "Usuario no encontrado"

        # Comparación SIN bcrypt (texto plano)
        if password != usuario["password"]:
            return None, "Contraseña incorrecta"

        return usuario, None

