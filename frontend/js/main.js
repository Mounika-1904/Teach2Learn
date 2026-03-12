document.addEventListener('DOMContentLoaded', () => {
    console.log('Teach2Learn Frontend Loaded');

    // Smooth scrolling for anchor links
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

    // Tab Switching Logic for Register Page
    const tabs = document.querySelectorAll('.auth-tab');
    const roleFields = document.querySelectorAll('.role-fields');

    if (tabs.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const selectedRole = tab.getAttribute('data-tab');
                roleFields.forEach(field => field.classList.add('hidden'));
                const targetFields = document.getElementById(`${selectedRole}-fields`);
                if (targetFields) {
                    targetFields.classList.remove('hidden');
                }
            });
        });
    }

    // Register Form Handler
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const activeTab = document.querySelector('.auth-tab.active');
            const role = activeTab ? activeTab.getAttribute('data-tab') : 'student';

            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                role: role
            };

            if (role === 'student') {
                formData.class_level = document.getElementById('class-level').value;
                formData.interests = document.getElementById('interests').value;
            } else {
                formData.subjects = document.getElementById('subjects').value;
                formData.experience = document.getElementById('experience').value;
                formData.availability_info = document.getElementById('availability').value;
            }

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (response.ok) {
                    alert('Registration successful! Please login.');
                    window.location.href = 'login.html';
                } else {
                    alert(data.error || 'Registration failed');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Connection error');
            }
        });
    }

    // Login Form Handler
    const loginForm = document.querySelector('.auth-form');
    if (loginForm && !registerForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('user', JSON.stringify(data));
                    // Redirect based on role
                    if (data.role === 'student') {
                        window.location.href = 'student-dashboard.html';
                    } else if (data.role === 'tutor') {
                        window.location.href = 'tutor-dashboard.html';
                    } else if (data.role === 'admin') {
                        window.location.href = 'admin-dashboard.html';
                    } else {
                        window.location.href = 'index.html';
                    }
                } else {
                    alert(data.error || 'Login failed');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Connection error');
            }
        });
    }

    // Logout Logic
    const logoutBtn = document.querySelector('.logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('user');
            window.location.href = 'login.html';
        });
    }

    // Search Bar Integration
    const searchInput = document.querySelector('.search-bar input');
    if (searchInput) {
        searchInput.addEventListener('keypress', async function (e) {
            if (e.key === 'Enter') {
                const query = this.value;
                if (!query) return;

                try {
                    const response = await fetch(`/api/tutors/search?q=${encodeURIComponent(query)}`);
                    const tutors = await response.json();

                    const tutorsList = document.querySelector('.tutors-list');
                    if (tutorsList) {
                        tutorsList.innerHTML = '';
                        if (tutors.length === 0) {
                            tutorsList.innerHTML = `<p class="empty-text">No tutors found for "${query}"</p>`;
                        } else {
                            tutors.forEach(tutor => {
                                const card = document.createElement('div');
                                card.className = 'tutor-card';
                                card.innerHTML = `
                                    <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(tutor.name)}&background=random" alt="${tutor.name}" class="tutor-img">
                                    <div class="tutor-info">
                                        <h3>${tutor.name}</h3>
                                        <span class="subject">${tutor.subjects}</span>
                                        <div class="rating">
                                            <i class="fas fa-star"></i> ${tutor.rating || 'New'}
                                        </div>
                                    </div>
                                    <button class="btn btn-sm btn-primary">Book</button>
                                `;
                                tutorsList.appendChild(card);
                            });
                        }
                    } else {
                        alert(`Found ${tutors.length} tutors for "${query}"`);
                    }
                } catch (error) {
                    console.error('Search error:', error);
                }
            }
        });
    }
});

