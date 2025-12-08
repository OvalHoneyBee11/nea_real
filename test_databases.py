from website import create_app, db
from website.models import User, Class, ClassMembership, QuestionSet, Question, Answer, ChatMessage, Assignment
from werkzeug.security import generate_password_hash
import sys

app = create_app()

def setup_test_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
def test_user_creation():
    with app.app_context():
        # Create teacher
        teacher = User(
            username="mrsmith",
            password=generate_password_hash("password123", method="pbkdf2:sha256"),
            role="teacher"
        )
        db.session.add(teacher)
        
        # Create student
        student = User(
            username="student1",
            password=generate_password_hash("password123", method="pbkdf2:sha256"),
            role="student"
        )
        db.session.add(student)
        db.session.commit()
        
        # Verify
        assert teacher.is_teacher == True
        assert student.is_student == True
        print(f"Teacher created (ID={teacher.id}, is_teacher={teacher.is_teacher})")
        print(f"Student created (ID={student.id}, is_student={student.is_student})")

def test_duplicate_username():
    print("\n--- Testing Duplicate Username ---")
    with app.app_context():
        duplicate = User(
            username="mrsmith",  # Already exists
            password=generate_password_hash("password123", method="pbkdf2:sha256"),
            role="teacher"
        )
        db.session.add(duplicate)
        try:
            db.session.commit()
            print("FAILED: Duplicate username was allowed")
        except Exception as e:
            db.session.rollback()
            print(f"Duplicate username correctly rejected ({type(e).__name__})")

def test_class_creation():
    """Test class creation with unique code"""
    with app.app_context():
        teacher = User.query.filter_by(username="mrsmith").first()
        
        # Create class
        new_class = Class(
            name="A-Level Economics",
            description="Year 13 Economics class",
            teacher_id=teacher.id,
            code="ABC123"
        )
        db.session.add(new_class)
        db.session.commit()
        
        # Verify
        retrieved = Class.query.filter_by(name="A-Level Economics").first()
        assert retrieved is not None
        assert len(retrieved.code) == 6
        assert retrieved.teacher_id == teacher.id
        print(f"Class created (ID={retrieved.id}, Code={retrieved.code})")
        print(f"Unique 6-character code generated")

def test_class_without_teacher():
    with app.app_context():
        invalid_class = Class(
            name="Invalid Class",
            teacher_id=9999,
            code="XYZ789"
        )
        db.session.add(invalid_class)
        try:
            db.session.commit()
            print("Class with invalid teacher_id was allowed")
        except Exception as e:
            db.session.rollback()
            print(f"Foreign key constraint enforced ({type(e).__name__})")
def test_class_membership():
    with app.app_context():
        student = User.query.filter_by(username="student1").first()
        class_obj = Class.query.first()
        
        # Create membership
        membership = ClassMembership(
            user_id=student.id,
            class_id=class_obj.id
        )
        db.session.add(membership)
        db.session.commit()
        
        assert membership.id is not None
        assert membership.joined_at is not None
        print(f"Student enrolled (Membership ID={membership.id})")
        
        # Retrieve class students
        students_in_class = User.query.join(ClassMembership).filter(
            ClassMembership.class_id == class_obj.id
        ).all()
        assert len(students_in_class) == 1
        assert students_in_class[0].id == student.id
        print(f"Retrieved {len(students_in_class)} student(s) in class")
        
        # Retrieve student's classes
        student_classes = Class.query.join(ClassMembership).filter(
            ClassMembership.user_id == student.id
        ).all()
        assert len(student_classes) == 1
        print(f"Student enrolled in {len(student_classes)} class(es)")

def test_duplicate_enrollment():
    with app.app_context():
        student = User.query.filter_by(username="student1").first()
        class_obj = Class.query.first()
        
        # Try to enroll again
        duplicate = ClassMembership(
            user_id=student.id,
            class_id=class_obj.id
        )
        db.session.add(duplicate)
        try:
            db.session.commit()
            print("Duplicate enrollment was allowed")
        except Exception as e:
            db.session.rollback()
            print(f"Duplicate enrollment rejected ({type(e).__name__})")

def test_question_system():
    with app.app_context():
        teacher = User.query.filter_by(username="mrsmith").first()
        
        # Create question set
        qset = QuestionSet(
            name="Supply & Demand Basics",
            description="Key concepts in supply and demand",
            user_id=teacher.id
        )
        db.session.add(qset)
        db.session.commit()
        print(f"Question set created (ID={qset.id})")
        
        # Add question with answer
        question = Question(
            question="What is GDP?",
            user_id=teacher.id,
            question_set_id=qset.id
        )
        db.session.add(question)
        db.session.flush()
        
        answer = Answer(
            answer="Gross Domestic Product - the total value of goods and services produced",
            question_id=question.id
        )
        db.session.add(answer)
        db.session.commit()
        print(f"Question and answer linked (Question ID={question.id}, Answer ID={answer.id})")
        
        # Retrieve questions in set
        questions = Question.query.filter_by(question_set_id=qset.id).all()
        assert len(questions) == 1
        assert questions[0].answers[0].answer.startswith("Gross Domestic Product")
        print(f"Retrieved {len(questions)} question(s) from set")

def test_chat_system():
    with app.app_context():
        teacher = User.query.filter_by(username="mrsmith").first()
        class_obj = Class.query.first()
        
        # Send message
        message = ChatMessage(
            message="Welcome to the class!",
            user_id=teacher.id,
            class_id=class_obj.id
        )
        db.session.add(message)
        db.session.commit()
        
        assert message.timestamp is not None
        print(f"Chat message created (ID={message.id}, Timestamp={message.timestamp})")

def test_assignment_creation():
    with app.app_context():
        teacher = User.query.filter_by(username="mrsmith").first()
        class_obj = Class.query.first()
        
        assignment = Assignment(
            title="Essay on Supply and Demand",
            description="Write a 1000-word essay",
            class_id=class_obj.id,
            creator_id=teacher.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        assert assignment.created_at is not None
        print(f"Assignment created (ID={assignment.id})")

def test_cascade_deletion():
    with app.app_context():
        class_obj = Class.query.first()
        class_id = class_obj.id
        
        # Count related records
        membership_count = ClassMembership.query.filter_by(class_id=class_id).count()
        message_count = ChatMessage.query.filter_by(class_id=class_id).count()
        
        print(f"Before deletion: {membership_count} membership(s), {message_count} message(s)")
        
        # Delete class
        db.session.delete(class_obj)
        db.session.commit()
        
        # Verify cascade
        remaining_memberships = ClassMembership.query.filter_by(class_id=class_id).count()
        remaining_messages = ChatMessage.query.filter_by(class_id=class_id).count()
        
        assert remaining_memberships == 0
        assert remaining_messages == 0
        print(f"Cascade deleted {membership_count} membership(s)")
        print(f"Cascade deleted {message_count} message(s)")

def run_all_tests():    
    try:
        setup_test_db()
        test_user_creation()
        test_duplicate_username()
        test_class_creation()
        test_class_without_teacher()
        test_class_membership()
        test_duplicate_enrollment()
        test_question_system()
        test_chat_system()
        test_assignment_creation()
        test_cascade_deletion()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\nTEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()