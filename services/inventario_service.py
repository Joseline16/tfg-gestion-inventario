from repositories.inventario_repository import InventarioRepository


class InventarioService:

    def __init__(self, repo=None):
        self.repo = repo or InventarioRepository()
