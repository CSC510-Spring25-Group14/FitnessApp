"""
Copyright (c) 2025 Shivang Nithinkumar Patel, Neel Ghoshal and Mano Prakash Parthasarathi
This code is licensed under MIT license (see LICENSE for details)

@author: Mano Prakash Parthasarathi


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/CSC510-Spring25-Group14/FitnessApp
"""

from utilities import convert_date_to_words
from math import floor
from datetime import datetime, timedelta, timezone
from flask import jsonify

def get_insights(email, db):
  """
    This function accepts email address of the user as input and 
    then returns all the insights based on the user data from MongoDB.
  """
  insights = []
  
  # Courses Enrolled in
  insights.append(get_number_of_courses_enrolled(email, db))
  
  # Courses Completed
  insights.append(get_number_of_courses_completed(email, db))
  
  # Reviews Submitted
  insights.append(get_number_of_reviews_submitted(email,db))

  # Max Calories in a day
  insights.append(get_max_calorie(email, db))

  # Min Calories in a day
  insights.append(get_min_calorie(email, db))

  # Average Calories per day
  insights.append(get_avg_calorie_intake(email, db))

  # Max Water intake in a day
  insights.append(get_max_water_intake(email, db))

  # Min Water intake in a day
  insights.append(get_min_water_intake(email, db))

  # Average Water intake per day
  insights.append(get_avg_water_intake(email, db))

  # Max Burnout in a day
  insights.append(get_max_burnout(email, db))

  # Min Burnout in a day
  insights.append(get_min_burnout(email, db))

  # Average Burnout per day
  insights.append(get_avg_burnout(email, db))

  # Get data for past 7 days water intake
  water_intake_data = get_chart_data(email, db, data_type="water")

  # Get data for past 7 days calorie intake
  calorie_intake_data = get_chart_data(email, db, data_type="calories")

  # Get data for past 7 days burnout
  burnout_data = get_chart_data(email, db, data_type="burnout")

  return insights, water_intake_data, calorie_intake_data, burnout_data

def get_number_of_courses_enrolled(email, db):
  """
    Get the Number of Courses in which the current user enrolled in
  """
  courses_enrolled_count = db.user_activity.count_documents({"Email": email,"Status": "Enrolled"})
  description = ""
  
  if courses_enrolled_count == 0:
    description = "No worries. Let's get enrolled in your favorite course !"

  courses_enrolled_data = {"name": "Number of Courses Enrolled", "data": courses_enrolled_count, "description": description} 
  
  return courses_enrolled_data

def get_number_of_courses_completed(email, db):
  """
    Get the Number of Courses completed by the current user
  """
  courses_completed_count = db.user_activity.count_documents({"Email": email,"Status": "Completed"})
  courses_enrolled_count = db.user_activity.count_documents({"Email": email,"Status": "Enrolled"})
  description = ""

  if courses_enrolled_count != 0:
    completion_rate = (courses_completed_count / courses_enrolled_count) * 100
    if completion_rate != 0:
      description = "Completed " + str(completion_rate) + "% of the courses enrolled in"
    else:
      description = "No worries. Let's get your first course completed"
  else:
    description = "" # Left empty as it is handled in Courses Enrolled Tab

  courses_completed_data = {"name": "Number of Courses Completed", "data": courses_completed_count, "description": description} 

  return courses_completed_data

def get_number_of_reviews_submitted(email, db):
  """
    Get the Number of Reviews submitted by the current user
  """
  reviews_submitted_count = db.reviews.count_documents({"Email": email})
  description = ""

  if reviews_submitted_count == 0:
    description = "It's never late to submit your review"

  reviews_submitted_data = {"name": "Number of Reviews Submitted", "data": reviews_submitted_count, "description": description} 

  return reviews_submitted_data

def get_max_calorie(email, db):
  """
    Get the Maximum number of Calorie consumed by the current user in a day
  """
  max_calorie_pipeline = [
    {"$match": {"email": email}},
    {"$group": {"_id": "$date", "totalCalories": {"$sum": "$calories"}}},
    {"$sort": {"totalCalories": -1}},
    {"$limit": 1},
    {"$project": {"_id": 0, "date": "$_id", "calories": "$totalCalories"}}
  ]
  
  query_output_list = list(db.calories.aggregate(max_calorie_pipeline))
  
  if query_output_list[0]["calories"] > 0:
    max_calorie_in_a_day = query_output_list[0]["calories"]
    description = "On " + convert_date_to_words(query_output_list[0]["date"])
  else:
    max_calorie_in_a_day = 0
    description = "No records on calorie intake"

  max_calorie_data = {"name": "Maximum Calories in a day", "data": max_calorie_in_a_day, "description": description}

  return max_calorie_data

def get_min_calorie(email, db):
  """
    Get the Minimum number of Calorie consumed by the current user in a day
  """
  min_calorie_pipeline = [
    {"$match": {"email": email}},
    {"$group": {"_id": "$date", "totalCalories": {"$sum": "$calories"}}},
    {"$sort": {"totalCalories": 1}},
    {"$limit": 1},
    {"$project": {"_id": 0, "date": "$_id", "calories": "$totalCalories"}}
  ]
  
  query_output_list = list(db.calories.aggregate(min_calorie_pipeline))
  
  if query_output_list[0]["calories"] > 0:
    min_calorie_in_a_day = query_output_list[0]["calories"]
    description = "On " + convert_date_to_words(query_output_list[0]["date"])
  else:
    min_calorie_in_a_day = 0
    description = "No records on calorie intake"

  min_calorie_data = {"name": "Minimum Calories in a day", "data": min_calorie_in_a_day, "description": description}

  return min_calorie_data

def get_avg_calorie_intake(email, db):
  """
    Get the Average number of Calorie consumed by the current user in a day
  """
  avg_calorie_pipeline = [
    {"$match": {"email": email}},
    {"$group": {"_id": "$date", "dailyTotal": {"$sum": "$calories"}}},
    {"$group": {"_id": None, "averageCalories": {"$avg": "$dailyTotal"}}}
  ]
  
  query_output_list = list(db.calories.aggregate(avg_calorie_pipeline))
  
  if query_output_list[0]["averageCalories"] > 0:
    avg_calorie_in_a_day = floor(query_output_list[0]["averageCalories"])
    if avg_calorie_in_a_day > 2100 or avg_calorie_in_a_day < 1900:
      description = "Recommended 2000 calories in a day"
    else:
      description = "It's always good to maintain around 2000 calories per day"
  else:
    avg_calorie_in_a_day = 0
    description = "No records on calorie intake"

  avg_calorie_data = {"name": "Minimum Calories in a day", "data": avg_calorie_in_a_day, "description": description}

  return avg_calorie_data
