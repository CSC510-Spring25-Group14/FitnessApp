import pytest
from application import app, mongo  # Import your Flask app and the `get_insights` function
from datetime import date
import os
import json

@pytest.fixture
def client():
    """Fixture to set up the Flask test client."""
    app.testing = True
    with app.test_client() as client:
        yield client

# Database user
def mock_user():
    return {
        "name": "mpartha",
        "email": "mpartha@gmail.com",
        "password": "3g:$*fe9R=@9zx",
    }

def insert_test_calorie_burnout_data(data_file_name):
    
    # Set project root directory for standardization.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Define the path to the CSV file
    calorie_data_file_path = os.path.join(project_root, "tests", "data", data_file_name)

    # Load JSON data
    try:
        with open(calorie_data_file_path, "r") as file:
            json_data = json.load(file)
        
        if isinstance(json_data, list):
            mongo.db.calories.insert_many(json_data)
            print("Test calorie, burnout data inserted successfully")
        else:
            print("The JSON file does not contain an array of objects.")
    except FileNotFoundError:
        print(f"File not found: {calorie_data_file_path}")
    except json.JSONDecodeError:
        print("Error decoding JSON. Please check the file format.")
    except Exception as e:
        print(f"An error occurred: {e}")

def test_zero_course_completion_rate(client):
    """
        Test case for when the user has enrolled in a course, but has not completed it.
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": user["email"]})

    # Try to enroll in abs
    response = client.post(
        "/abs",
        data={
            "action": "enroll",
            "Email": user["email"],
            "Activity": "abs",
            "Status": "Enrolled",
            "Date": date.today().strftime("%Y-%m-%d"),
        },
        follow_redirects=True,
    )

    assert b"You have successfully enrolled in abs!" in response.data
    
    # Make a GET request to the /insights route
    response = client.get('/insights')

    # As of now, the user has enrolled in one course, but have not completed it.
    # Assert the corresponding message for not completing any of the enrolled courses
    assert b"get your first course completed" in response.data

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": user["email"]})

def test_non_zero_course_completion_rate(client):
    """
        Test case for when the user has enrolled in a course, but has not completed it.
    """
    
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": user["email"]})

    # Try to enroll in abs
    response = client.post(
        "/abs",
        data={
            "action": "enroll",
            "Email": user["email"],
            "Activity": "abs",
            "Status": "Enrolled",
            "Date": date.today().strftime("%Y-%m-%d"),
        },
        follow_redirects=True,
    )

    assert b"You have successfully enrolled in abs!" in response.data
    
    # Mark the enrolled course in abs as completed
    response = client.post(
        "/abs",
        data={
            "action": "complete",
            "Email": user["email"],
            "Activity": "abs",
            "Status": "Completed",
            "Date": date.today().strftime("%Y-%m-%d"),
        },
        follow_redirects=True,
    )

    # Make a GET request to the /insights route
    insight_response = client.get('/insights')

    # As of now, the user has enrolled in one course, and completed it.
    # Assert the corresponding message for not completing any of the enrolled courses
    assert b"Completed 100.0% of the courses enrolled in" in insight_response.data

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": user["email"]})
    mongo.db.achievements.delete_many({"Email": user["email"]})

def test_get_max_calorie_intake(client):
    """
        Test case for when the user has logged their calorie intake, one should be able to retrieve the max calorie intake in a day.
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_max_min_calorie_burnout_data.json"
    
    # Insert test data
    insert_test_calorie_burnout_data(data_file_name)
    
    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"1970" in response.data
    assert b"On March 29, 2025" in response.data

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

def test_get_min_calorie_intake(client):
    """
        Test case for when the user has logged their calorie intake, one should be able to retrieve the min calorie intake in a day.
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_max_min_calorie_burnout_data.json"
    
    # Insert test data
    insert_test_calorie_burnout_data(data_file_name)
    
    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"500" in response.data
    assert b"On April 03, 2025" in response.data

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

def test_get_avg_calorie_intake_1(client):
    """
        Test case for when the user has logged their calorie intake, one should be able to retrieve the average calorie intake in a day.
        In this case, we expect a 'Recommended 2000 calories in a day' message 
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_max_min_calorie_burnout_data.json"
    
    # Insert test data (Recommended 2000 calories in a day)
    insert_test_calorie_burnout_data(data_file_name)
    
    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"1101" in response.data
    assert b"Recommended 2000 calories in a day" in response.data

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

def test_get_avg_calorie_intake_2(client):
    """
        Test case for when the user has logged their calorie intake, one should be able to retrieve the average calorie intake in a day.
        In this case, we expect a 'always good to maintain around 2000 calories per day' message. 
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_good_avg_calorie_burnout_data.json"
    
    # Insert test data ()
    insert_test_calorie_burnout_data(data_file_name)

    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"2013" in response.data
    assert b"always good to maintain around 2000 calories per day" in response.data

def test_get_max_burnout(client):
    """
        Test case for when the user has logged their calorie intake, one should be able to retrieve the max burnout in a day.
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_max_min_calorie_burnout_data.json"
    
    # Insert test data
    insert_test_calorie_burnout_data(data_file_name)
    
    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"3000" in response.data
    assert b"On April 01, 2025" in response.data

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

def test_get_min_burnout(client):
    """
        Test case for when the user has logged their calorie intake, one should be able to retrieve the min burnout in a day.
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_max_min_calorie_burnout_data.json"
    
    # Insert test data
    insert_test_calorie_burnout_data(data_file_name)
    
    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"180" in response.data
    assert b"On March 26, 2025" in response.data

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

def test_get_avg_burnout_1(client):
    """
        Test case for when the user has logged their burnout, one should be able to retrieve the average burnout in a day.
        In this case, we expect a 'Recommended a burnout of about 2000 calories in a day' message.
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_max_min_calorie_burnout_data.json"
    
    # Insert test data (Recommended 2000 calories in a day)
    insert_test_calorie_burnout_data(data_file_name)
    
    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"1257" in response.data
    assert b"Recommended a burnout of about 2000 calories in a day" in response.data

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

def test_get_avg_burnout_2(client):
    """
       Test case for when the user has logged their burnout, one should be able to retrieve the average burnout in a day.
        In this case, we expect a 'always good to maintain around 2000 calories per day' message.
    """
    # Simulate a logged-in user by setting session data
    with client.session_transaction() as sess:
        user = mock_user()
        sess['email'] = user["email"]

    # Get rid of everything related to this user
    mongo.db.calories.delete_many({"email": user["email"]})

    # JSON data file name
    data_file_name = "test_good_avg_calorie_burnout_data.json"
    
    # Insert test data ()
    insert_test_calorie_burnout_data(data_file_name)

    # Make a GET request to the /insights route
    response = client.get('/insights')

    assert b"2500" in response.data
    assert b"doing great !" in response.data
