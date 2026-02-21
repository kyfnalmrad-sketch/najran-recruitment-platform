from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from models import db, Admin, Company, Job, JobSeeker, Application
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

app = Flask(__name__)

# إعدادات الأمان والقاعدة
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///recruitment.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعدادات رفع الملفات
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)

# إنشاء جداول قاعدة البيانات
with app.app_context():
    db.create_all()

# ==================== الصفحات العامة ====================

@app.route('/')
def index():
    """الصفحة الرئيسية - عرض الوظائف المنشورة"""
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(status='Published').paginate(page=page, per_page=12)
    
    # الحصول على المدن والتصنيفات المتاحة للتصفية
    cities = db.session.query(Job.city).distinct().filter_by(status='Published').all()
    categories = db.session.query(Job.category_name).distinct().filter_by(status='Published').all()
    
    return render_template('index.html', jobs=jobs, cities=cities, categories=categories)


@app.route('/search')
def search_jobs():
    """البحث والتصفية على الوظائف"""
    city = request.args.get('city', '')
    category = request.args.get('category', '')
    job_type = request.args.get('job_type', '')
    
    query = Job.query.filter_by(status='Published')
    
    if city:
        query = query.filter_by(city=city)
    if category:
        query = query.filter_by(category_name=category)
    if job_type:
        query = query.filter_by(job_type=job_type)
    
    jobs = query.all()
    return render_template('search_results.html', jobs=jobs)


@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """صفحة تفاصيل الوظيفة"""
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)


# ==================== نظام المصادقة ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول الموحدة"""
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if user_type == 'admin':
            admin = Admin.query.filter_by(email=email).first()
            if admin and admin.check_password(password):
                session['user_id'] = admin.admin_id
                session['user_type'] = 'admin'
                session['user_name'] = admin.full_name
                return redirect(url_for('admin_dashboard'))
        
        elif user_type == 'company':
            company = Company.query.filter_by(email=email).first()
            if company and company.check_password(password):
                session['user_id'] = company.company_id
                session['user_type'] = 'company'
                session['user_name'] = company.company_name
                return redirect(url_for('company_dashboard'))
        
        elif user_type == 'seeker':
            seeker = JobSeeker.query.filter_by(email=email).first()
            if seeker and seeker.check_password(password):
                session['user_id'] = seeker.seeker_id
                session['user_type'] = 'seeker'
                session['user_name'] = seeker.full_name
                return redirect(url_for('seeker_dashboard'))
        
        return render_template('login.html', error='البريد الإلكتروني أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        
        if user_type == 'seeker':
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            password = request.form.get('password')
            phone = request.form.get('phone')
            city = request.form.get('city')
            
            if JobSeeker.query.filter_by(email=email).first():
                return render_template('register.html', error='البريد الإلكتروني مسجل بالفعل')
            
            seeker = JobSeeker(full_name=full_name, email=email, phone=phone, city=city)
            seeker.set_password(password)
            db.session.add(seeker)
            db.session.commit()
            
            return redirect(url_for('login'))
        
        elif user_type == 'company':
            company_name = request.form.get('company_name')
            email = request.form.get('email')
            password = request.form.get('password')
            phone = request.form.get('phone')
            city = request.form.get('city')
            description = request.form.get('description')
            
            if Company.query.filter_by(email=email).first():
                return render_template('register.html', error='البريد الإلكتروني مسجل بالفعل')
            
            company = Company(company_name=company_name, email=email, phone=phone, city=city, description=description)
            company.set_password(password)
            db.session.add(company)
            db.session.commit()
            
            return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('index'))


# ==================== لوحة تحكم الباحث ====================

@app.route('/seeker/dashboard')
def seeker_dashboard():
    """لوحة تحكم الباحث عن عمل"""
    if 'user_type' not in session or session['user_type'] != 'seeker':
        return redirect(url_for('login'))
    
    seeker_id = session['user_id']
    seeker = JobSeeker.query.get(seeker_id)
    applications = Application.query.filter_by(seeker_id=seeker_id).all()
    
    return render_template('seeker_dashboard.html', seeker=seeker, applications=applications)


@app.route('/seeker/apply/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    """تقديم طلب على وظيفة مع رفع السيرة الذاتية"""
    if 'user_type' not in session or session['user_type'] != 'seeker':
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    seeker_id = session['user_id']
    cover_letter = request.form.get('cover_letter')
    
    # التحقق من عدم التقديم مسبقاً
    existing_app = Application.query.filter_by(job_id=job_id, seeker_id=seeker_id).first()
    if existing_app:
        return jsonify({'success': False, 'message': 'لقد قدمت على هذه الوظيفة بالفعل'}), 400
    
    cv_filename = None
    
    # معالجة رفع الملف
    if 'cv_file' in request.files:
        file = request.files['cv_file']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'صيغة الملف غير مدعومة. استخدم PDF أو DOC أو DOCX'}), 400
            
            # حفظ الملف بشكل آمن
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cv_filename = filename
    
    # إنشاء الطلب
    application = Application(
        job_id=job_id,
        seeker_id=seeker_id,
        cover_letter=cover_letter,
        cv_filename=cv_filename,
        status='Pending'
    )
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'تم تقديم الطلب بنجاح'})


@app.route('/uploads/<filename>')
def download_cv(filename):
    """تحميل السيرة الذاتية"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return "الملف غير موجود", 404
    except Exception as e:
        return str(e), 500


# ==================== لوحة تحكم الشركة ====================

@app.route('/company/dashboard')
def company_dashboard():
    """لوحة تحكم الشركة"""
    if 'user_type' not in session or session['user_type'] != 'company':
        return redirect(url_for('login'))
    
    company_id = session['user_id']
    company = Company.query.get(company_id)
    jobs = Job.query.filter_by(company_id=company_id).all()
    
    return render_template('company_dashboard.html', company=company, jobs=jobs)


@app.route('/company/add-job', methods=['GET', 'POST'])
def add_job():
    """إضافة وظيفة جديدة"""
    if 'user_type' not in session or session['user_type'] != 'company':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        company_id = session['user_id']
        
        job = Job(
            company_id=company_id,
            category_name=request.form.get('category_name'),
            title=request.form.get('title'),
            description=request.form.get('description'),
            city=request.form.get('city'),
            job_type=request.form.get('job_type'),
            salary=request.form.get('salary'),
            requirements=request.form.get('requirements'),
            status='Pending'  # تنتظر موافقة المشرف
        )
        
        db.session.add(job)
        db.session.commit()
        
        return redirect(url_for('company_dashboard'))
    
    return render_template('add_job.html')


@app.route('/company/job/<int:job_id>/applicants')
def job_applicants(job_id):
    """عرض المتقدمين على وظيفة"""
    if 'user_type' not in session or session['user_type'] != 'company':
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    
    # التحقق من أن الوظيفة تابعة للشركة الحالية
    if job.company_id != session['user_id']:
        return redirect(url_for('company_dashboard'))
    
    applications = Application.query.filter_by(job_id=job_id).all()
    
    return render_template('job_applicants.html', job=job, applications=applications)


@app.route('/company/application/<int:app_id>/status', methods=['POST'])
def update_application_status(app_id):
    """تحديث حالة الطلب"""
    if 'user_type' not in session or session['user_type'] != 'company':
        return jsonify({'success': False}), 403
    
    application = Application.query.get_or_404(app_id)
    
    # التحقق من أن الطلب يتعلق بوظيفة تابعة للشركة
    if application.job.company_id != session['user_id']:
        return jsonify({'success': False}), 403
    
    status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    application.status = status
    application.internal_notes = notes
    db.session.commit()
    
    return jsonify({'success': True})


# ==================== لوحة تحكم المشرف ====================

@app.route('/admin/dashboard')
def admin_dashboard():
    """لوحة تحكم المشرف"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    companies = Company.query.all()
    jobs = Job.query.all()
    seekers = JobSeeker.query.all()
    
    return render_template('admin_dashboard.html', companies=companies, jobs=jobs, seekers=seekers)


@app.route('/admin/company/<int:company_id>/status', methods=['POST'])
def update_company_status(company_id):
    """تحديث حالة الشركة"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return jsonify({'success': False}), 403
    
    company = Company.query.get_or_404(company_id)
    status = request.form.get('status')
    
    company.status = status
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/admin/job/<int:job_id>/status', methods=['POST'])
def update_job_status(job_id):
    """تحديث حالة الوظيفة"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return jsonify({'success': False}), 403
    
    job = Job.query.get_or_404(job_id)
    status = request.form.get('status')
    
    job.status = status
    db.session.commit()
    
    return jsonify({'success': True})


# ==================== معالجة الأخطاء ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
