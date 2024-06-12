# word_test/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_complex_and_secret_key'
app.config['TEMPLATES_DIR'] = 'templates'  # 设置模板文件夹路径
# 配置数据库URI，这里使用SQLite数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///word_test.db'
# 配置SQLAlchemy以追踪模型的修改
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
# 配置 Flask-Login
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面。'

# 导入模型和路由
from word_test import models, routes

# 在应用程序上下文中创建所有表
with app.app_context():
    db.create_all()
