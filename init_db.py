"""
Database initialization — creates Supabase Auth users + seeds app data.
Run inside an active Flask app context.
"""
from datetime import date


def init_database():
    from app import db
    from app.models import (User, Department, Program, Course,
                             Trainer, Trainee, Enrollment, AcademicYear)
    from app.supabase_client import get_supabase_admin

    db.create_all()
    print("✓ Tables created")

    if User.query.first():
        print("⚠  Already seeded — skipping")
        return

    admin_sb = get_supabase_admin()

    def create_auth_user(email, password, role, full_name):
        """Create user in Supabase Auth and return their UUID."""
        resp = admin_sb.auth.admin.create_user({
            'email': email,
            'password': password,
            'email_confirm': True,
            'user_metadata': {'role': role, 'full_name': full_name}
        })
        return resp.user.id

    # ── Academic Year ─────────────────────────────────────────────────────────
    year = AcademicYear(name='2024/2025', is_current=True,
                        start_date=date(2024, 9, 1), end_date=date(2025, 8, 31))
    db.session.add(year)
    db.session.flush()
    print("✓ Academic year 2024/2025")

    # ── Departments ───────────────────────────────────────────────────────────
    depts_data = [
        ('Electrical Engineering',  'EE'),
        ('Mechanical Engineering',  'ME'),
        ('Civil Engineering',       'CE'),
        ('ICT & Computing',         'ICT'),
        ('Business Studies',        'BS'),
        ('Hospitality & Tourism',   'HT'),
        ('Building & Construction', 'BC'),
    ]
    dept_map = {}
    for name, code in depts_data:
        d = Department(name=name, code=code)
        db.session.add(d)
        db.session.flush()
        dept_map[code] = d.id
    print(f"✓ {len(depts_data)} departments")

    # ── Program ───────────────────────────────────────────────────────────────
    prog = Program(name='Electrical Engineering', code='EE-L6-C3',
                   department_id=dept_map['EE'], level='KNQF Level 6',
                   isced_code='0713 554B', duration_years=3,
                   description='Competency-Based Modular Curriculum EE KNQF Level 6 Cycle 3',
                   entry_requirements='KCSE C- or Certificate EE KNQF Level 5')
    db.session.add(prog)
    db.session.flush()
    prog_id = prog.id
    print("✓ Program: Electrical Engineering Level 6")

    # ── 33 Units ──────────────────────────────────────────────────────────────
    units = [
        ('PVC Sheathed Cable System Installation',      '0713 251 23B','ENG/CU/EI/CR/01/3/MB',1,'CR',10,100,10.0),
        ('Trunking System Installation',                '0713 251 24B','ENG/CU/EI/CR/02/3/MB',1,'CR',10,100,10.0),
        ('Conduit System Installation',                 '0713 251 25B','ENG/CU/EI/CR/03/3/MB',1,'CR',10,100,10.0),
        ('Stand-Alone Solar PV Systems',                '0713 351 26B','ENG/CU/EI/CR/01/4/MB',2,'CR',10,120,12.0),
        ('Bell and Alarm Installation',                 '0714 351 27B','ENG/CU/EI/CR/02/4/MB',2,'CR',10,120,12.0),
        ('Electrical Machine Winding',                  '0713 351 28B','ENG/CU/EI/CR/03/4/MB',2,'CR',10,120,12.0),
        ('Digital Literacy',                            '0611 451 02B','ENG/CU/EI/BC/01/5/MB',3,'BC',30, 40, 4.0),
        ('Communication Skills',                        '0031 441 01B','ENG/CU/EI/BC/02/5/MB',3,'BC',30, 40, 4.0),
        ('Basic Electrical Principles',                 '0713 441 09B','ENG/CU/EI/CC/01/5/MB',3,'CC',30,100,10.0),
        ('Technical Drawing',                           '0732 441 13B','ENG/CU/EI/CC/02/5/MB',3,'CC',30, 80, 8.0),
        ('Electrical Installation',                     '0713 451 29B','ENG/CU/EI/CR/01/5/MB',3,'CR',30,110,11.0),
        ('Work Ethics and Practices',                   '0417 441 04B','ENG/CU/EI/BC/03/5/MB',4,'BC',30, 40, 4.0),
        ('Engineering Technician Mathematics I',        '0541 441 05B','ENG/CU/EI/CC/03/5/MB',4,'CC',30,100,10.0),
        ('Analogue Electronics I',                      '0714 441 15B','ENG/CU/EI/CC/04/5/MB',4,'CC',30, 70, 7.0),
        ('Digital Electronics I',                       '0714 441 17B','ENG/CU/EI/CC/05/5/MB',4,'CC',30, 70, 7.0),
        ('Security Systems Installation',               '0713 451 33B','ENG/CU/EI/CR/02/5/MB',4,'CR',30,120,12.0),
        ('Entrepreneurial Skills',                      '0413 451 03B','ENG/CU/EI/BC/04/5/MB',5,'BC',30, 40, 4.0),
        ('Analogue Electronics II',                     '0714 441 16B','ENG/CU/EI/CC/06/5/MB',5,'CC',30, 80, 8.0),
        ('Engineering Technician Mathematics II',       '0541 441 06B','ENG/CU/EI/CC/07/5/MB',5,'CC',30,100,10.0),
        ('Digital Electronics II',                      '0714 441 18B','ENG/CU/EI/CC/08/5/MB',5,'CC',30, 80, 8.0),
        ('Electrical Machines Installation',            '0713 451 31B','ENG/CU/EI/CR/03/5/MB',5,'CR',30,120,12.0),
        ('Solar PV Systems Installation',               '0713 451 32B','ENG/CU/EI/CR/04/5/MB',5,'CR',30, 60, 6.0),
        ('Engineering Technician Mathematics III',      '0541 541 07B','ENG/CU/EI/CC/01/6/MB',6,'CC',40,100,10.0),
        ('Electrical Principles I',                     '0713 541 10B','ENG/CU/EI/CC/02/6/MB',6,'CC',40, 80, 8.0),
        ('Micro-Control Systems',                       '0714 541 19B','ENG/CU/EI/CC/03/6/MB',6,'CC',40, 80, 8.0),
        ('Electrical Powerlines Installation',          '0713 551 30B','ENG/CU/EI/CR/01/6/MB',6,'CR',40,180,18.0),
        ('Engineering Technician Mathematics IV',       '0541 541 08B','ENG/CU/EI/CC/04/6/MB',7,'CC',40,100,10.0),
        ('Electrical Principles II',                    '0713 541 11B','ENG/CU/EI/CC/05/6/MB',7,'CC',40,100,10.0),
        ('Control Systems',                             '0714 541 12B','ENG/CU/EI/CC/06/6/MB',7,'CC',40,100,10.0),
        ('Electrical Systems Automation',               '0714 551 36B','ENG/CU/EI/CR/02/6/MB',7,'CR',40,160,16.0),
        ('Research Methods',                            '0111 541 14B','ENG/CU/EI/CC/07/6/MB',8,'CC',40, 80, 6.0),
        ('Electrical Project Supervision',              '0713 551 22B','ENG/CU/EI/CC/08/6/MB',8,'CC',40, 60, 6.0),
        ('Electrical Measurement and Fault Diagnosis I','0713 541 20B','ENG/CU/EI/CC/09/6/MB',8,'CC',40, 80, 8.0),
        ('Power Electronic Circuits Fabrication',       '0714 551 35B','ENG/CU/EI/CR/03/6/MB',8,'CR',40,150,15.0),
    ]
    for name, code, tvet, mod, cat, tw, hrs, cr in units:
        db.session.add(Course(name=name, code=code, tvet_unit_code=tvet,
                               program_id=prog_id, module_number=mod, unit_category=cat,
                               theory_weight=float(tw), practical_weight=float(100-tw),
                               duration_hours=hrs, credit_factor=cr))
    print(f"✓ {len(units)} units")

    # ── Admin user ────────────────────────────────────────────────────────────
    try:
        uid = create_auth_user('admin@ttti.ac.ke', 'Admin@2025', 'admin', 'System Administrator')
        db.session.add(User(supabase_uid=uid, username='admin',
                             email='admin@ttti.ac.ke', role='admin',
                             full_name='System Administrator', phone='+254-67-22396'))
        print("✓ Admin: admin@ttti.ac.ke / Admin@2025")
    except Exception as e:
        print(f"⚠  Admin auth error: {e}")

    # ── Sample Trainer ────────────────────────────────────────────────────────
    try:
        uid = create_auth_user('trainer1@ttti.ac.ke', 'Trainer@2025', 'trainer', 'John Kamau Mwangi')
        t_user = User(supabase_uid=uid, username='trainer1',
                      email='trainer1@ttti.ac.ke', role='trainer',
                      full_name='John Kamau Mwangi', phone='0712345678')
        db.session.add(t_user)
        db.session.flush()
        db.session.add(Trainer(user_id=t_user.id, department_id=dept_map['EE'],
                                employee_id='TTTI/TR/0001',
                                qualification='BSc Electrical Engineering',
                                tveta_license='TVETA/2024/001',
                                specialization='Power Systems'))
        print("✓ Trainer: trainer1@ttti.ac.ke / Trainer@2025")
    except Exception as e:
        print(f"⚠  Trainer auth error: {e}")

    # ── Sample Trainee ────────────────────────────────────────────────────────
    try:
        uid = create_auth_user('trainee1@ttti.ac.ke', 'Trainee@2025', 'trainee', 'Mary Wanjiku Njoroge')
        s_user = User(supabase_uid=uid, username='trainee1',
                      email='trainee1@ttti.ac.ke', role='trainee',
                      full_name='Mary Wanjiku Njoroge', phone='0723456789')
        db.session.add(s_user)
        db.session.flush()
        trainee = Trainee(user_id=s_user.id, admission_number='TTTI/2024/0001',
                           national_id='12345678', gender='Female',
                           county='Kiambu', date_of_birth=date(2000, 3, 15))
        db.session.add(trainee)
        db.session.flush()
        db.session.add(Enrollment(trainee_id=trainee.id, program_id=prog_id,
                                   intake_year=2024, intake_month='September'))
        print("✓ Trainee: trainee1@ttti.ac.ke / Trainee@2025")
    except Exception as e:
        print(f"⚠  Trainee auth error: {e}")

    db.session.commit()
    print("\n" + "="*50)
    print("  DATABASE INITIALIZED SUCCESSFULLY")
    print("="*50)
    print("  admin@ttti.ac.ke    /  Admin@2025")
    print("  trainer1@ttti.ac.ke /  Trainer@2025")
    print("  trainee1@ttti.ac.ke /  Trainee@2025")
    print("="*50)


if __name__ == '__main__':
    from app import create_app, db as _db
    _app = create_app('production')
    with _app.app_context():
        init_database()
