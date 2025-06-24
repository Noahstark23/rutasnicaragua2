import os
import csv
import pandas as pd
import datetime as dt
from models import (
    db,
    Route,
    Stop,
    Trip,
    StopTime,
    Agency,
    Calendar,
    CalendarDate,
)


def row_to_route(row):
    return Route(
        id=row["route_id"],
        region_id=1,
        short_name=row.get("route_short_name"),
        long_name=row.get("route_long_name"),
        type=row.get("route_type"),
    )


def row_to_stop(row):
    return Stop(
        id=row["stop_id"],
        name=row["stop_name"],
        lat=row["stop_lat"],
        lon=row["stop_lon"],
    )


def row_to_trip(row):
    return Trip(
        id=row["trip_id"],
        route_id=row["route_id"],
        service_id=row.get("service_id"),
        headsign=row.get("trip_headsign"),
        direction_id=row.get("direction_id"),
    )


def row_to_stop_time(row):
    return StopTime(
        trip_id=row["trip_id"],
        arrival_time=row.get("arrival_time"),
        departure_time=row.get("departure_time"),
        stop_id=row["stop_id"],
        stop_sequence=row["stop_sequence"],
    )


def load_agency(session, path_agency_txt):
    objs = []
    if os.path.exists(path_agency_txt):
        with open(path_agency_txt, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                objs.append(
                    Agency(
                        agency_id=row.get("agency_id"),
                        agency_name=row["agency_name"],
                        agency_url=row["agency_url"],
                        agency_timezone=row["agency_timezone"],
                        agency_lang=row.get("agency_lang"),
                        agency_phone=row.get("agency_phone"),
                    )
                )
    if objs:
        session.bulk_save_objects(objs)


def load_calendar(session, path_calendar_txt):
    objs = []
    if os.path.exists(path_calendar_txt):
        with open(path_calendar_txt, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                objs.append(
                    Calendar(
                        service_id=row["service_id"],
                        monday=bool(int(row["monday"])),
                        tuesday=bool(int(row["tuesday"])),
                        wednesday=bool(int(row["wednesday"])),
                        thursday=bool(int(row["thursday"])),
                        friday=bool(int(row["friday"])),
                        saturday=bool(int(row["saturday"])),
                        sunday=bool(int(row["sunday"])),
                        start_date=dt.datetime.strptime(row["start_date"], "%Y%m%d").date(),
                        end_date=dt.datetime.strptime(row["end_date"], "%Y%m%d").date(),
                    )
                )
    if objs:
        session.bulk_save_objects(objs)


def load_calendar_dates(session, path_calendar_dates_txt):
    objs = []
    if os.path.exists(path_calendar_dates_txt):
        with open(path_calendar_dates_txt, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                objs.append(
                    CalendarDate(
                        service_id=row["service_id"],
                        date=dt.datetime.strptime(row["date"], "%Y%m%d").date(),
                        exception_type=int(row["exception_type"]),
                    )
                )
    if objs:
        session.bulk_save_objects(objs)


def load_gtfs(session, folder_path):
    load_agency(session, f"{folder_path}/agency.txt")
    load_calendar(session, f"{folder_path}/calendar.txt")
    load_calendar_dates(session, f"{folder_path}/calendar_dates.txt")
    session.commit()


def load_gtfs_data(app, data_dir="data/gtfs"):
    """Carga archivos GTFS desde el directorio especificado a la base de datos."""
    with app.app_context():
        if not os.path.isdir(data_dir):
            raise FileNotFoundError(f"GTFS directory '{data_dir}' not found")

        counts = {}

        # Stops
        file_path = os.path.join(data_dir, "stops.txt")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            existing = {s.id for s in Stop.query.with_entities(Stop.id).all()}
            count = 0
            for _, row in df.iterrows():
                if row["stop_id"] in existing:
                    continue
                db.session.add(row_to_stop(row))
                existing.add(row["stop_id"])
                count += 1
            db.session.commit()
            counts["stops"] = count

        # Routes
        file_path = os.path.join(data_dir, "routes.txt")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            existing = {r.id for r in Route.query.with_entities(Route.id).all()}
            count = 0
            for _, row in df.iterrows():
                if row["route_id"] in existing:
                    continue
                db.session.add(row_to_route(row))
                existing.add(row["route_id"])
                count += 1
            db.session.commit()
            counts["routes"] = count

        # Trips
        file_path = os.path.join(data_dir, "trips.txt")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            existing = {t.id for t in Trip.query.with_entities(Trip.id).all()}
            count = 0
            for _, row in df.iterrows():
                if row["trip_id"] in existing:
                    continue
                db.session.add(row_to_trip(row))
                existing.add(row["trip_id"])
                count += 1
            db.session.commit()
            counts["trips"] = count

        # Stop Times
        file_path = os.path.join(data_dir, "stop_times.txt")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            existing = {
                (st.trip_id, st.stop_id, st.stop_sequence)
                for st in db.session.query(
                    StopTime.trip_id, StopTime.stop_id, StopTime.stop_sequence
                ).all()
            }
            count = 0
            for _, row in df.iterrows():
                key = (row["trip_id"], row["stop_id"], row["stop_sequence"])
                if key in existing:
                    continue
                db.session.add(row_to_stop_time(row))
                existing.add(key)
                count += 1
            db.session.commit()
            counts["stop_times"] = count

        for k, v in counts.items():
            print(f"Imported {v} {k}")
        return counts


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    load_gtfs_data(app)
