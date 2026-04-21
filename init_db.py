"""
Database initialization script for Render deployment.
Can be called standalone:  python init_db.py
Or imported by wsgi.py on first startup.
"""
from datetime import date


def init_database():
    """Seed all initial data. Must be called inside an active app context."""
    from app import db
    from app.models import (User, Department, Program, Course,
                             Trainer, Trainee, Enrollment, AcademicYear)

    db.create_all()
    print("✓ Tables created / verified")

    # ── Guard: skip if already seeded ────────────────────────────────────────
    if User.query.filter_by(username='admin').first():
        print("⚠  Database already seeded. Skipping.")
        return

    # ── Admin User ───────────────────────────────────────────────────────────
    admin = User(
        username='admin',
        email='admin@ttti.ac.ke',
        full_name='System Administrator',
        role='admin',
        phone='+254-67-22396'
    )
    admin.set_password('Admin@2025')
    db.session.add(admin)
    db.session.flush()
    print("✓ Admin user created  →  admin / Admin@2025")

    # ── Academic Year ─────────────────────────────────────────────────────────
    year = AcademicYear(
        name='2024/2025',
        is_current=True,
        start_date=date(2024, 9, 1),
        end_date=date(2025, 8, 31)
    )
    db.session.add(year)
    db.session.flush()
    print("✓ Academic year 2024/2025 created")

    # ── Departments ───────────────────────────────────────────────────────────
    departments_data = [
        ('Electrical Engineering',  'EE',  'Department of Electrical Engineering'),
        ('Mechanical Engineering',  'ME',  'Department of Mechanical Engineering'),
        ('Civil Engineering',       'CE',  'Department of Civil Engineering'),
        ('ICT & Computing',         'ICT', 'Department of ICT and Computing'),
        ('Business Studies',        'BS',  'Department of Business Studies'),
        ('Hospitality & Tourism',   'HT',  'Department of Hospitality and Tourism'),
        ('Building & Construction', 'BC',  'Department of Building and Construction'),
    ]
    dept_map = {}
    for name, code, desc in departments_data:
        dept = Department(name=name, code=code, description=desc)
        db.session.add(dept)
        db.session.flush()
        dept_map[code] = dept.id
    print(f"✓ {len(departments_data)} departments created")

    # ── Program: Electrical Engineering Level 6 ───────────────────────────────
    prog = Program(
        name='Electrical Engineering',
        code='EE-L6-C3',
        department_id=dept_map['EE'],
        level='KNQF Level 6',
        isced_code='0713 554B',
        duration_years=3,
        description=(
            'Competency-Based Modular Curriculum for Electrical Engineering '
            'KNQF Level 6 Cycle 3. Programme ISCED Code: 0713 554B'
        ),
        entry_requirements=(
            'a) KCSE Grade C- (minus); OR\n'
            'b) Certificate in Electrical Engineering KNQF Level 5; OR\n'
            'c) Equivalent qualifications as determined by TVETA'
        ),
    )
    db.session.add(prog)
    db.session.flush()
    prog_id = prog.id
    print("✓ Program: Electrical Engineering Level 6 created")

    # ── Units / Courses ───────────────────────────────────────────────────────
    # (code, tvet_code, name, module, category, theory_pct, hours, credits)
    units = [
        # MODULE I — Theory 10% / Practical 90%
        ('0713 251 23B', 'ENG/CU/EI/CR/01/3/MB', 'PVC Sheathed Cable System Installation',      1, 'CR', 10, 100, 10.0),
        ('0713 251 24B', 'ENG/CU/EI/CR/02/3/MB', 'Trunking System Installation',                 1, 'CR', 10, 100, 10.0),
        ('0713 251 25B', 'ENG/CU/EI/CR/03/3/MB', 'Conduit System Installation',                  1, 'CR', 10, 100, 10.0),
        # MODULE II — Theory 10% / Practical 90%
        ('0713 351 26B', 'ENG/CU/EI/CR/01/4/MB', 'Stand-Alone Solar PV Systems',                 2, 'CR', 10, 120, 12.0),
        ('0714 351 27B', 'ENG/CU/EI/CR/02/4/MB', 'Bell and Alarm Installation',                  2, 'CR', 10, 120, 12.0),
        ('0713 351 28B', 'ENG/CU/EI/CR/03/4/MB', 'Electrical Machine Winding',                   2, 'CR', 10, 120, 12.0),
        # MODULE III — Theory 30% / Practical 70%
        ('0611 451 02B', 'ENG/CU/EI/BC/01/5/MB', 'Digital Literacy',                             3, 'BC', 30,  40,  4.0),
        ('0031 441 01B', 'ENG/CU/EI/BC/02/5/MB', 'Communication Skills',                         3, 'BC', 30,  40,  4.0),
        ('0713 441 09B', 'ENG/CU/EI/CC/01/5/MB', 'Basic Electrical Principles',                  3, 'CC', 30, 100, 10.0),
        ('0732 441 13B', 'ENG/CU/EI/CC/02/5/MB', 'Technical Drawing',                            3, 'CC', 30,  80,  8.0),
        ('0713 451 29B', 'ENG/CU/EI/CR/01/5/MB', 'Electrical Installation',                      3, 'CR', 30, 110, 11.0),
        # MODULE IV — Theory 30% / Practical 70%
        ('0417 441 04B', 'ENG/CU/EI/BC/03/5/MB', 'Work Ethics and Practices',                    4, 'BC', 30,  40,  4.0),
        ('0541 441 05B', 'ENG/CU/EI/CC/03/5/MB', 'Engineering Technician Mathematics I',         4, 'CC', 30, 100, 10.0),
        ('0714 441 15B', 'ENG/CU/EI/CC/04/5/MB', 'Analogue Electronics I',                       4, 'CC', 30,  70,  7.0),
        ('0714 441 17B', 'ENG/CU/EI/CC/05/5/MB', 'Digital Electronics I',                        4, 'CC', 30,  70,  7.0),
        ('0713 451 33B', 'ENG/CU/EI/CR/02/5/MB', 'Security Systems Installation',                4, 'CR', 30, 120, 12.0),
        # MODULE V — Theory 30% / Practical 70%
        ('0413 451 03B', 'ENG/CU/EI/BC/04/5/MB', 'Entrepreneurial Skills',                       5, 'BC', 30,  40,  4.0),
        ('0714 441 16B', 'ENG/CU/EI/CC/06/5/MB', 'Analogue Electronics II',                      5, 'CC', 30,  80,  8.0),
        ('0541 441 06B', 'ENG/CU/EI/CC/07/5/MB', 'Engineering Technician Mathematics II',        5, 'CC', 30, 100, 10.0),
        ('0714 441 18B', 'ENG/CU/EI/CC/08/5/MB', 'Digital Electronics II',                       5, 'CC', 30,  80,  8.0),
        ('0713 451 31B', 'ENG/CU/EI/CR/03/5/MB', 'Electrical Machines Installation',             5, 'CR', 30, 120, 12.0),
        ('0713 451 32B', 'ENG/CU/EI/CR/04/5/MB', 'Solar PV Systems Installation',                5, 'CR', 30,  60,  6.0),
        # MODULE VI — Theory 40% / Practical 60%
        ('0541 541 07B', 'ENG/CU/EI/CC/01/6/MB', 'Engineering Technician Mathematics III',       6, 'CC', 40, 100, 10.0),
        ('0713 541 10B', 'ENG/CU/EI/CC/02/6/MB', 'Electrical Principles I',                      6, 'CC', 40,  80,  8.0),
        ('0714 541 19B', 'ENG/CU/EI/CC/03/6/MB', 'Micro-Control Systems',                        6, 'CC', 40,  80,  8.0),
        ('0713 551 30B', 'ENG/CU/EI/CR/01/6/MB', 'Electrical Powerlines Installation',           6, 'CR', 40, 180, 18.0),
        # MODULE VII — Theory 40% / Practical 60%
        ('0541 541 08B', 'ENG/CU/EI/CC/04/6/MB', 'Engineering Technician Mathematics IV',        7, 'CC', 40, 100, 10.0),
        ('0713 541 11B', 'ENG/CU/EI/CC/05/6/MB', 'Electrical Principles II',                     7, 'CC', 40, 100, 10.0),
        ('0714 541 12B', 'ENG/CU/EI/CC/06/6/MB', 'Control Systems',                              7, 'CC', 40, 100, 10.0),
        ('0714 551 36B', 'ENG/CU/EI/CR/02/6/MB', 'Electrical Systems Automation',                7, 'CR', 40, 160, 16.0),
        # MODULE VIII — Theory 40% / Practical 60%
        ('0111 541 14B', 'ENG/CU/EI/CC/07/6/MB', 'Research Methods',                             8, 'CC', 40,  80,  6.0),
        ('0713 551 22B', 'ENG/CU/EI/CC/08/6/MB', 'Electrical Project Supervision',               8, 'CC', 40,  60,  6.0),
        ('0713 541 20B', 'ENG/CU/EI/CC/09/6/MB', 'Electrical Measurement and Fault Diagnosis I', 8, 'CC', 40,  80,  8.0),
        ('0714 551 35B', 'ENG/CU/EI/CR/03/6/MB', 'Power Electronic Circuits Fabrication',        8, 'CR', 40, 150, 15.0),
    ]

    for code, tvet_code, name, module, cat, theory_w, hours, credits in units:
        course = Course(
            name=name, code=code, tvet_unit_code=tvet_code,
            program_id=prog_id, module_number=module,
            unit_category=cat, theory_weight=float(theory_w),
            practical_weight=float(100 - theory_w),
            duration_hours=hours, credit_factor=credits,
        )
        db.session.add(course)
    print(f"✓ {len(units)} units seeded for Electrical Engineering Level 6")

    # ── Sample Trainer ────────────────────────────────────────────────────────
    t_user = User(
        username='trainer1', email='trainer1@ttti.ac.ke',
        full_name='John Kamau Mwangi', role='trainer', phone='0712345678'
    )
    t_user.set_password('Trainer@2025')
    db.session.add(t_user)
    db.session.flush()
    trainer = Trainer(
        user_id=t_user.id, department_id=dept_map['EE'],
        employee_id='TTTI/TR/0001',
        qualification='BSc Electrical Engineering',
        tveta_license='TVETA/2024/001',
        specialization='Power Systems & Electrical Installation'
    )
    db.session.add(trainer)
    print("✓ Sample trainer created  →  trainer1 / Trainer@2025")

    # ── Sample Trainee ────────────────────────────────────────────────────────
    s_user = User(
        username='trainee1', email='trainee1@ttti.ac.ke',
        full_name='Mary Wanjiku Njoroge', role='trainee', phone='0723456789'
    )
    s_user.set_password('Trainee@2025')
    db.session.add(s_user)
    db.session.flush()
    trainee = Trainee(
        user_id=s_user.id, admission_number='TTTI/2024/0001',
        national_id='12345678', gender='Female',
        county='Kiambu', date_of_birth=date(2000, 3, 15)
    )
    db.session.add(trainee)
    db.session.flush()
    db.session.add(Enrollment(
        trainee_id=trainee.id, program_id=prog_id,
        intake_year=2024, intake_month='September'
    ))
    print("✓ Sample trainee created  →  trainee1 / Trainee@2025")

    # ── Commit ────────────────────────────────────────────────────────────────
    db.session.commit()
    print("\n" + "=" * 50)
    print("  DATABASE INITIALIZED SUCCESSFULLY")
    print("=" * 50)
    print("  Admin:   admin    /  Admin@2025")
    print("  Trainer: trainer1 /  Trainer@2025")
    print("  Trainee: trainee1 /  Trainee@2025")
    print("=" * 50)


if __name__ == '__main__':
    from app import create_app, db as _db
    _app = create_app('production')
    with _app.app_context():
        init_database()
