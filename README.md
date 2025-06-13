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
