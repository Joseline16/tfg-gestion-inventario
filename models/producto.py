# models/producto.py

class Producto:
    def __init__(
        self,
        id_producto,
        nombre_producto,
        categoria,
        marca,
        stock_actual,
        stock_minimo,
        precio_unitario,
        estado,
        fecha_creacion,
    ):
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.categoria = categoria
        self.marca = marca
        self.stock_actual = stock_actual
        self.stock_minimo = stock_minimo
        self.precio_unitario = precio_unitario
        self.estado = estado
        self.fecha_creacion = fecha_creacion

    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "nombre_producto": self.nombre_producto,
            "categoria": self.categoria,
            "marca": self.marca,
            "stock_actual": self.stock_actual,
            "stock_minimo": self.stock_minimo,
            "precio_unitario": self.precio_unitario,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion,
        }
