from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = "m37aitask"
    from app.reception import reception
    from app.ui import ui
    from app.scheduler import schedule_bp
    
    app.register_blueprint(reception)
    app.register_blueprint(ui)
    app.register_blueprint(schedule_bp)
    return app
