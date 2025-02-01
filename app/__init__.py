from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.reception import reception
    app.register_blueprint(reception)

    return app
