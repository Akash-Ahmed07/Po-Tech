from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[Optional(), Length(max=500)])
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('technology', 'Technology'),
        ('education', 'Education'),
        ('science', 'Science'),
        ('programming', 'Programming')
    ], validators=[DataRequired()])
    tags = StringField('Tags (comma separated)', validators=[Optional()])
    featured_image = FileField('Featured Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    author = StringField('Author', validators=[DataRequired(), Length(max=255)])
    category = SelectField('Category', choices=[
        ('bangladeshi', 'Bangladeshi Literature'),
        ('international', 'International Literature'),
        ('hsc', 'HSC Books'),
        ('ssc', 'SSC Books'),
        ('undergraduate', 'Undergraduate'),
        ('masters', 'Masters')
    ], validators=[DataRequired()])
    subject = StringField('Subject', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    book_file = FileField('Book File (PDF)', validators=[
        Optional(),
        FileAllowed(['pdf'], 'PDF files only!')
    ])
    cover_image = FileField('Cover Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])

class AnimationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    animation_type = SelectField('Animation Type', choices=[
        ('sine_wave', 'Sine Wave'),
        ('spiral', 'Spiral'),
        ('interference', 'Wave Interference'),
        ('particles', 'Particle System'),
        ('data_viz', 'Data Visualization'),
        ('banner', 'Educational Banner')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[Optional(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
