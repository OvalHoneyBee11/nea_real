"""
EconSpark Database Testing Script
Tests all database functionality according to the test plan
"""

from website import create_app, db
from website.models import User, Class, ClassMembership, QuestionSet, Question, ChatMessage, Assignment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_test(test_name, passed):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")

def test_user_creation():
    """Test T10, T10-A: Create teacher and student accounts"""
    print_section("Testing User Creation (T10, T10-A)")
    
    try:
        # Test teacher creation
        teacher = User(
            username="test_teacher",
            password=generate_password_hash("Teacher123"),
            role="teacher"  # Use role field, not is_teacher property
        )
        db.session.add(teacher)
        db.session.commit()
        
        # Verify teacher in database
        teacher_check = User.query.filter_by(username="test_teacher").first()
        print_test("Teacher account created", teacher_check is not None)
        print_test("Teacher role stored correctly", teacher_check.is_teacher == True)
        
        # Test student creation
        student = User(
            username="test_student",
            password=generate_password_hash("Student123"),
            role="student"  # Use role field, not is_teacher property
        )
        db.session.add(student)
        db.session.commit()
        
        # Verify student in database
        student_check = User.query.filter_by(username="test_student").first()
        print_test("Student account created", student_check is not None)
        print_test("Student role stored correctly", student_check.is_teacher == False)
        
        return teacher, student
    except Exception as e:
        print(f"✗ FAIL: Error during user creation - {e}")
        return None, None

def test_password_hashing(user):
    """Test T14-B: Password hashing in database"""
    print_section("Testing Password Hashing (T14-B)")
    
    try:
        # Check password is hashed
        is_hashed = (user.password.startswith('pbkdf2:') or 
                     user.password.startswith('scrypt:') or
                     len(user.password) > 50)  # Hashes are long
        print_test("Password stored as hash (not plaintext)", is_hashed)
        print_test("Password NOT in plaintext", 'Teacher123' not in user.password)
        
        # Test password verification
        correct_password = check_password_hash(user.password, "Teacher123")
        wrong_password = check_password_hash(user.password, "WrongPassword")
        print_test("Correct password validates", correct_password)
        print_test("Incorrect password rejected", not wrong_password)
        
        # Create another user with same password - different hash
        user2 = User(
            username="test_teacher2",
            password=generate_password_hash("Teacher123"),
            role="teacher"  # Use role field
        )
        db.session.add(user2)
        db.session.commit()
        
        same_hash = user.password == user2.password
        print_test("Same password produces different hash (salt)", not same_hash)
        
    except Exception as e:
        print(f"✗ FAIL: Error during password hashing test - {e}")

def test_unique_username():
    """Test T15-B: Duplicate username constraint"""
    print_section("Testing Unique Username Constraint (T15-B)")
    
    try:
        # Try to create duplicate username
        duplicate = User(
            username="test_teacher",  # Already exists
            password=generate_password_hash("Password123"),
            role="student"  # Use role field
        )
        db.session.add(duplicate)
        
        try:
            db.session.commit()
            print_test("Duplicate username rejected", False)
        except Exception:
            db.session.rollback()
            print_test("Duplicate username rejected", True)
            
    except Exception as e:
        print(f"✗ FAIL: Error during unique username test - {e}")

def test_username_validation(teacher):
    """Test T13, T13-A: Username exists check"""
    print_section("Testing Username Validation (T13, T13-A)")
    
    try:
        # Test existing username
        existing = User.query.filter_by(username="test_teacher").first()
        print_test("Existing username found", existing is not None)
        print_test("Username matches expected", existing.username == "test_teacher")
        
        # Test non-existent username
        non_existing = User.query.filter_by(username="nonexistent999").first()
        print_test("Non-existent username returns None", non_existing is None)
        
    except Exception as e:
        print(f"✗ FAIL: Error during username validation test - {e}")

def test_class_creation(teacher):
    """Test T11: Class creation with unique join code"""
    print_section("Testing Class Creation (T11)")
    
    try:
        # Create class
        test_class = Class(
            name="Test Economics 101",
            description="Test class for database testing",
            teacher_id=teacher.id,
            join_code="TESTAB"  # Set join code manually for testing
        )
        
        db.session.add(test_class)
        db.session.commit()
        
        # Verify class created
        class_check = Class.query.filter_by(name="Test Economics 101").first()
        print_test("Class created successfully", class_check is not None)
        print_test("Join code stored", class_check.join_code is not None)
        print_test("Join code length is 6", len(class_check.join_code) == 6)
        print_test("Teacher ID stored correctly", class_check.teacher_id == teacher.id)
        
        return test_class
    except Exception as e:
        print(f"✗ FAIL: Error during class creation - {e}")
        return None

def test_duplicate_class_names(teacher):
    """Test T12-W, T12-X: Duplicate class names"""
    print_section("Testing Duplicate Class Names (T12-W, T12-X)")
    
    try:
        # Test same teacher, same name
        class1 = Class(
            name="Economics 101",
            description="First class",
            teacher_id=teacher.id,
            join_code="ECON01"
        )
        db.session.add(class1)
        db.session.commit()
        
        class2 = Class(
            name="Economics 101",
            description="Second class",
            teacher_id=teacher.id,
            join_code="ECON02"
        )
        db.session.add(class2)
        
        try:
            db.session.commit()
            print_test("Same teacher duplicate class name rejected", False)
        except Exception:
            db.session.rollback()
            print_test("Same teacher duplicate class name rejected", True)
        
        # Test different teachers, same name (should work)
        teacher2 = User(
            username="test_teacher3",
            password=generate_password_hash("Teacher123"),
            role="teacher"  # Use role field
        )
        db.session.add(teacher2)
        db.session.commit()
        
        class3 = Class(
            name="Economics 101",
            description="Different teacher class",
            teacher_id=teacher2.id,
            join_code="ECON03"
        )
        db.session.add(class3)
        db.session.commit()
        
        print_test("Different teachers can have same class name", True)
        
    except Exception as e:
        print(f"✗ FAIL: Error during duplicate class name test - {e}")

def test_class_membership(test_class, student):
    """Test T11, T11-B: Class membership"""
    print_section("Testing Class Membership (T11, T11-B)")
    
    try:
        # Add student to class
        membership = ClassMembership(
            user_id=student.id,
            class_id=test_class.id
        )
        db.session.add(membership)
        db.session.commit()
        
        # Verify membership
        membership_check = ClassMembership.query.filter_by(
            user_id=student.id,
            class_id=test_class.id
        ).first()
        print_test("Student joined class", membership_check is not None)
        
        # Try to join again (should fail)
        membership2 = ClassMembership(
            user_id=student.id,
            class_id=test_class.id
        )
        db.session.add(membership2)
        
        try:
            db.session.commit()
            print_test("Duplicate membership rejected", False)
        except Exception:
            db.session.rollback()
            print_test("Duplicate membership rejected", True)
            
    except Exception as e:
        print(f"✗ FAIL: Error during class membership test - {e}")

def test_question_set_creation(teacher):
    """Test question set creation"""
    print_section("Testing Question Set Creation")
    
    try:
        # Create question set with unique name
        question_set = QuestionSet(
            name="Test Question Set 1",  # Unique name
            description="Test description",
            user_id=teacher.id
        )
        db.session.add(question_set)
        db.session.commit()
        
        # Verify question set
        set_check = QuestionSet.query.filter_by(name="Test Question Set 1").first()
        print_test("Question set created", set_check is not None)
        print_test("User ID stored correctly", set_check.user_id == teacher.id)
        
        # Test duplicate name by same user (should fail)
        question_set2 = QuestionSet(
            name="Test Question Set 1",  # Same name
            description="Another description",
            user_id=teacher.id
        )
        db.session.add(question_set2)
        
        try:
            db.session.commit()
            print_test("Duplicate set name (same user) rejected", False)
        except Exception:
            db.session.rollback()
            print_test("Duplicate set name (same user) rejected", True)
        
        return question_set
    except Exception as e:
        print(f"✗ FAIL: Error during question set creation - {e}")
        return None

def test_question_creation(question_set):
    """Test T05 series: Question creation"""
    print_section("Testing Question Creation (T05 series)")
    
    try:
        # Create normal question
        question1 = Question(
            question="What is GDP?",
            answer="Gross Domestic Product",
            question_set_id=question_set.id
        )
        db.session.add(question1)
        db.session.commit()
        
        q_check = Question.query.filter_by(question="What is GDP?").first()
        print_test("Question created successfully", q_check is not None)
        print_test("Answer stored correctly", q_check.answer == "Gross Domestic Product")
        
        # Test special characters (T05-E)
        question2 = Question(
            question="What is GDP📈?",
            answer="Test",
            question_set_id=question_set.id
        )
        db.session.add(question2)
        db.session.commit()
        
        q2_check = Question.query.filter_by(question="What is GDP📈?").first()
        print_test("Special characters in question handled", q2_check is not None)
        
        # Test long text (T05-D)
        long_question = "x" * 500
        question3 = Question(
            question=long_question,
            answer="Test",
            question_set_id=question_set.id
        )
        db.session.add(question3)
        db.session.commit()
        
        print_test("Long question text (500+ chars) handled", True)
        
        return question1
    except Exception as e:
        print(f"✗ FAIL: Error during question creation - {e}")
        return None

def test_sql_injection():
    """Test T07, T07-A, T12-S, T12-T, T12-U: SQL injection protection"""
    print_section("Testing SQL Injection Protection (T07, T12 series)")
    
    try:
        # First, get or create a question set for testing
        teacher = User.query.filter_by(username="test_teacher").first()
        if not teacher:
            print_test("SQL injection tests skipped - no teacher found", False)
            return
            
        test_set = QuestionSet(
            name="SQL Injection Test Set",  # Unique name
            description="For SQL injection testing",
            user_id=teacher.id
        )
        db.session.add(test_set)
        db.session.commit()
        
        # Test SQL injection in question (T07)
        malicious_question = "'; DROP TABLE question; --"
        question = Question(
            question=malicious_question,
            answer="Test",
            question_set_id=test_set.id
        )
        db.session.add(question)
        db.session.commit()
        
        # Check it was stored as plain text
        q_check = Question.query.filter_by(question=malicious_question).first()
        print_test("SQL injection in question stored as text", q_check is not None)
        
        # Verify tables still exist
        table_check = Question.query.count()
        print_test("Database tables intact after injection attempt", table_check >= 0)
        
        # Test SQL injection in question set name (T07-A)
        malicious_name = "' OR '1'='1 SQL Test"  # Made unique
        question_set = QuestionSet(
            name=malicious_name,
            description="Test",
            user_id=teacher.id
        )
        db.session.add(question_set)
        db.session.commit()
        
        set_check = QuestionSet.query.filter_by(name=malicious_name).first()
        print_test("SQL injection in set name stored as text", set_check is not None)
        
        # Test SQL injection in class name (T12-S)
        malicious_class = "Test'; DROP TABLE class;--"
        test_class = Class(
            name=malicious_class,
            description="Test",
            teacher_id=teacher.id,
            join_code="SQLTES"
        )
        db.session.add(test_class)
        db.session.commit()
        
        class_check = Class.query.filter_by(name=malicious_class).first()
        print_test("SQL injection in class name stored as text", class_check is not None)
        
        # Test SQL injection in chat message (T12-U)
        malicious_message = "Hello'; DROP TABLE chatmessage;--"
        message = ChatMessage(
            message=malicious_message,
            user_id=teacher.id,
            class_id=test_class.id
        )
        db.session.add(message)
        db.session.commit()
        
        message_check = ChatMessage.query.filter_by(message=malicious_message).first()
        print_test("SQL injection in chat message stored as text", message_check is not None)
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ FAIL: Error during SQL injection test - {e}")

def test_cascade_deletion(teacher):
    """Test T12-O: Cascade deletion"""
    print_section("Testing Cascade Deletion (T12-O)")
    
    try:
        # Create class with related data
        test_class = Class(
            name="Delete Test Class",
            description="For cascade testing",
            teacher_id=teacher.id,
            join_code="DELTES"
        )
        db.session.add(test_class)
        db.session.commit()
        
        # Add membership
        membership = ClassMembership(
            user_id=teacher.id,
            class_id=test_class.id
        )
        db.session.add(membership)
        
        # Add chat message
        message = ChatMessage(
            message="Test message for cascade",
            user_id=teacher.id,
            class_id=test_class.id
        )
        db.session.add(message)
        
        # Add assignment
        assignment = Assignment(
            title="Cascade Test Assignment",
            description="Test description for cascade",
            class_id=test_class.id,
            creator_id=teacher.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        class_id = test_class.id
        
        # Count related records
        membership_count = ClassMembership.query.filter_by(class_id=class_id).count()
        message_count = ChatMessage.query.filter_by(class_id=class_id).count()
        assignment_count = Assignment.query.filter_by(class_id=class_id).count()
        
        print_test(f"Related records created (memberships: {membership_count})", membership_count > 0)
        print_test(f"Related records created (messages: {message_count})", message_count > 0)
        print_test(f"Related records created (assignments: {assignment_count})", assignment_count > 0)
        
        # Delete class
        db.session.delete(test_class)
        db.session.commit()
        
        # Check cascade deletion
        membership_after = ClassMembership.query.filter_by(class_id=class_id).count()
        message_after = ChatMessage.query.filter_by(class_id=class_id).count()
        assignment_after = Assignment.query.filter_by(class_id=class_id).count()
        
        print_test("Memberships cascade deleted", membership_after == 0)
        print_test("Chat messages cascade deleted", message_after == 0)
        print_test("Assignments cascade deleted", assignment_after == 0)
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ FAIL: Error during cascade deletion test - {e}")

def test_foreign_key_relationships():
    """Test foreign key relationships"""
    print_section("Testing Foreign Key Relationships")
    
    try:
        # Test User -> QuestionSet relationship
        teacher = User.query.filter_by(username="test_teacher").first()
        if teacher:
            sets_count = len(teacher.question_sets)
            print_test("User -> QuestionSet relationship works", sets_count >= 0)
        
            # Test User -> Class (teacher) relationship
            # Try different possible relationship names
            if hasattr(teacher, 'classes_taught'):
                classes_count = len(teacher.classes_taught)
                print_test("User -> Class (teacher) relationship works", classes_count >= 0)
            elif hasattr(teacher, 'classes'):
                classes_count = len(teacher.classes)
                print_test("User -> Class (teacher) relationship works", classes_count >= 0)
            else:
                print_test("User -> Class (teacher) relationship works", False)
                print("  Note: Relationship attribute not found (tried 'classes_taught' and 'classes')")
        
        # Test Class -> Teacher relationship
        test_class = Class.query.first()
        if test_class:
            print_test("Class -> Teacher relationship works", test_class.teacher is not None)
        
        # Test QuestionSet -> Questions relationship
        question_set = QuestionSet.query.first()
        if question_set:
            questions_count = len(question_set.questions)
            print_test("QuestionSet -> Questions relationship works", questions_count >= 0)
        
    except Exception as e:
        print(f"✗ FAIL: Error during foreign key relationship test - {e}")

def test_chat_messages(test_class, teacher, student):
    """Test T12-B to T12-F: Chat message functionality"""
    print_section("Testing Chat Messages (T12-B to T12-F)")
    
    try:
        # Create chat message
        message = ChatMessage(
            message="Hello class from chat test!",  # Unique message
            user_id=teacher.id,
            class_id=test_class.id
        )
        db.session.add(message)
        db.session.commit()
        
        # Verify message
        msg_check = ChatMessage.query.filter_by(
            user_id=teacher.id,
            class_id=test_class.id
        ).first()
        print_test("Chat message created", msg_check is not None)
        print_test("Message text stored correctly", "chat test" in msg_check.message)
        print_test("Timestamp created", msg_check.timestamp is not None)
        print_test("User relationship works", msg_check.user is not None)
        
        # Test chronological order
        message2 = ChatMessage(
            message="Second message from student",  # Unique message
            user_id=student.id,
            class_id=test_class.id
        )
        db.session.add(message2)
        db.session.commit()
        
        messages = ChatMessage.query.filter_by(class_id=test_class.id).order_by(ChatMessage.timestamp).all()
        if len(messages) >= 2:
            chronological = messages[0].timestamp <= messages[1].timestamp
            print_test("Messages in chronological order", chronological)
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ FAIL: Error during chat message test - {e}")

def test_assignments(test_class, teacher):
    """Test T12-G to T12-N: Assignment functionality"""
    print_section("Testing Assignments (T12-G to T12-N)")
    
    try:
        # Create complete assignment (T12-G)
        assignment = Assignment(
            title="Essay on Supply & Demand - Assignment Test",  # Unique title
            description="Write 500 words for assignment test",
            due_date=datetime(2025, 12, 25),
            attachment_url="rubric.pdf",
            class_id=test_class.id,
            creator_id=teacher.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        a_check = Assignment.query.filter_by(title="Essay on Supply & Demand - Assignment Test").first()
        print_test("Complete assignment created", a_check is not None)
        print_test("Due date stored correctly", a_check.due_date is not None)
        print_test("Attachment URL stored", a_check.attachment_url == "rubric.pdf")
        
        # Create assignment with optional fields empty (T12-H)
        assignment2 = Assignment(
            title="Reading Assignment - Test Optional Fields",  # Unique title
            description="Read Chapter 5 for testing",
            class_id=test_class.id,
            creator_id=teacher.id
        )
        db.session.add(assignment2)
        db.session.commit()
        
        a2_check = Assignment.query.filter_by(title="Reading Assignment - Test Optional Fields").first()
        print_test("Assignment with optional fields created", a2_check is not None)
        print_test("Null due date accepted", a2_check.due_date is None)
        print_test("Null attachment accepted", a2_check.attachment_url is None)
        
        # Verify foreign key relationships
        if a_check:
            print_test("Assignment -> Class relationship works", a_check.class_obj is not None)
            print_test("Assignment -> Creator relationship works", a_check.creator is not None)
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ FAIL: Error during assignment test - {e}")

def run_all_tests():
    """Run all database tests"""
    print("\n" + "="*60)
    print("  ECONSPARK DATABASE TEST SUITE")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        # Clear existing test data thoroughly
        print("\nClearing test data...")
        try:
            # Delete test data in reverse order of dependencies
            Assignment.query.filter(Assignment.title.like('%Test%')).delete()
            ChatMessage.query.filter(ChatMessage.message.like('%Test%')).delete()
            ClassMembership.query.filter(
                ClassMembership.user_id.in_(
                    db.session.query(User.id).filter(User.username.like('test_%'))
                )
            ).delete(synchronize_session=False)
            
            Question.query.filter(Question.question.like('%Test%')).delete()
            Question.query.filter(Question.question.like("%'%")).delete()  # SQL injection tests
            
            QuestionSet.query.filter(QuestionSet.name.like('%Test%')).delete()
            QuestionSet.query.filter(QuestionSet.name.like("%'%")).delete()  # SQL injection tests
            
            Class.query.filter(Class.name.like('%Test%')).delete()
            Class.query.filter(Class.name.like('%Economics%')).delete()
            Class.query.filter(Class.name.like("%'%")).delete()  # SQL injection tests
            
            User.query.filter(User.username.like('test_%')).delete()
            
            db.session.commit()
            print("✓ Test data cleared successfully")
        except Exception as e:
            print(f"⚠ Warning during cleanup: {e}")
            db.session.rollback()
        
        # Run tests
        teacher, student = test_user_creation()
        
        if teacher and student:
            test_password_hashing(teacher)
            test_unique_username()
            test_username_validation(teacher)
            
            test_class = test_class_creation(teacher)
            test_duplicate_class_names(teacher)
            
            if test_class:
                test_class_membership(test_class, student)
                test_chat_messages(test_class, teacher, student)
                test_assignments(test_class, teacher)
            
            question_set = test_question_set_creation(teacher)
            if question_set:
                test_question_creation(question_set)
            
            test_sql_injection()
            test_foreign_key_relationships()
            test_cascade_deletion(teacher)
        
        print_section("DATABASE TESTS COMPLETE")
        print("Review results above to identify any failures.\n")

if __name__ == "__main__":
    run_all_tests()