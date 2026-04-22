from flask import render_template, redirect, url_for, g
from app.main import main
from app.auth.routes import login_required


@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    user = g.get('current_user')
    if not user:
        return redirect(url_for('auth.login'))
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'trainer':
        return redirect(url_for('trainer.dashboard'))
    elif user.role == 'trainee':
        return redirect(url_for('trainee.dashboard'))
    return redirect(url_for('auth.login'))
