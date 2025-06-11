import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from models import db


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/ping')
    def ping():
        return jsonify({'message': 'API operativa'})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
