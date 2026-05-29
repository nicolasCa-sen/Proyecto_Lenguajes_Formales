import os
import json

class Database:
    def __init__(self):
        self.local_db_path = "database.json"
        self.mongo_uri = os.environ.get("MONGO_URI") or os.environ.get("MONGODB_URI")
        self.use_mongo = False
        
        # Generar casos obligatorios por defecto de la especificación
        default_cases = [
            {
                "name": "1. Expresión Aritmética Mixta",
                "description": "Caso obligatorio: (3 + 4 * 2) / (1 - 5)^2",
                "code": "-- Expresión obligatoria\nlet resultado = (3 + 4 * 2) / (1 - 5)^2\nprint(resultado)"
            },
            {
                "name": "2. Factorial Recursivo",
                "description": "Caso obligatorio: Función factorial recursiva con llamada y print de resultado",
                "code": "-- Función factorial recursiva\ndef factorial(n) {\n  if n <= 1 {\n    return 1\n  }\n  return n * factorial(n - 1)\n}\n\nlet res = factorial(5)\nprint(\"El factorial de 5 es:\")\nprint(res)"
            },
            {
                "name": "3. Acumulador con Bucle While",
                "description": "Caso obligatorio: Bucle while que acumula la suma de 1 a n",
                "code": "-- Suma acumulativa de 1 a n\nlet n = 10\nlet i = 1\nlet suma = 0\nwhile i <= n {\n  let suma = suma + i\n  let i = i + 1\n}\nprint(\"Suma acumulada de 1 a 10:\")\nprint(suma)"
            },
            {
                "name": "4. Funciones Trigonométricas",
                "description": "Caso obligatorio: Uso de sin, cos y sqrt dentro de expresiones compuestas",
                "code": "-- Pruebas de funciones matemáticas trigonométricas\nlet angulo = 0.785398 -- Aprox pi/4 (45 grados)\nlet s = sin(angulo)\nlet c = cos(angulo)\nlet raiz = sqrt(2.0)\n\nprint(\"Seno de pi/4:\")\nprint(s)\nprint(\"Coseno de pi/4:\")\nprint(c)\nprint(\"Raiz cuadrada de 2:\")\nprint(raiz)"
            },
            {
                "name": "5. Funciones Anidadas",
                "description": "Caso obligatorio: Una función que llama a otra función definida en el mismo programa",
                "code": "-- Funciones anidadas en MathLite\ndef duplicar(x) {\n  return x * 2\n}\n\ndef operar(y) {\n  let d = duplicar(y)\n  return d + 5\n}\n\nlet res = operar(10)\nprint(\"Resultado de operar(10) -> (10 * 2) + 5:\")\nprint(res)"
            }
        ]
        
        if self.mongo_uri and "<db_password>" not in self.mongo_uri:
            try:
                from pymongo import MongoClient
                self.client = MongoClient(self.mongo_uri)
                self.db = self.client["mathlite_db"]
                self.collection = self.db["test_cases"]
                
                # Forzar verificación de conexión inmediata (ej: login e IP permitida)
                self.client.server_info()
                
                self.use_mongo = True
                print(">>> Conectado exitosamente a MongoDB Atlas.")
                
                # Sembrado automático en la nube si está vacía
                if self.collection.count_documents({}) == 0:
                    self.collection.insert_many([c.copy() for c in default_cases])
                    print(">>> Sembrado automático exitoso en MongoDB Atlas.")
            except Exception as e:
                self.use_mongo = False
                print(f">>> Error al conectar a MongoDB Atlas: {e}. Usando fallback local JSON.")
        
        if not self.use_mongo:
            if not os.path.exists(self.local_db_path):
                with open(self.local_db_path, "w", encoding="utf-8") as f:
                    json.dump(default_cases, f, indent=4, ensure_ascii=False)
            print(">>> Usando base de datos NoSQL local (JSON).")

    def get_all(self):
        if self.use_mongo:
            try:
                cases = list(self.collection.find({}, {"_id": 0}))
                return cases
            except Exception as e:
                print(f"Error MongoDB get_all: {e}")
        
        try:
            with open(self.local_db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error local db get_all: {e}")
            return []

    def save(self, case):
        if self.use_mongo:
            try:
                self.collection.insert_one(case.copy())
                return True
            except Exception as e:
                print(f"Error MongoDB save: {e}")
        
        try:
            cases = self.get_all()
            # Evitar duplicados por nombre
            cases = [c for c in cases if c.get("name") != case.get("name")]
            cases.append(case)
            with open(self.local_db_path, "w", encoding="utf-8") as f:
                json.dump(cases, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error local db save: {e}")
            return False
