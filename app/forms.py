from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import sys, os
sys.path.append("C:\\Users\\brand\\OneDrive\\Desktop\\Programs\\NFL wordle")
from wordle import isValidGuess


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


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class GuessForm(FlaskForm):
    guess = StringField('Guess', validators=[ValidGuess()])
    submit = SubmitField('Submit')
    reset = SubmitField('Give up')