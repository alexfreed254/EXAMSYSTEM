from app import create_app, db
from app.models import User, Department, Program, Course, Trainer, Trainee, Enrollment, AcademicYear, Result, Transcript
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Department': Department,
        'Program': Program, 'Course': Course, 'Trainer': Trainer,
        'Trainee': Trainee, 'Enrollment': Enrollment,
        'AcademicYear': AcademicYear, 'Result': Result, 'Transcript': Transcript,
    }


@app.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
