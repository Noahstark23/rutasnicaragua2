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

Abre `http://localhost:5000/login` y utiliza la contraseña definida en
`ADMIN_PASSWORD` para acceder al panel de administración.

Para cargar datos GTFS de la carpeta `data/gtfs` a la base de datos ejecuta:
```bash
./load_gtfs.sh
```

El endpoint de prueba `/api/ping` responderá con `{"message": "API operativa"}`.
