import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from config import Config
from app.db import execute_query, init_db
from app.models.user_model import UserModel
from app.models.daily_record_model import DailyRecordModel

def seed_user_historical_records(user_id, num_days=15):
    """
    Populates realistic historical daily records for a specific user.
    Skips dates that already exist to avoid duplicate records.
    """
    start_date = datetime.now() - timedelta(days=num_days)
    inserted_count = 0

    for i in range(num_days):
        cur_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Check if record already exists for this date
        existing = DailyRecordModel.get_by_date(user_id, cur_date)
        if existing:
            continue

        # Generate realistic habit metrics
        profile_type = random.choices(['balanced', 'workaholic', 'burnout_risk', 'sedentary'], weights=[0.4, 0.3, 0.15, 0.15])[0]
        if profile_type == 'balanced':
            sleep, work, screen, exercise, stress, mood = 7.5, 7.5, 3.0, 45, 3, 'Happy'
        elif profile_type == 'workaholic':
            sleep, work, screen, exercise, stress, mood = 6.0, 10.0, 5.0, 15, 7, 'Focused'
        elif profile_type == 'burnout_risk':
            sleep, work, screen, exercise, stress, mood = 5.0, 11.0, 7.0, 10, 9, 'Stressed'
        else:
            sleep, work, screen, exercise, stress, mood = 8.5, 4.0, 7.0, 10, 5, 'Tired'

        prod_score = (
            (sleep / 8.0) * 25.0 +
            min(work / 8.0, 1.2) * 35.0 +
            (exercise / 45.0) * 15.0 -
            (stress / 10.0) * 20.0 -
            (screen / 10.0) * 10.0 +
            random.uniform(-3.0, 3.0)
        )
        prod_score = round(max(10.0, min(100.0, prod_score)), 2)

        DailyRecordModel.add_or_update(
            user_id, cur_date, sleep, work, screen, exercise, stress, mood, prod_score, f"Historical log {cur_date}"
        )
        inserted_count += 1

    return inserted_count

def generate_synthetic_data(num_days=180):
    """Generates synthetic daily logs and tasks for training ML models."""
    print("Ensuring database schema exists...")
    init_db()

    # Create demo user if not exists
    demo_user = UserModel.get_by_email("demo@lifepilot.ai")
    if not demo_user:
        user_id = UserModel.create_user("demo_user", "demo@lifepilot.ai", "DemoPassword123!")
        print(f"Created demo user with ID: {user_id}")
    else:
        user_id = demo_user['id']
        print(f"Using existing demo user ID: {user_id}")

    moods = ['Happy', 'Focused', 'Neutral', 'Tired', 'Stressed']
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Health', 'Shopping']
    
    start_date = datetime.now() - timedelta(days=num_days)
    
    print(f"Generating {num_days} days of synthetic daily life records...")
    
    for i in range(num_days):
        cur_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Simulate realistic lifestyle clusters
        profile_type = random.choices(['balanced', 'workaholic', 'burnout_risk', 'sedentary'], weights=[0.4, 0.3, 0.15, 0.15])[0]
        
        if profile_type == 'balanced':
            sleep = round(random.uniform(7.0, 8.5), 2)
            work = round(random.uniform(6.0, 8.0), 2)
            screen = round(random.uniform(2.0, 4.0), 2)
            exercise = random.randint(30, 60)
            stress = random.randint(2, 4)
            mood = random.choice(['Happy', 'Focused', 'Neutral'])
        elif profile_type == 'workaholic':
            sleep = round(random.uniform(5.5, 6.8), 2)
            work = round(random.uniform(9.0, 12.0), 2)
            screen = round(random.uniform(4.0, 7.0), 2)
            exercise = random.randint(0, 20)
            stress = random.randint(6, 8)
            mood = random.choice(['Focused', 'Stressed', 'Tired'])
        elif profile_type == 'burnout_risk':
            sleep = round(random.uniform(4.0, 5.5), 2)
            work = round(random.uniform(10.0, 13.0), 2)
            screen = round(random.uniform(6.0, 9.0), 2)
            exercise = random.randint(0, 15)
            stress = random.randint(8, 10)
            mood = random.choice(['Stressed', 'Tired'])
        else: # sedentary / low activity
            sleep = round(random.uniform(8.0, 10.0), 2)
            work = round(random.uniform(3.0, 5.0), 2)
            screen = round(random.uniform(6.0, 10.0), 2)
            exercise = random.randint(0, 15)
            stress = random.randint(4, 6)
            mood = random.choice(['Neutral', 'Tired'])

        # Ground truth formula for realistic synthetic productivity score (0-100)
        prod_score = (
            (sleep / 8.0) * 25.0 +
            min(work / 8.0, 1.2) * 35.0 +
            (exercise / 45.0) * 15.0 -
            (stress / 10.0) * 20.0 -
            (screen / 10.0) * 10.0 +
            random.uniform(-5.0, 5.0)
        )
        prod_score = round(max(10.0, min(100.0, prod_score)), 2)

        # Insert record
        sql = """
        INSERT INTO daily_records 
            (user_id, record_date, sleep_hours, work_hours, screen_time, exercise_mins, stress_level, mood, productivity_score, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            sleep_hours=VALUES(sleep_hours), work_hours=VALUES(work_hours), screen_time=VALUES(screen_time),
            exercise_mins=VALUES(exercise_mins), stress_level=VALUES(stress_level), mood=VALUES(mood),
            productivity_score=VALUES(productivity_score);
        """
        execute_query(sql, (user_id, cur_date, sleep, work, screen, exercise, stress, mood, prod_score, f"Synthetic log day {i+1}"), commit=True)
        
        # Add random expenses periodically
        if random.random() > 0.4:
            exp_sql = "INSERT INTO expenses (user_id, expense_date, category, amount, description) VALUES (%s, %s, %s, %s, %s)"
            execute_query(exp_sql, (user_id, cur_date, random.choice(categories), round(random.uniform(5.0, 120.0), 2), "Daily expense"), commit=True)

    # Add sample tasks
    sample_tasks = [
        ("Prepare Q3 Financial Analysis", "High", 3.0, "Pending"),
        ("Complete ML Model Evaluator", "High", 2.5, "In Progress"),
        ("Review Weekly Expenses", "Medium", 1.0, "Pending"),
        ("30-minute Cardio Session", "Low", 0.5, "Completed"),
        ("Draft LifePilot AI Presentation", "High", 4.0, "Pending"),
        ("Organize Daily Schedule", "Medium", 0.5, "Completed")
    ]
    for title, priority, est, status in sample_tasks:
        task_sql = "INSERT INTO tasks (user_id, title, priority, estimated_hours, status) VALUES (%s, %s, %s, %s, %s)"
        execute_query(task_sql, (user_id, title, priority, est, status), commit=True)

    print("Synthetic dataset successfully seeded into MySQL!")

if __name__ == '__main__':
    generate_synthetic_data()
