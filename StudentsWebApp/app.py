from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask import jsonify
import wikipedia
from transformers import pipeline
import re
import enum
import random
from dateutil.parser import parse
import math
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("STARTUP: Flask application initialization begins...")

app = Flask(__name__)
logger.info("STARTUP: Flask app object created.")

default_db_uri = 'postgresql://user:password@localhost/default_db' # Updated fallback URI
database_url = os.environ.get('DATABASE_URL')

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    try:
        uri_parts = database_url.split('://')
        scheme = uri_parts[0]
        rest = uri_parts[1]
        username_part = rest.split('@')[0].split(':')[0]
        host_part = rest.split('@')[1].split('/')[0] if '@' in rest and '/' in rest.split('@')[1] else "details_unavailable"
        app.logger.info(f"Using DATABASE_URL from environment. Scheme: {scheme}, User: {username_part}, Host: {host_part}")
    except Exception:
        app.logger.info("Using DATABASE_URL from environment (details redacted).")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = default_db_uri
    app.logger.info("Using default local MySQL database.")

logger.info(f"STARTUP: SQLALCHEMY_DATABASE_URI is configured to: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
gpt_pipeline = None
logger.info("STARTUP: AI model loading initiated (google/flan-t5-small)...")
model_load_start_time = time.time()
# try:
#     gpt_pipeline = pipeline("text2text-generation", model="google/flan-t5-small")
#     model_load_duration = time.time() - model_load_start_time
#     logger.info(f"STARTUP: AI model loaded successfully in {model_load_duration:.2f} seconds.")
#     app.logger.info("Successfully loaded Flan T5 model for AI assistant.") # Original app log
# except Exception as e:
#     model_load_duration = time.time() - model_load_start_time
#     logger.error(f"STARTUP: AI model loading failed after {model_load_duration:.2f} seconds. Error: {e}", exc_info=True)
#     gpt_pipeline = None # Ensure it's None if loading failed
#     # Original app logs for failure are already here, which is fine.
#     app.logger.error(f"Failed to load Flan T5 model for AI assistant: {e}", exc_info=True)
#     app.logger.warning("AI assistant features will be limited or unavailable.")

def dummy_text_generator(*args, **kwargs):
    # Simulate the structure of the pipeline output or return a message
    logger.warning("AI MODEL STUB: Using dummy text generator. AI features will not work.")
    # Example: if pipeline returns a list of dicts like [{'generated_text': '...'}]
    # This handles both single string input and list of strings input to the pipeline
    input_text = args[0] if args else ""
    if isinstance(input_text, list):
        return [{"generated_text": "AI model is currently disabled due to resource constraints."}] * len(input_text)
    return [{"generated_text": "AI model is currently disabled due to resource constraints."}]

gpt_pipeline = dummy_text_generator
logger.info("STARTUP: Using STUBBED (dummy) AI model to save memory.")

app.secret_key = os.environ.get('SECRET_KEY', 'dev_fallback_key_123!@#_do_not_use_in_prod')
if app.secret_key == 'dev_fallback_key_123!@#_do_not_use_in_prod':
    print("WARNING: Using fallback SECRET_KEY. Set a strong SECRET_KEY environment variable for production.")
    app.logger.warning("Using fallback SECRET_KEY. Set a strong SECRET_KEY environment variable for production.")

csrf = CSRFProtect(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
logger.info("STARTUP: SQLAlchemy object 'db' initialized.") # Adding this one back

COURSES = {
    "Cyber Security": "CYB", "Data Science": "DAT", "PowerBI": "POW",
    "Marketing Analytics": "MAR", "Sales Analytics": "SAL", "Supply Chain Analytics": "SUP",
    "HR Analytics": "HRA", "Finance Analytics": "FIN", "Banking Analytics": "BNK",
    "Coding for Kids": "KID", "Excel": "EXC", "Data Law and Governance": "LAW",
    "Long Program (with modules)": "LNG", "Telkom Analytics": "TEL",
    "Data Journalism": "JRN", "Robotics and Automation": "ROB", "Location Intelligence and GIS": "GIS"
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    course = db.Column(db.String(100))
    cohort = db.Column(db.String(10))
    fee_expected = db.Column(db.Float, default=0.0)
    fee_paid = db.Column(db.Float, default=0.0)
    next_class = db.Column(db.DateTime)
    graduation_status = db.Column(db.String(100))
    completion_date = db.Column(db.Date)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def fee_balance(self):
        return self.fee_expected - self.fee_paid

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent'), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    type = db.Column(db.String(50))
    link = db.Column(db.String(200))
    course = db.Column(db.String(100))
    cohort = db.Column(db.String(10))


class RoleEnum(enum.Enum):
    GRADUATE = 'graduate'
    GUEST = 'guest'
class GraduationRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(RoleEnum, name="role_enum"), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

class GraduationInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    graduation_date = db.Column(db.Date)
    media_title = db.Column(db.String(100))
    media_link = db.Column(db.String(200))

logger.info("STARTUP: Module-level database operations (db.create_all(), default admin) initiated...")
db_ops_start_time = time.time()
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(email='timoriedo@gmail.com').first():
        default_admin = Admin(email='timoriedo@gmail.com')
        default_admin.set_password('12345')
        db.session.add(default_admin)
        db.session.commit()
db_ops_duration = time.time() - db_ops_start_time
logger.info(f"STARTUP: Module-level database operations completed in {db_ops_duration:.2f} seconds.")

def generate_admission_number(course, cohort):
    prefix = COURSES.get(course, "XXX")
    count = User.query.filter_by(course=course, cohort=cohort).count()
    return f"{prefix}{cohort}-{str(count + 1).zfill(3)}"

def calculate_attendance_stats(student):
    records = student.attendance_records
    total = len(records)
    present = sum(1 for r in records if r.status == 'Present')
    absent = total - present
    percent = round((present / total) * 100, 1) if total else 0
    return total, present, absent, percent

def format_date(date_str, input_format="%Y-%m-%d", output_format="%A, %d %B %Y"):
    try:
        if not isinstance(date_str, str):
            raise TypeError(f"Input date_str must be a string, got {type(date_str)} with value {date_str}")
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError) as e:
        app.logger.warning(
            f"Failed to format date string '{date_str}' with input format '{input_format}'. Error: {e}. Returning original string.",
            exc_info=True
        )
        return date_str

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            session['user'] = user.email
            return redirect(url_for('dashboard'))
        error = "Invalid email or password"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(email=session['user']).first()
    return render_template('dashboard.html', user=user)

@app.route('/attendance')
def attendance():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(email=session['user']).first()
    records = Attendance.query.filter_by(student_id=user.id).order_by(Attendance.date.desc()).all()
    total = len(records)
    absent = sum(1 for r in records if r.status == 'Absent')
    attendance_percent = round((absent / total) * 100, 1) if total > 0 else 0
    return render_template(
        'attendance.html',
        user=user,
        records=records,
        absent_count=absent,
        total_count=total,
        attendance_percent=attendance_percent
    )

@app.route('/resources')
def student_resources():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(email=session['user']).first()
    resources = Resource.query.filter_by(course=user.course, cohort=user.cohort).all()
    return render_template('resources.html', user=user, resources=resources)

@app.route('/graduation', methods=['GET', 'POST'])
def student_graduation():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(email=session['user']).first()
    if request.method == 'POST':
        role = request.form['role']
        full_name = request.form['name']
        existing = GraduationRegistration.query.filter_by(student_email=user.email).first()
        if not existing:
            reg = GraduationRegistration(student_email=user.email, full_name=full_name, role=role)
            db.session.add(reg)
            if role == 'graduate':
                user.graduation_status = 'Registered'
            db.session.commit()
            flash("Registered successfully.")
        else:
            flash("You've already registered.")
    latest_date = db.session.query(GraduationInfo).filter(GraduationInfo.graduation_date != None)                       .order_by(GraduationInfo.graduation_date.desc()).first()
    media_links = GraduationInfo.query.filter(GraduationInfo.media_link != None).all()
    return render_template(
        'graduation.html',
        user=user,
        upcoming_graduation_date=latest_date.graduation_date.strftime('%d %B, %Y') if latest_date else None,
        graduation_media=media_links
    )

@app.route('/admin/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(email=request.form['email']).first()
        if admin and admin.check_password(request.form['password']):
            session['admin'] = admin.email
            return redirect(url_for('admin_dashboard'))
        flash("Invalid credentials")
    return render_template('Admin-Section/admin-login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    students = User.query.count()
    grads = User.query.filter_by(graduation_status='Registered').count()
    attendance_records = Attendance.query.all() # Renamed for clarity
    present = sum(1 for r in attendance_records if r.status == 'Present')
    avg_attendance = round((present / len(attendance_records)) * 100, 1) if attendance_records else 0
    return render_template('Admin-Section/dashboard.html', total_students=students,
                           graduation_count=grads, avg_attendance=avg_attendance,
                           resource_count=Resource.query.count())

def paginate_items(items, page, per_page):
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages

@app.route('/admin/students', methods=['GET', 'POST'])
def manage_students():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        course = request.form['course']
        cohort = request.form['cohort']
        admission_number = generate_admission_number(course, cohort)
        student = User(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            course=course,
            cohort=cohort,
            admission_number=admission_number,
            fee_expected=float(request.form.get('fee_expected', 0)),
            fee_paid=float(request.form.get('fee_paid', 0)),
            graduation_status=request.form['graduation_status']
        )
        student.set_password(request.form['password'])
        db.session.add(student)
        db.session.commit()
        flash(f"Student {student.name} added successfully.")
        return redirect(url_for('manage_students'))
    page = int(request.args.get('page', 1))
    per_page = 5
    all_students = User.query.order_by(User.name).all()
    students, total_pages = paginate_items(all_students, page, per_page)
    return render_template(
        'Admin-Section/manage-students.html',
        students=students,
        courses=COURSES,
        total_pages=total_pages,
        current_page=page
    )

@app.route('/admin/resources', methods=['GET', 'POST'])
def manage_resources():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        res = Resource(title=request.form['title'], type=request.form['type'],
                       link=request.form['link'], course=request.form['course'],
                       cohort=request.form['cohort'])
        db.session.add(res)
        db.session.commit()
        flash("Resource added successfully.")
        return redirect(url_for('manage_resources'))
    return render_template('Admin-Section/manage-resources.html', resources=Resource.query.all(), courses=COURSES)

@app.route('/admin/resource/delete/<int:id>', methods=['POST'])
def delete_resource(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    res = Resource.query.get_or_404(id)
    db.session.delete(res)
    db.session.commit()
    flash('Resource deleted successfully.')
    return redirect(url_for('manage_resources'))

@app.route('/admin/attendance', methods=['GET', 'POST'])
def admin_attendance():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    course_selected = request.args.get('course')
    cohort_selected = request.args.get('cohort')
    students_for_filter = [] # Renamed from students
    if course_selected and cohort_selected:
        students_for_filter = User.query.filter_by(course=course_selected, cohort=cohort_selected).all()
    elif course_selected:
        students_for_filter = User.query.filter_by(course=course_selected).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        if not student_id:
            flash("Please select a student.")
            return redirect(url_for('admin_attendance', course=course_selected, cohort=cohort_selected))
        student_id = int(student_id)
        date_str = request.form.get('date')
        if not date_str:
            flash("Date is required.")
            return redirect(url_for('admin_attendance', course=course_selected, cohort=cohort_selected))
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date() # Use .date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for('admin_attendance', course=course_selected, cohort=cohort_selected))
        status = request.form['status']
        next_class_str = request.form.get('next_class')
        existing_attendance = Attendance.query.filter_by(student_id=student_id, date=date_obj).first()
        if existing_attendance:
            existing_attendance.status = status
            flash_message = "Attendance record updated."
        else:
            new_attendance = Attendance(student_id=student_id, date=date_obj, status=status) # Renamed
            db.session.add(new_attendance)
            flash_message = "Attendance record added."
        if next_class_str:
            try:
                next_class_dt = datetime.strptime(next_class_str, "%Y-%m-%dT%H:%M") # Renamed
                student_to_update = User.query.get(student_id) # Renamed
                if student_to_update:
                    student_to_update.next_class = next_class_dt
            except ValueError:
                flash("Invalid next class date format. Not updated.")
        db.session.commit()
        flash(flash_message)
        return redirect(url_for('admin_attendance', course=course_selected, cohort=cohort_selected))

    current_attendance_records = Attendance.query.order_by(Attendance.date.desc()).limit(20).all() # Renamed
    all_distinct_cohorts = [c[0] for c in db.session.query(User.cohort).distinct().all() if c[0]] # Renamed
    all_students_for_dropdown = User.query.order_by(User.name).all()
    return render_template(
        'Admin-Section/attendance-management.html',
        courses=COURSES,
        cohorts=all_distinct_cohorts,
        students_for_dropdown=all_students_for_dropdown,
        filtered_students=students_for_filter,
        attendance_records=current_attendance_records,
        selected_course=course_selected,
        selected_cohort=cohort_selected
    )

@app.route('/admin/student/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    student = User.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.course = request.form['course']
        student.cohort = request.form['cohort']
        student.phone = request.form['phone']
        if request.form.get('password'):
            student.set_password(request.form['password'])
        student.fee_expected = float(request.form.get('fee_expected', 0))
        student.fee_paid = float(request.form.get('fee_paid', 0))
        student.graduation_status = request.form['graduation_status']
        if request.form.get('completion_date'):
            try:
                student.completion_date = datetime.strptime(request.form['completion_date'], "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid completion date format. Not updated.")
        db.session.commit()
        flash(f"Student {student.name} updated successfully.")
        return redirect(url_for('manage_students'))
    return render_template('Admin-Section/edit-student.html', student=student, courses=COURSES)

@app.route('/admin/student/delete/<int:id>', methods=['POST'])
def delete_student(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    student = User.query.get_or_404(id)
    Attendance.query.filter_by(student_id=id).delete()
    db.session.delete(student)
    db.session.commit()
    flash(f"Student {student.name} and their attendance records deleted successfully.")
    return redirect(url_for('manage_students'))

@app.route('/admin/graduation', methods=['GET', 'POST'])
def manage_graduation():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        if 'student_id' in request.form:
            student = User.query.get_or_404(request.form['student_id'])
            student.graduation_status = 'Graduated'
            if not student.completion_date:
                student.completion_date = datetime.utcnow().date()
            db.session.commit()
            flash(f"{student.name} marked as Graduated.")
        else:
            date_str = request.form.get('graduation_date')
            title = request.form.get('media_title')
            link = request.form.get('media_link')
            new_info_added = False
            if date_str:
                try:
                    grad_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if not GraduationInfo.query.filter_by(graduation_date=grad_date).first():
                        db.session.add(GraduationInfo(graduation_date=grad_date))
                        new_info_added = True
                except ValueError:
                    flash("Invalid graduation date format.")
            if title and link:
                if not GraduationInfo.query.filter_by(media_link=link).first():
                    db.session.add(GraduationInfo(media_title=title, media_link=link))
                    new_info_added = True
            if new_info_added:
                db.session.commit()
                flash("Graduation details updated.")
            elif not date_str and not (title and link):
                 flash("No new information provided to update.")
            else:
                flash("Information might already exist or was not added.")
    students_eligible = User.query.filter(User.graduation_status != 'Graduated').all()
    grad_info_events = GraduationInfo.query.filter(GraduationInfo.graduation_date != None).order_by(GraduationInfo.graduation_date.desc()).all()
    grad_info_media = GraduationInfo.query.filter(GraduationInfo.media_link != None).order_by(GraduationInfo.id.desc()).all()
    return render_template(
        'Admin-Section/manage-graduation.html',
        students=students_eligible,
        graduation_events=grad_info_events,
        graduation_media=grad_info_media
    )

@app.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    if 'user' not in session:
        return jsonify({'reply': '🔒 Please log in to use the assistant.', 'status': 'error'})
    user = User.query.filter_by(email=session['user']).first()
    data = request.get_json()
    prompt = data.get('message', '').strip().lower()
    attachments = data.get('attachments', [])
    question_patterns = {
        "resources": [
            r" (resources?|materials?|files?|documents?|readings?|slides?) ",
            r" where (can I find|are|to get).*(resources?|materials?|files?)",
            r" (course|class|module).*(materials?|resources?|documents?)",
            r" upload|download|access.*(materials?|resources?)"
        ],
        "fee": [
            r" (fees?|payments?|balance|tuition|outstanding|amount due) ",
            r" how much (do I owe|is remaining|to pay) ",
            r" (my|current) (fee|payment) (status|balance|information) ",
            r" check (my)? payment(s)? "
        ],
        "attendance": [
            r" attendance ", r" absent ", r" present ", r" missed\s*class ",
            r" was\s*I\s*in\s*class ", r" show\s*attendance ", r" how\s*often ",
            r" attendance\s*record ", r" my\s*attendance ", r" class\s*attendance "
        ],
        "next_class": [
            r" next\s*class ", r" when\s*is\s*class ", r" schedule ",
            r" upcoming\s*class ", r" next\s*lesson ", r" class\s*time ",
            r" when\s*do\s*we\s*meet ", r" next\s*session ", r" when's\s*the\s*next\s*class "
        ],
        "graduation": [
            r" graduation ", r" graduate ", r" register\s*for\s*graduation ",
            r" when\s*is\s*graduation ", r" how\s*to\s*graduate ", r" graduating ",
            r" ceremony ", r" when\s*do\s*I\s*graduate ", r" completion "
        ],
        "summary": [
            r" tell\s*me\s*about ", r" summary\s*of ", r" explain ",
            r" what\s*is ", r" brief\s*on ", r" who\s*is ",
            r" define ", r" describe ", r" what\s*are ", r" how\s*does "
        ],
        "summarize": [
            r" summar(y|ize|ise) ",
            r" (shorten|condense|brief) ",
            r" main points? ",
            r" key ideas? ",
            r" can you (make|give).*shorter "
        ],
        "greeting": [
            r" hello ", r" hi ", r" hey ", r" greetings ",
            r" good\s*(morning|afternoon|evening) ", r" what's\s*up "
        ],
        "help": [
            r" help ", r" what\s*can\s*you\s*do ", r" assist ",
            r" support ", r" options ", r" how\s*to\s*use "
        ],
        "personal_info": [
            r" my\s*info ", r" my\s*details ", r" student\s*information ",
            r" my\s*profile ", r" about\s*me ", r" who\s*am\s*I "
        ],
        "course_info": [
            r" course\s*details ", r" about\s*my\s*course ",
            r" what's\s*my\s*course ", r" program\s*info "
        ]
    }

    def preprocess_text(text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_sentences(text):
        return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)

    def summarize_local(text, ratio=0.3):
        sentences = extract_sentences(preprocess_text(text))
        if len(sentences) <= 3: return text
        scored = []
        important_keywords = ['important', 'key', 'summary', 'conclusion', 'essential', 'main']
        for i, sent in enumerate(sentences):
            score = 0
            if i < 3 or i > len(sentences)-3: score += 2
            score += min(len(sent.split()) * 0.1, 3)
            if any(word in sent.lower() for word in important_keywords): score += 3
            if '?' in sent: score += 1
            if re.search(r'\d', sent): score += 1.5
            scored.append((score, sent))
        scored.sort(reverse=True, key=lambda x: x[0])
        keep = max(2, int(len(sentences) * ratio))
        top_sentences = [s for _, s in scored[:keep]]
        summary_ordered = [s for s in sentences if s in top_sentences] # Maintain original order
        return ' '.join(summary_ordered)

    def handle_summarization(prompt_text, attachments_list): # Renamed attachments
        if ':' in prompt_text:
            parts = prompt_text.split(':', 1)
            if len(parts) > 1 and len(parts[1].strip().split()) > 5:
                return summarize_local(parts[1].strip())
        for att in attachments_list:
            if att.get('type') == 'text' and att.get('content') and len(att.get('content', '').split()) > 5:
                return summarize_local(att['content'])
        if data.get('previous_message') and len(data['previous_message'].split()) > 10:
            return summarize_local(data['previous_message'])
        return None

    def detect_intent(user_prompt): # Added detect_intent locally
        for intent_name, patterns_list in question_patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, user_prompt, re.IGNORECASE):
                    return intent_name
        return None

    intent = detect_intent(prompt)
    response_text = "I'm not sure how to help with that. Can you try rephrasing?" # Renamed

    if intent == "summarize":
        summary_text = handle_summarization(prompt, attachments) # Renamed
        if summary_text:
            response_text = f"📝 Here's a summary:\n\n{summary_text}"
            if ':' in prompt and len(summary_text.split()) < len(prompt.split(':')[-1].strip().split()):
                 response_text += f"\n\n(Reduced to {len(summary_text.split())} words)"
        else:
            response_text = ("Please provide the text you'd like summarized, either by:\n"
                             "1. Typing 'summarize: [your text]'\n"
                             "2. Attaching a text file with your text\n"
                             "3. Or, if you just sent a long message, ask me to 'summarize that'.")
    elif intent == "greeting":
        greeting_msg = get_greeting() # Renamed
        user_first_name = user.name.split()[0] if user.name else "Student" # Renamed
        response_text = random.choice([
            f"{greeting_msg}, {user_first_name}! How can I assist you today?",
            f"{greeting_msg}, {user_first_name}! What can I help you with?",
            f"{greeting_msg} {user_first_name}! Ask me anything about your studies."
        ])
    elif intent == "help":
        response_text = ("📚 I'm your student portal assistant. I can help with:\n\n"
                         "- Course resources and materials\n- Fee balances and payments\n"
                         "- Attendance records\n- Class schedules\n- Graduation information\n"
                         "- Summarizing your notes/text (type 'summarize: your text here')\n"
                         "- General knowledge questions (e.g., 'tell me about Python')\n\n"
                         "Try asking:\n- 'Show my attendance record'\n- 'What's my fee balance?'\n"
                         "- 'When is my next class?'")
    elif intent == "personal_info":
        response_text = (f"👤 Your Information:\n\nName: {user.name}\nAdmission: {user.admission_number}\n"
                         f"Course: {user.course}\nCohort: {user.cohort}\nStatus: {user.graduation_status or 'Active'}")
    elif intent == "resources":
        user_resources = Resource.query.filter_by(course=user.course, cohort=user.cohort).all() # Renamed
        if user_resources:
            response_text = f"📂 You have {len(user_resources)} resources for {user.course} ({user.cohort}):\n\n"
            for i, r_item in enumerate(user_resources[:5], 1): # Renamed r
                response_text += f"{i}. {r_item.title} ({r_item.type}) - <a href='{r_item.link}' target='_blank'>Open</a>\n"
            if len(user_resources) > 5:
                response_text += f"\nView all {len(user_resources)} on the Resources page."
        else:
            response_text = f"No specific resources found for your course ({user.course}, {user.cohort}) yet. Check the general resources or ask your instructor."
    elif intent == "fee":
        if user.fee_balance <= 0:
            response_text = f"✅ Your fees are fully paid! (Expected: KES {user.fee_expected:,.2f}, Paid: KES {user.fee_paid:,.2f})"
        else:
            response_text = (f"💳 Fee Balance:\n\nExpected: KES {user.fee_expected:,.2f}\nPaid: KES {user.fee_paid:,.2f}\n"
                             f"**Remaining: KES {user.fee_balance:,.2f}**")
    elif intent == "attendance":
        total_records, present_records, absent_records, percent_present = calculate_attendance_stats(user) # Renamed
        if total_records == 0:
            response_text = "No attendance records found yet for your account."
        else:
            response_text = (f"📊 Attendance for {user.name}:\n\nPresent: {present_records}/{total_records} ({percent_present}%)\n"
                             f"Absent: {absent_records}\n\n"
                             f"{'👍 Excellent attendance!' if percent_present >= 90 else ('✅ Good job, keep it up!' if percent_present >=75 else '⚠️ Try to attend more classes to meet requirements.')}")
    elif intent == "next_class":
        if user.next_class:
            now = datetime.now()
            delta_time = user.next_class - now # Renamed
            class_status_msg = "" # Renamed
            if user.next_class < now:
                 class_status_msg = f"This class was on {user.next_class.strftime('%A, %d %B %Y at %I:%M %p')}. Hope you attended!"
            elif delta_time.days == 0 and now.day == user.next_class.day:
                class_status_msg = f"Today, {user.next_class.strftime('%I:%M %p')}!"
            elif delta_time.days == 1 and now.day != user.next_class.day:
                 class_status_msg = f"Tomorrow, {user.next_class.strftime('%I:%M %p')}."
            else:
                class_status_msg = f"In {delta_time.days +1} day{'s' if delta_time.days > 0 else ''} on {user.next_class.strftime('%A, %d %B')}"
            response_text = (f"📅 Next Class for {user.course}:\n\nDate: {user.next_class.strftime('%A, %d %B %Y')}\n"
                             f"Time: {user.next_class.strftime('%I:%M %p')}\nStatus: {class_status_msg}")
        else:
            response_text = "Your next class schedule hasn't been updated yet. Please check back later or contact administration."
    elif intent == "graduation":
        grad_reg = GraduationRegistration.query.filter_by(student_email=user.email).first() # Renamed
        latest_grad_event_info = GraduationInfo.query.filter(GraduationInfo.graduation_date != None).order_by(GraduationInfo.graduation_date.desc()).first() # Renamed
        response_text = f"🎓 Graduation Status for {user.name}:\nOverall Status: {user.graduation_status or 'Not yet specified'}\n"
        response_text += f"Registered for an event: {'Yes (as ' + grad_reg.role + ')' if grad_reg else 'No'}\n"
        if latest_grad_event_info and latest_grad_event_info.graduation_date:
             response_text += f"The next general graduation event is on: {latest_grad_event_info.graduation_date.strftime('%d %B, %Y')}.\n"
        else:
            response_text += "No upcoming general graduation event date announced yet.\n"
        response_text += "\nVisit the Graduation page for more details or to register if eligible."
    elif intent == "summary":
        topic_search = re.search(r"(?:tell me about|summary of|what is|explain|define|describe)\s*(.+)", prompt, re.IGNORECASE) # Renamed
        search_topic = topic_search.group(1) if topic_search else prompt # Renamed
        cleaned_topic = " ".join([word for word in search_topic.split() if word.lower() not in ["summary", "of", "the", "an", "a", "is", "are", "what", "tell", "me", "about"]]).strip() # Renamed
        if cleaned_topic:
            try:
                wikipedia.set_user_agent("StudentPortalAssistant/1.0 (mercy@example.com)") # Consider setting this once globally
                wiki_summary = wikipedia.summary(cleaned_topic, sentences=3, auto_suggest=True, redirect=True) # Renamed
                wiki_page_url = wikipedia.page(cleaned_topic, auto_suggest=True, redirect=True).url # Renamed
                response_text = f"🔍 Here's a brief summary of '{cleaned_topic.title()}':\n\n{wiki_summary}\n\n<a href='{wiki_page_url}' target='_blank'>Read more on Wikipedia</a>"
            except wikipedia.exceptions.PageError:
                response_text = f"Sorry, I couldn't find a Wikipedia page for '{cleaned_topic}'. Please try a different topic or rephrase."
            except wikipedia.exceptions.DisambiguationError as e_disambig: # Renamed
                options_list = "\n - ".join(e_disambig.options[:5]) # Renamed
                response_text = f"Your topic '{cleaned_topic}' is ambiguous. It could mean:\n - {options_list}\n\nPlease be more specific."
            except Exception as e_wiki: # Renamed
                response_text = f"Couldn't fetch information about '{cleaned_topic}' at the moment. Error: {str(e_wiki)[:100]}" # Increased error length
        else:
            response_text = "What topic would you like me to summarize for you from Wikipedia?"
    else:
        if gpt_pipeline and len(prompt.split()) > 3:
            try:
                llm_prompt = f"Student question: {prompt}" # Renamed
                generated_texts = gpt_pipeline(llm_prompt, max_length=150, min_length=10, num_beams=2, early_stopping=True, temperature=0.7) # Renamed
                if generated_texts and generated_texts[0]['generated_text']:
                    response_text = generated_texts[0]['generated_text']
                else:
                    app.logger.warning(f"AI assistant generated an empty response for prompt: {prompt}")
                    response_text = "I'm not sure I understand. Could you rephrase?"
            except Exception as e_llm: # Renamed
                app.logger.error(f"Error during AI assistant text generation: {e_llm}", exc_info=True)
                response_text = "I'm having trouble answering that right now. Please try again later."
        else:
            if not gpt_pipeline: app.logger.info(f"AI assistant (gpt_pipeline) is None. Prompt '{prompt}' not processed by LLM.")
            elif len(prompt.split()) <=3: app.logger.info(f"Prompt '{prompt}' too short, not processed by LLM.")
            response_text = random.choice([
                "I'm not sure about that. Could you ask about your course or student records?",
                "I specialize in student information. Try asking about your classes or fees.",
                "Can you rephrase that? I'm best with questions about your studies."])

    def get_contextual_suggestions(detected_intent, user_grad_status): # Renamed
        base_suggs = ["My fee balance", "Next class schedule", "Available resources", "My attendance"] # Renamed
        sugg_list = [] # Renamed
        if detected_intent == "graduation" or user_grad_status == "Awaiting Graduation":
            sugg_list = ["Register for graduation", "Upcoming graduation dates", "Graduation media"]
        elif detected_intent == "resources":
            sugg_list = ["Summarize my notes", "Latest course uploads", "Help with an assignment"]
        elif detected_intent == "fee":
             sugg_list = ["How to pay fees", "Payment history", "Fee structure"]
        else:
            sugg_list = random.sample(base_suggs, min(len(base_suggs), 3))
        return [s for i, s in enumerate(sugg_list) if sugg_list.index(s) == i][:3] # Unique and limit 3

    return jsonify({
        'reply': response_text,
        'status': 'success',
        'suggestions': get_contextual_suggestions(intent, user.graduation_status),
        'context': intent or "general_fallback"
    })

if __name__ == '__main__':
    logger.info("STARTUP: Reached __main__ block (direct execution, not via Gunicorn).")
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    logger.info(f"STARTUP: Flask development server debug mode is {'ON' if debug_mode else 'OFF'}.")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_mode)
