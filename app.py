from flask import Flask, flash, redirect, render_template, request, url_for
from models import Answer, Course, Enrollment, Question, Quiz, Result, db
from initialize_db import initialize_db  # Assurez-vous d'importer depuis initialize_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def dashboard():
    # Supposons que l'utilisateur connecté soit un étudiant avec id=1 pour cet exemple
    student_id = 1
    
    # Récupérer les cours inscrits
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    courses = [Course.query.get(enrollment.course_id) for enrollment in enrollments]
    
    # Récupérer les évaluations disponibles pour les cours inscrits
    quizzes = []
    for course in courses:
        course_quizzes = Quiz.query.filter_by(course_id=course.id).all()
        quizzes.extend(course_quizzes)
    
    # Récupérer la progression de l'étudiant
    progress_list = []
    for course in courses:
        total_quizzes = Quiz.query.filter_by(course_id=course.id).count()
        completed_quizzes = Result.query.filter_by(student_id=student_id).filter(Result.quiz_id.in_([quiz.id for quiz in course_quizzes])).count()
        percentage = (completed_quizzes / total_quizzes) * 100 if total_quizzes > 0 else 0
        progress_list.append({'course_title': course.title, 'percentage': percentage})
    
    # Dernières notifications (juste des exemples pour le moment)
    notifications = [
        "Nouveau quiz disponible pour le cours de Mathématiques.",
        "Votre évaluation en Sciences a été notée.",
        "Nouveau cours disponible : Histoire."
    ]
    
    return render_template('dashboard.html', courses=courses, quizzes=quizzes, progress_list=progress_list, notifications=notifications)

@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/manage_courses', methods=['GET', 'POST'])
def manage_courses():
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        title = request.form.get('title')
        description = request.form.get('description')

        if course_id:
            course = Course.query.get(course_id)
            course.title = title
            course.description = description
        else:
            course = Course(title=title, description=description, teacher_id=1)  # Remplacez 1 par l'id de l'enseignant connecté
            db.session.add(course)

        db.session.commit()
        return redirect(url_for('courses'))

    course_id = request.args.get('course_id')
    course = Course.query.get(course_id) if course_id else None
    return render_template('manage_courses.html', course=course, courses=Course.query.all())

@app.route('/delete_course', methods=['POST'])
def delete_course():
    course_id = request.form.get('course_id')
    course = Course.query.get(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('courses'))

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)



@app.route('/quizzes')
def quizzes():
    quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)

@app.route('/quizzes/<int:quiz_id>')
def quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz_details.html', quiz=quiz, questions=questions)

@app.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    # Récupérer l'utilisateur actuel (assumons que l'utilisateur est connecté)
    user_id = 1  # Remplacez ceci par l'ID de l'utilisateur connecté
    
    # Récupérer le quiz et les questions associées
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Calculer le score
    score = 0
    total_questions = len(questions)
    
    for question in questions:
        selected_answer_id = request.form.get(f'question{question.id}')
        if selected_answer_id:
            selected_answer = Answer.query.get(selected_answer_id)
            if selected_answer and selected_answer.correct:
                score += 1
    
    # Enregistrer le résultat dans la base de données
    result = Result(student_id=user_id, quiz_id=quiz_id, score=score)
    db.session.add(result)
    db.session.commit()
    
    flash('Quiz soumis avec succès!', 'success')
    return redirect(url_for('quizzes'))



@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/progress/<int:course_id>')
def view_progress(course_id):
    # Récupérer l'utilisateur actuel (assumons que l'utilisateur est connecté)
    user_id = 1  # Remplacez ceci par l'ID de l'utilisateur connecté
    
    # Calculer la progression
    progress_percentage = calculate_progress(user_id, course_id)
    
    # Récupérer les détails du cours
    course = Course.query.get_or_404(course_id)
    
    return render_template('progress.html', course=course, progress_percentage=progress_percentage)
def calculate_progress(student_id, course_id):
    total_quizzes = Quiz.query.filter_by(course_id=course_id).count()
    completed_quizzes = Result.query.join(Quiz).filter(Result.student_id == student_id, Quiz.course_id == course_id).count()
    
    if total_quizzes == 0:
        return 0
    

    
    progress_percentage = (completed_quizzes / total_quizzes) * 100
    return progress_percentage

@app.route('/progress/<int:course_id>')
def show_progress(course_id):
    # Récupérer l'utilisateur actuel (assumons que l'utilisateur est connecté)
    user_id = 1  # Remplacez ceci par l'ID de l'utilisateur connecté
    
    # Calculer la progression
    progress_percentage = calculate_progress(user_id, course_id)
    
    # Récupérer les détails du cours
    course = Course.query.get_or_404(course_id)
    
    # Assurez-vous que la variable `course` est passée au template
    return render_template('progress.html', course=course, progress_percentage=progress_percentage)


if __name__ == '__main__':
    with app.app_context():
        initialize_db()
    app.run(debug=True)
