from app import app, db
from models import Admin, Company, Job, JobSeeker, Application
from datetime import datetime

def init_database():
    """تهيئة قاعدة البيانات ببيانات تجريبية"""
    
    with app.app_context():
        # حذف الجداول القديمة
        db.drop_all()
        
        # إنشاء الجداول الجديدة
        db.create_all()
        
        print("✓ تم إنشاء الجداول بنجاح")
        
        # إضافة مشرف
        admin = Admin(
            full_name='مدير النظام',
            email='admin@example.com'
        )
        admin.set_password('123456')
        db.session.add(admin)
        print("✓ تم إضافة مشرف")
        
        # إضافة شركات
        company1 = Company(
            company_name='شركة التقنية المتقدمة',
            email='company@example.com',
            phone='+966501234567',
            city='الرياض',
            description='شركة متخصصة في تطوير البرمجيات والحلول التقنية',
            status='Approved'
        )
        company1.set_password('123456')
        
        company2 = Company(
            company_name='شركة الاستشارات المالية',
            email='finance@example.com',
            phone='+966502345678',
            city='جدة',
            description='شركة متخصصة في الاستشارات المالية والمحاسبة',
            status='Approved'
        )
        company2.set_password('123456')
        
        db.session.add(company1)
        db.session.add(company2)
        print("✓ تم إضافة شركات")
        
        # إضافة وظائف
        job1 = Job(
            company_id=1,
            category_name='IT',
            title='مهندس برمجيات - Python',
            description='نبحث عن مهندس برمجيات متخصص في Python مع خبرة 3+ سنوات.\n\nالمسؤوليات:\n- تطوير تطبيقات ويب باستخدام Flask و Django\n- المشاركة في تصميم العمارة البرمجية\n- كتابة اختبارات شاملة للكود\n- المساهمة في مراجعة الأكواد',
            city='الرياض',
            job_type='Full-time',
            salary='8000 - 12000 ريال',
            requirements='- درجة بكالوريوس في علوم الحاسب أو ما يعادله\n- خبرة 3+ سنوات في تطوير Python\n- معرفة بـ SQL و قواعد البيانات\n- مهارات تواصل جيدة\n- العمل ضمن فريق',
            status='Published'
        )
        
        job2 = Job(
            company_id=1,
            category_name='IT',
            title='مصمم واجهات المستخدم (UI/UX)',
            description='نبحث عن مصمم واجهات متخصص في تصميم تجارب المستخدم الحديثة.\n\nالمسؤوليات:\n- تصميم واجهات المستخدم للتطبيقات الويب والموبايل\n- إنشاء نماذج أولية وتصاميم تفاعلية\n- التعاون مع فريق التطوير',
            city='الرياض',
            job_type='Full-time',
            salary='6000 - 9000 ريال',
            requirements='- خبرة 2+ سنوات في تصميم UI/UX\n- إتقان أدوات التصميم (Figma, Adobe XD)\n- معرفة بمبادئ تصميم التفاعل\n- مهارات تواصل قوية',
            status='Published'
        )
        
        job3 = Job(
            company_id=2,
            category_name='Accounting',
            title='محاسب مالي',
            description='نبحث عن محاسب مالي ذو خبرة في الإدارة المالية والتقارير المالية.\n\nالمسؤوليات:\n- إعداد التقارير المالية الشهرية\n- إدارة الحسابات والفواتير\n- التدقيق المالي الداخلي',
            city='جدة',
            job_type='Full-time',
            salary='5000 - 7000 ريال',
            requirements='- درجة بكالوريوس في المحاسبة\n- خبرة 2+ سنوات في المحاسبة المالية\n- معرفة بالبرامج المحاسبية\n- دقة عالية في العمل',
            status='Published'
        )
        
        db.session.add(job1)
        db.session.add(job2)
        db.session.add(job3)
        print("✓ تم إضافة وظائف")
        
        # إضافة باحثين
        seeker1 = JobSeeker(
            full_name='أحمد محمد علي',
            email='seeker@example.com',
            phone='+966503456789',
            city='الرياض'
        )
        seeker1.set_password('123456')
        
        seeker2 = JobSeeker(
            full_name='فاطمة أحمد سالم',
            email='seeker2@example.com',
            phone='+966504567890',
            city='جدة'
        )
        seeker2.set_password('123456')
        
        db.session.add(seeker1)
        db.session.add(seeker2)
        print("✓ تم إضافة باحثين")
        
        # إضافة طلبات
        app1 = Application(
            job_id=1,
            seeker_id=1,
            cover_letter='أنا مهتم جداً بهذه الوظيفة لأن لدي خبرة قوية في Python وأتطلع للعمل مع فريق متميز.',
            status='Pending'
        )
        
        app2 = Application(
            job_id=2,
            seeker_id=2,
            cover_letter='أملك خبرة 3 سنوات في تصميم الواجهات وأنا متحمس للعمل على مشاريع جديدة.',
            status='Accepted'
        )
        
        db.session.add(app1)
        db.session.add(app2)
        print("✓ تم إضافة طلبات")
        
        # حفظ البيانات
        db.session.commit()
        print("\n✅ تم تهيئة قاعدة البيانات بنجاح!")
        print("\nبيانات الاختبار:")
        print("=" * 50)
        print("مشرف:")
        print("  البريد: admin@example.com")
        print("  كلمة المرور: 123456")
        print("\nشركة:")
        print("  البريد: company@example.com")
        print("  كلمة المرور: 123456")
        print("\nباحث:")
        print("  البريد: seeker@example.com")
        print("  كلمة المرور: 123456")
        print("=" * 50)

if __name__ == '__main__':
    init_database()
