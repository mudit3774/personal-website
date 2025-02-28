// Tab switching functionality
function showTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`[onclick="showTab('${tabId}')"]`).classList.add('active');
}

// Time Slots Management
function createTimeSlot(event) {
    event.preventDefault();
    
    if (!validateTimeSlotForm()) {
        return;
    }

    const date = document.getElementById('slot-date').value;
    const time = document.getElementById('slot-time').value;
    const duration = document.getElementById('slot-duration').value;

    fetch('/api/timeslots', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ date, time, duration }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('time-slot-form').reset();
            loadTimeSlots();
        } else {
            showError(document.getElementById('slot-date'), data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError(document.getElementById('slot-date'), 'Failed to create time slot');
    });
}

function showError(element, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    element.parentNode.appendChild(errorDiv);
}

function clearError(element) {
    const errorDiv = element.parentNode.querySelector('.error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function validateTimeSlotForm() {
    let isValid = true;
    const date = document.getElementById('slot-date');
    const time = document.getElementById('slot-time');
    const duration = document.getElementById('slot-duration');

    clearError(date);
    clearError(time);
    clearError(duration);

    if (!date.value) {
        showError(date, 'Date is required');
        isValid = false;
    }

    if (!time.value) {
        showError(time, 'Time is required');
        isValid = false;
    }

    if (!duration.value) {
        showError(duration, 'Duration is required');
        isValid = false;
    }

    return isValid;
}

function loadTimeSlots() {
    fetch('/api/timeslots')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('time-slots');
            container.innerHTML = '';
            
            data.forEach(slot => {
                const slotElement = document.createElement('div');
                slotElement.className = 'time-slot';
                slotElement.innerHTML = `
                    <p>${formatDate(slot.date)} at ${slot.time}</p>
                    <p>${slot.duration} minutes</p>
                    <button onclick="deleteTimeSlot(${slot.id})" class="button button-danger">Delete</button>
                `;
                container.appendChild(slotElement);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Appointments Management
function loadAppointments() {
    fetch('/api/appointments')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('appointments');
            container.innerHTML = '';
            
            data.forEach(appointment => {
                const appointmentElement = document.createElement('div');
                appointmentElement.className = 'appointment';
                appointmentElement.innerHTML = `
                    <h3>${appointment.name}</h3>
                    <p>${formatDate(appointment.date)} at ${appointment.time}</p>
                    <p>Duration: ${appointment.duration} minutes</p>
                    <textarea onchange="updateNotes(${appointment.id})" placeholder="Add notes...">${appointment.notes || ''}</textarea>
                `;
                container.appendChild(appointmentElement);
            });
        })
        .catch(error => console.error('Error:', error));
}

function updateNotes(appointmentId) {
    const textarea = event.target;
    fetch(`/api/appointments/${appointmentId}/notes`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ notes: textarea.value }),
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Failed to update notes');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Contact Messages Management
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function toggleReplyForm(id) {
    const form = document.getElementById(`reply-form-${id}`);
    const button = document.querySelector(`[onclick="toggleReplyForm(${id})"]`);
    
    if (form.classList.contains('active')) {
        form.classList.remove('active');
        button.textContent = 'Reply';
    } else {
        form.classList.add('active');
        button.textContent = 'Cancel';
    }
}

function sendReply(id) {
    const replyText = document.getElementById(`reply-${id}`).value;
    
    fetch(`/api/contact/${id}/reply`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reply: replyText }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            toggleReplyForm(id);
            document.getElementById(`reply-${id}`).value = '';
            
            // Update status in UI
            const statusElement = document.querySelector(`#message-${id} .message-meta`);
            statusElement.textContent = 'Status: Replied';
        } else {
            alert('Failed to send reply');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error sending reply');
    });
}

function deleteContact(id) {
    if (!confirm('Are you sure you want to delete this message?')) {
        return;
    }

    fetch(`/api/contact/${id}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`message-${id}`).remove();
        } else {
            alert('Failed to delete message');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting message');
    });
}

function loadContacts() {
    fetch('/api/contact')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('messages');
            container.innerHTML = '';
            
            data.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.className = 'message-card';
                messageElement.id = `message-${message.id}`;
                
                messageElement.innerHTML = `
                    <div class="message-header">
                        <div>
                            <h3>${message.name}</h3>
                            <p class="message-meta">
                                ${message.email} | ${formatDate(message.date)}
                                Status: ${message.replied ? 'Replied' : 'Pending'}
                            </p>
                        </div>
                    </div>
                    
                    <div class="message-content">
                        ${message.message}
                    </div>
                    
                    <div class="message-actions">
                        <button onclick="toggleReplyForm(${message.id})" class="button button-primary">
                            Reply
                        </button>
                        <button onclick="deleteContact(${message.id})" class="button button-danger">
                            Delete
                        </button>
                    </div>
                    
                    <div id="reply-form-${message.id}" class="reply-form">
                        <div class="form-group">
                            <label for="reply-${message.id}">Your Reply</label>
                            <textarea id="reply-${message.id}" required></textarea>
                        </div>
                        <button onclick="sendReply(${message.id})" class="button button-primary">
                            Send Reply
                        </button>
                    </div>
                `;
                
                container.appendChild(messageElement);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Load all data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadContacts();
    loadTimeSlots();
    loadAppointments();
    
    // Show first tab by default
    showTab('messages-tab');
});
