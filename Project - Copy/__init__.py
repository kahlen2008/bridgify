# __init__.py
import os
from flask import Flask
from database import init_db

# Import blueprints
from routes.main import main_bp
from routes.posts import posts_bp
from routes.comments import comments_bp
from routes.profile import profile_bp


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # File Upload Setup
    UPLOAD_FOLDER = 'static/uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Initialize database
    init_db()
    
    # Register blueprints
    app.register_blueprint(main_bp)           # Routes: /
    app.register_blueprint(posts_bp)          # Routes: /journal, /create_post, /get_drafts, /delete_post, /report_post
    app.register_blueprint(comments_bp)       # Routes: /add_comment, /delete_comment
    app.register_blueprint(profile_bp)        # Routes: /profile
    
    return app


# Create the app instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)