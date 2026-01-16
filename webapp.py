from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from Forms import CreateUserForm, LoginForm
from database import Database
from profile import Profile

app = Flask(__name__)
app.secret_key = "My Secret Key"

UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_helper = Database()

@app.route('/')
def home(): 
    user_id = session.get('user_id')
    first_name = session.get('first_name')
    full_name = session.get('full_name')
    display_name = session.get('display_name')
    role = session.get('role')
    user_type = session.get('user_type')
    profile_picture = session.get('profile_picture')
    print("SESSION profile_picture:", profile_picture)


    if user_id:
        # User is logged in
        return render_template('home.html', logged_in=True, role=role, first_name=first_name, full_name=full_name, display_name=display_name, user_type=user_type, profile_picture=profile_picture)
    else:
        # User is not logged in
        return render_template('home.html', logged_in=False)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    create_user_form = CreateUserForm(request.form)

    if request.method == 'POST':
        # Include files for validation
        create_user_form = CreateUserForm(request.form, meta={'csrf': False})
        profile_pic = request.files.get('profile_picture')
        profile_pic_filename = None

        if profile_pic and profile_pic.filename != "":
            # Get file extension
            ext = profile_pic.filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                import re
                # Make email safe for filenames
                safe_email = re.sub(r'[^a-zA-Z0-9_-]', '_', create_user_form.email.data)
                profile_pic_filename = f"user_{safe_email}.{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                profile_pic.save(save_path)
                print(f"[DEBUG] Saved profile picture as: {profile_pic_filename}")

        # Set defaults
        create_user_form.role.data = 'Admin'

        if create_user_form.validate():
            try:
                existing_user = db_helper.get_user_by_email(create_user_form.email.data)
                
                if existing_user:
                    # If the email is already registered, show an error message
                    flash("Registration failed. That email is already in use.")
                    return render_template('sign-up.html', form=create_user_form)
                # Hash the password
                hashed_password = generate_password_hash(create_user_form.password.data)

                user_id = db_helper.insert_user(
                    password=hashed_password,
                    first_name=create_user_form.first_name.data,
                    last_name=create_user_form.last_name.data,
                    display_name=create_user_form.display_name.data,
                    email=create_user_form.email.data,
                    profile_picture=profile_pic_filename,
                    user_type=create_user_form.user_type.data,
                    role=create_user_form.role.data
                )

                flash("Registration successful! Please login.")
                return redirect(url_for('login'))

            except Exception as e:
                print(f"Error storing user: {e}")
                flash("Registration failed. That email may already exist.")
        else:
            print("[DEBUG] Form validation errors:", create_user_form.errors)
            flash("Please fix the errors in the form.")

    return render_template('sign-up.html', form=create_user_form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)

    if request.method == 'POST' and login_form.validate():
        try:
            # Get the user from the database
            email = login_form.email.data.strip()
            user_data = db_helper.get_user_by_email(email)

            print("Trying to log in with:", email)
            print("User data:", user_data)

            if not user_data:
                flash("Invalid username or password")
                return render_template('login.html', form=login_form)

            # Turn the row into a User object
            user = Profile.from_database_row(user_data)

            # Verify the hashed password
            if check_password_hash(user.get_password(), login_form.password.data):
                session['user_id'] = user.get_user_id()
                session['first_name'] = user.get_first_name()
                session['last_name'] = user.get_last_name()
                session['full_name'] = user.get_full_name()
                session['display_name'] = user.get_display_name()
                session['email'] = user.get_email()
                session['user_type'] = user.get_user_type()
                session['role'] = user.get_role()
                session['profile_picture'] = user.get_profile_picture()
                print("user_data from DB:", user_data)
                print("profile_picture from user object:", user.get_profile_picture())

                return redirect(url_for('home'))
            else:
                flash("Invalid username or password")

        except Exception as e:
            print(f"Error during login: {e}")
            flash("An error occurred. Please try again.")

    return render_template('login.html', form=login_form)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/retrieve-users')
def retrieve_users():
    user_id = session.get('user_id')
    first_name = session.get('first_name')
    full_name = session.get('full_name')
    display_name = session.get('display_name')
    role = session.get('role')
    profile_picture = session.get('profile_picture')
    """Display all users from the database"""
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for("home"))
    else:
        try:
            users_data = db_helper.get_all_users()
            users_list = [Profile.from_database_row(row) for row in users_data]
            print(f"[DEBUG] Retrieved users data: {users_data}")
            if user_id:
                return render_template('retrieve-users.html', logged_in=True, role=role, first_name=first_name, full_name=full_name, display_name=display_name, users_list=users_list, profile_picture=profile_picture)
        except Exception as e:
            print(f"Error retrieving users: {e}")
            return render_template('retrieve-users.html', users_list=[])

if __name__ == '__main__':
    app.run()