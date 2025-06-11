import os
import pandas as pd
from models import db, Route, Stop, Trip, StopTime


def load_gtfs_data(app, data_dir="/data/gtfs"):
    """Carga archivos GTFS desde el directorio especificado a la base de datos."""
    with app.app_context():
        if not os.path.isdir(data_dir):
            raise FileNotFoundError(f"GTFS directory '{data_dir}' not found")

        # Stops
        stops_file = os.path.join(data_dir, "stops.txt")
        if os.path.exists(stops_file):
            stops = pd.read_csv(stops_file)
            for _, row in stops.iterrows():
                stop = Stop(id=row["stop_id"], name=row["stop_name"],
                            lat=row["stop_lat"], lon=row["stop_lon"])
                db.session.merge(stop)
            db.session.commit()

        # Routes
        routes_file = os.path.join(data_dir, "routes.txt")
        if os.path.exists(routes_file):
            routes = pd.read_csv(routes_file)
            for _, row in routes.iterrows():
                route = Route(id=row["route_id"],
                              region_id=1,
                              short_name=row.get("route_short_name"),
                              long_name=row.get("route_long_name"),
                              type=row.get("route_type"))
                db.session.merge(route)
            db.session.commit()

        # Trips
        trips_file = os.path.join(data_dir, "trips.txt")
        if os.path.exists(trips_file):
            trips = pd.read_csv(trips_file)
            for _, row in trips.iterrows():
                trip = Trip(id=row["trip_id"],
                            route_id=row["route_id"],
                            service_id=row.get("service_id"),
                            headsign=row.get("trip_headsign"),
                            direction_id=row.get("direction_id"))
                db.session.merge(trip)
            db.session.commit()

        # Stop times
        stop_times_file = os.path.join(data_dir, "stop_times.txt")
        if os.path.exists(stop_times_file):
            stop_times = pd.read_csv(stop_times_file)
            for _, row in stop_times.iterrows():
                st = StopTime(trip_id=row["trip_id"],
                              arrival_time=row.get("arrival_time"),
                              departure_time=row.get("departure_time"),
                              stop_id=row["stop_id"],
                              stop_sequence=row["stop_sequence"])
                db.session.add(st)
            db.session.commit()
