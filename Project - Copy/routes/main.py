# routes/main.py
from flask import Blueprint, render_template

# Create the blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Render the home page."""
    return render_template('home.html', active_page='home')
