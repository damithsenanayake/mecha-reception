from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.reception import reception
    from app.ui import ui
    app.register_blueprint(reception)
    app.register_blueprint(ui)
    return app
