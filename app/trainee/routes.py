from flask import render_template, redirect, url_for, flash, request, send_file, abort, g
from functools import wraps
from app.trainee import trainee
from app.models import Trainee, Result, Transcript, Enrollment, AcademicYear, Course, Program
from app import db
from app.auth.routes import login_required
from app.utils.pdf_generator import generate_transcript_pdf
from datetime import datetime


def trainee_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = g.get('current_user')
        if not user:
            return redirect(url_for('auth.login'))
        if user.role != 'trainee':
            flash('Trainee access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


def get_trainee():
    return Trainee.query.filter_by(user_id=g.current_user.id).first()


@trainee.route('/dashboard')
@login_required
@trainee_required
def dashboard():
    t = get_trainee()
    if not t:
        flash('Trainee profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    enrollments = Enrollment.query.filter_by(trainee_id=t.id).all()
    published_results = Result.query.filter_by(trainee_id=t.id, is_published=True).all()
    transcripts = Transcript.query.filter_by(trainee_id=t.id).all()

    # Compute stats
    competent_count = sum(1 for r in published_results if r.competency_status == 'Competent')
    stats = {
        'total_results': len(published_results),
        'competent': competent_count,
        'not_yet_competent': len(published_results) - competent_count,
        'transcripts': len(transcripts),
    }

    return render_template('trainee/dashboard.html', trainee=t, enrollments=enrollments,
                           stats=stats, recent_results=published_results[-5:])


@trainee.route('/results')
@login_required
@trainee_required
def results():
    t = get_trainee()
    year_id = request.args.get('year_id', type=int)
    program_id = request.args.get('program_id', type=int)

    query = Result.query.filter_by(trainee_id=t.id, is_published=True)
    if year_id:
        query = query.filter_by(academic_year_id=year_id)
    if program_id:
        query = query.join(Course).filter(Course.program_id == program_id)

    results_list = query.order_by(Result.uploaded_at.desc()).all()
    years = AcademicYear.query.order_by(AcademicYear.name.desc()).all()
    enrollments = Enrollment.query.filter_by(trainee_id=t.id).all()

    return render_template('trainee/results.html', trainee=t, results=results_list,
                           years=years, enrollments=enrollments,
                           selected_year=year_id, selected_program=program_id)


@trainee.route('/results/by-module')
@login_required
@trainee_required
def results_by_module():
    t = get_trainee()
    year_id = request.args.get('year_id', type=int)
    program_id = request.args.get('program_id', type=int)

    query = Result.query.filter_by(trainee_id=t.id, is_published=True)
    if year_id:
        query = query.filter_by(academic_year_id=year_id)

    results_list = query.join(Course).order_by(Course.module_number, Course.name).all()

    # Group by module
    modules = {}
    for r in results_list:
        if program_id and r.course.program_id != program_id:
            continue
        mod = r.course.module_number or 0
        if mod not in modules:
            modules[mod] = {'results': [], 'name': f'Module {mod}'}
        modules[mod]['results'].append(r)

    years = AcademicYear.query.order_by(AcademicYear.name.desc()).all()
    enrollments = Enrollment.query.filter_by(trainee_id=t.id).all()

    return render_template('trainee/results_by_module.html', trainee=t, modules=modules,
                           years=years, enrollments=enrollments,
                           selected_year=year_id, selected_program=program_id)


@trainee.route('/transcripts')
@login_required
@trainee_required
def transcripts():
    t = get_trainee()
    transcripts_list = Transcript.query.filter_by(trainee_id=t.id).order_by(
        Transcript.generated_at.desc()).all()
    return render_template('trainee/transcripts.html', trainee=t, transcripts=transcripts_list)


@trainee.route('/transcripts/download/<int:transcript_id>')
@login_required
@trainee_required
def download_transcript(transcript_id):
    t = get_trainee()
    transcript = Transcript.query.get_or_404(transcript_id)

    if transcript.trainee_id != t.id:
        abort(403)

    # Generate PDF
    pdf_buffer = generate_transcript_pdf(transcript)

    # Increment download count
    transcript.download_count += 1
    db.session.commit()

    filename = f'Transcript_{transcript.serial_number.replace("/", "_")}.pdf'
    return send_file(pdf_buffer, as_attachment=True, download_name=filename,
                     mimetype='application/pdf')


@trainee.route('/transcripts/view/<int:transcript_id>')
@login_required
@trainee_required
def view_transcript(transcript_id):
    t = get_trainee()
    transcript = Transcript.query.get_or_404(transcript_id)

    if transcript.trainee_id != t.id:
        abort(403)

    # Get results for this transcript
    results_list = (Result.query
                    .filter_by(trainee_id=t.id, is_published=True,
                               academic_year_id=transcript.academic_year_id)
                    .join(Course)
                    .filter(Course.program_id == transcript.program_id)
                    .order_by(Course.module_number, Course.name).all())

    return render_template('trainee/view_transcript.html', trainee=t,
                           transcript=transcript, results=results_list)


@trainee.route('/profile')
@login_required
@trainee_required
def profile():
    t = get_trainee()
    return render_template('trainee/profile.html', trainee=t)


@trainee.route('/notifications')
@login_required
@trainee_required
def notifications():
    from app.models import Notification
    notifs = (Notification.query
              .filter_by(user_id=g.current_user.id)
              .order_by(Notification.created_at.desc()).all())
    # Mark all as read
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('trainee/notifications.html', notifications=notifs)
