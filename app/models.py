"""
Database models for TTTI ERMS.
Authentication is handled by Supabase Auth.
User profiles and all app data are stored in PostgreSQL via SQLAlchemy.
"""
from app import db
from datetime import datetime
import random
import string


class User(db.Model):
    """
    User profile table — linked to Supabase auth.users via supabase_uid.
    Passwords are NOT stored here — managed entirely by Supabase Auth.
    """
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    supabase_uid      = db.Column(db.String(36), unique=True, nullable=False)
    username          = db.Column(db.String(80), unique=True, nullable=False)
    email             = db.Column(db.String(120), unique=True, nullable=False)
    role              = db.Column(db.String(20), nullable=False)
    full_name         = db.Column(db.String(150), nullable=False)
    phone             = db.Column(db.String(20))
    is_active         = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=True)  # force change on first login
    profile_photo     = db.Column(db.String(200))
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    trainer_profile = db.relationship('Trainer', backref='user', uselist=False, cascade='all, delete-orphan')
    trainee_profile = db.relationship('Trainee', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications   = db.relationship('Notification', backref='user', lazy='dynamic')
    logs            = db.relationship('SystemLog', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


class Department(db.Model):
    __tablename__ = 'departments'
    id                 = db.Column(db.Integer, primary_key=True)
    name               = db.Column(db.String(150), unique=True, nullable=False)
    code               = db.Column(db.String(20), unique=True, nullable=False)
    description        = db.Column(db.Text)
    head_of_department = db.Column(db.String(150))
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)

    programs = db.relationship('Program', backref='department', lazy='dynamic')
    trainers = db.relationship('Trainer', backref='department', lazy='dynamic')


class Program(db.Model):
    __tablename__ = 'programs'
    id                 = db.Column(db.Integer, primary_key=True)
    name               = db.Column(db.String(200), nullable=False)
    code               = db.Column(db.String(50), unique=True, nullable=False)
    department_id      = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    level              = db.Column(db.String(50))
    isced_code         = db.Column(db.String(50))
    duration_years     = db.Column(db.Integer, default=3)
    description        = db.Column(db.Text)
    entry_requirements = db.Column(db.Text)
    is_active          = db.Column(db.Boolean, default=True)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)

    courses     = db.relationship('Course', backref='program', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='program', lazy='dynamic')


class Course(db.Model):
    __tablename__ = 'courses'
    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(200), nullable=False)
    code             = db.Column(db.String(50), nullable=False)
    tvet_unit_code   = db.Column(db.String(100))
    program_id       = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    module_number    = db.Column(db.Integer)
    unit_category    = db.Column(db.String(50))   # BC | CC | CR
    credit_factor    = db.Column(db.Float, default=10.0)
    duration_hours   = db.Column(db.Integer, default=100)
    theory_weight    = db.Column(db.Float, default=30.0)
    practical_weight = db.Column(db.Float, default=70.0)
    description      = db.Column(db.Text)
    is_active        = db.Column(db.Boolean, default=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('Result', backref='course', lazy='dynamic')


class Trainer(db.Model):
    __tablename__ = 'trainers'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    employee_id   = db.Column(db.String(50), unique=True)
    qualification = db.Column(db.String(200))
    tveta_license = db.Column(db.String(100))
    specialization = db.Column(db.String(200))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    results_uploaded = db.relationship('Result', backref='uploaded_by_trainer', lazy='dynamic')


class Trainee(db.Model):
    __tablename__ = 'trainees'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    national_id      = db.Column(db.String(20))
    date_of_birth    = db.Column(db.Date)
    gender           = db.Column(db.String(10))
    county           = db.Column(db.String(100))
    address          = db.Column(db.Text)
    guardian_name    = db.Column(db.String(150))
    guardian_phone   = db.Column(db.String(20))
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship('Enrollment', backref='trainee', lazy='dynamic')
    results     = db.relationship('Result', backref='trainee', lazy='dynamic')
    transcripts = db.relationship('Transcript', backref='trainee', lazy='dynamic')


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id              = db.Column(db.Integer, primary_key=True)
    trainee_id      = db.Column(db.Integer, db.ForeignKey('trainees.id'), nullable=False)
    program_id      = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    intake_year     = db.Column(db.Integer, nullable=False)
    intake_month    = db.Column(db.String(20))
    status          = db.Column(db.String(30), default='active')
    completion_date = db.Column(db.Date)
    enrolled_at     = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('trainee_id', 'program_id', name='unique_enrollment'),)


class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.Date)
    end_date   = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('Result', backref='academic_year', lazy='dynamic')


class Result(db.Model):
    __tablename__ = 'results'
    id               = db.Column(db.Integer, primary_key=True)
    trainee_id       = db.Column(db.Integer, db.ForeignKey('trainees.id'), nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    trainer_id       = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)

    ca_theory    = db.Column(db.Float)
    ca_practical = db.Column(db.Float)
    sa_theory    = db.Column(db.Float)
    sa_practical = db.Column(db.Float)

    weighted_theory    = db.Column(db.Float)
    weighted_practical = db.Column(db.Float)
    overall_score      = db.Column(db.Float)
    competency_status  = db.Column(db.String(30))
    competency_rating  = db.Column(db.String(50))
    remarks            = db.Column(db.String(200))
    is_published       = db.Column(db.Boolean, default=False)
    uploaded_at        = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at         = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('trainee_id', 'course_id', 'academic_year_id', name='unique_result'),)

    def compute_results(self):
        course    = self.course
        theory_w  = course.theory_weight / 100
        practical_w = course.practical_weight / 100

        if self.ca_theory is not None and self.sa_theory is not None:
            self.weighted_theory = (self.ca_theory * 0.6) + (self.sa_theory * 0.4)
        elif self.ca_theory is not None:
            self.weighted_theory = self.ca_theory
        else:
            self.weighted_theory = None

        if self.ca_practical is not None and self.sa_practical is not None:
            self.weighted_practical = (self.ca_practical * 0.6) + (self.sa_practical * 0.4)
        elif self.ca_practical is not None:
            self.weighted_practical = self.ca_practical
        else:
            self.weighted_practical = None

        if self.weighted_theory is not None and self.weighted_practical is not None:
            self.overall_score = (theory_w * self.weighted_theory) + (practical_w * self.weighted_practical)
        elif self.weighted_theory is not None:
            self.overall_score = self.weighted_theory
        elif self.weighted_practical is not None:
            self.overall_score = self.weighted_practical
        else:
            self.overall_score = None

        self._determine_competency()

    def _determine_competency(self):
        competent = True
        reasons   = []

        if self.weighted_theory is not None and self.weighted_theory < 40:
            competent = False
            reasons.append('Theory below 40%')
        if self.weighted_practical is not None and self.weighted_practical < 50:
            competent = False
            reasons.append('Practical below 50%')
        if self.overall_score is not None and self.overall_score < 50:
            competent = False
            reasons.append('Overall below 50%')

        self.competency_status = 'Competent' if competent else 'Not Yet Competent'

        if self.overall_score is not None:
            if self.overall_score >= 80:
                self.competency_rating = 'Attained Mastery'
            elif self.overall_score >= 65:
                self.competency_rating = 'Proficient'
            elif self.overall_score >= 50:
                self.competency_rating = 'Competent'
            else:
                self.competency_rating = 'Not Yet Competent'

        if not competent:
            self.competency_rating = 'Not Yet Competent'
            self.remarks = '; '.join(reasons)


class Transcript(db.Model):
    __tablename__ = 'transcripts'
    id               = db.Column(db.Integer, primary_key=True)
    serial_number    = db.Column(db.String(50), unique=True, nullable=False)
    trainee_id       = db.Column(db.Integer, db.ForeignKey('trainees.id'), nullable=False)
    program_id       = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    generated_by     = db.Column(db.Integer, db.ForeignKey('users.id'))
    generated_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_official      = db.Column(db.Boolean, default=False)
    download_count   = db.Column(db.Integer, default=0)
    qr_code_data     = db.Column(db.Text)

    program      = db.relationship('Program', backref='transcripts')
    academic_year = db.relationship('AcademicYear', backref='transcripts')
    generator    = db.relationship('User', backref='generated_transcripts')

    @staticmethod
    def generate_serial():
        year = datetime.utcnow().year
        random_part = ''.join(random.choices(string.digits, k=6))
        serial = f"TTTI/{year}/{random_part}"
        while Transcript.query.filter_by(serial_number=serial).first():
            random_part = ''.join(random.choices(string.digits, k=6))
            serial = f"TTTI/{year}/{random_part}"
        return serial


class Notification(db.Model):
    __tablename__ = 'notifications'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    action     = db.Column(db.String(200), nullable=False)
    details    = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
