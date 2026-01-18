from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, IntegerField
from wtforms.fields.simple import PasswordField, EmailField
from wtforms.validators import DataRequired, Optional
from wtforms_components import TimeField

class PreorderForm(FlaskForm):
    person_name = StringField("Person's Name", validators=[DataRequired()])

    starter = SelectField("Starter", validators=[Optional()],
        coerce=lambda x: int(x) if x not in (None, "", "None") else None)

    main = SelectField("Main Course", validators=[Optional()],
        coerce=lambda x: int(x) if x not in (None, "", "None") else None)

    dessert = SelectField("Dessert", validators=[Optional()],
        coerce=lambda x: int(x) if x not in (None, "", "None") else None)

    drink = SelectField("Drink", validators=[Optional()],
        coerce=lambda x: int(x) if x not in (None, "", "None") else None)

    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Update Preorder")


class CodeForm(FlaskForm):
    code = IntegerField('Code', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class CostumerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = IntegerField('Phone', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    table_number = IntegerField('Table Number', validators=[DataRequired()])
    num_people = IntegerField('Number of People', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
