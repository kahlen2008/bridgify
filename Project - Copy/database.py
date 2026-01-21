# database.py
import sqlite3

# Currently logged in user ID (simulating authentication)
CURRENT_USER_ID = 1

def get_db_connection():
    conn = sqlite3.connect('bridgify.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_current_user():
    """Get the currently logged in user."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (CURRENT_USER_ID,)).fetchone()
    conn.close()
    return dict(user) if user else None

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            handle TEXT NOT NULL UNIQUE,
            bio TEXT DEFAULT '',
            profile_pic TEXT DEFAULT 'default.jpg',
            joined_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            caption TEXT,
            location TEXT,
            status TEXT DEFAULT 'published',
            category TEXT,
            post_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parent_id INTEGER DEFAULT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE
        )
    ''')
    
    # Reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            reporter_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (reporter_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def seed_sample_data():
    """Seed the database with sample users and posts for demonstration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we already have users
    existing_users = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    if existing_users == 0:
        # Add sample users with their corresponding profile pictures
        sample_users = [
            ('Sasha Tan', '@Sasha123', 'Passionate about bridging generations through technology and traditions. 🌉', 'default.jpg'),
            ('Exp_Farmer', '@exp_farmer', 'Learning new recipes from the wisdom of elders. 🌿', 'Exp_Farmer.png'),
            ('CozyCardigan', '@cozycardi', 'Never too old to learn something new! Tech enthusiast at 68. 💻', 'CozyCardigan.png'),
            ('TheOldOakTree', '@oldoaktree', 'Capturing life one photo at a time. Photography newbie. 📸', 'TheOldOakTree.png'),
            ('Pov.Learning', '@povlearning', 'Sharing traditional skills with the next generation. 🎨', 'Pov.Learning.png'),
        ]
        
        for username, handle, bio, pic in sample_users:
            cursor.execute('INSERT INTO users (username, handle, bio, profile_pic) VALUES (?, ?, ?, ?)', 
                           (username, handle, bio, pic))
        
        print("Sample users added.")
    
    # Check if we already have sample posts
    existing_posts = cursor.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    
    if existing_posts == 0:
        # Get user IDs
        users = {row['username']: row['id'] for row in cursor.execute('SELECT id, username FROM users').fetchall()}
        
        # Add a diverse set of sample posts to test all filters
        # Categories: Technology, Cooking, Arts & Crafts, Language
        # Locations: North, East, West, Central
        # Types: Learn, Teach, Memory
        sample_posts = [
            # 1. Cooking, Learn, North
            (
                users.get('Exp_Farmer', 2),
                '/static/images/Popiah.png',
                'Learning the art of Popiah rolling in the North! 🌯',
                'North',
                'published',
                'Cooking',
                'Learn'
            ),
            # 2. Technology, Learn, East
            (
                users.get('CozyCardigan', 3),
                '/static/images/Payment.png',
                'Mastering mobile payments in the East district! 📱',
                'East',
                'published',
                'Technology',
                'Learn'
            ),
            # 3. Arts & Crafts, Memory, Central
            (
                users.get('TheOldOakTree', 4),
                '/static/images/Photography.png',
                'A beautiful memory of sunset photography at Marina Bay. 🌅',
                'Central',
                'published',
                'Arts & Crafts',
                'Memory'
            ),
            # 4. Cooking, Teach, West
            (
                users.get('Pov.Learning', 5),
                '/static/images/Kueh.png',
                'Teaching the secrets of traditional Kueh making in the West side! 🌸',
                'West',
                'published',
                'Cooking',
                'Teach'
            ),
        ]
        
        for post in sample_posts:
            cursor.execute('''
                INSERT INTO posts (user_id, image_url, caption, location, status, category, post_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', post)
        
        print("Sample posts added.")
    
    # Add some sample comments
    existing_comments = cursor.execute('SELECT COUNT(*) FROM comments').fetchone()[0]
    
    if existing_comments == 0:
        posts = cursor.execute('SELECT id FROM posts').fetchall()
        users = {row['username']: row['id'] for row in cursor.execute('SELECT id, username FROM users').fetchall()}
        
        if len(posts) >= 4:
            sample_comments = [
                (posts[0]['id'], users.get('CozyCardigan', 3), 'This looks absolutely delicious! 😋'),
                (posts[1]['id'], users.get('Exp_Farmer', 2), 'So proud of you! Technology isn\'t so scary after all 💪'),
                (posts[2]['id'], users.get('Sasha Tan', 1), 'What a beautiful shot! 🌅'),
            ]
            
            for post_id, user_id, content in sample_comments:
                cursor.execute('INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)', (post_id, user_id, content))
            
            print("Sample comments added.")
    
    conn.commit()
    conn.close()


def reset_and_seed():
    """Reset the database and add fresh sample data."""
    import os
    
    # Delete existing database
    if os.path.exists('bridgify.db'):
        os.remove('bridgify.db')
        print("Old database removed.")
    
    # Reinitialize and seed
    init_db()
    seed_sample_data()
    print("Database reset and seeded successfully!")


if __name__ == '__main__':
    reset_and_seed()