import os
import datetime
import jwt
from functools import wraps
from flask import (
    Flask,
    jsonify,
    request,
    session,
    redirect,
    url_for,
    render_template,
    flash,
    send_file,
)
from dotenv import load_dotenv
from models import db, User, Region, Route, Stop, Trip, StopTime
import pandas as pd
import tempfile
import zipfile
import io


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'changeme')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'changeme')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.permanent_session_lifetime = datetime.timedelta(days=int(os.getenv('SESSION_DAYS', '7')))
    db.init_app(app)

    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            admin = User(username='admin')
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('login_page'))
            return view(*args, **kwargs)
        return wrapped

    @app.route('/api/ping')
    def ping():
        return jsonify({'message': 'API operativa'})

    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session.permanent = True
                session['logged_in'] = True
                session['username'] = user.username
                return redirect(url_for('list_routes'))
            flash('Credenciales incorrectas')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        return redirect(url_for('login_page'))

    @app.route('/')
    @login_required
    def list_routes():
        search = request.args.get('region')
        query = Route.query.join(Region)
        if search:
            query = query.filter(Region.name.ilike(f"%{search}%"))
        routes = query.all()
        return render_template('routes.html', routes=routes, search=search)

    @app.route('/routes/new', methods=['GET', 'POST'])
    @login_required
    def new_route():
        regions = Region.query.all()
        if request.method == 'POST':
            region_id = request.form.get('region_id')
            short_name = request.form.get('short_name')
            long_name = request.form.get('long_name')
            route = Route(region_id=region_id, short_name=short_name, long_name=long_name)
            db.session.add(route)
            db.session.commit()
            return redirect(url_for('list_routes'))
        return render_template('route_form.html', regions=regions, route=None)

    @app.route('/routes/<int:route_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_route(route_id):
        route = Route.query.get_or_404(route_id)
        regions = Region.query.all()
        if request.method == 'POST':
            route.region_id = request.form.get('region_id')
            route.short_name = request.form.get('short_name')
            route.long_name = request.form.get('long_name')
            db.session.commit()
            return redirect(url_for('list_routes'))
        return render_template('route_form.html', route=route, regions=regions)

    @app.route('/routes/<int:route_id>/delete', methods=['POST'])
    @login_required
    def delete_route(route_id):
        route = Route.query.get_or_404(route_id)
        db.session.delete(route)
        db.session.commit()
        return redirect(url_for('list_routes'))

    @app.route('/routes/<int:route_id>/stops')
    @login_required
    def view_stops(route_id):
        route = Route.query.get_or_404(route_id)
        stops = Stop.query.join(StopTime).join(Trip).filter(Trip.route_id == route_id).all()
        return render_template('stops.html', route=route, stops=stops)

    @app.route('/stops/<stop_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_stop(stop_id):
        stop = Stop.query.get_or_404(stop_id)
        if request.method == 'POST':
            stop.name = request.form.get('name')
            stop.lat = float(request.form.get('lat'))
            stop.lon = float(request.form.get('lon'))
            db.session.commit()
            return redirect(url_for('view_stops', route_id=request.form.get('route_id')))
        return render_template('stop_form.html', stop=stop)

    @app.route('/import', methods=['GET', 'POST'])
    @login_required
    def import_json():
        preview = None
        if request.method == 'POST':
            file = request.files.get('file')
            if file:
                data = json.load(file)
                preview = data
                # simplistic validation
                if isinstance(data, list):
                    for item in data:
                        route = Route(
                            region_id=1,
                            short_name=item.get('ruta'),
                            long_name=item.get('ruta'),
                        )
                        db.session.add(route)
                    db.session.commit()
                    flash('Datos importados')
                    return redirect(url_for('list_routes'))
        return render_template('import.html', preview=preview)

    @app.route('/export_gtfs')
    @login_required
    def export_gtfs():
        # Export simple routes and stops to GTFS format
        tmpdir = tempfile.mkdtemp()
        routes_df = pd.read_sql(Route.query.statement, db.session.bind)
        routes_df.rename(columns={'id': 'route_id', 'short_name': 'route_short_name', 'long_name': 'route_long_name', 'type': 'route_type'}, inplace=True)
        routes_df.to_csv(os.path.join(tmpdir, 'routes.txt'), index=False)

        stops_df = pd.read_sql(Stop.query.statement, db.session.bind)
        stops_df.rename(columns={'id': 'stop_id', 'name': 'stop_name', 'lat': 'stop_lat', 'lon': 'stop_lon'}, inplace=True)
        stops_df.to_csv(os.path.join(tmpdir, 'stops.txt'), index=False)

        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fname in ['routes.txt', 'stops.txt']:
                path = os.path.join(tmpdir, fname)
                if os.path.exists(path):
                    zf.write(path, arcname=fname)
        data.seek(0)
        return send_file(data, mimetype='application/zip', download_name='gtfs.zip', as_attachment=True)

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'username and password required'}), 400
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'username already exists'}), 400
        user = User(username=data['username'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'user created'})

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'username and password required'}), 400

        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            expiration_hours = int(os.getenv('TOKEN_EXPIRATION_HOURS', '12'))
            payload = {
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            response = jsonify({'token': token, 'username': user.username})
            response.set_cookie(
                'auth_token',
                token,
                httponly=True,
                max_age=expiration_hours * 3600,
                samesite='Lax',
            )
            return response

        return jsonify({'error': 'invalid credentials'}), 401

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
