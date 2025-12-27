// Mobile Menu Toggle
const mobileMenu = document.getElementById('mobile-menu');
const navLinks = document.querySelector('.nav-links');

mobileMenu.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    // Animate Icon
    const icon = mobileMenu.querySelector('i');
    if (navLinks.classList.contains('active')) {
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-times');
    } else {
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    }
});

// Close mobile menu when clicking a link
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        const icon = mobileMenu.querySelector('i');
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    });
});

// Smooth Scrolling for Anchor Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Navbar Scroll Effect (Glassmorphism intensity change)
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.background = 'rgba(15, 23, 42, 0.95)';
        header.style.boxShadow = '0 5px 20px rgba(0,0,0,0.2)';
    } else {
        header.style.background = 'rgba(15, 23, 42, 0.85)';
        header.style.boxShadow = 'none';
    }
});

// Number Counter Animation
const stats = document.querySelectorAll('.stat-number');
const observerOptions = {
    threshold: 0.5
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const target = entry.target;
            const countTo = parseInt(target.getAttribute('data-target'));
            let count = 0;
            const duration = 2000; // 2 seconds
            const increment = countTo / (duration / 16); // 60fps

            const timer = setInterval(() => {
                count += increment;
                if (count >= countTo) {
                    target.textContent = countTo;
                    clearInterval(timer);
                } else {
                    target.textContent = Math.floor(count);
                }
            }, 16);

            observer.unobserve(target); // Only run once
        }
    });
}, observerOptions);

stats.forEach(stat => {
    observer.observe(stat);
});

// Accordion Functionality for Courses
document.querySelectorAll('.course-title').forEach(title => {
    title.addEventListener('click', () => {
        // 1. Tıklanan başlığın active sınıfını aç/kapa
        title.classList.toggle('active');

        // 2. İlgili materyal gridini bul
        const grid = title.nextElementSibling;

        // 3. Grid'in active sınıfını aç/kapa
        grid.classList.toggle('active');

        // 4. Pürüzsüz açılma animasyonu (Max-Height)
        if (title.classList.contains('active')) {
            // İçeriğin gerçek yüksekliğini alıp stil olarak ekle
            grid.style.maxHeight = grid.scrollHeight + 50 + "px"; // +50px padding payı
        } else {
            // Kapatırken yüksekliği sıfırla
            grid.style.maxHeight = null;
        }
    });
});