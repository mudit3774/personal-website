import unittest
from flask import Flask
from your_flask_app import app  # Make sure to import your Flask app

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        """Test the home page loads successfully."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mudit Gupta', response.data)  # Check for a specific text

    def test_experience_page(self):
        """Test the experience page loads successfully."""
        response = self.app.get('/experience')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Professional Experience', response.data)

    def test_projects_page(self):
        """Test the projects page loads successfully."""
        response = self.app.get('/projects')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Featured Projects', response.data)

    def test_schedule_meeting(self):
        """Test the schedule meeting form submission."""
        response = self.app.post('/schedule', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'date': '2025-02-23',
            'time': '10:00'
        })
        self.assertEqual(response.status_code, 302)  # Assuming it redirects after submission

    def test_contact_form(self):
        """Test the contact form submission."""
        response = self.app.post('/contact', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Hello!'
        })
        self.assertEqual(response.status_code, 302)  # Assuming it redirects after submission

if __name__ == '__main__':
    unittest.main()
