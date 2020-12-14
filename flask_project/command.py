# coding=utf-8

from flask_project import app, db
from flask_project.models import User, Movie
import click


@app.cli.command()
@click.option('--m', required=True, nargs=2)
def admin(m):
    m = list(m)
    name = m[0]
    pwd = m[1]
    user = User.query.first()
    if user is None:
        pwd = User().set_password(password=pwd)  # 设置密码
        user = User(username=name, password=pwd, name='Grey Li')
        db.session.add(user)
    else:
        user.username = name
        user.set_password(pwd)
    db.session.commit()


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """初始化数据库"""
    if drop:  # 判断是否输入了选项
        db.drop_all()
        db.create_all()
        click.echo('drop database & init database')
    else:
        db.create_all()
        click.echo('初始化数据库')  # 输出提示信息


@app.cli.command()
def forge():
    db.create_all()
    # name = 'Grey Li'
    movies = [
                {'title': 'My Neighbor Totoro', 'year': '1988', 'user_id': 1},
                {'title': 'Dead Poets Society', 'year': '1989', 'user_id': 1},
                {'title': 'A Perfect World', 'year': '1993', 'user_id': 1},
                {'title': 'Leon', 'year': '1994', 'user_id': 1},
                {'title': 'Mahjong', 'year': '1996', 'user_id': 1},
                {'title': 'Swallowtail Butterfly', 'year': '1996', 'user_id': 1},
                {'title': 'King of Comedy', 'year': '1999', 'user_id': 1},
                {'title': 'Devils on the Doorstep', 'year': '1999', 'user_id': 1},
                {'title': 'WALL-E', 'year': '2008', 'user_id': 1},
                {'title': 'The Pork of Music', 'year': '2012', 'user_id': 1},
                {'title': '大家好，我是旺哥', 'year': '2020', 'user_id': 1}
    ]
    for i in movies:
        movie = Movie(title=i['title'], year=i['year'], user_id=i['user_id'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done')




