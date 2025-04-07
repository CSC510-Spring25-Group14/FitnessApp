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
  
  if len(query_output_list) > 0 and query_output_list[0]["calories"] > 0:
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
  
  if len(query_output_list) > 0 and query_output_list[0]["calories"] > 0:
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
  
  if len(query_output_list) > 0 and query_output_list[0]["averageCalories"] > 0:
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

def get_max_water_intake(email, db):
  """
    Get the Maximum amount of Water Intake by the current user in a day
  """
  max_water_pipeline = [
    {"$match": {"email": email}},
    {"$group": {
      "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$time", "timezone": "+00:00"}},
      "totalIntake": {"$sum": {"$toInt": "$intake"}}
      }
    },
    {"$sort": {"totalIntake": -1}},
    {"$limit": 1},
    {"$project": {"_id": 0, "date": "$_id", "intake": "$totalIntake"}}
  ]

  query_output_list = list(db.intake_collection.aggregate(max_water_pipeline))
  
  if len(query_output_list) > 0 and query_output_list[0]["intake"] > 0:
    max_water_in_a_day = query_output_list[0]["intake"]
    description = "On " + convert_date_to_words(query_output_list[0]["date"])
  else:
    max_water_in_a_day = 0
    description = "No records on Water intake"

  max_water_data = {"name": "Maximum Water Intake in a day", "data": max_water_in_a_day, "description": description}

  return max_water_data

def get_min_water_intake(email, db):
  """
    Get the Minimum amount of Water Intake by the current user in a day
  """
  min_water_pipeline = [
    {"$match": {"email": email}},
    {"$group": {
      "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$time", "timezone": "+00:00"}},
      "totalIntake": {"$sum": {"$toInt": "$intake"}}
      }
    },
    {"$sort": {"totalIntake": 1}},
    {"$limit": 1},
    {"$project": {"_id": 0, "date": "$_id", "intake": "$totalIntake"}}
  ]

  query_output_list = list(db.intake_collection.aggregate(min_water_pipeline))
  
  if len(query_output_list) > 0 and query_output_list[0]["intake"] > 0:
    min_water_in_a_day = query_output_list[0]["intake"]
    description = "On " + convert_date_to_words(query_output_list[0]["date"])
  else:
    min_water_in_a_day = 0
    description = "No records on Water intake"

  min_water_data = {"name": "Minimum Water Intake in a day", "data": min_water_in_a_day, "description": description}

  return min_water_data

def get_avg_water_intake(email, db):
  """
    Get the Average amount of Water Intake by the current user in a day
  """
  avg_water_pipeline = [
    {"$match": {"email": email}},
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$time", "timezone": "+00:00"}},
        "dailyTotal": {"$sum": {"$toInt": "$intake"}}
      }
    },
    {"$group": {"_id": None, "average": {"$avg": "$dailyTotal"}}
    }
  ]

  query_output_list = list(db.intake_collection.aggregate(avg_water_pipeline))
  
  if len(query_output_list) > 0 and query_output_list[0]["average"] > 0:
    avg_water_in_a_day = floor(query_output_list[0]["average"]) 
    if avg_water_in_a_day > 4000 or avg_water_in_a_day < 1900:
      description = "Recommended 2-3 litres of water in a day"
    else:
      description = "It's always good to maintain around 2-3 litres of water intake per day"
  else:
    avg_water_in_a_day = 0
    description = "No records on Water intake"

  avg_water_data = {"name": "Average Water Intake per day", "data": avg_water_in_a_day, "description": description}

  return avg_water_data

def get_max_burnout(email, db):
  """
    Get the Maximum Burnout consumed by the current user in a day
  """
  max_burnout_pipeline = [
    {"$match": {"email": email}},
    {"$group": {"_id": "$date", "totalBurnout": {"$sum": "$burnout"}}},
    {"$sort": {"totalBurnout": -1}},
    {"$limit": 1},
    {"$project": {"_id": 0, "date": "$_id", "burnout": "$totalBurnout"}}
  ]
  
  query_output_list = list(db.calories.aggregate(max_burnout_pipeline))
  
  if len(query_output_list) > 0 and query_output_list[0]["burnout"] > 0:
    max_burnout_in_a_day = query_output_list[0]["burnout"]
    description = "On " + convert_date_to_words(query_output_list[0]["date"])
  else:
    max_burnout_in_a_day = 0
    description = "No records on burnout"

  max_burnout_data = {"name": "Maximum Burnout Calories in a day", "data": max_burnout_in_a_day, "description": description}

  return max_burnout_data

def get_min_burnout(email, db):
  """
    Get the Minimum Burnout consumed by the current user in a day
  """
  min_burnout_pipeline = [
    {"$match": {"email": email}},
    {"$group": {"_id": "$date", "totalBurnout": {"$sum": "$burnout"}}},
    {"$sort": {"totalBurnout": -1}},
    {"$limit": 1},
    {"$project": {"_id": 0, "date": "$_id", "burnout": "$totalBurnout"}}
  ]
  
  query_output_list = list(db.calories.aggregate(min_burnout_pipeline))
  
  if len(query_output_list) > 0 and query_output_list[0]["burnout"] > 0:
    min_burnout_in_a_day = query_output_list[0]["burnout"]
    description = "On " + convert_date_to_words(query_output_list[0]["date"])
  else:
    min_burnout_in_a_day = 0
    description = "No records on burnout"

  min_burnout_data = {"name": "Maximum Burnout Calories in a day", "data": min_burnout_in_a_day, "description": description}

  return min_burnout_data

def get_avg_burnout(email, db):
  """
    Get the Average Burnout by the current user in a day
  """
  avg_burnout_pipeline = [
    {"$match": {"email": email}},
    {"$group": {"_id": "$date", "dailyTotal": {"$sum": "$burnout"}}},
    {"$group": {"_id": None, "averageBurnout": {"$avg": "$dailyTotal"}}}
  ]
  
  query_output_list = list(db.calories.aggregate(avg_burnout_pipeline))
  
  if len(query_output_list) > 0 and query_output_list[0]["averageBurnout"] > 0:
    avg_burnout_in_a_day = floor(query_output_list[0]["averageBurnout"])
    if avg_burnout_in_a_day > 2900 or avg_burnout_in_a_day < 1500:
      description = "Recommended a burnout of about 2000 calories in a day"
    else:
      description = "You're doing great !"
  else:
    avg_burnout_in_a_day = 0
    description = "No records on Water intake"

  avg_burnout_data = {"name": "Average Burnout Calories per day", "data": avg_burnout_in_a_day, "description": description}

  return avg_burnout_data

def get_chart_data(email, db, data_type):
  """
    Get the past 7 days data of the current user
  """

  try:
    # Calculate date range (last 7 days inclusive)
    end_date = datetime.now(timezone.utc) - timedelta(hours=4) - timedelta(days=1)
    start_date = end_date - timedelta(days=6)  # 7 days including today
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    if data_type == "water":
      pipeline = [
          {"$match": {
              "email": email,
              "time": {"$gte": start_date, "$lte": end_date}
          }},
          {"$addFields": {
              "numericValue": {"$toInt": "$intake"}
          }},
          {"$group": {
              "_id": {"$dateToString": {
                  "format": "%Y-%m-%d",
                  "date": "$time",
                  "timezone": "+00:00"
              }},
              "total": {"$sum": "$numericValue"}
          }},
          {"$sort": {"_id": 1}}
        ]
      results = list(db.intake_collection.aggregate(pipeline))
    else:
      value_field = "$" + str(data_type)
      pipeline = [
        {"$match": {"email": email, "date": {"$gte": start_date_str, "$lte": end_date_str}}},
        {"$addFields": {"numericValue": {"$toInt": value_field}}},
        {"$group": {"_id": "$date", "total": {"$sum": "$numericValue"}}},
        {"$sort": {"_id": 1}}
      ]

      results = list(db.calories.aggregate(pipeline))
    
    # Convert to date:value dictionary
    user_data = {item['_id']: item['total'] for item in results}
    
    # Generate labels for last 7 days
    date_labels = [
        (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(6, -1, -1)
    ]
    
    # Fill missing dates with 0
    chart_data = [user_data.get(date, 0) for date in date_labels]
    
    return {
      "labels": date_labels,
      "values": chart_data
    }
  
  except Exception as e:
    return {"error": str(e)}
