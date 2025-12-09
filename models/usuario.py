# models/usuario.py

class Usuario:
   
    def __init__(self, id_usuario, nombre_usuario, email, rol,
                 id_telegram, telefono, password, fecha_registro):
        self.id = id_usuario
        self.nombre = nombre_usuario
        self.email = email
        self.rol = rol
        self.telegram = id_telegram
        self.telefono = telefono
        self.password = password
        self.fecha_registro = fecha_registro

    def to_dict(self):
        return {
            "id_usuario": self.id,
            "nombre_usuario": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "id_telegram": self.telegram,
            "telefono": self.telefono,
            "password": self.password,
            "fecha_registro": self.fecha_registro
        }
