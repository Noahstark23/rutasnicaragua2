import os
from flask import Flask, jsonify, request
import datetime
import jwt
from dotenv import load_dotenv
from models import db, User


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'changeme')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/ping')
    def ping():
        return jsonify({'message': 'API operativa'})

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
