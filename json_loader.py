import os
import json
from uuid import uuid4
from typing import Dict

from models import db, Region, Route, Stop, Trip, StopTime


def json_to_db(app, data_dir: str = "data/json_routes") -> Dict[str, Dict[str, int]]:
    """Carga archivos JSON con rutas hacia la base de datos.

    Por cada archivo se insertan regiones, rutas, paradas, viajes y horarios
    evitando duplicados. Retorna un diccionario con el conteo de registros
    insertados por archivo.
    """
    summary: Dict[str, Dict[str, int]] = {}
    with app.app_context():
        if not os.path.isdir(data_dir):
            raise FileNotFoundError(f"JSON directory '{data_dir}' not found")

        for fname in os.listdir(data_dir):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(data_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            counts = {"regions": 0, "routes": 0, "stops": 0, "trips": 0, "stop_times": 0}

            # Region
            region_name = data.get("region")
            region = None
            if region_name:
                region = Region.query.filter_by(name=region_name).first()
                if region is None:
                    region = Region(name=region_name)
                    db.session.add(region)
                    db.session.commit()
                    counts["regions"] += 1

            # Route
            route_name = data.get("ruta") or ""
            route = Route.query.filter_by(long_name=route_name).first()
            if route is None:
                route = Route(region_id=region.id if region else None,
                              short_name=route_name,
                              long_name=route_name)
                db.session.add(route)
                db.session.commit()
                counts["routes"] += 1

            # Stops
            stop_ids = []
            for stop_name in data.get("paradas", []):
                stop = Stop.query.filter_by(name=stop_name).first()
                if stop is None:
                    stop = Stop(id=uuid4().hex, name=stop_name, lat=0.0, lon=0.0)
                    db.session.add(stop)
                    db.session.commit()
                    counts["stops"] += 1
                stop_ids.append(stop.id)

            # Trips and StopTimes
            for idx, salida in enumerate(data.get("salidas", []), 1):
                trip_id = f"{route.id}_t{idx}"
                if Trip.query.filter_by(id=trip_id).first():
                    continue
                trip = Trip(id=trip_id, route_id=route.id)
                db.session.add(trip)
                db.session.commit()
                counts["trips"] += 1

                for seq, stop_id in enumerate(stop_ids, 1):
                    if StopTime.query.filter_by(trip_id=trip_id, stop_id=stop_id, stop_sequence=seq).first():
                        continue
                    time_val = salida.get("hora")
                    st = StopTime(trip_id=trip_id,
                                  arrival_time=time_val,
                                  departure_time=time_val,
                                  stop_id=stop_id,
                                  stop_sequence=seq)
                    db.session.add(st)
                    counts["stop_times"] += 1
                db.session.commit()

            summary[fname] = counts

        for file, counts in summary.items():
            print(f"{file}: {counts}")
    return summary


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    json_to_db(app)
