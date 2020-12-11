# coding=utf-8

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_project import app, db
from flask_project.models import User, Movie


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


if __name__ == '__main__':
    pass

