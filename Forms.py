from wtforms import Form, StringField, EmailField, PasswordField, validators
from wtforms.validators import Email, Optional
from flask_wtf.file import FileField, FileAllowed

  
class CreateUserForm(Form):
    first_name = StringField('First Name', [
        validators.Length(min=1, max=100), 
        validators.DataRequired() # Ensures the field is not empty
    ])
    last_name = StringField('Last Name', [
        validators.Length(min=1, max=150),
        validators.DataRequired()
    ])
    email = EmailField('Email', [ 
        validators.DataRequired(),
        Email(message="Invalid email address format.")
    ])
    password = PasswordField('New Password', [
        validators.Length(min=8, max=50),
        validators.DataRequired(), 
    ])
    confirmpassword = PasswordField('Repeat Password', [
        validators.Length(min=8, max=50),
        validators.DataRequired(),
    ])
    display_name = StringField('Display Name', [
        validators.DataRequired(),],
        render_kw={"placeholder": "Enter your Display Name"}
    )
    profile_picture = FileField('Profile Picture', [
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    user_type = StringField('User Type', [
        validators.Length(min=1, max=100), 
        validators.DataRequired()
    ])
    role = StringField('Role', [
        validators.Length(min=1, max=100), 
        validators.DataRequired()
    ])

    def validate(self):
        """Override default validate to check if passwords match."""
        # First run default validation
        rv = super().validate()
        if not rv:
            return False
            
        """Simple helper to check if passwords match."""
        if self.password.data != self.confirmpassword.data:
            self.password.errors.append('Passwords must match')
            self.confirmpassword.errors.append('Passwords must match')
            return False
        return True

class LoginForm(Form):
        email = EmailField('Email', [ 
        validators.DataRequired(),
        Email(message="Invalid email address format.")
    ])
        password = PasswordField('New Password', [
        validators.Length(min=8, max=50),
        validators.DataRequired(), 
    ])