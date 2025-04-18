from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import datetime

app = Flask(__name__)
app.secret_key = 'nfl_defense_secret_key' 

with open('data.json', 'r') as f:
    content_data = json.load(f)

user_data = {
    'current_lesson': 0,
    'lesson_timestamps': {},
    'quiz_answers': {},
    'quiz_score': 0
}

@app.route('/')
def home():
    session['user_data'] = user_data.copy()
    return render_template('home.html')

@app.route('/learn/<int:lesson_id>')
def learn(lesson_id):
    if lesson_id < 1 or lesson_id > len(content_data['lessons']):
        return redirect(url_for('home'))
    
    user_data = session.get('user_data', {})
    user_data['current_lesson'] = lesson_id
    user_data['lesson_timestamps'][str(lesson_id)] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session['user_data'] = user_data
    
    lesson = content_data['lessons'][lesson_id - 1]
    
    next_page = f'/learn/{lesson_id + 1}' if lesson_id < len(content_data['lessons']) else '/quiz/1'
    
    return render_template('learn.html', lesson=lesson, lesson_id=lesson_id, next_page=next_page)

@app.route('/quiz/<int:question_id>', methods=['GET', 'POST'])
def quiz(question_id):
    if question_id < 1 or question_id > len(content_data['quiz']):
        return redirect(url_for('learn', lesson_id=1))
    
    user_data = session.get('user_data', {})

    if request.method == 'POST':
        selected_answer = request.form.get('answer')
        user_data['quiz_answers'][str(question_id)] = selected_answer
        session['user_data'] = user_data
        
        if question_id == len(content_data['quiz']):
            correct_count = 0
            for i, question in enumerate(content_data['quiz']):
                question_num = str(i + 1)
                user_answer = user_data['quiz_answers'].get(question_num, '')
                if user_answer == question['correct_answer']:
                    correct_count += 1
            
            score = correct_count / len(content_data['quiz']) * 100
            user_data['quiz_score'] = score
            session['user_data'] = user_data
            
            return redirect(url_for('congratulations'))
        else:
            return redirect(url_for('quiz', question_id=question_id + 1))
    
    question = content_data['quiz'][question_id - 1]
    
    return render_template('quiz.html', question=question, question_id=question_id, 
                          total_questions=len(content_data['quiz']))

@app.route('/quiz/results')
def quiz_results():
    user_data = session.get('user_data', {})
    quiz_answers = user_data.get('quiz_answers', {})
    
    correct_count = 0
    results = []
    
    for i, question in enumerate(content_data['quiz']):
        question_num = str(i + 1)
        user_answer = quiz_answers.get(question_num, '')
        is_correct = user_answer == question['correct_answer']
        
        if is_correct:
            correct_count += 1
            
        results.append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': question['correct_answer'],
            'is_correct': is_correct
        })
    
    score = correct_count / len(content_data['quiz']) * 100
    user_data['quiz_score'] = score
    session['user_data'] = user_data
    
    return render_template('results.html', score=score, results=results, 
                          correct_count=correct_count, total=len(content_data['quiz']))

@app.route('/congratulations')
def congratulations():
    user_data = session.get('user_data', {})
    quiz_score = user_data.get('quiz_score', 0)
    correct_count = int((quiz_score / 100) * len(content_data['quiz']))
    
    return render_template('congrats.html', 
                          score=quiz_score, 
                          correct_count=correct_count, 
                          total=len(content_data['quiz']))

@app.route('/api/user_data')
def get_user_data():
    return jsonify(session.get('user_data', {}))

if __name__ == '__main__':
    app.run(debug=True)
