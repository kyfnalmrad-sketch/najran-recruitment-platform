from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# جدول المشرفين (Admins)
class Admin(db.Model):
    __tablename__ = 'admins'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Admin {self.full_name}>'


# جدول الشركات (Companies)
class Company(db.Model):
    __tablename__ = 'companies'
    
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    jobs = db.relationship('Job', backref='company', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Company {self.company_name}>'


# جدول الوظائف (Jobs)
class Job(db.Model):
    __tablename__ = 'jobs'
    
    job_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)  # IT, Accounting, HR, etc.
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)  # Full-time, Part-time, Internship
    salary = db.Column(db.String(100), nullable=True)  # Optional
    requirements = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Published, Rejected, Hidden
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Job {self.title}>'


# جدول الباحثين عن عمل (Job Seekers)
class JobSeeker(db.Model):
    __tablename__ = 'job_seekers'
    
    seeker_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    applications = db.relationship('Application', backref='seeker', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<JobSeeker {self.full_name}>'


# جدول الطلبات (Applications)
class Application(db.Model):
    __tablename__ = 'applications'
    
    application_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), nullable=False)
    seeker_id = db.Column(db.Integer, db.ForeignKey('job_seekers.seeker_id'), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)
    cv_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Pending')  # Pending, Accepted, Rejected
    internal_notes = db.Column(db.Text, nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application Job:{self.job_id} Seeker:{self.seeker_id}>'
