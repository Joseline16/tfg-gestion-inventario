# database/connection.py

import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Ruta absoluta al .env (2 niveles arriba)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

print("Cargando .env desde:", ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH)

def get_connection():
    try:
        print("\n========== VARIABLES .ENV ==========")
        print("HOST:", os.getenv("PGHOST"))
        print("DB:", os.getenv("PGDATABASE"))
        print("USER:", os.getenv("PGUSER"))
        print("PORT:", os.getenv("PGPORT"))
        print("====================================\n")

        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            dbname=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            port=os.getenv("PGPORT")
        )
        return conn

    except Exception as e:
        print("❌ ERROR AL CONECTAR A LA BD:", e)
        return None
