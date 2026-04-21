from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, trainer, trainee
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_photo = db.Column(db.String(200))

    # Relationships
    trainer_profile = db.relationship('Trainer', backref='user', uselist=False, cascade='all, delete-orphan')
    trainee_profile = db.relationship('Trainee', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    head_of_department = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    programs = db.relationship('Program', backref='department', lazy='dynamic')
    trainers = db.relationship('Trainer', backref='department', lazy='dynamic')

    def __repr__(self):
        return f'<Department {self.name}>'


class Program(db.Model):
    __tablename__ = 'programs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    level = db.Column(db.String(50))  # e.g., KNQF Level 6
    isced_code = db.Column(db.String(50))
    duration_years = db.Column(db.Integer, default=3)
    description = db.Column(db.Text)
    entry_requirements = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courses = db.relationship('Course', backref='program', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='program', lazy='dynamic')

    def __repr__(self):
        return f'<Program {self.name}>'


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    tvet_unit_code = db.Column(db.String(100))  # e.g., ENG/CU/EI/CR/01/6/MB
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    module_number = db.Column(db.Integer)  # Module I, II, etc.
    unit_category = db.Column(db.String(50))  # BC=Basic, CC=Common, CR=Core
    credit_factor = db.Column(db.Float, default=10.0)
    duration_hours = db.Column(db.Integer, default=100)
    theory_weight = db.Column(db.Float, default=30.0)   # % theory
    practical_weight = db.Column(db.Float, default=70.0)  # % practical
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('Result', backref='course', lazy='dynamic')

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'


class Trainer(db.Model):
    __tablename__ = 'trainers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    employee_id = db.Column(db.String(50), unique=True)
    qualification = db.Column(db.String(200))
    tveta_license = db.Column(db.String(100))
    specialization = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results_uploaded = db.relationship('Result', backref='uploaded_by_trainer', lazy='dynamic')

    def __repr__(self):
        return f'<Trainer {self.employee_id}>'


class Trainee(db.Model):
    __tablename__ = 'trainees'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    national_id = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    county = db.Column(db.String(100))
    address = db.Column(db.Text)
    guardian_name = db.Column(db.String(150))
    guardian_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship('Enrollment', backref='trainee', lazy='dynamic')
    results = db.relationship('Result', backref='trainee', lazy='dynamic')
    transcripts = db.relationship('Transcript', backref='trainee', lazy='dynamic')

    def __repr__(self):
        return f'<Trainee {self.admission_number}>'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    trainee_id = db.Column(db.Integer, db.ForeignKey('trainees.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    intake_year = db.Column(db.Integer, nullable=False)
    intake_month = db.Column(db.String(20))  # January, September, etc.
    status = db.Column(db.String(30), default='active')  # active, completed, withdrawn
    completion_date = db.Column(db.Date)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('trainee_id', 'program_id', name='unique_enrollment'),)

    def __repr__(self):
        return f'<Enrollment {self.trainee_id}-{self.program_id}>'


class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 2024/2025
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('Result', backref='academic_year', lazy='dynamic')

    def __repr__(self):
        return f'<AcademicYear {self.name}>'


class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    trainee_id = db.Column(db.Integer, db.ForeignKey('trainees.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)

    # Continuous Assessment (Formative) - 60% weight
    ca_theory = db.Column(db.Float)       # out of 100
    ca_practical = db.Column(db.Float)    # out of 100

    # Summative Assessment - 40% weight
    sa_theory = db.Column(db.Float)       # out of 100
    sa_practical = db.Column(db.Float)    # out of 100

    # Computed fields
    weighted_theory = db.Column(db.Float)
    weighted_practical = db.Column(db.Float)
    overall_score = db.Column(db.Float)
    competency_status = db.Column(db.String(30))  # Competent / Not Yet Competent
    competency_rating = db.Column(db.String(50))  # Attained Mastery / Proficient / Competent / Not Yet Competent

    remarks = db.Column(db.String(200))
    is_published = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('trainee_id', 'course_id', 'academic_year_id', name='unique_result'),)

    def compute_results(self):
        """Compute weighted scores and competency status per TVET CDACC guidelines."""
        course = self.course
        theory_w = course.theory_weight / 100  # e.g., 0.30
        practical_w = course.practical_weight / 100  # e.g., 0.70

        # Weighted theory: CA(60%) + SA(40%)
        if self.ca_theory is not None and self.sa_theory is not None:
            self.weighted_theory = (self.ca_theory * 0.6) + (self.sa_theory * 0.4)
        elif self.ca_theory is not None:
            self.weighted_theory = self.ca_theory
        else:
            self.weighted_theory = None

        # Weighted practical: CA(60%) + SA(40%)
        if self.ca_practical is not None and self.sa_practical is not None:
            self.weighted_practical = (self.ca_practical * 0.6) + (self.sa_practical * 0.4)
        elif self.ca_practical is not None:
            self.weighted_practical = self.ca_practical
        else:
            self.weighted_practical = None

        # Overall score: theory_weight * weighted_theory + practical_weight * weighted_practical
        if self.weighted_theory is not None and self.weighted_practical is not None:
            self.overall_score = (theory_w * self.weighted_theory) + (practical_w * self.weighted_practical)
        elif self.weighted_theory is not None:
            self.overall_score = self.weighted_theory
        elif self.weighted_practical is not None:
            self.overall_score = self.weighted_practical
        else:
            self.overall_score = None

        # Determine competency
        self._determine_competency()

    def _determine_competency(self):
        """Apply TVET CDACC competency determination rules."""
        competent = True
        reasons = []

        # Rule 1: Theory >= 40%
        if self.weighted_theory is not None and self.weighted_theory < 40:
            competent = False
            reasons.append('Theory below 40%')

        # Rule 2: Practical >= 50% (where applicable)
        if self.weighted_practical is not None and self.weighted_practical < 50:
            competent = False
            reasons.append('Practical below 50%')

        # Rule 3: Overall >= 50%
        if self.overall_score is not None and self.overall_score < 50:
            competent = False
            reasons.append('Overall below 50%')

        self.competency_status = 'Competent' if competent else 'Not Yet Competent'

        # Rating
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

    def __repr__(self):
        return f'<Result trainee={self.trainee_id} course={self.course_id}>'


class Transcript(db.Model):
    __tablename__ = 'transcripts'
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    trainee_id = db.Column(db.Integer, db.ForeignKey('trainees.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_official = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)
    qr_code_data = db.Column(db.Text)

    program = db.relationship('Program', backref='transcripts')
    academic_year = db.relationship('AcademicYear', backref='transcripts')
    generator = db.relationship('User', backref='generated_transcripts')

    @staticmethod
    def generate_serial():
        """Generate unique serial: TTTI/YYYY/XXXXXX"""
        year = datetime.utcnow().year
        random_part = ''.join(random.choices(string.digits, k=6))
        serial = f"TTTI/{year}/{random_part}"
        # Ensure uniqueness
        while Transcript.query.filter_by(serial_number=serial).first():
            random_part = ''.join(random.choices(string.digits, k=6))
            serial = f"TTTI/{year}/{random_part}"
        return serial

    def __repr__(self):
        return f'<Transcript {self.serial_number}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title}>'


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='logs')
