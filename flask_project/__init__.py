# coding=utf-8


from importlib import reload
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# WIN = sys.platform.startswith('win')   # sqlite数据库
# if WIN:  # 如果是 Windows 系统，使用三个斜线
#     prefix = 'sqlite:///'
# else:  # 否则使用四个斜线
#     prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234567@localhost:3306/flask_base'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 对模型修改的监控
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True  # 每次请求结束后都会自动提交数据库中的变动
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from flask_project.models import User
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.context_processor  # 定义了自动引入的变量user，往后的页面都会自动带上user这个参数
def inject_user():
    from flask_project.models import User
    user = User.query.first()
    return dict(user=user)


from flask_project import views, errors, command


