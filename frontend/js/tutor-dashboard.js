document.addEventListener('DOMContentLoaded', () => {
    // --- Auth Check ---
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || user.role !== 'tutor') {
        window.location.href = 'login.html';
        return;
    }

    const tutorId = user.role_id;
    const userId = user.id;
    let activeChatUserId = null;

    const headerUserName = document.getElementById('header-user-name');
    if (headerUserName) headerUserName.textContent = user.name;
    const headerAvatar = document.getElementById('header-avatar');
    if (headerAvatar) headerAvatar.textContent = user.name.substring(0, 2).toUpperCase();

    // --- Navigation ---
    const sidebarLinks = document.querySelectorAll('.sidebar-link[data-section]');
    const sections = document.querySelectorAll('.dashboard-section');

    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('data-section');
            sidebarLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            sections.forEach(s => s.classList.remove('active'));
            const activeSec = document.getElementById(targetSection);
            if (activeSec) activeSec.classList.add('active');

            if (targetSection === 'overview') loadOverview();
            if (targetSection === 'schedule') loadTutorSchedule();
            if (targetSection === 'messages') loadMessaging();
            if (targetSection === 'profile') loadTutorProfile();
            if (targetSection === 'availability') loadAvailability();
        });
    });

    function initNotifications() {
        const notifBell = document.getElementById('notif-bell');
        const notifDropdown = document.getElementById('notif-dropdown');
        if (!notifBell) return;
        
        notifBell.onclick = (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle('hidden');
            if (!notifDropdown.classList.contains('hidden')) loadNotifications();
        };

        window.onclick = () => { if(notifDropdown) notifDropdown.classList.add('hidden'); };
        if(notifDropdown) notifDropdown.onclick = (e) => e.stopPropagation();

        const markReadBtn = document.getElementById('mark-all-read');
        if (markReadBtn) {
            markReadBtn.onclick = async () => {
                // Implementation for marking all as read if needed
                const badge = document.getElementById('notif-count');
                if (badge) badge.classList.add('hidden');
            };
        }

        setInterval(checkNotificationCount, 30000);
        checkNotificationCount();
    }

    async function checkNotificationCount() {
        try {
            const res = await fetch(`/api/notifications/${userId}`);
            const data = await res.json();
            const unreadCount = data.filter(n => !n.is_read).length;
            const badge = document.getElementById('notif-count');
            if (badge) {
                if (unreadCount > 0) {
                    badge.textContent = unreadCount;
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            }
        } catch (err) { console.error(err); }
    }

    async function loadNotifications() {
        const container = document.getElementById('notif-list');
        if (!container) return;
        container.innerHTML = '<div class="loading-state">Loading...</div>';
        try {
            const res = await fetch(`/api/notifications/${userId}`);
            const data = await res.json();
            container.innerHTML = '';
            if (data.length === 0) {
                container.innerHTML = '<p class="empty-text">No notifications</p>';
                return;
            }
            data.forEach(n => {
                const item = document.createElement('div');
                item.className = `notif-item ${n.is_read ? '' : 'unread'}`;
                item.innerHTML = `<p>${n.message}</p><span>${n.created_at}</span>`;
                item.onclick = async () => {
                    await fetch(`/api/notifications/read/${n.id}`, { method: 'POST' });
                    item.classList.remove('unread');
                    checkNotificationCount();
                };
                container.appendChild(item);
            });
        } catch (err) { console.error(err); }
    }

    // --- MESSAGING ---
    async function loadMessaging() {
        try {
            const res = await fetch(`/api/schedules/tutor/${tutorId}`);
            const sessions = await res.json();
            const students = [];
            const seen = new Set();
            sessions.forEach(s => {
                if (!seen.has(s.student_name)) {
                    students.push({ name: s.student_name, user_id: s.student_user_id }); 
                    seen.add(s.student_name);
                }
            });
            renderContacts(students);
        } catch (err) { console.error(err); }
    }

    function renderContacts(students) {
        const list = document.getElementById('contacts-list');
        if (!list) return;
        list.innerHTML = '';
        if (students.length === 0) {
            list.innerHTML = '<p class="empty-text">No students yet.</p>';
            return;
        }
        students.forEach(s => {
            const item = document.createElement('div');
            item.className = 'contact-item';
            const name = s.name || 'Unknown Student';
            const avatar = name.substring(0,2);
            item.innerHTML = `
                <div class="user-avatar" style="width: 40px; height: 40px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-weight: 600;">${avatar}</div>
                <div class="contact-info"><h4>${name}</h4><p>Student</p></div>`;
            item.onclick = () => {
                document.querySelectorAll('.contact-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                openChat(s);
            };
            list.appendChild(item);
        });
    }

    function openChat(student) {
        console.log('openChat called for student:', student);
        activeChatUserId = student.user_id;
        
        const placeholder = document.querySelector('.chat-placeholder');
        if (placeholder) placeholder.style.display = 'none';
        
        const info = document.querySelector('.selected-user-info');
        if (info) info.style.display = 'flex';
        
        const nameHeader = document.getElementById('chat-user-name');
        const avatarHeader = document.getElementById('chat-avatar');
        
        const name = student.name || 'Unknown Student';
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
        if (!activeChatUserId) return;
        try {
            const res = await fetch(`/api/messages/${userId}?other_id=${activeChatUserId}`);
            const messages = await res.json();
            const list = document.getElementById('message-list');
            if (!list) return;
            list.innerHTML = '';
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
                
                list.appendChild(bubble);
            });
            list.scrollTop = list.scrollHeight;
        } catch (err) { console.error(err); }
    }

    const sendBtn = document.getElementById('send-msg-btn');
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
                    const res = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (res.ok) {
                        // Send message with file_url immediately
                        await fetch('/api/messages', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                sender_id: userId, 
                                receiver_id: activeChatUserId, 
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

    if (sendBtn) {
        sendBtn.onclick = async () => {
            const input = document.getElementById('message-input');
            const content = input.value.trim();
            if (!content || !activeChatUserId) return;
            try {
                await fetch('/api/messages', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sender_id: userId, receiver_id: activeChatUserId, content: content })
                });
                input.value = '';
                loadChatMessages();
            } catch (err) { console.error(err); }
        };
    }

    const msgInput = document.getElementById('message-input');
    if (msgInput) {
        msgInput.onkeydown = (e) => {
            if (e.key === 'Enter') sendBtn.click();
        };
    }

    // --- Data Loaders (Remaining) ---

    async function loadOverview() {
        try {
            const res = await fetch(`/api/schedules/tutor/${tutorId}`);
            const sessions = await res.json();

            const studentsCount = new Set(sessions.map(s => s.student_name)).size;
            updateTutorMetrics(studentsCount);
            renderRecentStudents(sessions);
            initCharts();

            const upcomingList = document.getElementById('upcoming-sessions-list');
            if (upcomingList) {
                upcomingList.innerHTML = '';
                const upcoming = sessions.filter(s => s.status === 'upcoming');
                if (upcoming.length === 0) {
                    upcomingList.innerHTML = '<p class="empty-text">No upcoming sessions today.</p>';
                } else {
                    upcoming.slice(0, 3).forEach(s => {
                        const item = document.createElement('div');
                        item.className = 'dashboard-list-item';
                        item.innerHTML = `
                             <div class="item-icon"><i class="fas fa-video"></i></div>
                             <div class="item-details">
                                 <h4>${s.subject}</h4>
                                 <p>Student: ${s.student_name}</p>
                             </div>
                             <div class="item-meta">
                                 <span class="item-time">${s.time}</span>
                                 <span class="item-date">${s.date}</span>
                             </div>`;
                        upcomingList.appendChild(item);
                    });
                }
            }
        } catch (err) { console.error(err); }
    }

    function updateTutorMetrics(studentCount) {
        const s = document.getElementById('stat-students');
        if (s) s.textContent = studentCount || '0';
    }

    function renderRecentStudents(sessions) {
        const container = document.getElementById('recent-students-list');
        if (!container) return;
        const recent = [];
        const seen = new Set();
        sessions.forEach(s => {
            if (!seen.has(s.student_name)) {
                recent.push(s);
                seen.add(s.student_name);
            }
        });
        container.innerHTML = '';
        recent.slice(0, 4).forEach(s => {
            const item = document.createElement('div');
            item.className = 'dashboard-list-item';
            item.innerHTML = `
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(s.student_name)}&background=random" style="width: 32px; height: 32px; border-radius: 50%;">
                <div class="item-details"><h4>${s.student_name}</h4><p>${s.subject}</p></div>
                <div class="item-meta"><span class="item-date">Active</span></div>`;
            container.appendChild(item);
        });
    }

    function initCharts() {
        const revElem = document.getElementById('revenueChart');
        if (revElem) {
            const revCtx = revElem.getContext('2d');
            new Chart(revCtx, {
                type: 'bar',
                data: {
                    labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
                    datasets: [{ label: 'Revenue ($)', data: [1200, 1650, 1400, 1800, 2150, 2340], backgroundColor: '#6C63FF', borderRadius: 6 }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }
        const growthElem = document.getElementById('growthChart');
        if (growthElem) {
            const growthCtx = growthElem.getContext('2d');
            new Chart(growthCtx, {
                type: 'line',
                data: {
                    labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
                    datasets: [{ label: 'Students', data: [8, 10, 9, 11, 12, 14], borderColor: '#6C63FF', fill: true, tension: 0.4 }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }
    }

    async function loadTutorSchedule() {
        const tableBody = document.getElementById('tutor-schedule-table');
        if (!tableBody) return;
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
        try {
            const res = await fetch(`/api/schedules/tutor/${tutorId}`);
            const sessions = await res.json();
            tableBody.innerHTML = '';
            sessions.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${s.student_name}</td>
                    <td>${s.subject}</td>
                    <td>${s.date} at ${s.time}</td>
                    <td><span class="badge ${s.status}">${s.status}</span></td>
                    <td><a href="${s.meeting_link}" target="_blank" class="btn btn-sm btn-outline">Join</a></td>`;
                tableBody.appendChild(tr);
            });
        } catch (err) { console.error(err); }
    }

    async function loadTutorProfile() {
        try {
            const res = await fetch(`/api/profile/tutor/${tutorId}`);
            const data = await res.json();
            const n = document.getElementById('t-prof-name'); if(n) n.value = data.name;
            const e = document.getElementById('t-prof-email'); if(e) e.value = data.email;
            const s = document.getElementById('t-prof-subjects'); if(s) s.value = data.subjects || '';
            const ex = document.getElementById('t-prof-exp'); if(ex) ex.value = data.experience || '';
            const pn = document.getElementById('tutor-profile-name'); if(pn) pn.textContent = data.name;
            
            // Also update availability input if we are on that section
            const avInput = document.getElementById('tutor-availability-input');
            if(avInput) avInput.value = data.availability_info || '';
        } catch (err) { console.error(err); }
    }

    async function loadAvailability() {
        await loadTutorProfile();
    }

    const saveAvailBtn = document.getElementById('save-availability-btn');
    if (saveAvailBtn) {
        saveAvailBtn.onclick = async () => {
            const availability = document.getElementById('tutor-availability-input').value;
            try {
                const res = await fetch('/api/tutor/availability', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tutor_id: tutorId, availability_info: availability })
                });
                if (res.ok) {
                    alert('Availability updated successfully!');
                } else {
                    alert('Failed to update availability');
                }
            } catch (err) { console.error(err); }
        };
    }

    // --- Profile Actions ---
    const editBtn = document.getElementById('tutor-edit-profile-btn');
    const cancelBtn = document.getElementById('t-cancel-profile-btn');
    const profileForm = document.getElementById('tutor-profile-form');

    if (editBtn) {
        editBtn.onclick = () => {
            profileForm.querySelectorAll('input').forEach(i => i.disabled = false);
            document.getElementById('t-profile-actions').classList.remove('hidden');
            editBtn.classList.add('hidden');
        };
    }
    if (cancelBtn) {
        cancelBtn.onclick = () => {
            profileForm.querySelectorAll('input').forEach(i => i.disabled = true);
            document.getElementById('t-profile-actions').classList.add('hidden');
            editBtn.classList.remove('hidden');
        };
    }

    // Initial Load
    loadOverview();
    initNotifications();
    setInterval(() => {
        if (activeChatUserId) loadChatMessages();
    }, 5000);
});
