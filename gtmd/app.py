from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from gtmd import config


app = Flask("dataBaseFinalProject")

app.config.from_object(config)
db = SQLAlchemy(app)

app.config["SECRET_KEY"] = "12345678"


from gtmd.blueprints.auth import auth_bp
from gtmd.blueprints.shutdown import shutdown_bp

# from blueprints.main import main_bp
# from blueprints.merchant import merchant_bp
# from blueprints.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(shutdown_bp)
# app.register_blueprint(main_bp)
# app.register_blueprint(user_bp)
# app.register_blueprint(merchant_bp)

if __name__ == '__main__':
    app.run()
