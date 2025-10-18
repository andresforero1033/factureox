import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") or input("MONGO_URI (mongodb+srv://...): ")
DB_NAME = os.getenv("FACTUREO_DB_NAME", "factureo")

client = MongoClient(MONGO_URI)
db = client.get_database(DB_NAME)

print(f"Usando base de datos: {db.name}")

# Crear colecciones e índices recomendados
users = db["users"]
users.create_index("email", unique=True)

productos = db["productos"]
productos.create_index([("nombre", 1)])
productos.create_index([("categoria", 1)])

clientes = db["clientes"]
clientes.create_index([("correo", 1)], unique=False)

ventas = db["ventas"]
ventas.create_index([("fecha", -1)])
ventas.create_index([("cliente_id", 1)])

print("Colecciones e índices preparados.")
