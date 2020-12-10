import click
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


app = Flask(__name__)

encoding = 'utf-8'
# WIN = sys.platform.startswith('win')   # sqlite数据库
# if WIN:  # 如果是 Windows 系统，使用三个斜线
#     prefix = 'sqlite:///'
# else:  # 否则使用四个斜线
#     prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/flask_base'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 对模型修改的监控
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True  # 每次请求结束后都会自动提交数据库中的变动
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, pwd):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password, pwd)  # 返回布尔值


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


def admin(name, pwd):
    user = User.query.first()
    if user is None:
        pwd = user.set_password(pwd)  # 设置密码
        user = User(username=name, password=pwd, name='Grey Li')
        db.session.add(user)
    else:
        user.username = name
        user.set_password(pwd)
    db.session.commit()


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def init_db(drop):
    """初始化数据库"""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    forge()
    click.echo('初始化数据库')  # 输出提示信息


@app.cli.command()
def forge():
    db.create_all()
    name = 'Grey Li'
    movies = [
                {'title': 'My Neighbor Totoro', 'year': '1988'},
                {'title': 'Dead Poets Society', 'year': '1989'},
                {'title': 'A Perfect World', 'year': '1993'},
                {'title': 'Leon', 'year': '1994'},
                {'title': 'Mahjong', 'year': '1996'},
                {'title': 'Swallowtail Butterfly', 'year': '1996'},
                {'title': 'King of Comedy', 'year': '1999'},
                {'title': 'Devils on the Doorstep', 'year': '1999'},
                {'title': 'WALL-E', 'year': '2008'},
                {'title': 'The Pork of Music', 'year': '2012'},
                {'title': '大家好，我是旺哥', 'year': '2020'}
    ]
    name = User(name=name)
    db.session.add(name)
    for i in movies:
        movie = Movie(title=i['title'], year=i['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
        title1 = request.form.get('title')
        year1 = request.form.get('year')
        if not title1 or not year1 or len(year1) > 4 or len(title1) > 60:
            flash('输入有误')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        movie = Movie(title=title1, year=year1)
        db.session.add(movie)
        db.session.commit()
        flash('添加成功')
        return redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['POST', 'GET'])
@login_required  # 登录保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('输入有误')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('编辑成功')
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required  # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('已删除')
    return redirect(url_for('index'))  # 重定向回主页


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('用户名或密码不可为空')
            return redirect(url_for('login'))
        user = User.query.first()
        if user.username == username and user.validate_password(password):
            login_user(user)
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('慢走，不送')
    return redirect(url_for('index'))  # 重定向回首页


@app.route('/settings', methods=['GET', 'POST'])
@login_required  # 登录保护
def settings():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name or len(name) > 20:
            flash('输入有误')
            return redirect(url_for('settings'))
        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('修改用户名成功')
        return redirect(url_for('index'))
    return render_template('setting.html')


@app.context_processor  # 定义了自动引入的变量user，往后的页面都会自动带上user这个参数
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.cli.command()
def app_run():
    app.run()
    click.echo('运行ing')


if __name__ == '__main__':
    # init_db('drop')
    # admin('admin', '123456')
    app.run()
