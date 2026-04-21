from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth
from app.models import User, SystemLog
from app import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=bool(remember))
            # Log the action
            log = SystemLog(user_id=user.id, action='LOGIN',
                            details=f'User {user.username} logged in',
                            ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials or account disabled.', 'danger')

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    log = SystemLog(user_id=current_user.id, action='LOGOUT',
                    details=f'User {current_user.username} logged out',
                    ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')

        if not current_user.check_password(current_pw):
            flash('Current password is incorrect.', 'danger')
        elif new_pw != confirm_pw:
            flash('New passwords do not match.', 'danger')
        elif len(new_pw) < 8:
            flash('Password must be at least 8 characters.', 'danger')
        else:
            current_user.set_password(new_pw)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('main.dashboard'))

    return render_template('auth/change_password.html')
