# rutasnicaragua2

Backend en Flask para administrar rutas de transporte de Nicaragua.

## Uso

1. Copia `.env.example` a `.env` y completa tus datos de base de datos PostgreSQL.
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la aplicación:
   ```bash
   python app.py
   ```

Al iniciar la aplicación se crea un usuario `admin` con la contraseña
especificada en `ADMIN_PASSWORD`. Accede a
`http://localhost:5000/login` utilizando esas credenciales.

Para cargar datos GTFS de la carpeta `data/gtfs` a la base de datos ejecuta:
```bash
./load_gtfs.sh
```

Para importar rutas desde archivos JSON ubicados en `data/json_routes` puedes
utilizar el script `json_loader.py`:
```bash
python json_loader.py
```

El endpoint de prueba `/api/ping` responderá con `{"message": "API operativa"}`.

### Endpoints GTFS

Obtén información de rutas y paradas cargadas en la base de datos:

```bash
# Listar rutas opcionalmente filtrando por región
curl "http://localhost:5000/api/rutas?region=Managua"

# Paradas de una ruta
curl "http://localhost:5000/api/paradas?ruta=1"

# Horarios en una parada para una fecha concreta
curl "http://localhost:5000/api/horarios?ruta=1&parada=S1&fecha=2025-01-01"
```

## Migraciones de la base de datos

Para aplicar las migraciones de la base de datos ejecuta:

```bash
pip install -r requirements.txt
export DATABASE_URL="<tu-string-DB>"
alembic upgrade head
```
