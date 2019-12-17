from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from gtmd import config


app = Flask("dataBaseFinalProject")

app.config.from_object(config)
db = SQLAlchemy(app)

app.config["SECRET_KEY"] = "12345678"

# 因为变量db对应的对象SQLAlchemy在前面创建且下列Blueprints都要导入变量db，所以这些Blueprint对象要在SQlAlchemy创建之后再导入
from gtmd.blueprints.auth import auth_bp
from gtmd.blueprints.shutdown import shutdown_bp
from gtmd.blueprints.seller import seller_bp
from gtmd.blueprints.buyer import buyer_bp

# from blueprints.main import main_bp
# from blueprints.merchant import merchant_bp

# 注册blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(shutdown_bp)
app.register_blueprint(buyer_bp)
# app.register_blueprint(user_bp)
app.register_blueprint(seller_bp)

if __name__ == '__main__':
    app.run()
