from flask import render_template, flash, redirect, url_for, session
from app import app
from random import randrange
import csv
from app.forms import LoginForm, GuessForm
from wordle import getPlayerData, do_guess, decide, std, get_color, isHardPlayer

# @app.route('/')
# def index():
    # fhand = open("data/pool.csv")
    # players = list(csv.reader(fhand))
    # index = randrange(2,508)
    # row = players[index]
    # player = str(row[1])
    
    # user = {'username': 'Miguel'}
    # posts = [
        # {
            # 'author': {'username': 'John'},
            # 'body': player
        # }
    # ]
    

    # return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/', methods=['GET', 'POST'])
@app.route('/play', methods=['GET', 'POST'])
def play():
    form = GuessForm()
    if 'answer' not in session:
        session['answer'] = decide()
        if isHardPlayer(session['answer']["PlayerName"]): session["isHard"] = True
        else: session["isHard"] = False
    if 'isHard' not in session:
        if isHardPlayer(session['answer']["PlayerName"]): session["isHard"] = True
        else: session["isHard"] = False
    isHard = session.get('isHard')
    if form.validate_on_submit():
        if form.reset.data:
            guesses=[]
            answer=session.get('answer')["PlayerName"]
            isHard = session.get('isHard')
            for key in list(session.keys()):
                print(key)
                session.pop(key)
            return render_template('play.html', title='Wardle', form=form, guesses=guesses, answer=answer, get_color=get_color, college=False, stat=False, found=False, lost=True, isHard=isHard)
        

        
        #flash('{} was a valid guess.'.format(form.guess.data))
        guess = form.guess.data
        guessData = getPlayerData(std(guess))
        data = do_guess(session.get('answer'), guessData)
        if not "guesses" in session: session['guesses'] = [data]
        else: session['guesses'].append(data)
        guesses = session.get('guesses')
        answer = session.get('answer')["PlayerName"]
        college = False
        stat = [False, None]
        found = False
        for guess in session['guesses']:
            if guess.get("College")[0] == "CORRECT": college = True
            if guess.get("Stat")[0] != "NA": stat = [True, guess.get("Stat")[2]]
            if guess.get("Found"):
                found = True
                session["found"] = 1
                
        lost = False
        isHard = session.get('isHard')
        if 'guesses' in session and len(session.get('guesses')) > 5:
            if 'found' not in session:
                #print("LOST!")
                lost = True
                guesses=[]
            else: guesses = session.get('guesses')
            answer=session.get('answer')["PlayerName"]
            for key in list(session.keys()): session.pop(key)
            
        if 'found' in session:
            for key in list(session.keys()): session.pop(key)
        #line 1622-1644 is my own css
        return render_template('play.html', title='Wardle', form=form, guesses=guesses, answer=answer, get_color=get_color, college=college, stat=stat, found=found, lost=lost, isHard=isHard)

        
        
    #if session.get('guesses'): session.pop('guesses')
    if form.reset.data:
        guesses=[]
        answer=session.get('answer')["PlayerName"]
        isHard = session.get('isHard')
        for key in list(session.keys()): session.pop(key)
        return render_template('play.html', title='Wardle', form=form, guesses=guesses, answer=answer, get_color=get_color, college=False, stat=False, found=False, lost=True, isHard=isHard)
    #print("Loading page with empty guesses...")
    return render_template('play.html', title='Wardle', form=form, guesses=session.get('guesses', []), answer=session['answer']["PlayerName"], get_color=get_color, college=False, stat=False, found=False, lost=False, isHard=isHard)
    
    
@app.route('/howtoplay', methods=['GET', 'POST'])
def howtoplay():
    return render_template('howtoplay.html')
    
@app.route('/divisions', methods=['GET', 'POST'])
def divisions():
    return render_template('divisions.html')