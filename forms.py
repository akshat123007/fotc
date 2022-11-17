from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed

class RegistrationForm_po(FlaskForm):
       fullname = StringField('Enterprise Name', validators=[DataRequired()])
       username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
       phone = StringField('Phone', validators=[DataRequired()])
       email = StringField('Email', validators=[DataRequired(),Email()])
       password = PasswordField('Password', validators=[DataRequired()])
       confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
       submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
       username = StringField('Username', validators=[DataRequired()])
       password = PasswordField('Password', validators=[DataRequired()])
       remember = BooleanField('Remember Me')
       submit = SubmitField('Login')       

class ContactForm(FlaskForm):
       name = StringField('Name', validators=[DataRequired(), Length(min=2, max=30)])
       email = StringField('Email', validators=[DataRequired(),Email()])
       subject = StringField('Subject', validators=[DataRequired()])
       message= TextAreaField('Message', validators=[DataRequired()])
       submit = SubmitField('Send') 

class RegistrationForm(FlaskForm):
       lat = StringField('Latitude', validators=[DataRequired()])
       lon = StringField('Longitude', validators=[DataRequired()])
       Fullname = StringField('Full Name', validators=[DataRequired()])
       Featurename = StringField('Features', validators=[DataRequired()])
       File = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
       submit = SubmitField('Upload')