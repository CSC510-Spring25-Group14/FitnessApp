import pytest
from flask import session
from unittest.mock import patch
import mongomock
from application import app, mongo  # Import your Flask app and the `get_insights` function
from datetime import date

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

    with open("response_2.html", "w") as file:
        file.write(str(insight_response.data))

    # As of now, the user has enrolled in one course, and completed it.
    # Assert the corresponding message for not completing any of the enrolled courses
    assert b"Completed 100.0% of the courses enrolled in" in insight_response.data

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": user["email"]})
    mongo.db.achievements.delete_many({"Email": user["email"]})

