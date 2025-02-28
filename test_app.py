import unittest
from flask import Flask
from your_flask_app import app  # Make sure to import your Flask app
from unittest.mock import patch, MagicMock
from datetime import datetime
from api import validate_meeting_time, process_payment, send_contact_email

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

    # Payment Processing Tests
    @patch('api.razorpay.Client')
    def test_payment_creation(self, mock_razorpay):
        """Test payment order creation."""
        mock_client = MagicMock()
        mock_razorpay.return_value = mock_client
        mock_client.order.create.return_value = {'id': 'test_order_id'}

        response = self.app.post('/create_payment', json={
            'amount': 1000,  # Amount in paise (Rs. 10)
            'currency': 'INR'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_id', response.json)
        mock_client.order.create.assert_called_once()

    @patch('api.razorpay.Client')
    def test_payment_verification(self, mock_razorpay):
        """Test payment verification."""
        mock_client = MagicMock()
        mock_razorpay.return_value = mock_client
        mock_client.utility.verify_payment_signature.return_value = True

        response = self.app.post('/verify_payment', json={
            'razorpay_order_id': 'test_order',
            'razorpay_payment_id': 'test_payment',
            'razorpay_signature': 'test_signature'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')

    # Meeting Scheduler Tests
    def test_validate_meeting_time(self):
        """Test meeting time validation logic."""
        # Test valid time
        valid_time = datetime.now().replace(hour=14, minute=0)  # 2 PM
        self.assertTrue(validate_meeting_time(valid_time))

        # Test invalid time (outside business hours)
        invalid_time = datetime.now().replace(hour=23, minute=0)  # 11 PM
        self.assertFalse(validate_meeting_time(invalid_time))

        # Test weekend
        weekend_time = datetime.strptime('2025-03-01 14:00', '%Y-%m-%d %H:%M')  # Saturday
        self.assertFalse(validate_meeting_time(weekend_time))

    def test_schedule_meeting(self):
        """Test meeting scheduling endpoint."""
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'date': '2025-02-28',  # A weekday
            'time': '14:00',
            'duration': 30
        }
        
        response = self.app.post('/schedule_meeting', json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('meeting_id', response.json)

    def test_invalid_meeting_schedule(self):
        """Test invalid meeting schedule attempts."""
        # Test weekend scheduling
        weekend_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'date': '2025-03-01',  # Saturday
            'time': '14:00',
            'duration': 30
        }
        
        response = self.app.post('/schedule_meeting', json=weekend_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    # Contact Form Tests
    @patch('api.send_contact_email')
    def test_contact_form_submission(self, mock_send_email):
        """Test contact form submission."""
        mock_send_email.return_value = True
        
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Hello, this is a test message!'
        }
        
        response = self.app.post('/contact', json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        mock_send_email.assert_called_once_with(
            test_data['name'],
            test_data['email'],
            test_data['message']
        )

    def test_invalid_contact_form(self):
        """Test contact form validation."""
        # Test missing fields
        invalid_data = {
            'name': 'Test User',
            # Missing email
            'message': 'Test message'
        }
        
        response = self.app.post('/contact', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

        # Test invalid email format
        invalid_email_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'message': 'Test message'
        }
        
        response = self.app.post('/contact', json=invalid_email_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

if __name__ == '__main__':
    unittest.main()
