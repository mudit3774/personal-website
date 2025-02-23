// JavaScript for interactive features
console.log('Welcome to Mudit Gupta\'s personal website!');

// Function to load resume data
async function loadResumeData() {
    try {
        console.log('Attempting to load resume data...');
        const response = await fetch('/static/assets/resume_data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log('Resume data fetched successfully');
        const data = await response.json();
        console.log('Resume data parsed:', data);
        
        // Populate summary
        const summaryElement = document.getElementById('summary');
        if (summaryElement) {
            summaryElement.innerHTML = `
                <p class="summary-text">${data.summary}</p>
            `;
            console.log('Summary populated');
        } else {
            console.error('Summary element not found');
        }
        
        // Populate experience
        const experienceContent = document.getElementById('experience-content');
        if (experienceContent) {
            experienceContent.innerHTML = data.experience
                .map(exp => `
                    <div class="experience-item">
                        <h3>${exp.company}</h3>
                        <div class="role-duration">
                            <span class="role">${exp.role}</span>
                            <span class="duration">${exp.duration}</span>
                        </div>
                        <ul class="experience-description">
                            ${exp.description.map(desc => `<li>${desc}</li>`).join('')}
                        </ul>
                    </div>
                `).join('');
            console.log('Experience populated');
        } else {
            console.error('Experience element not found');
        }
        
        // Populate education
        const educationContent = document.getElementById('education-content');
        if (educationContent) {
            educationContent.innerHTML = data.education
                .map(edu => `
                    <div class="education-item">
                        <h3>${edu.school}</h3>
                        <div class="degree-duration">
                            <span class="degree">${edu.degree}</span>
                            <span class="duration">${edu.duration}</span>
                        </div>
                    </div>
                `).join('');
            console.log('Education populated');
        } else {
            console.error('Education element not found');
        }
        
        // Populate skills
        const skillsContent = document.getElementById('skills-content');
        if (skillsContent) {
            skillsContent.innerHTML = data.skills
                .map(skill => `<span class="skill-tag">${skill}</span>`)
                .join('');
            console.log('Skills populated');
        } else {
            console.error('Skills element not found');
        }
            
    } catch (error) {
        console.error('Error loading resume data:', error);
        // Display error message on the page
        document.querySelectorAll('section div').forEach(div => {
            div.innerHTML = `<p class="error">Error loading content. Please try refreshing the page.</p>`;
        });
    }
}

// Handle contact form submission
const contactForm = document.getElementById('contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                message: document.getElementById('message').value
            };
            
            const response = await fetch('http://localhost:5006/api/contacts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to submit form');
            }
            
            const result = await response.json();
            console.log('Form submitted successfully:', result);
            alert('Thank you for your message! I will get back to you soon.');
            this.reset();
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Sorry, there was an error submitting your message. Please try again.');
        }
    });
}

// Add smooth scrolling for navigation links
document.querySelectorAll('nav a').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Meeting Scheduler Functions
async function loadAvailableSlots() {
    const dateInput = document.getElementById('meeting-date');
    const slotSelect = document.getElementById('time-slot');
    
    if (!dateInput.value) {
        return;
    }

    try {
        const response = await fetch(`http://localhost:5006/api/available-slots?start_date=${dateInput.value}&days=1`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to load available slots');
        }
        
        const slots = await response.json();
        
        // Clear existing options
        slotSelect.innerHTML = '<option value="">Select a time slot</option>';
        
        // Sort slots by time
        slots.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
        
        // Add new options
        slots.forEach(slot => {
            const datetime = new Date(slot.datetime);
            const option = document.createElement('option');
            option.value = JSON.stringify(slot);
            option.textContent = `${datetime.toLocaleTimeString()} (${slot.duration} minutes)`;
            slotSelect.appendChild(option);
        });

        if (slots.length === 0) {
            const option = document.createElement('option');
            option.disabled = true;
            option.textContent = 'No available slots for this date';
            slotSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading available slots:', error);
        slotSelect.innerHTML = '<option value="">Error loading slots</option>';
    }
}

async function bookAppointment() {
    const slotSelect = document.getElementById('time-slot');
    const emailInput = document.getElementById('meeting-email');
    const agendaInput = document.getElementById('meeting-agenda');
    
    // Clear previous errors
    document.querySelectorAll('.form-group').forEach(group => group.classList.remove('error'));
    
    // Validate inputs
    let isValid = true;
    if (!slotSelect.value) {
        showError(slotSelect, 'Please select a time slot');
        isValid = false;
    }
    if (!emailInput.value) {
        showError(emailInput, 'Please enter your email');
        isValid = false;
    } else if (!isValidEmail(emailInput.value)) {
        showError(emailInput, 'Please enter a valid email address');
        isValid = false;
    }
    if (!agendaInput.value.trim()) {
        showError(agendaInput, 'Please enter the meeting agenda');
        isValid = false;
    }
    
    if (!isValid) {
        return;
    }

    try {
        const selectedSlot = JSON.parse(slotSelect.value);
        const response = await fetch('http://localhost:5006/api/appointments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: emailInput.value,
                agenda: agendaInput.value,
                datetime: selectedSlot.datetime,
                duration: selectedSlot.duration,
                timeslot_id: selectedSlot.pattern_id
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to book appointment');
        }

        alert('Meeting scheduled successfully! You will receive a confirmation email.');
        
        // Clear form
        emailInput.value = '';
        agendaInput.value = '';
        slotSelect.value = '';
        document.getElementById('meeting-date').value = '';
    } catch (error) {
        console.error('Error booking appointment:', error);
        alert(error.message);
    }
}

function showError(element, message) {
    const formGroup = element.closest('.form-group');
    formGroup.classList.add('error');
    
    let errorDiv = formGroup.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        formGroup.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function updateAmount() {
    const duration = parseInt(document.getElementById('duration').value);
    const baseAmount = Math.max(500, Math.floor(duration / 30) * 500);
    const amountInput = document.getElementById('amount');
    amountInput.value = baseAmount;
    amountInput.min = baseAmount;
    document.querySelector('.payment-amount').textContent = `₹${baseAmount}`;
}

function validateAmount() {
    const duration = parseInt(document.getElementById('duration').value);
    const minAmount = Math.floor(duration / 30) * 500;
    const amount = parseInt(document.getElementById('amount').value);
    const amountInput = document.getElementById('amount');
    
    if (amount < minAmount) {
        amountInput.value = minAmount;
        document.querySelector('.payment-amount').textContent = `₹${minAmount}`;
    } else {
        document.querySelector('.payment-amount').textContent = `₹${amount}`;
    }
}

async function handlePayment() {
    const dateInput = document.getElementById('meeting-date');
    const slotSelect = document.getElementById('time-slot');
    const emailInput = document.getElementById('meeting-email');
    const agendaInput = document.getElementById('meeting-agenda');
    const durationInput = document.getElementById('duration');
    const amountInput = document.getElementById('amount');

    // Reset error states
    document.querySelectorAll('.form-group').forEach(group => group.classList.remove('error'));

    // Validate inputs
    let hasError = false;
    if (!dateInput.value) {
        dateInput.parentElement.classList.add('error');
        dateInput.parentElement.querySelector('.error-message').textContent = 'Please select a date';
        hasError = true;
    }
    if (!slotSelect.value) {
        slotSelect.parentElement.classList.add('error');
        slotSelect.parentElement.querySelector('.error-message').textContent = 'Please select a time slot';
        hasError = true;
    }
    if (!emailInput.value || !emailInput.value.includes('@')) {
        emailInput.parentElement.classList.add('error');
        emailInput.parentElement.querySelector('.error-message').textContent = 'Please enter a valid email';
        hasError = true;
    }
    if (!agendaInput.value) {
        agendaInput.parentElement.classList.add('error');
        agendaInput.parentElement.querySelector('.error-message').textContent = 'Please enter meeting agenda';
        hasError = true;
    }

    if (hasError) return;

    try {
        // Create order on server
        const response = await fetch('http://localhost:5006/api/create-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: parseInt(amountInput.value),
                email: emailInput.value,
                duration: parseInt(durationInput.value),
                date: dateInput.value,
                timeSlot: JSON.parse(slotSelect.value),
                agenda: agendaInput.value
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create order');
        }

        const orderData = await response.json();

        // Initialize Razorpay payment
        const options = {
            key: 'YOUR_RAZORPAY_KEY_ID', // Replace with your actual key
            amount: orderData.amount,
            currency: 'INR',
            name: 'Coffee/Beer Chat with Mudit',
            description: `${durationInput.value} minutes consultation`,
            order_id: orderData.id,
            handler: async function(response) {
                // Verify payment on server
                const verifyResponse = await fetch('http://localhost:5006/api/verify-payment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_signature: response.razorpay_signature
                    })
                });

                if (!verifyResponse.ok) {
                    throw new Error('Payment verification failed');
                }

                // Book the appointment
                await bookAppointment(orderData.id);
                alert('Meeting scheduled successfully! Check your email for details.');
            },
            prefill: {
                email: emailInput.value
            },
            theme: {
                color: '#6c5ce7'
            }
        };

        const razorpay = new Razorpay(options);
        razorpay.open();

    } catch (error) {
        alert(error.message || 'Something went wrong. Please try again.');
    }
}

async function bookAppointment(orderId) {
    const dateInput = document.getElementById('meeting-date');
    const slotSelect = document.getElementById('time-slot');
    const emailInput = document.getElementById('meeting-email');
    const agendaInput = document.getElementById('meeting-agenda');
    const durationInput = document.getElementById('duration');

    try {
        const selectedSlot = JSON.parse(slotSelect.value);
        const response = await fetch('http://localhost:5006/api/appointments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: dateInput.value,
                slot: selectedSlot,
                email: emailInput.value,
                agenda: agendaInput.value,
                duration: parseInt(durationInput.value),
                order_id: orderId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to schedule the meeting');
        }

    } catch (error) {
        throw new Error('Failed to schedule the meeting. Please contact support.');
    }
}

// Set minimum date for date picker to today
document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('meeting-date');
    if (dateInput) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        dateInput.min = `${yyyy}-${mm}-${dd}`;
    }
    
    console.log('DOM loaded, loading resume data...');
    loadResumeData();
});
