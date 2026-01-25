from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional


class CodeForm(FlaskForm):
    code = IntegerField('Code', validators=[DataRequired()])
    submit = SubmitField('Submit')


