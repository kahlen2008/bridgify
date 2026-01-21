# routes/posts.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from werkzeug.utils import secure_filename
from database import get_db_connection, CURRENT_USER_ID

# Create the blueprint
posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/journal')
def journal():
    """Render the journal page with all published posts."""
    conn = get_db_connection()
    
    # Fetch published posts with user info
    posts_data = conn.execute('''
        SELECT posts.*, users.username, users.handle, users.profile_pic 
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        WHERE posts.status = 'published' 
        ORDER BY timestamp DESC
    ''').fetchall()

    # Convert SQLite rows to usable dictionary list
    posts = [dict(row) for row in posts_data]

    # Fetch comments for each post
    for post in posts:
        all_comments = conn.execute('''
            SELECT comments.*, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE post_id = ?
            ORDER BY timestamp ASC
        ''', (post['id'],)).fetchall()
        
        # Organize comments so replies follow their parents
        comment_list = [dict(c) for c in all_comments]
        threaded_comments = []
        
        # Get top-level comments (those with no parent_id)
        for c in comment_list:
            if c['parent_id'] is None:
                threaded_comments.append(c)
                # Immediately look for replies to this specific comment
                for r in comment_list:
                    if r['parent_id'] == c['id']:
                        threaded_comments.append(r)
        
        post['comments'] = threaded_comments

    conn.close()
    return render_template('journal.html', 
                           active_page='journal', 
                           posts=posts,
                           current_user_id=CURRENT_USER_ID)


@posts_bp.route('/create_post', methods=['POST'])
def create_post():
    """Create a new post or update a draft."""
    file = request.files.get('photo')
    caption = request.form.get('caption')
    location = request.form.get('location')
    category = request.form.get('category')
    post_type = request.form.get('post_type')
    
    action = request.form.get('action') 
    draft_id = request.form.get('draft_id')

    conn = get_db_connection()
    status = 'draft' if action == 'draft' else 'published'

    # Handle Image URL
    image_url = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        image_url = url_for('static', filename='uploads/' + filename)

    # Update Existing Draft
    if draft_id:
        if image_url:
            conn.execute('UPDATE posts SET image_url=?, caption=?, location=?, status=?, category=?, post_type=? WHERE id=?',
                         (image_url, caption, location, status, category, post_type, draft_id))
        else:
            conn.execute('UPDATE posts SET caption=?, location=?, status=?, category=?, post_type=? WHERE id=?',
                         (caption, location, status, category, post_type, draft_id))
    
    # Create New Post
    else:
        if not image_url: 
            return "Error: Image required for new posts", 400
            
        conn.execute('INSERT INTO posts (user_id, image_url, caption, location, status, category, post_type) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (CURRENT_USER_ID, image_url, caption, location, status, category, post_type))

    conn.commit()
    conn.close()
    return redirect(url_for('posts.journal'))


@posts_bp.route('/get_drafts')
def get_drafts():
    """Get all draft posts as JSON (only current user's drafts)."""
    conn = get_db_connection()
    drafts = conn.execute("SELECT * FROM posts WHERE status = 'draft' AND user_id = ? ORDER BY timestamp DESC", 
                          (CURRENT_USER_ID,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in drafts])


@posts_bp.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    """Delete a post by ID - only if the current user owns it."""
    conn = get_db_connection()
    
    # Check if the post belongs to the current user
    post = conn.execute('SELECT user_id FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post and post['user_id'] == CURRENT_USER_ID:
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('posts.journal'))
    else:
        conn.close()
        return jsonify({'status': 'error', 'message': 'You can only delete your own posts'}), 403


@posts_bp.route('/report_post/<int:post_id>', methods=['POST'])
def report_post(post_id):
    """Report a post for review."""
    reason = request.form.get('reason', 'Inappropriate content')
    
    conn = get_db_connection()
    
    # Check if user already reported this post
    existing_report = conn.execute(
        'SELECT id FROM reports WHERE post_id = ? AND reporter_id = ?', 
        (post_id, CURRENT_USER_ID)
    ).fetchone()
    
    if existing_report:
        conn.close()
        return jsonify({'status': 'error', 'message': 'You have already reported this post'}), 400
    
    # Create the report
    conn.execute(
        'INSERT INTO reports (post_id, reporter_id, reason) VALUES (?, ?, ?)',
        (post_id, CURRENT_USER_ID, reason)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Post reported successfully. Thank you for helping keep our community safe.'})
