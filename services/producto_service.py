# services/producto_service.py
from repositories.producto_repository import ProductoRepository


class ProductoService:
    def __init__(self):
        self.repo = ProductoRepository()

    def listar(self, offset=0, limit=10, filtro_campo=None, filtro_valor=None, orden_field="id_producto", asc=True):
        return self.repo.obtener(offset, limit, filtro_campo, filtro_valor, orden_field, asc)

    def crear(self, nombre, categoria, marca, precio_unitario):
        return self.repo.insertar(nombre, categoria, marca, precio_unitario)

    def actualizar(self, id_producto, nombre, categoria, marca, precio_unitario, estado):
        id_producto = int(id_producto)
        precio_unitario = float(precio_unitario)
        return self.repo.actualizar(id_producto, nombre, categoria, marca, precio_unitario, estado)

    def eliminar(self, id_producto):
        return self.repo.eliminar(id_producto)
