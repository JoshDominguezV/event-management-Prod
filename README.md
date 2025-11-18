# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Instalar dependencias actualizadas
pip install -r requirements.txt

# 3. Inicializar la base de datos
python init_database.py

# 4. Ejecutar la aplicación
uvicorn app.main:app --reload --host localhost --port 8000
