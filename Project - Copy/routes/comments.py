# routes/comments.py
from flask import Blueprint, request, jsonify
from database import get_db_connection

# Create the blueprint
comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    """Add a comment to a post."""
    content = request.form.get('comment_content')
    parent_id = request.form.get('parent_id')
    user_id = 1  # Default user

    if content:
        conn = get_db_connection()
        actual_parent = parent_id if parent_id and parent_id.strip() != "" else None
        
        cursor = conn.execute('INSERT INTO comments (post_id, user_id, content, parent_id) VALUES (?, ?, ?, ?)',
                     (post_id, user_id, content, actual_parent))
        comment_id = cursor.lastrowid
        conn.commit()
        
        # Fetch username for the response
        user = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()

        # Return JSON response
        return jsonify({
            "status": "success",
            "id": comment_id,
            "username": user['username'],
            "content": content,
            "parent_id": actual_parent
        })
    
    return jsonify({"status": "error"}), 400


@comments_bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    """Delete a comment by ID."""
    conn = get_db_connection()
    conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})
