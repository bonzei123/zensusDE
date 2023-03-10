from flask_wtf import FlaskForm
from wtforms import (SelectField, HiddenField)
from wtforms.validators import InputRequired, Length


class ZensusForm(FlaskForm):
    schuld = SelectField('Wer ist Schuld?', choices=[('1', 'jobaxgaming'), ('2', 'jobaxgaming'), ('3', 'Philipp Lahm'), ('4', 'jobaxgaming'), ])
    user = HiddenField('user')
    state = HiddenField('state')
