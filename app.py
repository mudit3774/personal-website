from flask import Flask, render_template, jsonify, request
from flask_frozen import Freezer
import os

app = Flask(__name__)
freezer = Freezer(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/experience')
def experience():
    return render_template('experience.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# API endpoints that will be handled by JavaScript in the static site
@app.route('/api/schedule', methods=['POST'])
def schedule_meeting():
    return jsonify({'status': 'success'})

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(debug=True, port=5006)
    else:
        app.run()
