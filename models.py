from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    short_name = db.Column(db.String(50))
    long_name = db.Column(db.String(255))
    type = db.Column(db.Integer)
    region = db.relationship('Region', backref=db.backref('routes', lazy=True))

class Stop(db.Model):
    __tablename__ = 'stops'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)

class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.String(32), primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    service_id = db.Column(db.String(32))
    headsign = db.Column(db.String(255))
    direction_id = db.Column(db.Integer)
    route = db.relationship('Route', backref=db.backref('trips', lazy=True))

class StopTime(db.Model):
    __tablename__ = 'stop_times'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(32), db.ForeignKey('trips.id'), nullable=False)
    arrival_time = db.Column(db.String(8))
    departure_time = db.Column(db.String(8))
    stop_id = db.Column(db.String(32), db.ForeignKey('stops.id'), nullable=False)
    stop_sequence = db.Column(db.Integer, nullable=False)
    trip = db.relationship('Trip', backref=db.backref('stop_times', lazy=True))
    stop = db.relationship('Stop', backref=db.backref('stop_times', lazy=True))
