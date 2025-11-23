const API_BASE = 'http://127.0.0.1:5000/api';
let currentUser = null;
let courses = {};
let subjectCodes = {};

// Load courses and subject codes on startup
async function loadInitialData() {
    try {
        const coursesResponse = await fetch(`${API_BASE}/courses`);
        courses = await coursesResponse.json();
        
        const subjectCodesResponse = await fetch(`${API_BASE}/subject-codes`);
        subjectCodes = await subjectCodesResponse.json();
        
        populateCourseDropdowns();
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

function populateCourseDropdowns() {
    // Registration course dropdown
    const regCourseSelect = document.getElementById('regCourse');
    const filterCourseSelect = document.getElementById('filterCourse');
    const noteCourseSelect = document.getElementById('noteCourse');
    
    // Clear existing options except the first one
    [regCourseSelect, filterCourseSelect, noteCourseSelect].forEach(select => {
        while (select.options.length > 1) {
            select.remove(1);
        }
    });
    
    // Add course options
    Object.entries(courses).forEach(([code, name]) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = `${code} - ${name}`;
        
        regCourseSelect.appendChild(option.cloneNode(true));
        filterCourseSelect.appendChild(option.cloneNode(true));
        noteCourseSelect.appendChild(option.cloneNode(true));
    });
}

// Show/hide sections
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionName).classList.add('active');
    updateNavigation();
    
    if (sectionName === 'dashboard') {
        loadDashboard();
    } else if (sectionName === 'notes') {
        loadNotes();
    }
}

// Update navigation based on login status
function updateNavigation() {
    const isLoggedIn = currentUser !== null;
    
    document.getElementById('loginLink').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('registerLink').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('dashboardLink').style.display = isLoggedIn ? 'block' : 'none';
    document.getElementById('notesLink').style.display = isLoggedIn ? 'block' : 'none';
    document.getElementById('uploadLink').style.display = isLoggedIn ? 'block' : 'none';
    document.getElementById('logoutLink').style.display = isLoggedIn ? 'block' : 'none';
}

// Register user
async function registerUser(event) {
    event.preventDefault();
    
    const userData = {
        name: document.getElementById('regName').value,
        email: document.getElementById('regEmail').value,
        phone: document.getElementById('regPhone').value,
        roll_number: document.getElementById('regRoll').value,
        course: document.getElementById('regCourse').value,
        course_duration: document.getElementById('regDuration').value,
        is_professor: document.getElementById('regIsProfessor').checked,
        password: document.getElementById('regPassword').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('registerMessage', 'Registration successful! Please login.', 'success');
            document.querySelector('#register form').reset();
            setTimeout(() => showSection('login'), 2000);
        } else {
            showMessage('registerMessage', data.message, 'error');
        }
    } catch (error) {
        showMessage('registerMessage', 'Registration failed. Please try again.', 'error');
    }
}

// Login user
async function loginUser(event) {
    event.preventDefault();
    
    const loginData = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showMessage('loginMessage', 'Login successful!', 'success');
            document.querySelector('#login form').reset();
            setTimeout(() => {
                showSection('dashboard');
                updateNavigation();
            }, 1000);
        } else {
            showMessage('loginMessage', data.message, 'error');
        }
    } catch (error) {
        showMessage('loginMessage', 'Login failed. Please check your connection.', 'error');
    }
}

// Logout
function logout() {
    currentUser = null;
    showSection('home');
    updateNavigation();
}

// Load dashboard data
async function loadDashboard() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${API_BASE}/user/dashboard?user_id=${currentUser.id}`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('userName').textContent = data.user.name;
            displayProfileInfo(data.user);
            displayDonatedNotes(data.donated_notes);
            displayReceivedNotes(data.received_notes);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function displayProfileInfo(user) {
    const profileInfo = document.getElementById('profileInfo');
    profileInfo.innerHTML = `
        <p><strong>Name:</strong> ${user.name}</p>
        <p><strong>Email:</strong> ${user.email}</p>
        <p><strong>Phone:</strong> ${user.phone}</p>
        <p><strong>Roll Number:</strong> ${user.roll_number}</p>
        <p><strong>Course:</strong> ${courses[user.course] || user.course}</p>
        <p><strong>Course Duration:</strong> ${user.course_duration}</p>
    `;
}

function displayDonatedNotes(notes) {
    const container = document.getElementById('donatedNotes');
    
    if (notes.length === 0) {
        container.innerHTML = '<p class="no-notes">No notes donated yet.</p>';
        return;
    }
    
    container.innerHTML = notes.map(note => `
        <div class="note-card">
            <div class="note-header">
                <div class="note-title-container">
                    <h4>${note.title}</h4>
                    ${note.subject_code ? `<span class="subject-code">${note.subject_code}</span>` : ''}
                </div>
            </div>
            <p><strong>Subject:</strong> ${note.subject}</p>
            <p><strong>Rating:</strong> ${note.avg_rating}/5</p>
            <p><strong>Downloads:</strong> ${note.download_count}</p>
        </div>
    `).join('');
}

function displayReceivedNotes(notes) {
    const container = document.getElementById('receivedNotes');
    
    if (notes.length === 0) {
        container.innerHTML = '<p class="no-notes">No notes accessed yet.</p>';
        return;
    }
    
    container.innerHTML = notes.map(note => `
        <div class="note-card">
            <div class="note-header">
                <div class="note-title-container">
                    <h4>${note.title}</h4>
                    ${note.subject_code ? `<span class="subject-code">${note.subject_code}</span>` : ''}
                </div>
            </div>
            <p><strong>Subject:</strong> ${note.subject}</p>
            <p><strong>Accessed:</strong> ${new Date(note.accessed_at).toLocaleDateString()}</p>
        </div>
    `).join('');
}

// Load and display notes
async function loadNotes() {
    const course = document.getElementById('filterCourse').value;
    const semester = document.getElementById('filterSemester').value;
    const search = document.getElementById('filterSearch').value;
    
    const params = new URLSearchParams();
    if (course) params.append('course', course);
    if (semester) params.append('semester', semester);
    if (search) params.append('search', search);
    
    try {
        const response = await fetch(`${API_BASE}/notes?${params}`);
        const notes = await response.json();
        
        displayNotes(notes);
    } catch (error) {
        console.error('Error loading notes:', error);
    }
}

function displayNotes(notes) {
    const container = document.getElementById('notesList');
    
    if (notes.length === 0) {
        container.innerHTML = '<p class="no-notes">No notes found matching your criteria.</p>';
        return;
    }
    
    container.innerHTML = notes.map(note => `
        <div class="note-card">
            <div class="note-header">
                <div class="note-title-container">
                    <h3>${note.title}</h3>
                    ${note.subject_code ? `<span class="subject-code">${note.subject_code}</span>` : ''}
                </div>
                ${note.is_professional ? '<span class="pro-badge">Professional</span>' : ''}
            </div>
            <p class="note-description">${note.description || 'No description'}</p>
            <div class="note-details">
                <p><strong>Subject:</strong> ${note.subject}</p>
                <p><strong>Course:</strong> ${courses[note.course] || note.course}</p>
                <p><strong>Semester:</strong> ${note.semester}</p>
                <p><strong>Uploaded by:</strong> ${note.donor_name}</p>
                <p><strong>Rating:</strong> ${note.avg_rating}/5 ⭐</p>
                <p><strong>Downloads:</strong> ${note.download_count}</p>
            </div>
            <div class="note-actions">
                <button onclick="viewNote(${note.id})" class="view-btn">View Note</button>
                ${note.is_professional && note.price > 0 ? `<span class="price">₹${note.price}</span>` : ''}
            </div>
        </div>
    `).join('');
}

// View note
async function viewNote(noteId) {
    try {
        const url = `${API_BASE}/notes/${noteId}/view?user_id=${currentUser.id}`;
        window.open(url, '_blank');
        
        // Reload notes to update download count
        setTimeout(loadNotes, 1000);
    } catch (error) {
        console.error('Error viewing note:', error);
    }
}

// Upload note
async function uploadNote(event) {
    event.preventDefault();
    
    if (!currentUser) {
        showMessage('uploadMessage', 'Please login to upload notes', 'error');
        return;
    }
    
    const fileInput = document.getElementById('noteFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('uploadMessage', 'Please select a PDF file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', document.getElementById('noteTitle').value);
    formData.append('description', document.getElementById('noteDescription').value);
    formData.append('subject', document.getElementById('noteSubject').value);
    formData.append('subject_code', document.getElementById('noteSubjectCode').value);
    formData.append('course', document.getElementById('noteCourse').value);
    formData.append('semester', document.getElementById('noteSemester').value);
    formData.append('is_professional', document.getElementById('noteIsProfessional').checked);
    formData.append('price', document.getElementById('notePrice').value);
    formData.append('donor_id', currentUser.id);
    
    try {
        const response = await fetch(`${API_BASE}/notes`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('uploadMessage', 'Note uploaded successfully!', 'success');
            document.querySelector('#upload form').reset();
            setTimeout(() => showSection('notes'), 2000);
        } else {
            showMessage('uploadMessage', data.message, 'error');
        }
    } catch (error) {
        showMessage('uploadMessage', 'Upload failed. Please try again.', 'error');
    }
}

// Toggle price field
document.getElementById('noteIsProfessional').addEventListener('change', function() {
    document.getElementById('priceField').style.display = this.checked ? 'block' : 'none';
});

// Utility function to show messages
function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = message;
    element.className = `message ${type}`;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Load courses and subject codes
    loadInitialData();
    
    // Check if user is logged in (from localStorage)
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showSection('dashboard');
        updateNavigation();
    }
    
    // Save user to localStorage when logging in
    const originalLogin = window.loginUser;
    window.loginUser = async function(event) {
        await originalLogin(event);
        if (currentUser) {
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
        }
    };
    
    // Clear localStorage on logout
    const originalLogout = window.logout;
    window.logout = function() {
        originalLogout();
        localStorage.removeItem('currentUser');
    };
});
// Admin Login
async function adminLogin(event) {
    event.preventDefault();
    
    const loginData = {
        username: document.getElementById('adminUsername').value,
        password: document.getElementById('adminPassword').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showMessage('adminLoginMessage', 'Admin login successful!', 'success');
            document.querySelector('#adminLogin form').reset();
            setTimeout(() => {
                showSection('adminDashboard');
                updateNavigation();
                loadAdminDashboard();
            }, 1000);
        } else {
            showMessage('adminLoginMessage', data.message, 'error');
        }
    } catch (error) {
        showMessage('adminLoginMessage', 'Admin login failed. Please check your connection.', 'error');
    }
}

// Load Admin Dashboard
async function loadAdminDashboard() {
    try {
        const response = await fetch(`${API_BASE}/admin/dashboard`);
        const data = await response.json();
        
        if (response.ok) {
            displayAdminOverview(data.overview);
            displayRecentActivities(data.recent_activities);
            displayUsersList(data.all_users);
            displayCourseDistribution(data.course_distribution);
        }
    } catch (error) {
        console.error('Error loading admin dashboard:', error);
    }
}

function displayAdminOverview(overview) {
    document.getElementById('totalUsers').textContent = overview.total_users;
    document.getElementById('totalNotes').textContent = overview.total_notes;
    document.getElementById('totalProfessors').textContent = overview.total_professors;
    document.getElementById('totalDownloads').textContent = overview.total_downloads;
    document.getElementById('todayRegistrations').textContent = overview.today_registrations;
    document.getElementById('todayUploads').textContent = overview.today_uploads;
    document.getElementById('todayDownloads').textContent = overview.today_downloads;
}

function displayRecentActivities(activities) {
    const container = document.getElementById('recentActivities');
    
    if (activities.length === 0) {
        container.innerHTML = '<p class="no-data">No recent activities</p>';
        return;
    }
    
    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-details">
                <span class="activity-type ${activity.type}">${activity.type.replace('_', ' ')}</span>
                <span class="activity-user">${activity.user_name}</span>
                <span class="activity-subject">- ${activity.details}</span>
            </div>
            <div class="activity-time">
                ${new Date(activity.timestamp).toLocaleString()}
            </div>
        </div>
    `).join('');
}

function displayUsersList(users) {
    const container = document.getElementById('usersList');
    
    if (users.length === 0) {
        container.innerHTML = '<p class="no-data">No users registered</p>';
        return;
    }
    
    let html = `
        <div class="user-row header">
            <div>Name</div>
            <div>Email</div>
            <div>Course</div>
            <div>Roll Number</div>
            <div>Role</div>
        </div>
    `;
    
    html += users.map(user => `
        <div class="user-row">
            <div>${user.name}</div>
            <div>${user.email}</div>
            <div>${courses[user.course] || user.course}</div>
            <div>${user.roll_number}</div>
            <div class="user-role ${user.is_professor ? 'role-professor' : 'role-student'}">
                ${user.is_professor ? 'Professor' : 'Student'}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function displayCourseDistribution(distribution) {
    const container = document.getElementById('courseDistribution');
    
    if (Object.keys(distribution).length === 0) {
        container.innerHTML = '<p class="no-data">No course data available</p>';
        return;
    }
    
    // Sort by count descending
    const sortedDistribution = Object.entries(distribution)
        .sort((a, b) => b[1] - a[1]);
    
    container.innerHTML = sortedDistribution.map(([courseCode, count]) => `
        <div class="course-item">
            <span class="course-name">${courses[courseCode] || courseCode}</span>
            <span class="course-count">${count} users</span>
        </div>
    `).join('');
}

// Update the showSection function to handle admin dashboard
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionName).classList.add('active');
    updateNavigation();
    
    if (sectionName === 'dashboard') {
        loadDashboard();
    } else if (sectionName === 'notes') {
        loadNotes();
    } else if (sectionName === 'adminDashboard') {
        loadAdminDashboard();
    }
}

// Update the updateNavigation function for admin
function updateNavigation() {
    const isLoggedIn = currentUser !== null;
    const isAdmin = currentUser && currentUser.role === 'admin';
    const isRegularUser = currentUser && (currentUser.role === 'student' || currentUser.role === 'professor');
    
    document.getElementById('loginLink').style.display = (isLoggedIn || isAdmin) ? 'none' : 'block';
    document.getElementById('adminLoginLink').style.display = (isLoggedIn || isAdmin) ? 'none' : 'block';
    document.getElementById('registerLink').style.display = (isLoggedIn || isAdmin) ? 'none' : 'block';
    document.getElementById('dashboardLink').style.display = isRegularUser ? 'block' : 'none';
    document.getElementById('adminDashboardLink').style.display = isAdmin ? 'block' : 'none';
    document.getElementById('notesLink').style.display = isRegularUser ? 'block' : 'none';
    document.getElementById('uploadLink').style.display = isRegularUser ? 'block' : 'none';
    document.getElementById('logoutLink').style.display = isLoggedIn ? 'block' : 'none';
}

// Update logout function
function logout() {
    currentUser = null;
    showSection('home');
    updateNavigation();
}