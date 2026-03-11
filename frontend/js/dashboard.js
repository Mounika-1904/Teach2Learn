document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const sidebarLinks = document.querySelectorAll('.sidebar-link[data-section]');
    const sections = document.querySelectorAll('.dashboard-section');
    const welcomeTitle = document.getElementById('welcome-title');
    const headerAvatar = document.getElementById('header-avatar');
    const globalSearch = document.getElementById('global-search');
    const searchSuggestions = document.getElementById('search-suggestions');

    // Dashboard Lists
    const recsList = document.getElementById('recommendations-list');
    const allTutorsList = document.getElementById('all-tutors-list');
    const scheduleTableBody = document.getElementById('schedule-table-body');

    // Notification Elements
    const notifBell = document.getElementById('notif-bell');
    const notifDropdown = document.getElementById('notif-dropdown');
    const notifCount = document.getElementById('notif-count');
    const notifList = document.getElementById('notif-list');
    const markAllReadBtn = document.getElementById('mark-all-read');

    // Messaging Elements
    const contactsList = document.getElementById('contacts-list');
    const messageList = document.getElementById('message-list');
    const messageInput = document.getElementById('message-input');
    const sendMsgBtn = document.getElementById('send-msg-btn');
    let activeChatTutorId = null;

    // Modal Elements
    const bookingModal = document.getElementById('booking-modal');
    const bookingForm = document.getElementById('booking-form');
    const closeModalBtn = document.querySelector('#booking-modal .close-modal');

    const skillLevelModal = document.getElementById('skill-level-modal');
    const skillLevelForm = document.getElementById('skill-level-form');
    const closeSkillModalBtns = document.querySelectorAll('.close-skill-modal, #skip-skill-btn');
    const skillSubjectName = document.getElementById('skill-subject-name');
    const skillTargetSubject = document.getElementById('skill-target-subject');

    const feedbackModal = document.getElementById('feedback-modal');
    const feedbackForm = document.getElementById('feedback-form');
    const closeFeedbackModalBtn = document.querySelector('.close-feedback-modal');

    // Profile Elements
    const profileForm = document.getElementById('profile-form');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    const cancelProfileBtn = document.getElementById('cancel-profile-btn');
    const profileActions = document.getElementById('profile-actions');

    const API_BASE = 'http://127.0.0.1:5000/api';

    // --- Auth Check ---
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || user.role !== 'student') {
        window.location.href = 'login.html';
        return;
    }

    const studentId = user.role_id;
    const userId = user.id;
    updateUIWithUserData();

    // --- SPA Navigation ---
    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const sectionTarget = link.getAttribute('data-section');
            if (sectionTarget && !link.classList.contains('logout')) {
                e.preventDefault();
                switchSection(sectionTarget);
            }
        });
    });

    function switchSection(sectionId) {
        sections.forEach(s => {
            s.classList.remove('active');
            s.classList.add('hidden');
        });
        sidebarLinks.forEach(l => l.classList.remove('active'));

        const activeSection = document.getElementById(sectionId);
        const activeLink = document.querySelector(`.sidebar-link[data-section="${sectionId}"]`);

        if (activeSection) {
            activeSection.classList.remove('hidden');
            activeSection.classList.add('active');
        }
        if (activeLink) activeLink.classList.add('active');

        if (sectionId === 'overview-section') loadDashboard();
        if (sectionId === 'tutors-section') loadTutorsPage();
        if (sectionId === 'schedule-section') loadSchedule();
        if (sectionId === 'messages-section') loadMessaging();
        if (sectionId === 'profile-section') loadProfile();
    }

    // --- Data Loaders ---

    async function loadDashboard() {
        try {
            const recRes = await fetch(`${API_BASE}/recommend_tutors/${studentId}`);
            const recData = await recRes.json();
            renderTutorCards(recData.recommendations, recsList, { isRecommended: true });

            const scheduleRes = await fetch(`${API_BASE}/schedules/${studentId}`);
            const sessions = await scheduleRes.json();
            renderUpcomingClassesOverview(sessions);

            updateStudentMetrics();
            renderLearningProgress();
            checkNotifications();
        } catch (err) { console.error(err); }
    }

    // --- NOTIFICATIONS ---
    if (notifBell) {
        notifBell.onclick = (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle('hidden');
            if (!notifDropdown.classList.contains('hidden')) loadNotifications();
        };
    }

    async function checkNotifications() {
        try {
            const res = await fetch(`${API_BASE}/notifications/${userId}`);
            const data = await res.json();
            const unread = data.filter(n => !n.is_read).length;
            if (unread > 0) {
                notifCount.textContent = unread;
                notifCount.classList.remove('hidden');
            } else {
                notifCount.classList.add('hidden');
            }
        } catch (err) { console.error(err); }
    }

    async function loadNotifications() {
        try {
            const res = await fetch(`${API_BASE}/notifications/${userId}`);
            const data = await res.json();
            notifList.innerHTML = '';
            if (data.length === 0) {
                notifList.innerHTML = '<p class="empty-text">No notifications</p>';
                return;
            }
            data.forEach(n => {
                const item = document.createElement('div');
                item.className = `notif-item ${n.is_read ? '' : 'unread'}`;
                item.innerHTML = `<p>${n.message}</p><span class="time">${n.created_at}</span>`;
                item.onclick = async () => {
                    await fetch(`${API_BASE}/notifications/read/${n.id}`, { method: 'POST' });
                    checkNotifications();
                    item.classList.remove('unread');
                };
                notifList.appendChild(item);
            });
        } catch (err) { console.error(err); }
    }

    // --- MESSAGING ---
    async function loadMessaging() {
        try {
            // Load tutors student has sessions with
            const res = await fetch(`${API_BASE}/schedules/${studentId}`);
            const sessions = await res.json();
            const tutors = [];
            const seen = new Set();
            sessions.forEach(s => {
                if (!seen.has(s.tutor_name)) {
                    tutors.push({ name: s.tutor_name, id: s.tutor_id, user_id: s.tutor_user_id }); 
                    seen.add(s.tutor_name);
                }
            });
            renderContacts(tutors);
        } catch (err) { console.error(err); }
    }

    function renderContacts(tutors) {
        if (!contactsList) return;
        contactsList.innerHTML = tutors.length ? '' : '<p class="empty-text">No tutors yet.</p>';
        tutors.forEach(t => {
            const item = document.createElement('div');
            item.className = 'contact-item';
            const name = t.name || 'Unknown Tutor';
            const avatar = name.substring(0,2);
            item.innerHTML = `
                <div class="user-avatar" style="width: 40px; height: 40px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-weight: 600;">${avatar}</div>
                <div class="contact-info"><h4>${name}</h4><p>Tutor</p></div>`;
            item.onclick = () => {
                document.querySelectorAll('.contact-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                openChat(t);
            };
            contactsList.appendChild(item);
        });
    }

    function openChat(tutor) {
        console.log('openChat called for tutor:', tutor);
        activeChatTutorId = tutor.user_id; 
        
        const placeholder = document.querySelector('.chat-placeholder');
        if (placeholder) placeholder.style.display = 'none';
        
        const info = document.querySelector('.selected-user-info');
        if (info) info.style.display = 'flex';
        
        const nameHeader = document.getElementById('chat-user-name');
        const avatarHeader = document.getElementById('chat-avatar');
        
        const name = tutor.name || 'Unknown Tutor';
        if (nameHeader) nameHeader.textContent = name;
        if (avatarHeader) avatarHeader.textContent = name.substring(0,2).toUpperCase();
        
        const input = document.getElementById('message-input');
        const btn = document.getElementById('send-msg-btn');
        
        if (input) {
            console.log('Enabling message input');
            input.disabled = false;
            input.focus();
        } else {
            console.error('message-input element not found');
        }
        
        if (btn) {
            btn.disabled = false;
        } else {
            console.error('send-msg-btn element not found');
        }
        
        loadChatMessages();
    }

    async function loadChatMessages() {
        if (!activeChatTutorId) return;
        try {
            const res = await fetch(`${API_BASE}/messages/${userId}?other_id=${activeChatTutorId}`);
            const messages = await res.json();
            if (!messageList) return;
            messageList.innerHTML = '';
            messages.forEach(m => {
                const bubble = document.createElement('div');
                bubble.className = `message-bubble ${m.sender_name.includes('(You)') ? 'sent' : 'received'}`;
                
                if (m.message) {
                    const text = document.createElement('div');
                    text.textContent = m.message;
                    bubble.appendChild(text);
                }

                if (m.file_url) {
                    const isImage = /\.(jpg|jpeg|png|gif)$/i.test(m.file_url);
                    if (isImage) {
                        const img = document.createElement('img');
                        img.src = m.file_url;
                        img.className = 'message-image';
                        img.onclick = () => window.open(m.file_url, '_blank');
                        bubble.appendChild(img);
                    } else {
                        const fileLink = document.createElement('a');
                        fileLink.href = m.file_url;
                        fileLink.className = 'message-file';
                        fileLink.target = '_blank';
                        const fileName = m.file_url.split('/').pop().split('_').slice(1).join('_');
                        fileLink.innerHTML = `<i class="fas fa-file-alt"></i> <span>${fileName}</span>`;
                        bubble.appendChild(fileLink);
                    }
                }
                
                messageList.appendChild(bubble);
            });
            messageList.scrollTop = messageList.scrollHeight;
        } catch (err) { console.error(err); }
    }

    const attachBtn = document.getElementById('attach-btn');
    const fileInput = document.getElementById('file-input');

    if (attachBtn && fileInput) {
        attachBtn.onclick = () => fileInput.click();
        fileInput.onchange = async () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append('file', file);

                try {
                    attachBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    const res = await fetch(`${API_BASE}/upload`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (res.ok) {
                        // Send message with file_url immediately
                        await fetch(`${API_BASE}/messages`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                sender_id: userId, 
                                receiver_id: activeChatTutorId, 
                                content: "", 
                                file_url: data.file_url 
                            })
                        });
                        loadChatMessages();
                    } else {
                        alert(data.error || 'Upload failed');
                    }
                } catch (err) { console.error(err); }
                finally {
                    attachBtn.innerHTML = '<i class="fas fa-paperclip"></i>';
                    fileInput.value = '';
                }
            }
        };
    }

    if (sendMsgBtn) {
        sendMsgBtn.onclick = async () => {
            const content = messageInput.value.trim();
            if (!content || !activeChatTutorId) return;
            try {
                await fetch(`${API_BASE}/messages`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sender_id: userId, receiver_id: activeChatTutorId, content: content })
                });
                messageInput.value = '';
                loadChatMessages();
            } catch (err) { console.error(err); }
        };
    }

    if (messageInput) {
        messageInput.onkeydown = (e) => { if (e.key === 'Enter') sendMsgBtn.click(); };
    }

    // --- Search Integration ---
    if (globalSearch) {
        globalSearch.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                const query = globalSearch.value.trim();
                switchSection('tutors-section');
                if (allTutorsList) allTutorsList.innerHTML = '<div class="loading-state">Searching...</div>';
                try {
                    const res = await fetch(`${API_BASE}/search_tutors?query=${encodeURIComponent(query)}`);
                    const tutors = await res.json();
                    renderTutorCards(tutors, allTutorsList);
                    const title = document.getElementById('tutor-section-title');
                    if (title) title.textContent = query ? `Search Results for "${query}"` : 'Explore All Tutors';
                } catch (err) { console.error(err); }
            }
        });
    }

    // --- Other Logic (Metrics, Progress, Search) ---
    function updateStudentMetrics() {
        const c = document.getElementById('metric-courses'); if(c) c.textContent = '4';
        const h = document.getElementById('metric-hours'); if(h) h.textContent = '47.5';
        const cr = document.getElementById('metric-completion'); if(cr) cr.textContent = '78%';
    }

    function renderLearningProgress() {
        const container = document.getElementById('learning-progress-list');
        if (!container) return;
        const progressData = [{ subject: 'Mathematics', progress: 72 }, { subject: 'Python', progress: 58 }];
        container.innerHTML = '';
        progressData.forEach(p => {
            const item = document.createElement('div');
            item.className = 'progress-container';
            item.style.padding = '0 1rem';
            item.innerHTML = `
                <div class="progress-header"><span>${p.subject}</span><span>${p.progress}%</span></div>
                <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: ${p.progress}%"></div></div>`;
            container.appendChild(item);
        });
    }

    function renderUpcomingClassesOverview(sessions) {
        const container = document.getElementById('upcoming-classes-list');
        if (!container) return;
        const upcoming = sessions.filter(s => s.status === 'upcoming').slice(0, 3);
        container.innerHTML = upcoming.length ? '' : '<p class="empty-text">No classes scheduled.</p>';
        upcoming.forEach(s => {
            const item = document.createElement('div');
            item.className = 'dashboard-list-item';
            item.innerHTML = `
                <div class="item-icon"><i class="fas fa-book"></i></div>
                <div class="item-details"><h4>${s.subject}</h4><p>with ${s.tutor_name}</p></div>
                <div class="item-meta"><span class="item-time">${s.time}</span><span class="item-date">${s.date}</span></div>`;
            container.appendChild(item);
        });
    }

    async function loadTutorsPage() {
        try {
            if (allTutorsList) allTutorsList.innerHTML = '<div class="loading-state">Loading...</div>';
            const res = await fetch(`${API_BASE}/search_tutors?query=`);
            const tutors = await res.json();
            renderTutorCards(tutors, allTutorsList);
        } catch (err) { console.error(err); }
    }

    async function loadSchedule() {
        try {
            if (scheduleTableBody) scheduleTableBody.innerHTML = '<tr><td colspan="5" class="loading">Loading...</td></tr>';
            const res = await fetch(`${API_BASE}/schedules/${studentId}`);
            const sessions = await res.json();
            renderScheduleTable(sessions);
        } catch (err) { console.error(err); }
    }

    function renderScheduleTable(sessions) {
        if (!scheduleTableBody) return;
        scheduleTableBody.innerHTML = sessions.length ? '' : '<tr><td colspan="5">No sessions.</td></tr>';
        sessions.forEach(s => {
            const tr = document.createElement('tr');
            let actionHtml = '';
            if (s.status === 'upcoming') {
                actionHtml = `
                    <button class="btn btn-sm btn-primary" style="margin-right: 5px;" onclick="window.open('${s.meeting_link}', '_blank')">Join</button>
                    <button class="btn btn-sm btn-outline" style="border-color: var(--success); color: var(--success);" onclick="completeSession(${s.id})">Complete</button>
                `;
            } else if (s.status === 'completed') {
                actionHtml = `<button class="btn btn-sm btn-primary" onclick='openFeedbackModal(${JSON.stringify(s)})'><i class="fas fa-star" style="font-size: 0.8rem; margin-right: 4px;"></i> Rate Tutor</button>`;
            }

            tr.innerHTML = `
                <td>${s.subject}</td><td>${s.tutor_name}</td><td>${s.date} ${s.time}</td>
                <td><span class="badge ${s.status}">${s.status}</span></td>
                <td><div style="display: flex;">${actionHtml}</div></td>`;
            scheduleTableBody.appendChild(tr);
        });
    }

    window.completeSession = async (sessionId) => {
        if (!confirm('Mark this session as completed?')) return;
        try {
            const res = await fetch(`${API_BASE}/schedule/complete/${sessionId}`, { method: 'PUT' });
            if (res.ok) {
                alert('Session marked as completed!');
                loadSchedule();
            }
        } catch (err) { console.error(err); }
    };

    window.openFeedbackModal = (session) => {
        document.getElementById('feedback-tutor-id').value = session.tutor_id;
        document.getElementById('feedback-subject').value = session.subject;
        document.getElementById('feedback-tutor-name').textContent = session.tutor_name;
        document.getElementById('feedback-subject-display').textContent = session.subject;
        document.getElementById('feedback-subj-label').textContent = session.subject;
        
        // Reset stars to 5
        updateStars(5);
        
        feedbackModal.classList.remove('hidden');
        feedbackModal.style.display = 'flex';
    };

    // Star Rating Interaction
    const starContainer = document.getElementById('star-rating-container');
    const ratingInput = document.getElementById('feedback-rating');
    if (starContainer) {
        const stars = starContainer.querySelectorAll('i');
        stars.forEach(star => {
            star.addEventListener('click', () => {
                const val = parseInt(star.getAttribute('data-value'));
                updateStars(val);
            });
            star.addEventListener('mouseover', () => {
                const val = parseInt(star.getAttribute('data-value'));
                highlightStars(val);
            });
            star.addEventListener('mouseout', () => {
                highlightStars(parseInt(ratingInput.value));
            });
        });
    }

    function updateStars(val) {
        ratingInput.value = val;
        highlightStars(val);
    }

    function highlightStars(val) {
        const stars = document.querySelectorAll('#star-rating-container i');
        stars.forEach(s => {
            const sVal = parseInt(s.getAttribute('data-value'));
            if (sVal <= val) {
                s.style.color = '#FFD700';
                s.classList.add('active');
            } else {
                s.style.color = '#cbd5e1';
                s.classList.remove('active');
            }
        });
    }

    async function loadProfile() {
        try {
            const res = await fetch(`${API_BASE}/profile/${studentId}`);
            const data = await res.json();
            const n = document.getElementById('prof-name'); if(n) n.value = data.name;
            const e = document.getElementById('prof-email'); if(e) e.value = data.email;
            const pn = document.getElementById('profile-name'); if(pn) pn.textContent = data.name;
        } catch (err) { console.error(err); }
    }

    function updateUIWithUserData() {
        if (headerAvatar) headerAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=6C63FF&color=fff`;
        if (welcomeTitle) welcomeTitle.textContent = `Hello, ${user.name.split(' ')[0]} 👋`;
    }

    function renderTutorCards(tutors, container, options = {}) {
        if (!container) return;
        container.innerHTML = tutors.length ? '' : '<p class="empty-text">No tutors.</p>';
        tutors.forEach(t => {
            const card = document.createElement('div');
            card.className = 'tutor-card';
            card.innerHTML = `
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(t.name)}&background=random" class="tutor-img">
                <div class="tutor-info">
                    <h3>${t.name}</h3>
                    <p class="tutor-title">${t.subjects || 'Professional Tutor'}</p>
                </div>
                <div class="card-actions"><button class="btn btn-block btn-primary book-btn" data-id="${t.id}" data-subject="${t.subjects?.split(',')[0].trim() || 'General Learning'}">Book Session</button></div>`;
            
            const bookBtn = card.querySelector('.book-btn');
            bookBtn.onclick = async () => {
                document.getElementById('modal-tutor-id').value = t.id;
                document.getElementById('modal-subject').value = bookBtn.getAttribute('data-subject');
                
                // Fetch tutor's availability to show in modal
                try {
                    const res = await fetch(`${API_BASE}/profile/tutor/${t.id}`);
                    const data = await res.json();
                    const availText = data.availability_info || 'No availability set yet.';
                    
                    // Add availability help text to modal if not present
                    let helpText = document.getElementById('modal-availability-help');
                    if (!helpText) {
                        helpText = document.createElement('p');
                        helpText.id = 'modal-availability-help';
                        helpText.style.fontSize = '0.85rem';
                        helpText.style.color = 'var(--primary)';
                        helpText.style.marginBottom = '1rem';
                        const subjInput = document.getElementById('modal-subject');
                        subjInput.parentNode.insertBefore(helpText, subjInput.nextSibling);
                    }
                    helpText.innerHTML = `<strong>Tutor's Availability:</strong><br>${availText}`;
                } catch (err) { console.error(err); }

                bookingModal.classList.remove('hidden');
                bookingModal.style.display = 'flex';
            };

            container.appendChild(card);
        });
    }

    // --- Feedback Modal Logic ---
    if (closeFeedbackModalBtn) {
        closeFeedbackModalBtn.onclick = () => {
            feedbackModal.classList.add('hidden');
            feedbackModal.style.display = 'none';
        };
    }

    if (feedbackForm) {
        feedbackForm.onsubmit = async (e) => {
            e.preventDefault();
            const feedbackData = {
                student_id: studentId,
                tutor_id: document.getElementById('feedback-tutor-id').value,
                subject: document.getElementById('feedback-subject').value,
                rating: document.getElementById('feedback-rating').value,
                comment: document.getElementById('feedback-comment').value,
                student_skill_level: document.getElementById('feedback-skill-level').value
            };

            try {
                const res = await fetch(`${API_BASE}/feedback`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(feedbackData)
                });

                if (res.ok) {
                    alert('Thank you for your feedback!');
                    feedbackModal.classList.add('hidden');
                    feedbackModal.style.display = 'none';
                    loadSchedule(); // Refresh to ensure everything is updated
                } else {
                    const error = await res.json();
                    alert(`Submission failed: ${error.error}`);
                }
            } catch (err) {
                console.error(err);
                alert('Connection error');
            }
        };
    }

    // --- Booking Modal Logic ---
    if (closeModalBtn) {
        closeModalBtn.onclick = () => {
            bookingModal.classList.add('hidden');
            bookingModal.style.display = 'none';
        };
    }

    if (bookingForm) {
        bookingForm.onsubmit = async (e) => {
            e.preventDefault();
            const bookingData = {
                student_id: studentId,
                tutor_id: document.getElementById('modal-tutor-id').value,
                subject: document.getElementById('modal-subject').value,
                date: document.getElementById('modal-date').value,
                time: document.getElementById('modal-time').value
            };

            try {
                const res = await fetch(`${API_BASE}/schedule/book`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bookingData)
                });

                if (res.ok) {
                    alert('Session booked successfully!');
                    bookingModal.classList.add('hidden');
                    bookingModal.style.display = 'none';
                    loadSchedule(); // Refresh schedule
                } else {
                    const error = await res.json();
                    alert(`Booking failed: ${error.error}`);
                }
            } catch (err) {
                console.error(err);
                alert('Connection error');
            }
        };
    }

    // Default Section
    switchSection('overview-section');
    setInterval(checkNotifications, 30000);
    setInterval(() => {
        if (activeChatTutorId) loadChatMessages();
    }, 5000);
});
