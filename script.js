// Experience section data
const experienceData = [
    {
        title: 'Senior Software Engineer',
        company: 'Tech Company',
        duration: '2023 - Present',
        description: 'Leading development of microservices architecture and ML pipelines.'
    },
    // Add more experiences here
];

// Projects section data
const projectsData = [
    {
        name: 'ML Pipeline Framework',
        description: 'Developed a scalable machine learning pipeline framework.',
        technologies: ['Python', 'TensorFlow', 'Docker'],
        github: 'https://github.com/yourusername/project1'
    },
    // Add more projects here
];

// Populate experience section
function populateExperience() {
    const experienceContent = document.getElementById('experience-content');
    experienceData.forEach(exp => {
        const expElement = document.createElement('div');
        expElement.className = 'experience-item';
        expElement.innerHTML = `
            <h3>${exp.title}</h3>
            <p class="company">${exp.company}</p>
            <p class="duration">${exp.duration}</p>
            <p class="description">${exp.description}</p>
        `;
        experienceContent.appendChild(expElement);
    });
}

// Populate projects section
function populateProjects() {
    const projectsContent = document.getElementById('projects-content');
    projectsData.forEach(project => {
        const projectElement = document.createElement('div');
        projectElement.className = 'project-item';
        projectElement.innerHTML = `
            <h3>${project.name}</h3>
            <p>${project.description}</p>
            <div class="technologies">
                ${project.technologies.map(tech => `<span class="tech-tag">${tech}</span>`).join('')}
            </div>
            <a href="${project.github}" target="_blank" class="project-link">
                <i class="fab fa-github"></i> View on GitHub
            </a>
        `;
        projectsContent.appendChild(projectElement);
    });
}

// Handle contact form submission
document.getElementById('contact-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(Object.fromEntries(formData)),
        });
        if (response.ok) {
            alert('Message sent successfully!');
            e.target.reset();
        } else {
            throw new Error('Failed to send message');
        }
    } catch (error) {
        alert('Error sending message. Please try again.');
        console.error('Error:', error);
    }
});

// Handle meeting scheduler form
document.getElementById('scheduler-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
        const response = await fetch('/api/schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(Object.fromEntries(formData)),
        });
        if (response.ok) {
            alert('Meeting scheduled successfully!');
            e.target.reset();
        } else {
            throw new Error('Failed to schedule meeting');
        }
    } catch (error) {
        alert('Error scheduling meeting. Please try again.');
        console.error('Error:', error);
    }
});

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    populateExperience();
    populateProjects();
});
