from flask_frozen import Freezer
from app import app
import os

freezer = Freezer(app)

# Create URLs for static files
@freezer.register_generator
def static_files():
    for filename in os.listdir(app.static_folder):
        yield {'filename': filename}

if __name__ == '__main__':
    # Create build directory if it doesn't exist
    if not os.path.exists('build'):
        os.makedirs('build')
    
    # Freeze the app
    freezer.freeze()
