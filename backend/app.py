"""
Flask application factory and configuration.
"""

from flask import Flask
from flask_cors import CORS
import os


def create_app(config: dict = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config: Override config dict
    
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['ENV'] = os.getenv('FLASK_ENV', 'development')
    app.config['DEBUG'] = app.config['ENV'] == 'development'
    app.config['JSON_SORT_KEYS'] = False
    
    if config:
        app.config.update(config)
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.workspaces import workspaces_bp
    from routes.tasks import tasks_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspaces_bp)
    app.register_blueprint(tasks_bp)
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "ok"}, 200
    
    @app.teardown_appcontext
    def teardown_db(exception=None):
        from flask import g
        db = g.pop('db', None)
        if db is not None:
            db.close()
            
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
