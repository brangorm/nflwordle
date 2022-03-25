from flask import Flask, session, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_session import Session
import os
from random import randrange
import csv
from app.forms import LoginForm, GuessForm, DifficultyForm, RestrForm, NameForm
from wordle import do_guess, decide, std, get_color, isHardPlayer, hasData, clearSession, feedhandW
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config.from_object(__name__)#app.config.from_object(Config)
bootstrap = Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    player = db.Column(db.String(64), index=True)
    guesses = db.Column(db.Integer)
    won = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {}>'.format(self.name)

def clearUsers(): db.session.execute('DELETE FROM user')

def genFeed():
    data = []
    feedStr = ""
    stmt = "SELECT name, guesses, player, won FROM user ORDER BY id DESC LIMIT 5;"
    for row in db.session.execute(stmt):
        print(row)
        item = dict(row)
        if item['won']: feedStr = item['name'] + " guessed " + item['player'] + " in " + str(item['guesses']) + " guess" + ("es" if item['guesses'] > 1 else "") + "!\n"
        else: feedStr = item['name'] + " failed to guess " + item['player'] + " after 6 guesses.\n"
        data.append(feedStr)
    return data
    
@app.route('/', methods=['GET', 'POST'])
@app.route('/play', methods=['GET', 'POST'])
def play():
    form = GuessForm()
    diffForm = DifficultyForm()
    restrForm = RestrForm()
    nameForm = NameForm()
    feed = genFeed()
    name_submit = nameForm.assign.data and nameForm.validate()
    if name_submit:
        session['name'] = nameForm.name.data
    
    if restrForm: print("Data is " + str(restrForm.apply.data))
    
    #Set session variables: answer, isHard
    if 'answer' not in session:
        diffData = str(diffForm.diffField.data)
        if diffData == "None": diffData = "Easy"
        session['answer'] = decide(diffData, restrForm.data)
        if isHardPlayer(session['answer']): session["isHard"] = True
        else: session["isHard"] = False
    if 'isHard' not in session:
        if isHardPlayer(session['answer']): session["isHard"] = True
        else: session["isHard"] = False
    isHard = session.get('isHard')
    answer = session['answer']
    print(answer)
    
    #If the guess form's Submit button was submitted but the validation failed
    if form.submit.data and not form.validate():
        flash(form.errors)
        #print("I sense that the guess-submit button was pressed, but the validation may have failed. here is its status: " + str(form.validate()))
    
    #If the guess form's Submit button was submitted and validation passed:
    if form.submit.data and form.validate():
        print("ROUTE GUESS-SUBMIT")
        #flash('{} was a valid guess.'.format(form.guess.data))
        guess = form.guess.data
        data = do_guess(session.get('answer'), guess)
        if not "guesses" in session: session['guesses'] = [data]
        else: session['guesses'].append(data)
        guesses = session.get('guesses')
        answer = session.get('answer')
        college = False
        stat = [False, None]
        found = False
        for guess in session['guesses']:
            if guess.get("College")[0] == "CORRECT": college = True
            if guess.get("Stat")[0] != "NA": stat = [True, guess.get("Stat")[2]]
            if guess.get("Found"):
                found = True
                session["found"] = 1
                if 'name' in session:
                    feedStr = session['name'] + " guessed " + session['answer'] + " in " + str(len(session['guesses'])) + " guesses!\n"
                    print("Writing feed string: " + feedStr)
                    #feedhandW.write(feedStr)
                    u = User(name=session['name'], player=session['answer'], guesses=len(session['guesses']), won=True)
                    db.session.add(u)
                    db.session.commit()
                    feed = genFeed()

        lost = False
        isHard = session.get('isHard')
        if 'guesses' in session and len(session.get('guesses')) > 5:
            if 'found' not in session:
                #print("LOST!")
                lost = True
                guesses=[]
                if 'name' in session:
                    feedStr = session['name'] + " failed to guess " + session['answer'] + " after 6 guesses.\n"
                    print("Writing feed string: " + feedStr)
                    #feedhandW.write(feedStr)
                    u = User(name=session['name'], player=session['answer'], guesses=len(session['guesses']), won=False)
                    db.session.add(u)
                    db.session.commit()
                    feed = genFeed()
            else: guesses = session.get('guesses')
            answer=session.get('answer')
            clearSession(session)
            
        if 'found' in session:
            clearSession(session)
        #line 1622-1644 is my own css
        return render_template('play.html', title='NFL Wordle', form=form, diffForm=diffForm, restrForm=restrForm, nameForm=nameForm, name_submit=name_submit, guesses=guesses, answer=answer, get_color=get_color, college=college, stat=stat, found=found, lost=lost, isHard=isHard, feed=feed)

    #If the Give up button was submitted
    elif form.reset.data:
        print("ROUTE GUESS-RESET")
        guesses=[]
        answer=session.get('answer')
        isHard = session.get('isHard')
        clearSession(session)
        return render_template('play.html', title='NFL Wordle', form=form, diffForm=diffForm, restrForm=restrForm, nameForm=nameForm, name_submit=name_submit, guesses=guesses, answer=answer, get_color=get_color, college=False, stat=False, found=False, lost=True, isHard=isHard, feed=feed)

    #If the Restrictions form was submitted (must have hit the Apply&Reset button)
    elif restrForm.apply.data and restrForm.validate():
        print("Guess submit:  " + str(form.submit.data))
        print("Guess reset:  " + str(form.reset.data))
        print("Restr apply: " + str(restrForm.apply.data))
        
        restrForm.apply.data = False
        print("ROUTE APPLYRESET")
        print("Player hit ApplyReset")
        clearSession(session)
        diffData = str(diffForm.diffField.data)
        if diffData == "None": diffData = "Easy"
        session['answer'] = decide(diffData, restrForm.data)
        answer = session['answer']
        if isHardPlayer(session['answer']): session["isHard"] = True
        else: session["isHard"] = False
        isHard = session.get('isHard')
        return render_template('play.html', title='NFL Wordle', form=form, diffForm=diffForm, restrForm=restrForm, nameForm=nameForm, name_submit=name_submit, guesses=[], answer=answer, get_color=get_color, college=False, stat=False, found=False, lost=False, isHard=isHard, feed=feed)
    
        
    
    #print("Loading page with empty guesses...")
    else:
        print("Guess submit:  " + str(form.submit.data))
        print("Guess reset:  " + str(form.reset.data))
        print("Restr apply: " + str(restrForm.apply.data))
        
        print("ROUTE INITIAL")
        return render_template('play.html', title='NFL Wordle', form=form, diffForm=diffForm, restrForm=restrForm, nameForm=nameForm, name_submit=name_submit, guesses=session.get('guesses', []), answer=session['answer'], get_color=get_color, college=False, stat=False, found=False, lost=False, isHard=isHard, feed=feed)
    
@app.route('/howtoplay', methods=['GET', 'POST'])
def howtoplay():
    return render_template('howtoplay.html')
    
@app.route('/divisions', methods=['GET', 'POST'])
def divisions():
    return render_template('divisions.html')