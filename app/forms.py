from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, IntegerField, EmailField, PasswordField
from wtforms.validators import DataRequired, Optional


class CodeForm(FlaskForm):
    code = IntegerField('Code', validators=[DataRequired(message="Please enter a code")])
    submit = SubmitField('Submit')


class PreorderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Please enter your name")])
    notes = StringField('Name', validators=[Optional()])

    submit = SubmitField("Update Preorder")


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])