from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import traceback
import re
from sqlalchemy import and_
import razorpay
import hmac
import hashlib
import math
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'contacts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    replied = db.Column(db.Boolean, default=False)
    reply_message = db.Column(db.Text)
    reply_timestamp = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'replied': self.replied,
            'reply_message': self.reply_message,
            'reply_timestamp': self.reply_timestamp.isoformat() if self.reply_timestamp else None
        }

# TimeSlot model
class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(200), nullable=False)  # Regex pattern for recurring slots
    start_time = db.Column(db.Time, nullable=False)  # Base time for the pattern
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    def to_dict(self):
        return {
            'id': self.id,
            'pattern': self.pattern,
            'start_time': self.start_time.strftime('%H:%M'),
            'duration': self.duration,
            'created_at': self.created_at.isoformat()
        }

    def generate_slots(self, start_date, end_date):
        """Generate actual time slots based on the pattern"""
        slots = []
        current_date = start_date
        weekday_map = {
            'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3,
            'FRI': 4, 'SAT': 5, 'SUN': 6
        }
        allowed_days = [weekday_map[day] for day in self.pattern.split('|')]
        
        while current_date <= end_date:
            if current_date.weekday() in allowed_days:
                # Create datetime combining date and time
                slot_datetime = datetime.combine(current_date, self.start_time)
                
                # Convert to UTC for storage
                utc_datetime = to_utc_time(slot_datetime)
                
                slots.append({
                    'datetime': utc_datetime,
                    'duration': self.duration,
                    'timeslot_id': self.id
                })
            current_date += timedelta(days=1)
        
        return slots

# Appointment model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    agenda = db.Column(db.Text, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    timeslot_id = db.Column(db.Integer, db.ForeignKey('time_slot.id'), nullable=False)
    order_id = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'agenda': self.agenda,
            'datetime': self.datetime.isoformat(),
            'duration': self.duration,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'timeslot_id': self.timeslot_id,
            'order_id': self.order_id
        }

# Order model
class Order(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_KEY_SECRET"))

# Create tables
with app.app_context():
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create all tables fresh

def send_email(to_email, subject, body):
    try:
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))

        if not all([email_address, email_password, smtp_server, smtp_port]):
            raise ValueError("Missing email configuration. Please check your .env file.")

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email_address
        msg['To'] = to_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        try:
            server.login(email_address, email_password)
        except smtplib.SMTPAuthenticationError:
            raise ValueError(
                "Gmail authentication failed. Please ensure you have:\n"
                "1. Set up an App Password in your Google Account settings\n"
                "2. Added the correct App Password to your .env file\n"
                "3. Not used your regular Gmail password\n"
                "For help setting up App Password, visit: https://support.google.com/accounts/answer/185833"
            )
        
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        raise ValueError(f"Failed to send email: {str(e)}")

def to_local_time(utc_dt):
    """Convert UTC datetime to local time (IST)"""
    ist_offset = timedelta(hours=5, minutes=30)  # IST offset from UTC
    return utc_dt + ist_offset

def to_utc_time(local_dt):
    """Convert local time (IST) to UTC datetime"""
    ist_offset = timedelta(hours=5, minutes=30)  # IST offset from UTC
    return local_dt - ist_offset

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug print
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")  # Debug print
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new contact
        new_contact = Contact(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        return jsonify({'message': 'Contact created successfully', 'contact': new_contact.to_dict()}), 201
    
    except Exception as e:
        print("Error in create_contact:", str(e))  # Debug print
        print(traceback.format_exc())  # Print full traceback
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        contacts = Contact.query.order_by(Contact.timestamp.desc()).all()
        return jsonify([contact.to_dict() for contact in contacts])
    
    except Exception as e:
        print("Error in get_contacts:", str(e))  # Debug print
        print(traceback.format_exc())  # Print full traceback
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/reply', methods=['POST'])
def reply_to_contact(contact_id):
    try:
        data = request.get_json()
        reply_message = data.get('reply_message')
        
        if not reply_message:
            return jsonify({'error': 'Reply message is required'}), 400
            
        contact = Contact.query.get(contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404

        try:
            send_email(contact.email, 'Re: Website Contact Form', reply_message)
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

        contact.replied = True
        contact.reply_message = reply_message
        contact.reply_timestamp = datetime.now()
        db.session.commit()
        
        return jsonify({'message': 'Reply sent successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    try:
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': 'Contact deleted successfully'}), 200
    
    except Exception as e:
        print("Error in delete_contact:", str(e))  # Debug print
        print(traceback.format_exc())  # Print full traceback
        return jsonify({'error': str(e)}), 500

@app.route('/api/timeslots', methods=['GET', 'POST'])
def handle_timeslots():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['pattern', 'start_time', 'duration']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Validate pattern format
            pattern = data['pattern'].upper()
            valid_days = {'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'}
            days = pattern.split('|')
            if not all(day in valid_days for day in days):
                return jsonify({'error': 'Invalid day pattern. Use MON|TUE|WED|THU|FRI|SAT|SUN format'}), 400
            
            # Validate duration
            try:
                duration = int(data['duration'])
                if not (15 <= duration <= 180):
                    return jsonify({'error': 'Duration must be between 15 and 180 minutes'}), 400
            except ValueError:
                return jsonify({'error': 'Duration must be a number'}), 400
            
            # Create time slot
            new_slot = TimeSlot(
                pattern=pattern,
                start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
                duration=duration
            )
            db.session.add(new_slot)
            db.session.commit()
            return jsonify(new_slot.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        slots = TimeSlot.query.all()
        return jsonify([slot.to_dict() for slot in slots])

@app.route('/api/available-slots')
def get_available_slots():
    try:
        # Get date range from query params (default to next 7 days)
        start_date = datetime.strptime(
            request.args.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            '%Y-%m-%d'
        ).date()
        end_date = start_date + timedelta(days=int(request.args.get('days', '7')))
        
        # Get all time slot patterns
        patterns = TimeSlot.query.all()
        
        # Generate all possible slots
        all_slots = []
        for pattern in patterns:
            slots = pattern.generate_slots(start_date, end_date)
            # Convert UTC to local time for display
            for slot in slots:
                slot['datetime'] = to_local_time(slot['datetime']).isoformat()
            all_slots.extend(slots)
            
        # Get existing appointments
        existing_appointments = Appointment.query.filter(
            and_(
                Appointment.datetime >= start_date,
                Appointment.datetime <= end_date + timedelta(days=1)
            )
        ).all()
        
        # Remove booked slots
        booked_times = {apt.datetime.isoformat() for apt in existing_appointments}
        available_slots = [
            slot for slot in all_slots 
            if slot['datetime'] not in booked_times
        ]
        
        return jsonify(available_slots)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/appointments', methods=['GET', 'POST'])
def handle_appointments():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['email', 'agenda', 'datetime', 'duration', 'timeslot_id', 'order_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Convert local time to UTC for storage
            local_dt = datetime.fromisoformat(data['datetime'])
            utc_dt = to_utc_time(local_dt)
            
            # Verify order is paid
            order = Order.query.get(data['order_id'])
            if not order or order.status != 'completed':
                return jsonify({'error': 'Payment required'}), 400

            new_appointment = Appointment(
                email=data['email'],
                agenda=data['agenda'],
                datetime=utc_dt,
                duration=data['duration'],
                timeslot_id=data['timeslot_id'],
                order_id=data['order_id']
            )
            db.session.add(new_appointment)
            db.session.commit()
            
            # Convert back to local time for response
            appointment_dict = new_appointment.to_dict()
            appointment_dict['datetime'] = to_local_time(new_appointment.datetime).isoformat()
            return jsonify(appointment_dict), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        appointments = Appointment.query.all()
        # Convert to local time for display
        appointment_dicts = []
        for apt in appointments:
            apt_dict = apt.to_dict()
            apt_dict['datetime'] = to_local_time(apt.datetime).isoformat()
            appointment_dicts.append(apt_dict)
        return jsonify(appointment_dicts)

@app.route('/api/appointments/<int:appointment_id>/notes', methods=['PUT'])
def update_appointment_notes(appointment_id):
    try:
        data = request.get_json()
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.notes = data['notes']
        db.session.commit()
        return jsonify(appointment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/create-order', methods=['POST'])
def create_order():
    try:
        data = request.json
        amount = data.get('amount')
        email = data.get('email')
        duration = data.get('duration')
        date = data.get('date')
        time_slot = data.get('timeSlot')
        agenda = data.get('agenda')

        # Validate minimum amount based on duration
        min_amount = math.ceil(duration / 30) * 500
        if amount < min_amount:
            return jsonify({'error': f'Minimum amount for {duration} minutes is ₹{min_amount}'}), 400

        # Create Razorpay order
        order_data = {
            'amount': amount * 100,  # Amount in paise
            'currency': 'INR',
            'receipt': f'order_{int(time.time())}'
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)

        # Store order in database
        order = Order(
            id=razorpay_order['id'],
            amount=amount,
            email=email
        )
        db.session.add(order)
        db.session.commit()

        return jsonify({
            'id': razorpay_order['id'],
            'amount': amount * 100
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    try:
        data = request.json
        
        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Update order status
        order = Order.query.get(data.get('razorpay_order_id'))
        if order:
            order.status = 'completed'
            db.session.commit()

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
