from models import db, User, Course, Enrollment, Quiz, Question, Answer, Result

def initialize_db():
    db.drop_all()
    db.create_all()

    student = User(name='Élève Exemple', email='student@example.com', password='password', role='student')
    teacher = User(name='Professeur Exemple', email='teacher@example.com', password='password', role='teacher')
    
    db.session.add(student)
    db.session.add(teacher)
    db.session.commit()

    course1 = Course(title='Mathématiques', description='Cours de mathématiques.', teacher_id=teacher.id)
    course2 = Course(title='Sciences', description='Cours de sciences.', teacher_id=teacher.id)
    
    db.session.add(course1)
    db.session.add(course2)
    db.session.commit()

    enrollment1 = Enrollment(student_id=student.id, course_id=course1.id)
    enrollment2 = Enrollment(student_id=student.id, course_id=course2.id)
    
    db.session.add(enrollment1)
    db.session.add(enrollment2)
    db.session.commit()

    quiz1 = Quiz(title='Quiz 1', description='Premier quiz.', course_id=course1.id)
    quiz2 = Quiz(title='Quiz 2', description='Deuxième quiz.', course_id=course2.id)
    
    db.session.add(quiz1)
    db.session.add(quiz2)
    db.session.commit()

    db.session.commit()
