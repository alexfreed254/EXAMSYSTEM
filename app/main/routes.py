from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.main import main


@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'trainer':
        return redirect(url_for('trainer.dashboard'))
    elif current_user.role == 'trainee':
        return redirect(url_for('trainee.dashboard'))
    return redirect(url_for('auth.login'))
