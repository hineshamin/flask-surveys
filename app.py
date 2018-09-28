from flask import Flask, json, request, session, render_template, redirect, flash, jsonify, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, satisfaction_survey, surveys

app = Flask(__name__)
app.secret_key = "SECRET"

debug = DebugToolbarExtension(app)


@app.route('/')
def home():
    surveys_taken = json.loads(request.cookies.get("surveys_taken", '{}'))
    current_user_surveys = surveys.copy()
    for survey in surveys_taken:
        current_user_surveys.pop(survey, None)
    return render_template('home.html', surveys=current_user_surveys)


@app.route('/start-survey', methods=["POST"])
def start_survey():
    # store survey picked in session
    survey_picked = request.form.get("survey")
    session['survey_name'] = survey_picked
    session[survey_picked] = [()]*len(surveys[survey_picked].questions)
    return render_template('start-survey.html', title=surveys[survey_picked].title, instructions=surveys[survey_picked].instructions)


@app.route('/questions/<int:question_num>', methods=["POST"])
def question(question_num):
    survey_picked = session['survey_name']
    if question_num != 0:
        selection = request.form.get("selection")
        comments = request.form.get("comments", "N/A")
        answer = (selection, comments)
        print(answer)
        answers = session[survey_picked]
        answers[question_num-1] = answer
        session[survey_picked] = answers
    if question_num >= len(surveys[survey_picked].questions):
        for i in range(len(surveys[survey_picked].questions)):
            question = surveys[survey_picked].questions[i].question
            answer = session[survey_picked][i][0]
            comment = session[survey_picked][i][1]
            # TURN INTO DICT FIRST
            flash(question, 'question')
            flash(answer, 'answer')
            flash(comment, 'comment')
        return redirect('/thanks')

    return render_template('question.html', next_id=question_num + 1, question=surveys[survey_picked].questions[question_num].question, choices=surveys[survey_picked].questions[question_num].choices, textbox=surveys[survey_picked].questions[question_num].allow_text)


@app.route('/thanks')
def thanks():

    # Setting cookie that user has taken survey
    survey_picked = session['survey_name']
    surveys_taken = json.loads(request.cookies.get("surveys_taken", '{}'))
    surveys_taken[survey_picked] = 0
    html = render_template('thanks.html')
    resp = make_response(html)
    resp.set_cookie('surveys_taken', json.dumps(surveys_taken))

    return resp
