from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from flask_babel import lazy_gettext as _
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, FloatField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from application.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('User Role', choices=[('resident', 'Resident'), ('collector', 'Collector'), ('admin', 'Admin')])
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username taken.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ComplaintForm(FlaskForm):
    type = SelectField('Waste Category', choices=[
        ('Bulk Waste', 'Bulk Waste'),
        ('Public Cleaning', 'Public Cleaning'),
        ('Domestic Waste', 'Domestic Waste')
    ], validators=[DataRequired()])
    
    content = TextAreaField('Description', validators=[
        DataRequired(), 
        Length(min=10, max=500)
    ])
    
    photo = FileField('Upload Evidence', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    
    submit = SubmitField('Submit Report')


class FeedbackForm(FlaskForm):
    category = SelectField(label=_('Nature of Feedback'), choices=[
        ('Suggestion', _('Suggestion')),
        ('Compliment', _('Compliment')),
        ('Issue', _('Service Issue'))
    ], validators=[DataRequired()])
    
    subject = StringField(label=_('Subject'), validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField(label=_('Your Message'), validators=[
        DataRequired(), 
        Length(min=10, message=_('Your message is too short.'))
    ])
    
    submit = SubmitField(_('Send Feedback'))


class RequestPointsForm(FlaskForm):
    # Classification for Admin Dashboard analytics
    material_type = SelectField('Waste Classification', choices=[
        ('recyclable', 'Recyclable (Paper, Plastic, Metal, Glass)'),
        ('non-recyclable', 'Non-Recyclable (General Waste, Organic)')
    ], validators=[DataRequired()])

    # DecimalField ensures the user enters a valid number for weight
    quantity = DecimalField('Total Weight', 
                            places=2, 
                            validators=[DataRequired(), NumberRange(min=0.1, message="Weight must be at least 0.1kg")],
                            render_kw={"placeholder": "0.00"})

    # Photo proof is mandatory for point verification
    photo = FileField('Please send evidence', 
                      validators=[FileRequired(), FileAllowed(['png'], 'Only PNG files are allowed!')],
                      render_kw={"accept": ".jpg,.jpeg,.png"})

    submit = SubmitField('Submit & Earn Points')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Delivery Address', validators=[Length(max=500)], render_kw={"rows": 4, "placeholder": "Enter your full address for reward delivery"})
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        # 1. Check if the user actually changed the email field
        if email.data != current_user.email:
            # 2. Look for ANY other user with this new email
            user = User.query.filter_by(email=email.data).first()
            if user:
                # 3. If someone is found, stop the form from submitting
                raise ValidationError('That email is already in use by another account.')
            

class NewsForm(FlaskForm):
    title = StringField('Headline', validators=[DataRequired(), Length(min=2, max=100)])
    category = SelectField('Category', choices=[
        ('General', 'General Update'),
        ('Alert', 'Urgent Alert'),
        ('Event', 'Community Event')
    ], validators=[DataRequired()])
    content = TextAreaField('Message Content', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Submit')


class FAQForm(FlaskForm):
    question = StringField('Question', validators=[
        DataRequired(), 
        Length(min=5, max=255, message="Question must be between 5 and 255 characters.")
    ])
    answer = TextAreaField('Answer', validators=[
        DataRequired(),
        Length(min=10, message="Please provide a more detailed answer.")
    ])
    submit = SubmitField('Save FAQ')


class ChatChannelForm(FlaskForm):
    name = StringField('Channel Name', validators=[DataRequired(), Length(max=100)])
    description = StringField('Description', validators=[Length(max=255)])
    is_active = BooleanField('Active Status', default=True)
    submit = SubmitField('Save Channel')