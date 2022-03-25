from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError
import sys, os
sys.path.append("C:\\Users\\brand\\OneDrive\\Desktop\\Programs\\NFL wordle")
from wordle import isValidGuess, isValidRestr


class Length(object):
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        if not message:
            message = u'Field must be between %i and %i characters long.' % (min, max)
        self.message = message

    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            raise ValidationError(self.message)
            
            
class ValidGuess(object):
    def __init__(self, message=None):
        if not message: message = "Error: This player is not in the pool of possible players."
        self.message = message
        
    def __call__(self, form, field):
        guess = field.data
        print("The guess was " + guess + ".")
        if not isValidGuess(guess):
            raise ValidationError(self.message)

class ValidRestr(object):
    def __init__(self):
        self.message = "Error: The settings you have chosen do not apply to any players."

    def __call__(self, form, field):
        restr = form.data
        if not isValidRestr(restr):
            raise ValidationError(self.message)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class GuessForm(FlaskForm):
    guess = StringField('Guess', validators=[ValidGuess()])
    submit = SubmitField('Submit')
    reset = SubmitField('Give up')
    
class DifficultyForm(FlaskForm):
    diffField = SelectField("Select Difficulty", choices = ["Easy", "Medium", "Hard", "Extreme", "Include all players"])
    #choices = [("1, 76", "Easy"), ("30, 150", "Medium"), ("150, 300", "Hard"), ("300, 508", "Extreme"), ("1, 508", "Include all players")])#, coerce=convert)

class RestrForm(FlaskForm):
    apply = SubmitField('Apply & Reset', validators=[ValidRestr()])
    conField = SelectMultipleField("Select Conference:", choices=["All", "NFC", "AFC"], validators=[ValidRestr()])
    divField = SelectMultipleField("Select Division:", choices=["All", "NFC East", "NFC West", "NFC North", "NFC South", "AFC East", "AFC West", "AFC North", "AFC South"], validators=[ValidRestr()])
    posField = SelectMultipleField("Select Position:", choices=["All", "QB", "WR", "RB", "TE", "K"], validators=[ValidRestr()])

class NameForm(FlaskForm):
    name = StringField('Enter your name:', validators=[DataRequired()])
    assign = SubmitField('Submit')