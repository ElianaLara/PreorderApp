from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, IntegerField, EmailField, PasswordField, DateField, TimeField
from wtforms.validators import DataRequired, Optional
from wtforms_components import TimeField


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

    submit = SubmitField("Go to Dashboard")

class CostumerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    num_people = IntegerField('Number of People', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    submit = SubmitField("Create Preorder")