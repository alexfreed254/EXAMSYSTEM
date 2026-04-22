from flask import render_template, redirect, url_for, flash, request, g
from functools import wraps
from app.admin import admin
from app.models import (User, Department, Program, Course, Trainer, Trainee,
                         Enrollment, AcademicYear, Result, Transcript, Notification, SystemLog)
from app import db
from app.auth.routes import login_required
from datetime import datetime, date


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = g.get('current_user')
        if not user:
            return redirect(url_for('auth.login'))
        if user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_trainees':    Trainee.query.count(),
        'total_trainers':    Trainer.query.count(),
        'total_programs':    Program.query.count(),
        'total_courses':     Course.query.count(),
        'total_departments': Department.query.count(),
        'total_results':     Result.query.count(),
        'total_transcripts': Transcript.query.count(),
        'published_results': Result.query.filter_by(is_published=True).count(),
    }
    recent_logs        = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(10).all()
    recent_transcripts = Transcript.query.order_by(Transcript.generated_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_logs=recent_logs, recent_transcripts=recent_transcripts)


# ─── DEPARTMENTS ─────────────────────────────────────────────────────────────

@admin.route('/departments')
@login_required
@admin_required
def departments():
    return render_template('admin/departments.html',
                           departments=Department.query.order_by(Department.name).all())


@admin.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        if Department.query.filter_by(code=code).first():
            flash('Department code already exists.', 'danger')
        else:
            db.session.add(Department(
                name=request.form.get('name', '').strip(),
                code=code,
                description=request.form.get('description', '').strip(),
                head_of_department=request.form.get('head_of_department', '').strip(),
            ))
            db.session.commit()
            flash('Department added.', 'success')
            return redirect(url_for('admin.departments'))
    return render_template('admin/department_form.html', dept=None)


@admin.route('/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    if request.method == 'POST':
        dept.name               = request.form.get('name', '').strip()
        dept.code               = request.form.get('code', '').strip().upper()
        dept.description        = request.form.get('description', '').strip()
        dept.head_of_department = request.form.get('head_of_department', '').strip()
        db.session.commit()
        flash('Department updated.', 'success')
        return redirect(url_for('admin.departments'))
    return render_template('admin/department_form.html', dept=dept)


@admin.route('/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
@admin_required
def delete_department(dept_id):
    db.session.delete(Department.query.get_or_404(dept_id))
    db.session.commit()
    flash('Department deleted.', 'success')
    return redirect(url_for('admin.departments'))


# ─── PROGRAMS ────────────────────────────────────────────────────────────────

@admin.route('/programs')
@login_required
@admin_required
def programs():
    return render_template('admin/programs.html',
                           programs=Program.query.order_by(Program.name).all())


@admin.route('/programs/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_program():
    departments = Department.query.order_by(Department.name).all()
    if request.method == 'POST':
        db.session.add(Program(
            name=request.form.get('name', '').strip(),
            code=request.form.get('code', '').strip().upper(),
            department_id=int(request.form.get('department_id')),
            level=request.form.get('level', '').strip(),
            isced_code=request.form.get('isced_code', '').strip(),
            duration_years=int(request.form.get('duration_years', 3)),
            description=request.form.get('description', '').strip(),
            entry_requirements=request.form.get('entry_requirements', '').strip(),
        ))
        db.session.commit()
        flash('Program added.', 'success')
        return redirect(url_for('admin.programs'))
    return render_template('admin/program_form.html', prog=None, departments=departments)


@admin.route('/programs/edit/<int:prog_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_program(prog_id):
    prog = Program.query.get_or_404(prog_id)
    departments = Department.query.order_by(Department.name).all()
    if request.method == 'POST':
        prog.name               = request.form.get('name', '').strip()
        prog.code               = request.form.get('code', '').strip().upper()
        prog.department_id      = int(request.form.get('department_id'))
        prog.level              = request.form.get('level', '').strip()
        prog.isced_code         = request.form.get('isced_code', '').strip()
        prog.duration_years     = int(request.form.get('duration_years', 3))
        prog.description        = request.form.get('description', '').strip()
        prog.entry_requirements = request.form.get('entry_requirements', '').strip()
        db.session.commit()
        flash('Program updated.', 'success')
        return redirect(url_for('admin.programs'))
    return render_template('admin/program_form.html', prog=prog, departments=departments)


@admin.route('/programs/delete/<int:prog_id>', methods=['POST'])
@login_required
@admin_required
def delete_program(prog_id):
    db.session.delete(Program.query.get_or_404(prog_id))
    db.session.commit()
    flash('Program deleted.', 'success')
    return redirect(url_for('admin.programs'))


# ─── COURSES ─────────────────────────────────────────────────────────────────

@admin.route('/courses')
@login_required
@admin_required
def courses():
    program_id   = request.args.get('program_id', type=int)
    query        = Course.query
    if program_id:
        query = query.filter_by(program_id=program_id)
    return render_template('admin/courses.html',
                           courses=query.order_by(Course.module_number, Course.name).all(),
                           programs=Program.query.order_by(Program.name).all(),
                           selected_program=program_id)


@admin.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    programs = Program.query.order_by(Program.name).all()
    if request.method == 'POST':
        theory_w = float(request.form.get('theory_weight', 30))
        db.session.add(Course(
            name=request.form.get('name', '').strip(),
            code=request.form.get('code', '').strip().upper(),
            tvet_unit_code=request.form.get('tvet_unit_code', '').strip(),
            program_id=int(request.form.get('program_id')),
            module_number=int(request.form.get('module_number', 1)),
            unit_category=request.form.get('unit_category', 'CR'),
            credit_factor=float(request.form.get('credit_factor', 10)),
            duration_hours=int(request.form.get('duration_hours', 100)),
            theory_weight=theory_w,
            practical_weight=100 - theory_w,
            description=request.form.get('description', '').strip(),
        ))
        db.session.commit()
        flash('Course added.', 'success')
        return redirect(url_for('admin.courses'))
    return render_template('admin/course_form.html', course=None, programs=programs)


@admin.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course   = Course.query.get_or_404(course_id)
    programs = Program.query.order_by(Program.name).all()
    if request.method == 'POST':
        theory_w              = float(request.form.get('theory_weight', 30))
        course.name           = request.form.get('name', '').strip()
        course.code           = request.form.get('code', '').strip().upper()
        course.tvet_unit_code = request.form.get('tvet_unit_code', '').strip()
        course.program_id     = int(request.form.get('program_id'))
        course.module_number  = int(request.form.get('module_number', 1))
        course.unit_category  = request.form.get('unit_category', 'CR')
        course.credit_factor  = float(request.form.get('credit_factor', 10))
        course.duration_hours = int(request.form.get('duration_hours', 100))
        course.theory_weight  = theory_w
        course.practical_weight = 100 - theory_w
        course.description    = request.form.get('description', '').strip()
        db.session.commit()
        flash('Course updated.', 'success')
        return redirect(url_for('admin.courses'))
    return render_template('admin/course_form.html', course=course, programs=programs)


@admin.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    db.session.delete(Course.query.get_or_404(course_id))
    db.session.commit()
    flash('Course deleted.', 'success')
    return redirect(url_for('admin.courses'))


# ─── TRAINEES ────────────────────────────────────────────────────────────────

@admin.route('/trainees')
@login_required
@admin_required
def trainees():
    search = request.args.get('search', '')
    query  = Trainee.query.join(User)
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (Trainee.admission_number.ilike(f'%{search}%'))
        )
    return render_template('admin/trainees.html',
                           trainees=query.order_by(User.full_name).all(),
                           programs=Program.query.order_by(Program.name).all(),
                           search=search)


@admin.route('/trainees/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_trainee():
    programs = Program.query.order_by(Program.name).all()
    if request.method == 'POST':
        email     = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        password  = request.form.get('password', 'Ttti@2025')
        username  = request.form.get('username', '').strip()

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/trainee_form.html', trainee=None, programs=programs)

        try:
            # Create user in Supabase Auth
            from app.supabase_client import get_supabase_admin
            admin_client = get_supabase_admin()
            auth_response = admin_client.auth.admin.create_user({
                'email': email,
                'password': password,
                'email_confirm': True,
                'user_metadata': {'role': 'trainee', 'full_name': full_name}
            })
            supabase_uid = auth_response.user.id
        except Exception as e:
            flash(f'Error creating auth account: {str(e)}', 'danger')
            return render_template('admin/trainee_form.html', trainee=None, programs=programs)

        # Create profile in our DB
        user = User(supabase_uid=supabase_uid, username=username or email.split('@')[0],
                    email=email, full_name=full_name, role='trainee',
                    phone=request.form.get('phone', ''))
        db.session.add(user)
        db.session.flush()

        year         = datetime.utcnow().year
        count        = Trainee.query.count() + 1
        admission_no = f"TTTI/{year}/{count:04d}"
        dob_str      = request.form.get('date_of_birth', '')
        dob          = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

        trainee = Trainee(user_id=user.id, admission_number=admission_no,
                          national_id=request.form.get('national_id', '').strip(),
                          date_of_birth=dob, gender=request.form.get('gender', ''),
                          county=request.form.get('county', '').strip(),
                          address=request.form.get('address', '').strip(),
                          guardian_name=request.form.get('guardian_name', '').strip(),
                          guardian_phone=request.form.get('guardian_phone', '').strip())
        db.session.add(trainee)
        db.session.flush()

        program_id = request.form.get('program_id', type=int)
        if program_id:
            db.session.add(Enrollment(trainee_id=trainee.id, program_id=program_id,
                                      intake_year=datetime.utcnow().year,
                                      intake_month=request.form.get('intake_month', 'January')))
        db.session.commit()
        flash(f'Trainee "{full_name}" added. Admission: {admission_no}', 'success')
        return redirect(url_for('admin.trainees'))

    return render_template('admin/trainee_form.html', trainee=None, programs=programs)


@admin.route('/trainees/edit/<int:trainee_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trainee(trainee_id):
    trainee  = Trainee.query.get_or_404(trainee_id)
    programs = Program.query.order_by(Program.name).all()
    if request.method == 'POST':
        trainee.user.full_name    = request.form.get('full_name', '').strip()
        trainee.user.phone        = request.form.get('phone', '').strip()
        trainee.national_id       = request.form.get('national_id', '').strip()
        trainee.gender            = request.form.get('gender', '')
        trainee.county            = request.form.get('county', '').strip()
        trainee.address           = request.form.get('address', '').strip()
        trainee.guardian_name     = request.form.get('guardian_name', '').strip()
        trainee.guardian_phone    = request.form.get('guardian_phone', '').strip()
        dob_str = request.form.get('date_of_birth', '')
        if dob_str:
            trainee.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Trainee updated.', 'success')
        return redirect(url_for('admin.trainees'))
    return render_template('admin/trainee_form.html', trainee=trainee, programs=programs)


@admin.route('/trainees/view/<int:trainee_id>')
@login_required
@admin_required
def view_trainee(trainee_id):
    trainee     = Trainee.query.get_or_404(trainee_id)
    results     = Result.query.filter_by(trainee_id=trainee_id).all()
    transcripts = Transcript.query.filter_by(trainee_id=trainee_id).all()
    return render_template('admin/trainee_detail.html', trainee=trainee,
                           results=results, transcripts=transcripts)


# ─── TRAINERS ────────────────────────────────────────────────────────────────

@admin.route('/trainers')
@login_required
@admin_required
def trainers():
    return render_template('admin/trainers.html',
                           trainers=Trainer.query.join(User).order_by(User.full_name).all())


@admin.route('/trainers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_trainer():
    departments = Department.query.order_by(Department.name).all()
    if request.method == 'POST':
        email     = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        password  = request.form.get('password', 'Ttti@2025')
        username  = request.form.get('username', '').strip()

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/trainer_form.html', trainer=None, departments=departments)

        try:
            from app.supabase_client import get_supabase_admin
            admin_client = get_supabase_admin()
            auth_response = admin_client.auth.admin.create_user({
                'email': email,
                'password': password,
                'email_confirm': True,
                'user_metadata': {'role': 'trainer', 'full_name': full_name}
            })
            supabase_uid = auth_response.user.id
        except Exception as e:
            flash(f'Error creating auth account: {str(e)}', 'danger')
            return render_template('admin/trainer_form.html', trainer=None, departments=departments)

        user = User(supabase_uid=supabase_uid, username=username or email.split('@')[0],
                    email=email, full_name=full_name, role='trainer',
                    phone=request.form.get('phone', ''))
        db.session.add(user)
        db.session.flush()

        count  = Trainer.query.count() + 1
        emp_id = f"TTTI/TR/{count:04d}"
        db.session.add(Trainer(
            user_id=user.id,
            department_id=request.form.get('department_id', type=int),
            employee_id=emp_id,
            qualification=request.form.get('qualification', '').strip(),
            tveta_license=request.form.get('tveta_license', '').strip(),
            specialization=request.form.get('specialization', '').strip(),
        ))
        db.session.commit()
        flash(f'Trainer "{full_name}" added. ID: {emp_id}', 'success')
        return redirect(url_for('admin.trainers'))

    return render_template('admin/trainer_form.html', trainer=None, departments=departments)


@admin.route('/trainers/edit/<int:trainer_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trainer(trainer_id):
    trainer     = Trainer.query.get_or_404(trainer_id)
    departments = Department.query.order_by(Department.name).all()
    if request.method == 'POST':
        trainer.user.full_name  = request.form.get('full_name', '').strip()
        trainer.user.phone      = request.form.get('phone', '').strip()
        trainer.department_id   = request.form.get('department_id', type=int)
        trainer.qualification   = request.form.get('qualification', '').strip()
        trainer.tveta_license   = request.form.get('tveta_license', '').strip()
        trainer.specialization  = request.form.get('specialization', '').strip()
        db.session.commit()
        flash('Trainer updated.', 'success')
        return redirect(url_for('admin.trainers'))
    return render_template('admin/trainer_form.html', trainer=trainer, departments=departments)


# ─── ACADEMIC YEARS ──────────────────────────────────────────────────────────

@admin.route('/academic-years')
@login_required
@admin_required
def academic_years():
    return render_template('admin/academic_years.html',
                           years=AcademicYear.query.order_by(AcademicYear.name.desc()).all())


@admin.route('/academic-years/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_academic_year():
    if request.method == 'POST':
        is_current = request.form.get('is_current') == 'on'
        if is_current:
            AcademicYear.query.update({'is_current': False})
        start_str = request.form.get('start_date', '')
        end_str   = request.form.get('end_date', '')
        db.session.add(AcademicYear(
            name=request.form.get('name', '').strip(),
            is_current=is_current,
            start_date=datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else None,
            end_date=datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else None,
        ))
        db.session.commit()
        flash('Academic year added.', 'success')
        return redirect(url_for('admin.academic_years'))
    return render_template('admin/academic_year_form.html', year=None)


@admin.route('/academic-years/set-current/<int:year_id>', methods=['POST'])
@login_required
@admin_required
def set_current_year(year_id):
    AcademicYear.query.update({'is_current': False})
    year = AcademicYear.query.get_or_404(year_id)
    year.is_current = True
    db.session.commit()
    flash(f'"{year.name}" set as current.', 'success')
    return redirect(url_for('admin.academic_years'))


# ─── RESULTS ─────────────────────────────────────────────────────────────────

@admin.route('/results')
@login_required
@admin_required
def results():
    program_id = request.args.get('program_id', type=int)
    year_id    = request.args.get('year_id', type=int)
    query      = Result.query
    if program_id:
        query = query.join(Course).filter(Course.program_id == program_id)
    if year_id:
        query = query.filter(Result.academic_year_id == year_id)
    return render_template('admin/results.html',
                           results=query.order_by(Result.uploaded_at.desc()).limit(100).all(),
                           programs=Program.query.all(),
                           years=AcademicYear.query.order_by(AcademicYear.name.desc()).all(),
                           selected_program=program_id, selected_year=year_id)


@admin.route('/results/publish/<int:result_id>', methods=['POST'])
@login_required
@admin_required
def publish_result(result_id):
    result = Result.query.get_or_404(result_id)
    result.is_published = True
    db.session.add(Notification(user_id=result.trainee.user_id,
                                title='Results Published',
                                message=f'Your results for {result.course.name} are now available.'))
    db.session.commit()
    flash('Result published.', 'success')
    return redirect(url_for('admin.results'))


@admin.route('/results/publish-bulk', methods=['POST'])
@login_required
@admin_required
def publish_bulk():
    year_id    = request.form.get('year_id', type=int)
    program_id = request.form.get('program_id', type=int)
    query      = Result.query.filter_by(is_published=False)
    if year_id:
        query = query.filter_by(academic_year_id=year_id)
    if program_id:
        query = query.join(Course).filter(Course.program_id == program_id)
    count = query.count()
    query.update({'is_published': True}, synchronize_session='fetch')
    db.session.commit()
    flash(f'{count} results published.', 'success')
    return redirect(url_for('admin.results'))


# ─── TRANSCRIPTS ─────────────────────────────────────────────────────────────

@admin.route('/transcripts')
@login_required
@admin_required
def transcripts():
    return render_template('admin/transcripts.html',
                           transcripts=Transcript.query.order_by(Transcript.generated_at.desc()).all())


@admin.route('/transcripts/generate', methods=['GET', 'POST'])
@login_required
@admin_required
def generate_transcript():
    trainees = Trainee.query.join(User).order_by(User.full_name).all()
    programs = Program.query.order_by(Program.name).all()
    years    = AcademicYear.query.order_by(AcademicYear.name.desc()).all()

    if request.method == 'POST':
        trainee_id = request.form.get('trainee_id', type=int)
        program_id = request.form.get('program_id', type=int)
        year_id    = request.form.get('year_id', type=int)
        existing   = Transcript.query.filter_by(trainee_id=trainee_id,
                                                 program_id=program_id,
                                                 academic_year_id=year_id).first()
        if existing:
            flash(f'Transcript already exists: {existing.serial_number}', 'warning')
            return redirect(url_for('admin.transcripts'))

        serial = Transcript.generate_serial()
        db.session.add(Transcript(serial_number=serial, trainee_id=trainee_id,
                                   program_id=program_id, academic_year_id=year_id,
                                   generated_by=g.current_user.id, is_official=True))
        db.session.commit()
        flash(f'Transcript generated: {serial}', 'success')
        return redirect(url_for('admin.transcripts'))

    return render_template('admin/generate_transcript.html',
                           trainees=trainees, programs=programs, years=years)


# ─── USERS ───────────────────────────────────────────────────────────────────

@admin.route('/users')
@login_required
@admin_required
def users():
    return render_template('admin/users.html',
                           users=User.query.order_by(User.full_name).all())


@admin.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == g.current_user.id:
        flash('Cannot deactivate your own account.', 'danger')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f'User {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/users/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    try:
        from app.supabase_client import get_supabase_admin
        admin_client = get_supabase_admin()
        admin_client.auth.admin.update_user_by_id(
            user.supabase_uid, {'password': 'Ttti@2025'}
        )
        flash(f'Password reset to Ttti@2025 for {user.full_name}.', 'success')
    except Exception as e:
        flash(f'Error resetting password: {str(e)}', 'danger')
    return redirect(url_for('admin.users'))


# ─── LOGS / ENROLLMENTS ──────────────────────────────────────────────────────

@admin.route('/logs')
@login_required
@admin_required
def system_logs():
    return render_template('admin/logs.html',
                           logs=SystemLog.query.order_by(SystemLog.created_at.desc()).limit(200).all())


@admin.route('/enrollments')
@login_required
@admin_required
def enrollments():
    return render_template('admin/enrollments.html', enrollments=Enrollment.query.all())


@admin.route('/enrollments/add', methods=['POST'])
@login_required
@admin_required
def add_enrollment():
    trainee_id  = request.form.get('trainee_id', type=int)
    program_id  = request.form.get('program_id', type=int)
    intake_year = request.form.get('intake_year', type=int, default=datetime.utcnow().year)
    if not Enrollment.query.filter_by(trainee_id=trainee_id, program_id=program_id).first():
        db.session.add(Enrollment(trainee_id=trainee_id, program_id=program_id,
                                   intake_year=intake_year,
                                   intake_month=request.form.get('intake_month', 'January')))
        db.session.commit()
        flash('Enrollment added.', 'success')
    else:
        flash('Already enrolled.', 'warning')
    return redirect(url_for('admin.trainees'))
