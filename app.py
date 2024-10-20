from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample word list with questions and answers only
word_list = [
    {"question": "What color is an apple?", "answer": "red"},
    {"question": "What color is a banana?", "answer": "yellow"},
    {"question": "What is the shape of a grape?", "answer": "round"},
    {"question": "What is orange juice made from?", "answer": "oranges"},
    {"question": "What is the taste of a ripe mango?", "answer": "sweet"}
]

# Hangman stages
stages = [
    ''' 
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    ''',
    ''' 
      +---+
      |   |
      O   |
     /|\\  |
     /     |
          |
    =========
    ''',
    ''' 
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========
    ''',
    ''' 
      +---+
      |   |
      O   |
     /|    |
          |
          |
    =========
    ''',
    ''' 
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    ''',
    ''' 
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    ''',
    ''' 
      +---+
      |   |
          |
          |
          |
          |
    =========
    '''
]

# Route for the home page
@app.route('/')
def index():
    return redirect(url_for('start'))

# Initialize the game
@app.route('/start', methods=['POST', 'GET'])
def start():
    # Choose a random question
    chosen_item = random.choice(word_list)
    chosen_question = chosen_item["question"]
    chosen_answer = chosen_item["answer"]
    
    session['chosen_word'] = chosen_answer  # Use the answer as the word to guess
    session['chosen_question'] = chosen_question
    session['display'] = ['_' for _ in chosen_answer]
    session['lives'] = 6
    session['guessed_letters'] = []
    session['feedback'] = ""  # Reset feedback

    return redirect(url_for('game'))

# Main game page
@app.route('/game')
def game():
    display = session.get('display')
    lives = session.get('lives')
    guessed_letters = session.get('guessed_letters')
    
    # Ensure lives do not go below 0 to prevent index errors
    if lives > 6:
        lives = 6  # Reset to maximum lives
    current_stage = stages[min(lives, 6)]  # Get the correct stage
    
    chosen_question = session.get('chosen_question')
    feedback = session.get('feedback', "")  # Get feedback message

    return render_template('game.html', display=display, lives=lives, 
                           guessed_letters=guessed_letters, current_stage=current_stage, 
                           question=chosen_question, feedback=feedback)

# Handle the guess
@app.route('/guess', methods=['POST'])
def guess():
    guessed_letter = request.form['letter'].lower()
    chosen_word = session.get('chosen_word')
    display = session.get('display')
    lives = session.get('lives')
    guessed_letters = session.get('guessed_letters')

    if guessed_letter in guessed_letters:
        return redirect(url_for('game'))

    guessed_letters.append(guessed_letter)
    
    if guessed_letter in chosen_word:
        for idx, letter in enumerate(chosen_word):
            if letter == guessed_letter:
                display[idx] = guessed_letter
    else:
        lives -= 1

    session['display'] = display
    session['lives'] = max(lives, 0)  # Ensure lives don't drop below 0
    session['guessed_letters'] = guessed_letters

    if lives <= 0:
        return redirect(url_for('lose'))
    elif '_' not in display:
        return redirect(url_for('win'))

    return redirect(url_for('game'))

# Handle the quiz answer
@app.route('/check_answer', methods=['POST'])
def check_answer():
    user_answer = request.form['quiz_answer'].lower().strip()  # Get the user's answer
    correct_answer = session.get('chosen_word').lower().strip()  # Get the correct answer
    
    # Compare the user's answer with the correct answer
    if user_answer == correct_answer:
        session['lives'] += 1  # Give a bonus life for a correct answer
        session['feedback'] = "Correct! You've gained a life."
    else:
        session['lives'] -= 1  # Reduce lives for an incorrect answer
        session['feedback'] = "Incorrect! You've lost a life."
    
    session['lives'] = max(session['lives'], 0)  # Ensure lives don't drop below 0

    return redirect(url_for('game'))  # Redirect back to the game page

# Win route
@app.route('/win')
def win():
    return render_template('win.html', word=session['chosen_word'])

# Lose route
@app.route('/lose')
def lose():
    return render_template('lose.html', word=session['chosen_word'])

if __name__ == '__main__':
    app.run(debug=True)
