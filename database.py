import sqlite3

class Database:
    def __init__(self,db_name='Profile.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Profile (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    profile_picture TEXT,
                    user_type TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'Admin'      
                )
        ''')

        conn.commit()
        conn.close()

    def insert_user(self,password,first_name,last_name,display_name,email, profile_picture, user_type, role):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Profile (password, first_name, last_name, display_name, email, profile_picture, user_type, role)
            VALUES (?,?,?,?,?,?,?,?)   
            ''',(password, first_name, last_name, display_name, email, profile_picture, user_type, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_email(self, email):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Profile WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM Profile WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        conn.close()
        return user_data
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM Profile ORDER BY user_id')
        users_data = cursor.fetchall()
        
        conn.close()
        return users_data