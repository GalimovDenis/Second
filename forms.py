"""Forms for the bull application."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Form class for user login."""
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class FreeBookForm(FlaskForm):
    """Form class for free product link generation."""
    username = StringField('username', validators=[DataRequired()])
    product = SelectField('Product')
