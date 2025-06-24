from flask import Blueprint, jsonify, request
from sqlalchemy import func
from datetime import datetime

from models import db, Region, Route, Stop, Trip, StopTime, Calendar, CalendarDate

bp = Blueprint('gtfs_routes', __name__)

@bp.route('/api/rutas')
def rutas():
    region = request.args.get('region')
    query = Route.query
    if region:
        query = query.join(Region).filter(Region.name.ilike(f"%{region}%"))
    routes = query.all()
    return jsonify([
        {
            'route_id': r.id,
            'route_short_name': r.short_name,
            'route_long_name': r.long_name,
            'route_type': r.type,
        }
        for r in routes
    ])

@bp.route('/api/paradas')
def paradas():
    route_id = request.args.get('ruta')
    if not route_id:
        return jsonify([]), 400
    stops = (
        db.session.query(
            Stop.id.label('stop_id'),
            Stop.name.label('stop_name'),
            Stop.lat.label('stop_lat'),
            Stop.lon.label('stop_lon'),
            StopTime.stop_sequence.label('sequence'),
        )
        .join(StopTime)
        .join(Trip)
        .filter(Trip.route_id == route_id)
        .order_by(StopTime.stop_sequence)
        .all()
    )
    return jsonify([s._asdict() for s in stops])

@bp.route('/api/horarios')
def horarios():
    route_id = request.args.get('ruta')
    stop_id = request.args.get('parada')
    fecha = request.args.get('fecha')
    if not all([route_id, stop_id, fecha]):
        return jsonify([]), 400
    try:
        target_date = datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'fecha inválida'}), 400

    weekday = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][target_date.weekday()]
    base_services = db.session.query(Calendar.service_id).filter(
        Calendar.start_date <= target_date,
        Calendar.end_date >= target_date,
        getattr(Calendar, weekday) == True
    )
    added_services = db.session.query(CalendarDate.service_id).filter(
        CalendarDate.date == target_date,
        CalendarDate.exception_type == 1
    )
    removed_services = db.session.query(CalendarDate.service_id).filter(
        CalendarDate.date == target_date,
        CalendarDate.exception_type == 2
    )
    services = {s.service_id for s in base_services.union(added_services)}
    services -= {s.service_id for s in removed_services}
    if not services:
        return jsonify([])

    times = (
        db.session.query(StopTime.arrival_time, StopTime.departure_time)
        .join(Trip)
        .filter(
            Trip.route_id == route_id,
            Trip.service_id.in_(services),
            StopTime.stop_id == stop_id,
        )
        .order_by(StopTime.arrival_time)
        .limit(10)
        .all()
    )
    return jsonify([{'arrival_time': t.arrival_time, 'departure_time': t.departure_time} for t in times])
