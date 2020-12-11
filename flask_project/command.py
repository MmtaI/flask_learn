# coding=utf-8

from flask_project import app, db
from models import User, Movie
import click


@app.cli.command()
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


