// ==================== تسجيل Service Worker ====================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker تم تسجيله بنجاح');
            })
            .catch(err => {
                console.log('خطأ في تسجيل ServiceWorker:', err);
            });
    });
}

// ==================== شريط التنقل الذكي ====================
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar');
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    // تأثير التمرير على Navbar
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar?.classList.add('scrolled');
        } else {
            navbar?.classList.remove('scrolled');
        }
    });

    // قائمة الجوال (Hamburger Menu)
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks?.classList.toggle('active');
        });

        // إغلاق القائمة عند الضغط على رابط
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navLinks?.classList.remove('active');
            });
        });
    }
});

// ==================== نظام التنبيهات (Toast Notifications) ====================
function showAlert(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';
    if (type === 'warning') icon = '⚠️';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

// ==================== البحث عن الوظائف ====================
function searchJobs() {
    const city = document.getElementById('city-filter')?.value || '';
    const category = document.getElementById('category-filter')?.value || '';
    const jobType = document.getElementById('type-filter')?.value || '';
    
    let url = '/search?';
    if (city) url += `city=${city}&`;
    if (category) url += `category=${category}&`;
    if (jobType) url += `job_type=${jobType}`;
    
    window.location.href = url;
}

// ==================== تحديث حالة الطلب ====================
function updateApplicationStatus(appId, status) {
    const notes = document.getElementById(`notes-${appId}`)?.value || '';
    
    const confirmMsg = status === 'Accepted' ? 'هل أنت متأكد من قبول هذا المتقدم؟' : 'هل أنت متأكد من رفض هذا المتقدم؟';
    if (!confirm(confirmMsg)) return;

    fetch(`/company/application/${appId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${status}&notes=${encodeURIComponent(notes)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('تم تحديث حالة الطلب بنجاح ✨', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('حدث خطأ أثناء تحديث الحالة', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('خطأ في الاتصال بالخادم', 'error');
    });
}

// ==================== تحديث حالة الشركة ====================
function updateCompanyStatus(companyId, status) {
    fetch(`/admin/company/${companyId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${status}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('تم تحديث حالة الشركة بنجاح ✨', 'success');
            setTimeout(() => location.reload(), 1000);
        }
    });
}

// ==================== تحديث حالة الوظيفة ====================
function updateJobStatus(jobId, status) {
    fetch(`/admin/job/${jobId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${status}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('تم تحديث حالة الوظيفة بنجاح ✨', 'success');
            setTimeout(() => location.reload(), 1000);
        }
    });
}

// ==================== تأثيرات الأزرار ====================
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mousedown', function() {
        this.style.transform = 'scale(0.98)';
    });
    button.addEventListener('mouseup', function() {
        this.style.transform = 'scale(1)';
    });
});

// ==================== Skeleton Loader ====================
function showSkeletonLoader() {
    const container = document.querySelector('.jobs-grid');
    if (!container) return;

    container.innerHTML = '';
    for (let i = 0; i < 6; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-card';
        skeleton.innerHTML = `
            <div class="skeleton skeleton-title" style="width: 80%;"></div>
            <div class="skeleton skeleton-text" style="width: 60%;"></div>
            <div class="skeleton skeleton-text" style="width: 100%;"></div>
            <div class="skeleton skeleton-text" style="width: 70%;"></div>
        `;
        container.appendChild(skeleton);
    }
}

// ==================== تأثير Fade-in للصفحات ====================
document.addEventListener('DOMContentLoaded', function() {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease-in-out';
        document.body.style.opacity = '1';
    }, 100);
});
