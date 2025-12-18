from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from sqlalchemy import inspect, text
import pandas as pd
from io import StringIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

ALLOWED_CLASSES = ['8','9','10','11','12']
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_UPLOAD_EXTENSIONS = {'csv', 'xlsx', 'xls'}  # for data files
SUBJECT_FULL_MARKS = {
    '8': {
        'English': 75,
        'Urdu': 75,
        'Math': 75,
        'Bio': 65,
        'Physics': 65,
        'Chemistry': 65,
        'Islamiyat': 100,
        'Tarjamat-ul-Quran': 50,
        'Computer': 60
    },
    '9': {
        'English': 75,
        'Urdu': 75,
        'Math': 75,
        'Bio': 65,
        'Physics': 65,
        'Chemistry': 65,
        'Islamiyat': 100,
        'Tarjamat-ul-Quran': 50,
        'Computer': 60
    },
    '10': {
        'English': 75,
        'Urdu': 75,
        'Math': 75,
        'Bio': 65,
        'Physics': 65,
        'Chemistry': 65,
        'Pak Studies': 50,
        'Islamiyat': 50,
        'Computer': 55
    },
    '11': {
        'English': 100,
        'Urdu': 100,
        'Math': 100,
        'Bio': 80,
        'Physics': 80,
        'Chemistry': 80,
        'Tarjamat-ul-Quran': 50,
        'Islamiyat': 50,
        'Computer': 80
    },
    '12': {
        'English': 100,
        'Urdu': 100,
        'Math': 100,
        'Bio': 85,
        'Physics': 85,
        'Chemistry': 85,
        'Pak Studies': 50,
        'Computer': 75
    }
}
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    approved = db.Column(db.Boolean, default=False)  # teachers need approval
    assigned_subject = db.Column(db.String(80), nullable=True)  # for teachers

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    class_grade = db.Column(db.String(10), nullable=False)
    house_name = db.Column(db.String(80), nullable=True)  # student's house
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    first_term = db.Column(db.Float, default=0.0)
    second_term = db.Column(db.Float, default=0.0)
    board_mark = db.Column(db.Float, default=0.0)
    class_grade = db.Column(db.String(10), nullable=False)
    student = db.relationship('Student', backref=db.backref('marks', lazy=True))

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_path = db.Column(db.String(255), default=None)
    bg_image_path = db.Column(db.String(255), default=None)

@login_manager.user_loader
def load_user(user_id):
    # use session.get to avoid SQLAlchemy Query.get() deprecation warning
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_logo_path():
    settings = SiteSettings.query.first()
    return settings.logo_path if settings else None

def get_bg_image_path():
    settings = SiteSettings.query.first()
    return settings.bg_image_path if settings else None

@app.context_processor
def inject_logo():
    return dict(logo_path=get_logo_path(), bg_image_path=get_bg_image_path())

def init_db():
    with app.app_context():
        db.create_all()
        # ensure schema changes are applied for existing DB (add new columns if missing)
        inspector = inspect(db.engine)
        if 'site_settings' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('site_settings')]
            if 'bg_image_path' not in cols:
                db.session.execute(text('ALTER TABLE site_settings ADD COLUMN bg_image_path VARCHAR(255)'))
                db.session.commit()
        if 'student' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('student')]
            if 'house_name' not in cols:
                db.session.execute(text('ALTER TABLE student ADD COLUMN house_name VARCHAR(80)'))
                db.session.commit()

        # seed admin user
        admin = User.query.filter_by(username='hamdan').first()
        if not admin:
            admin = User(username='hamdan', role='admin', approved=True)
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
        # seed default logo and settings row
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings(logo_path='/static/uploads/logo_default.svg')
            db.session.add(settings)
            db.session.commit()

@app.route('/')
def portal():
    return render_template('portal.html')

@app.route('/login', methods=['GET','POST'])
def login():
    role = request.args.get('role', '')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.approved:
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('login'))
            login_user(user)
            flash('Logged in successfully.', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('student_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', role=role)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        user = User(username=username, role=role)
        user.set_password(password)
        # ALL registrations require admin approval
        user.approved = False
        if role == 'teacher':
            user.assigned_subject = request.form.get('assigned_subject')
        db.session.add(user)
        db.session.commit()
        if role == 'student':
            roll = request.form['roll_number']
            name = request.form['name']
            class_grade = request.form['class_grade']
            house_name = request.form.get('house_name', '')
            if class_grade not in ALLOWED_CLASSES:
                flash('Class must be between 8 and 12', 'danger')
                return redirect(url_for('register'))
            student = Student(user_id=user.id, roll_number=roll, name=name, class_grade=class_grade, house_name=house_name)
            db.session.add(student)
            db.session.commit()
        flash('✓ Registration successful! Your account is pending admin approval.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', classes=ALLOWED_CLASSES)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('✓ You have been logged out successfully', 'success')
    return redirect(url_for('portal'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    admins = User.query.filter_by(role='admin').all()
    teachers = User.query.filter_by(role='teacher').all()
    students = Student.query.all()
    # split students into pending and approved using related User.approved
    pending_students = [s for s in students if not (s.user and s.user.approved)]
    approved_students = [s for s in students if s.user and s.user.approved]
    return render_template('admin_dashboard.html', admins=admins, teachers=teachers, students=students, pending_students=pending_students, approved_students=approved_students)

@app.route('/admin/approve/<int:user_id>')
@login_required
def approve_teacher(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    user = User.query.get_or_404(user_id)
    if user.role == 'teacher':
        user.approved = True
        db.session.commit()
        flash('Teacher approved', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/approve_admin/<int:user_id>')
@login_required
def approve_admin(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        user.approved = True
        db.session.commit()
        flash('Admin approved', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/approve_student/<int:user_id>')
@login_required
def approve_student(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    user = User.query.get_or_404(user_id)
    if user.role == 'student':
        user.approved = True
        db.session.commit()
        flash('Student approved', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_student/<int:user_id>')
@login_required
def delete_student(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    user = User.query.get_or_404(user_id)
    if user.role == 'student':
        # delete marks first (foreign key)
        marks = Mark.query.filter_by(student_id=user.student_profile.id).all()
        for mark in marks:
            db.session.delete(mark)
        # delete student profile
        db.session.delete(user.student_profile)
        # delete user
        db.session.delete(user)
        db.session.commit()
        flash('Student deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_teacher/<int:user_id>')
@login_required
def delete_teacher(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    user = User.query.get_or_404(user_id)
    if user.role == 'teacher':
        db.session.delete(user)
        db.session.commit()
        flash('Teacher deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/reset_teachers', methods=['POST'])
@login_required
def reset_teachers():
    """Reset all teacher passwords to a default ('1234').
    Username is left unchanged. Admin must POST to this endpoint.
    """
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    teachers = User.query.filter_by(role='teacher').all()
    if not teachers:
        flash('No teachers found', 'info')
        return redirect(url_for('admin_dashboard'))
    for t in teachers:
        try:
            # keep username as-is; set password to '1234'
            t.set_password('1234')
        except Exception:
            # continue on errors
            continue
    db.session.commit()
    flash(f"✓ Reset password to '1234' for {len(teachers)} teacher(s)", 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/upload_logo', methods=['GET', 'POST'])
@login_required
def upload_logo():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    if request.method == 'POST':
        if 'logo' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_logo'))
        file = request.files['logo']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_logo'))
        if file and allowed_file(file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(f"logo_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            settings = SiteSettings.query.first()
            if not settings:
                settings = SiteSettings()
                db.session.add(settings)
            settings.logo_path = f"/static/uploads/{filename}"
            db.session.commit()
            flash('Logo uploaded successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid file type. Use PNG, JPG, JPEG, GIF, or WEBP', 'danger')
    return render_template('upload_logo.html')

@app.route('/admin/upload_background', methods=['GET', 'POST'])
@login_required
def upload_background():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    if request.method == 'POST':
        if 'background' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_background'))
        file = request.files['background']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_background'))
        if file and allowed_file(file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(f"background_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            settings = SiteSettings.query.first()
            if not settings:
                settings = SiteSettings()
                db.session.add(settings)
            settings.bg_image_path = f"/static/uploads/{filename}"
            db.session.commit()
            flash('Background image uploaded successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid file type. Use PNG, JPG, JPEG, GIF, or WEBP', 'danger')
    return render_template('upload_background.html')

@app.route('/admin/add_student', methods=['GET','POST'])
@login_required
def add_student():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        roll = request.form['roll_number']
        name = request.form['name']
        class_grade = request.form['class_grade']
        house_name = request.form.get('house_name', '')
        if User.query.filter_by(username=username).first() or Student.query.filter_by(roll_number=roll).first():
            flash('Username or roll number exists', 'danger')
            return redirect(url_for('add_student'))
        user = User(username=username, role='student', approved=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        student = Student(user_id=user.id, roll_number=roll, name=name, class_grade=class_grade, house_name=house_name)
        db.session.add(student)
        db.session.commit()
        flash('Student created', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_mark.html', action='add_student', classes=ALLOWED_CLASSES)

@app.route('/admin/add_mark', methods=['GET','POST'])
@login_required
def admin_add_mark():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    if request.method == 'POST':
        roll = request.form['roll_number']
        subject = request.form['subject']
        first = float(request.form.get('first_term') or 0)
        second = float(request.form.get('second_term') or 0)
        board = float(request.form.get('board_mark') or 0)
        # Validate at least one mark is provided
        if first == 0 and second == 0 and board == 0:
            flash('Please fill at least one term mark', 'warning')
            return redirect(url_for('admin_add_mark'))
        student = Student.query.filter_by(roll_number=roll).first()
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('admin_add_mark'))
        mark = Mark(student_id=student.id, subject=subject, first_term=first, second_term=second, board_mark=board, class_grade=student.class_grade)
        db.session.add(mark)
        db.session.commit()
        flash('Mark added', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_mark.html', action='add_mark', classes=ALLOWED_CLASSES)

@app.route('/teacher')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    # show marks for teacher's assigned subject
    subject = current_user.assigned_subject
    marks = []
    if subject:
        marks = Mark.query.filter_by(subject=subject).all()
    return render_template('teacher_dashboard.html', marks=marks, subject=subject, classes=ALLOWED_CLASSES)

@app.route('/teacher/search', methods=['GET', 'POST'])
@login_required
def teacher_search():
    """Teacher search students by class to view/edit marks for their subject"""
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    
    selected_class = request.form.get('class_grade', '') if request.method == 'POST' else ''
    students = []
    
    if selected_class:
        if selected_class not in ALLOWED_CLASSES:
            flash('Invalid class selected', 'danger')
            return redirect(url_for('teacher_search'))
        
        # Get all students in the selected class
        students = Student.query.filter_by(class_grade=selected_class).all()
        
        # Attach mark data for the teacher's subject
        for student in students:
            mark = Mark.query.filter_by(student_id=student.id, subject=current_user.assigned_subject).first()
            student.mark = mark  # attach mark object to student for template
    
    return render_template('teacher_search.html', classes=ALLOWED_CLASSES, selected_class=selected_class, students=students, subject=current_user.assigned_subject)

@app.route('/teacher/update/<int:mark_id>', methods=['GET','POST'])
@login_required
def teacher_update_mark(mark_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    mark = Mark.query.get_or_404(mark_id)
    if mark.subject != current_user.assigned_subject:
        flash('You may only edit your assigned subject marks', 'danger')
        return redirect(url_for('teacher_dashboard'))
    if request.method == 'POST':
        mark.first_term = float(request.form.get('first_term') or 0)
        mark.second_term = float(request.form.get('second_term') or 0)
        mark.board_mark = float(request.form.get('board_mark') or 0)
        db.session.commit()
        flash('Mark updated', 'success')
        return redirect(url_for('teacher_dashboard'))
    return render_template('add_mark.html', action='update_mark', mark=mark)

@app.route('/teacher/add_mark', methods=['GET', 'POST'])
@login_required
def teacher_add_mark():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    if not current_user.approved:
        flash('Your account is not yet approved by admin', 'danger')
        return redirect(url_for('teacher_dashboard'))
    if request.method == 'POST':
        roll = request.form['roll_number']
        student = Student.query.filter_by(roll_number=roll).first()
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('teacher_add_mark'))
        # Check if mark already exists for this student and subject
        existing = Mark.query.filter_by(student_id=student.id, subject=current_user.assigned_subject).first()
        if existing:
            flash('Marks already exist for this student in this subject. Edit instead.', 'warning')
            return redirect(url_for('teacher_add_mark'))
        first = float(request.form.get('first_term') or 0)
        second = float(request.form.get('second_term') or 0)
        board = float(request.form.get('board_mark') or 0)
        # Validate at least one mark is provided
        if first == 0 and second == 0 and board == 0:
            flash('Please fill at least one term mark', 'warning')
            return redirect(url_for('teacher_add_mark'))
        mark = Mark(student_id=student.id, subject=current_user.assigned_subject, 
                   first_term=first, second_term=second, board_mark=board, class_grade=student.class_grade)
        db.session.add(mark)
        db.session.commit()
        flash('Mark added successfully', 'success')
        return redirect(url_for('teacher_dashboard'))
    students = Student.query.all()
    return render_template('teacher_add_mark.html', students=students)

@app.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    student = Student.query.filter_by(user_id=current_user.id).first()
    marks = Mark.query.filter_by(student_id=student.id).all() if student else []
    # arrange marks into three boxes (1st, 2nd, board)
    return render_template('student_dashboard.html', marks=marks, student=student)

@app.route('/search', methods=['GET','POST'])
@login_required
def search():
    query = request.form.get('query') if request.method == 'POST' else request.args.get('q')
    students = []
    if query:
        students = Student.query.filter((Student.name.contains(query)) | (Student.roll_number.contains(query))).all()
    return render_template('search.html', students=students, query=query)

@app.route('/admin/class_results', methods=['GET','POST'])
@login_required
def class_results():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    selected_class = request.form.get('class_grade', '') if request.method == 'POST' else ''
    results = []
    subjects = []

    # get subjects for the selected class
    if selected_class:
        subjects = list(SUBJECT_FULL_MARKS.get(selected_class, {}).keys())
        students = Student.query.filter_by(class_grade=selected_class).all()

        # If admin submitted marks via the grid, process them
        if request.method == 'POST' and request.form.get('action') == 'save_marks':
            # iterate students and subjects, inputs named m-<studentid>-<subject>-<part>
            for student in students:
                for subj in subjects:
                    key_f = f'm-{student.id}-{subj}-first'
                    key_s = f'm-{student.id}-{subj}-second'
                    key_b = f'm-{student.id}-{subj}-board'
                    val_f = request.form.get(key_f, '').strip()
                    val_s = request.form.get(key_s, '').strip()
                    val_b = request.form.get(key_b, '').strip()
                    if val_f=='' and val_s=='' and val_b=='':
                        # no entry provided — skip (do not create a mark)
                        continue
                    # parse floats (empty -> 0.0)
                    try:
                        f_val = float(val_f) if val_f!='' else 0.0
                    except ValueError:
                        f_val = 0.0
                    try:
                        s_val = float(val_s) if val_s!='' else 0.0
                    except ValueError:
                        s_val = 0.0
                    try:
                        b_val = float(val_b) if val_b!='' else 0.0
                    except ValueError:
                        b_val = 0.0

                    # find existing mark or create
                    mark = Mark.query.filter_by(student_id=student.id, subject=subj).first()
                    if not mark:
                        mark = Mark(student_id=student.id, subject=subj, class_grade=selected_class)
                        db.session.add(mark)
                    mark.first_term = f_val
                    mark.second_term = s_val
                    mark.board_mark = b_val
            db.session.commit()
            flash('Marks saved successfully', 'success')

        # prepare results data including totals and percentages
        for student in students:
            marks = {m.subject: m for m in Mark.query.filter_by(student_id=student.id).all()}
            student_data = {
                'id': student.id,
                'roll': student.roll_number,
                'name': student.name,
                'house': student.house_name or '—',
                'marks_by_subject': {},
                'obtained_total': 0.0,
                'possible_total': 0.0,
                'percentage': 0.0,
                # per-term totals
                'first_term_obtained': 0.0,
                'first_term_total': 0.0,
                'first_term_percent': 0.0,
                'second_term_obtained': 0.0,
                'second_term_total': 0.0,
                'second_term_percent': 0.0,
                'board_obtained': 0.0,
                'board_total': 0.0,
                'board_percent': 0.0
            }
            for subj in subjects:
                mark = marks.get(subj)
                if not mark:
                    # no entry for this subject — skip including it in totals
                    student_data['marks_by_subject'][subj] = None
                    continue
                obtained = (mark.first_term or 0.0) + (mark.second_term or 0.0) + (mark.board_mark or 0.0)
                full = SUBJECT_FULL_MARKS.get(selected_class, {}).get(subj, 0)
                student_data['marks_by_subject'][subj] = {
                    'first_term': mark.first_term,
                    'second_term': mark.second_term,
                    'board': mark.board_mark,
                    'obtained': obtained,
                    'full': full,
                    'percent': (obtained / full * 100) if full>0 else 0
                }
                # include in overall totals
                student_data['obtained_total'] += obtained
                student_data['possible_total'] += full
                
                # per-term totals
                student_data['first_term_obtained'] += (mark.first_term or 0.0)
                student_data['first_term_total'] += full
                student_data['second_term_obtained'] += (mark.second_term or 0.0)
                student_data['second_term_total'] += full
                student_data['board_obtained'] += (mark.board_mark or 0.0)
                student_data['board_total'] += full
            
            # compute overall percentage (based only on included subjects)
            if student_data['possible_total'] > 0:
                student_data['percentage'] = (student_data['obtained_total'] / student_data['possible_total']) * 100
            
            # compute per-term percentages
            if student_data['first_term_total'] > 0:
                student_data['first_term_percent'] = (student_data['first_term_obtained'] / student_data['first_term_total']) * 100
            if student_data['second_term_total'] > 0:
                student_data['second_term_percent'] = (student_data['second_term_obtained'] / student_data['second_term_total']) * 100
            if student_data['board_total'] > 0:
                student_data['board_percent'] = (student_data['board_obtained'] / student_data['board_total']) * 100
            
            results.append(student_data)

    return render_template('class_results.html', classes=ALLOWED_CLASSES, selected_class=selected_class, results=results, subjects=subjects)

@app.route('/admin/upload_students', methods=['GET', 'POST'])
@login_required
def upload_students():
    """Bulk upload students from CSV/Excel file (roll_number, name, house_name, class_grade)"""
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_students'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_students'))
        
        # Check file extension
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_UPLOAD_EXTENSIONS):
            flash('Invalid file type. Use CSV or XLSX', 'danger')
            return redirect(url_for('upload_students'))
        
        try:
            # Parse file based on extension
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:  # xlsx or xls
                df = pd.read_excel(file)
            
            # Expected columns: roll_number, name, house_name, class_grade
            required_cols = ['roll_number', 'name', 'house_name', 'class_grade']
            if not all(col in df.columns for col in required_cols):
                flash(f'File must contain columns: {", ".join(required_cols)}', 'danger')
                return redirect(url_for('upload_students'))
            
            success_count = 0
            error_msgs = []
            
            for idx, row in df.iterrows():
                roll = str(row['roll_number']).strip()
                name = str(row['name']).strip()
                house = str(row['house_name']).strip() if pd.notna(row['house_name']) else ''
                class_grade = str(row['class_grade']).strip()
                
                # Validate
                if not roll or not name or class_grade not in ALLOWED_CLASSES:
                    error_msgs.append(f"Row {idx+2}: Invalid data (missing roll/name or invalid class)")
                    continue
                
                # Check if student or username already exists
                if Student.query.filter_by(roll_number=roll).first():
                    error_msgs.append(f"Row {idx+2}: Roll number '{roll}' already exists")
                    continue
                
                if User.query.filter_by(username=roll).first():
                    error_msgs.append(f"Row {idx+2}: Username '{roll}' already exists")
                    continue
                
                try:
                    # Create user with roll_number as username and password
                    user = User(username=roll, role='student', approved=True)
                    user.set_password(roll)  # password = roll_number
                    db.session.add(user)
                    db.session.flush()  # flush to get user.id
                    
                    # Create student profile
                    student = Student(user_id=user.id, roll_number=roll, name=name, 
                                     class_grade=class_grade, house_name=house)
                    db.session.add(student)
                    success_count += 1
                except Exception as e:
                    error_msgs.append(f"Row {idx+2}: Error creating student - {str(e)}")
            
            db.session.commit()
            
            if success_count > 0:
                flash(f'✓ Successfully registered {success_count} student(s)', 'success')
            if error_msgs:
                for msg in error_msgs[:10]:  # show first 10 errors
                    flash(msg, 'warning')
                if len(error_msgs) > 10:
                    flash(f'... and {len(error_msgs)-10} more errors', 'warning')
            
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(url_for('upload_students'))
    
    return render_template('upload_students.html')

@app.route('/admin/upload_results', methods=['GET', 'POST'])
@login_required
def upload_results():
    """Bulk upload marks from CSV/Excel file (roll_number, subject, mark for selected result_type)"""
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('portal'))
    
    if request.method == 'POST':
        class_grade = request.form.get('class_grade', '').strip()
        result_type = request.form.get('result_type', '').strip()  # 1st, 2nd, or board
        
        if class_grade not in ALLOWED_CLASSES:
            flash('Invalid class selected', 'danger')
            return redirect(url_for('upload_results'))
        
        if result_type not in ['1st', '2nd', 'board']:
            flash('Invalid result type. Choose 1st, 2nd, or board', 'danger')
            return redirect(url_for('upload_results'))
        
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_results'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_results'))
        
        # Check file extension
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_UPLOAD_EXTENSIONS):
            flash('Invalid file type. Use CSV or XLSX', 'danger')
            return redirect(url_for('upload_results'))
        
        try:
            # Parse file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:  # xlsx or xls
                df = pd.read_excel(file)
            
            # Expected columns: roll_number, subject, mark
            required_cols = ['roll_number', 'subject', 'mark']
            if not all(col in df.columns for col in required_cols):
                flash(f'File must contain columns: {", ".join(required_cols)}', 'danger')
                return redirect(url_for('upload_results'))
            
            success_count = 0
            error_msgs = []
            
            # Map result_type to Mark column names
            mark_column = 'first_term' if result_type == '1st' else ('second_term' if result_type == '2nd' else 'board_mark')
            
            for idx, row in df.iterrows():
                roll = str(row['roll_number']).strip()
                subject = str(row['subject']).strip()
                mark_value = row['mark']
                
                # Validate mark is numeric
                try:
                    mark_val = float(mark_value)
                except (ValueError, TypeError):
                    error_msgs.append(f"Row {idx+2}: Invalid mark value '{mark_value}'")
                    continue
                
                # Find student
                student = Student.query.filter_by(roll_number=roll, class_grade=class_grade).first()
                if not student:
                    error_msgs.append(f"Row {idx+2}: Student with roll '{roll}' not found in class {class_grade}")
                    continue
                
                # Validate subject is in SUBJECT_FULL_MARKS for this class
                if subject not in SUBJECT_FULL_MARKS.get(class_grade, {}):
                    error_msgs.append(f"Row {idx+2}: Subject '{subject}' not valid for class {class_grade}")
                    continue
                
                # Validate mark doesn't exceed full marks
                full_mark = SUBJECT_FULL_MARKS[class_grade][subject]
                if mark_val > full_mark:
                    error_msgs.append(f"Row {idx+2}: Mark {mark_val} exceeds full mark {full_mark} for {subject}")
                    continue
                
                try:
                    # Find existing mark or create
                    mark = Mark.query.filter_by(student_id=student.id, subject=subject).first()
                    if not mark:
                        mark = Mark(student_id=student.id, subject=subject, class_grade=class_grade)
                        db.session.add(mark)
                    
                    # Update the specific result type column
                    setattr(mark, mark_column, mark_val)
                    success_count += 1
                except Exception as e:
                    error_msgs.append(f"Row {idx+2}: Error saving mark - {str(e)}")
            
            db.session.commit()
            
            if success_count > 0:
                flash(f'✓ Successfully imported {success_count} mark(s) for {result_type} term', 'success')
            if error_msgs:
                for msg in error_msgs[:10]:  # show first 10 errors
                    flash(msg, 'warning')
                if len(error_msgs) > 10:
                    flash(f'... and {len(error_msgs)-10} more errors', 'warning')
            
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(url_for('upload_results'))
    
    return render_template('upload_results.html', classes=ALLOWED_CLASSES)

if __name__ == '__main__':
    # initialize DB and seed admin before starting server
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
