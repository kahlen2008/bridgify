# routes/profile.py
from flask import Blueprint, render_template
from database import get_db_connection, get_current_user, CURRENT_USER_ID

# Create the blueprint
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@profile_bp.route('/profile/<int:user_id>')
def profile(user_id=None):
    """Render the profile page for a user."""
    conn = get_db_connection()
    
    # If no user_id provided, show current user's profile
    if user_id is None:
        user_id = CURRENT_USER_ID
    
    # Get user info
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return "User not found", 404
    
    user = dict(user)
    
    # Check if viewing own profile
    is_own_profile = (user_id == CURRENT_USER_ID)
    
    # Get user's posts
    posts = conn.execute('''
        SELECT posts.*, users.username, users.handle 
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        WHERE posts.user_id = ? AND posts.status = 'published'
        ORDER BY timestamp DESC
    ''', (user_id,)).fetchall()
    posts = [dict(p) for p in posts]
    
    # Get post count
    post_count = len(posts)
    
    # Get follower/following counts (placeholder for now)
    follower_count = 0
    following_count = 0
    
    conn.close()
    
    return render_template('profile.html', 
                           active_page='profile',
                           user=user,
                           posts=posts,
                           post_count=post_count,
                           follower_count=follower_count,
                           following_count=following_count,
                           is_own_profile=is_own_profile,
                           current_user_id=CURRENT_USER_ID)
