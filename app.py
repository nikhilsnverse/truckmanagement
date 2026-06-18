from flask import Flask, redirect, session
from datetime import date, datetime
from config import Config
from database import db
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.trucks import trucks_bp
    from routes.trips import trips_bp
    from routes.expenses import expenses_bp
    from routes.reports import reports_bp
    from routes.api import api_bp
    from routes.owner import owner_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(trucks_bp, url_prefix='/trucks')
    app.register_blueprint(trips_bp, url_prefix='/trips')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(owner_bp, url_prefix='/owner')

    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.utcnow(),
            'today': date.today()
        }

    @app.route('/')
    def index():
        return redirect('/dashboard')

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    admin = User.query.filter_by(role='owner').first()
    if not admin:
        admin = User(
            name='Super Admin',
            email='admin@fleet.com',
            role='owner',
            phone='+1234567890'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Default admin created: admin@fleet.com / admin123')


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000)
