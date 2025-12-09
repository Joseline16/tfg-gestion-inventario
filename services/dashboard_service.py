# services/dashboard_service.py
from repositories.dashboard_repository import DashboardRepository
import pandas as pd
import datetime


class DashboardService:
    def __init__(self):
        self.repo = DashboardRepository()

    def obtener_resumen_mes(self):
        return self.repo.obtener_resumen_mes()

    def obtener_ventas_mes_actual(self) -> pd.DataFrame:
        df = self.repo.obtener_ventas_mes_actual()
        # Si está vacío devolvemos vacío
        if df.empty:
            # devolver rango completo del mes con ceros puede ser útil para gráficos
            hoy = datetime.date.today()
            start = datetime.date(hoy.year, hoy.month, 1)
            if hoy.month == 12:
                end = datetime.date(hoy.year, 12, 31)
            else:
                end = datetime.date(hoy.year, hoy.month + 1, 1) - datetime.timedelta(days=1)
            all_days = pd.DataFrame({"dia": pd.date_range(start=start, end=end).date})
            all_days["total_dia"] = 0.0
            return all_days

        # Construir rango completo del mes actual y hacer merge (rellenar con 0)
        hoy = datetime.date.today()
        start = datetime.date(hoy.year, hoy.month, 1)
        if hoy.month == 12:
            end = datetime.date(hoy.year, 12, 31)
        else:
            end = datetime.date(hoy.year, hoy.month + 1, 1) - datetime.timedelta(days=1)
        all_days = pd.DataFrame({"dia": pd.date_range(start=start, end=end).date})
        merged = all_days.merge(df, on="dia", how="left").fillna({"total_dia": 0})
        merged["total_dia"] = merged["total_dia"].astype(float)
        return merged

    def obtener_ranking_productos_vendidos(self, limit: int = 10):
        return self.repo.obtener_ranking_productos_vendidos(limit)

    def ultimas_ventas(self, limite: int = 10):
        return self.repo.ultimas_ventas(limite)

    def productos_bajo_stock(self):
        return self.repo.productos_bajo_stock()

    def ventas_por_categoria_mes(self):
        return self.repo.ventas_por_categoria_mes()
