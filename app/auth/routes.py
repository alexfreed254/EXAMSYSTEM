from flask import render_template, redirect, url_for, flash, request, session, g
from app.auth import auth
from app.models import User, SystemLog
from app import db
from app.supabase_client import get_supabase
from functools import wraps


# ── Auth decorators ───────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.get('current_user'):
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = g.get('current_user')
            if not user:
                flash('Please log in.', 'warning')
                return redirect(url_for('auth.login'))
            if user.role not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── Routes ────────────────────────────────────────────────────────────────────

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if g.get('current_user'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        try:
            supabase = get_supabase()
            # Sign in with Supabase Auth
            response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password,
            })

            if response.user:
                supabase_uid = response.user.id

                # Look up profile in our users table
                user = User.query.filter_by(supabase_uid=supabase_uid).first()

                if not user:
                    flash('Account not found in system. Contact administrator.', 'danger')
                    return render_template('auth/login.html')

                if not user.is_active:
                    flash('Your account has been deactivated. Contact administrator.', 'danger')
                    return render_template('auth/login.html')

                # Store in Flask session
                session.permanent = bool(request.form.get('remember'))
                session['user_id']       = user.id
                session['supabase_uid']  = supabase_uid
                session['access_token']  = response.session.access_token
                session['refresh_token'] = response.session.refresh_token
                session['role']          = user.role

                # Log
                log = SystemLog(user_id=user.id, action='LOGIN',
                                details=f'{user.username} signed in via Supabase Auth',
                                ip_address=request.remote_addr)
                db.session.add(log)
                db.session.commit()

                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.dashboard'))
            else:
                flash('Invalid email or password.', 'danger')

        except Exception as e:
            err = str(e).lower()
            if 'invalid' in err or 'credentials' in err or 'password' in err:
                flash('Invalid email or password.', 'danger')
            elif 'email not confirmed' in err:
                flash('Please confirm your email address first.', 'warning')
            else:
                flash(f'Login error: {str(e)}', 'danger')

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    user = g.get('current_user')
    if user:
        try:
            supabase = get_supabase()
            token = session.get('access_token')
            if token:
                supabase.auth.sign_out()
        except Exception:
            pass

        log = SystemLog(user_id=user.id, action='LOGOUT',
                        details=f'{user.username} signed out',
                        ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()

    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_pw     = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if new_pw != confirm_pw:
            flash('Passwords do not match.', 'danger')
        elif len(new_pw) < 8:
            flash('Password must be at least 8 characters.', 'danger')
        else:
            try:
                supabase = get_supabase()
                # Set the session token so Supabase knows who is changing password
                supabase.auth.set_session(
                    session.get('access_token', ''),
                    session.get('refresh_token', '')
                )
                supabase.auth.update_user({'password': new_pw})
                flash('Password changed successfully.', 'success')
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                flash(f'Error changing password: {str(e)}', 'danger')

    return render_template('auth/change_password.html')


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        try:
            supabase = get_supabase()
            supabase.auth.reset_password_email(email)
            flash('Password reset email sent. Check your inbox.', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('auth/forgot_password.html')
