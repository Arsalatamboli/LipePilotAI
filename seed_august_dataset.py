import os
from datetime import datetime
from config import Config
from app.db import execute_query, init_db
from app.models.user_model import UserModel
from app.models.daily_record_model import DailyRecordModel
from app.models.expense_model import ExpenseModel
from app.models.task_model import TaskModel
from app.ml.regression_model import ProductivityRegressor
from app.ml.classification_model import ProductivityClassifier
from app.ml.clustering_model import BehaviorClusterer
from app.ml.model_evaluator import ModelEvaluator

def run_august_seeding():
    print("=== LifePilot AI August 2026 Dataset Seeding (1 Aug - 21 Aug) ===")
    init_db()

    # 1. Ensure User ID 1 exists (Sara / demo user)
    user = UserModel.get_by_id(1)
    if not user:
        user = UserModel.get_by_email("sara@lifepilot.ai")
        if not user:
            user_id = UserModel.create_user("Sara", "sara@lifepilot.ai", "SaraPassword123!")
            print(f"Created user 'Sara' with ID: {user_id}")
        else:
            user_id = user['id']
            print(f"Found existing user 'Sara' (ID {user_id})")
    else:
        user_id = user['id']
        print(f"Using target User ID {user_id} ('{user['username']}')")

    # 2. 21-Day Synthetic August Dataset (2026-08-01 through 2026-08-21)
    august_records = [
        {"date": "2026-08-01", "mood": "Happy", "sleep": 8.0, "work": 7.5, "screen": 2.5, "exercise": 45, "stress": 3, "score": 88.50, "notes": "Great start to August! Feeling energized and completed morning cardio."},
        {"date": "2026-08-02", "mood": "Focused", "sleep": 7.5, "work": 8.5, "screen": 3.0, "exercise": 30, "stress": 4, "score": 84.00, "notes": "Strong focus on project milestones. Good pace throughout the day."},
        {"date": "2026-08-03", "mood": "Focused", "sleep": 7.0, "work": 9.0, "screen": 4.0, "exercise": 20, "stress": 5, "score": 78.50, "notes": "Long work session on backend APIs. Slightly tired by evening."},
        {"date": "2026-08-04", "mood": "Neutral", "sleep": 6.5, "work": 8.0, "screen": 4.5, "exercise": 15, "stress": 6, "score": 70.00, "notes": "Average productivity day. Worked on documentation and team sync."},
        {"date": "2026-08-05", "mood": "Stressed", "sleep": 5.5, "work": 10.5, "screen": 5.5, "exercise": 0, "stress": 8, "score": 54.00, "notes": "High deadline pressure. Low sleep and missed workout led to fatigue."},
        {"date": "2026-08-06", "mood": "Tired", "sleep": 5.0, "work": 11.0, "screen": 6.0, "exercise": 0, "stress": 9, "score": 42.00, "notes": "Burnout warning. Worked late into night with high stress."},
        {"date": "2026-08-07", "mood": "Neutral", "sleep": 8.5, "work": 5.0, "screen": 4.0, "exercise": 30, "stress": 4, "score": 76.00, "notes": "Recovery Friday. Caught up on sleep and lighter workload."},
        {"date": "2026-08-08", "mood": "Happy", "sleep": 9.0, "work": 3.5, "screen": 3.5, "exercise": 60, "stress": 2, "score": 92.00, "notes": "Weekend refresh! Long morning run and relaxing evening."},
        {"date": "2026-08-09", "mood": "Happy", "sleep": 8.5, "work": 4.0, "screen": 2.5, "exercise": 45, "stress": 2, "score": 90.00, "notes": "Balanced Sunday. Prepared weekly plan and spent time outdoors."},
        {"date": "2026-08-10", "mood": "Focused", "sleep": 7.5, "work": 8.0, "screen": 3.0, "exercise": 40, "stress": 3, "score": 86.50, "notes": "Solid Monday output. Completed key sprint deliverables."},
        {"date": "2026-08-11", "mood": "Focused", "sleep": 7.0, "work": 8.5, "screen": 3.5, "exercise": 30, "stress": 4, "score": 81.00, "notes": "Good progress on feature integration and code reviews."},
        {"date": "2026-08-12", "mood": "Neutral", "sleep": 6.5, "work": 7.5, "screen": 5.0, "exercise": 20, "stress": 5, "score": 68.50, "notes": "Moderate productivity. Too much non-work screen time in evening."},
        {"date": "2026-08-13", "mood": "Tired", "sleep": 5.8, "work": 9.5, "screen": 5.5, "exercise": 10, "stress": 7, "score": 58.00, "notes": "Felt sluggish in afternoon. High work hours with low exercise."},
        {"date": "2026-08-14", "mood": "Stressed", "sleep": 5.2, "work": 10.0, "screen": 6.5, "exercise": 0, "stress": 8, "score": 48.00, "notes": "Challenging day with technical bugs and client requests."},
        {"date": "2026-08-15", "mood": "Happy", "sleep": 8.0, "work": 6.0, "screen": 3.0, "exercise": 45, "stress": 3, "score": 85.00, "notes": "Rebalanced day. Good workout and steady progress."},
        {"date": "2026-08-16", "mood": "Happy", "sleep": 8.5, "work": 3.0, "screen": 2.0, "exercise": 50, "stress": 2, "score": 91.50, "notes": "Relaxing Sunday with family. Light reading and outdoor walk."},
        {"date": "2026-08-17", "mood": "Focused", "sleep": 7.8, "work": 8.0, "screen": 3.0, "exercise": 35, "stress": 3, "score": 87.00, "notes": "High focus Monday. Cleared pending backlog tasks."},
        {"date": "2026-08-18", "mood": "Focused", "sleep": 7.5, "work": 8.2, "screen": 2.8, "exercise": 40, "stress": 3, "score": 88.00, "notes": "Productive day! Optimized ML pipelines and updated LifePilot AI."},
        {"date": "2026-08-19", "mood": "Focused", "sleep": 7.2, "work": 8.5, "screen": 3.0, "exercise": 35, "stress": 4, "score": 83.50, "notes": "Focused on sprint testing and code quality review."},
        {"date": "2026-08-20", "mood": "Happy", "sleep": 8.0, "work": 7.8, "screen": 2.5, "exercise": 45, "stress": 3, "score": 88.00, "notes": "Productive Thursday session with evening gym workout."},
        {"date": "2026-08-21", "mood": "Focused", "sleep": 7.5, "work": 8.0, "screen": 3.2, "exercise": 40, "stress": 3, "score": 86.50, "notes": "Successful Friday deployment and weekly sprint retrospective."}
    ]

    records_count = 0
    for r in august_records:
        DailyRecordModel.add_or_update(
            user_id=user_id,
            record_date=r['date'],
            sleep_hours=r['sleep'],
            work_hours=r['work'],
            screen_time=r['screen'],
            exercise_mins=r['exercise'],
            stress_level=r['stress'],
            mood=r['mood'],
            productivity_score=r['score'],
            notes=r['notes']
        )
        records_count += 1
    print(f"[OK] Daily Records: Created/Updated {records_count} records (2026-08-01 through 2026-08-21) for User ID {user_id}.")

    # 3. August Expenses in INR (₹)
    august_expenses = [
        {"date": "2026-08-01", "category": "Food", "amount": 850.00, "desc": "Organic Grocery Shopping"},
        {"date": "2026-08-02", "category": "Transport", "amount": 350.00, "desc": "Fuel & Commute"},
        {"date": "2026-08-04", "category": "Utilities", "amount": 2250.00, "desc": "Monthly Internet & Cloud Services"},
        {"date": "2026-08-06", "category": "Food", "amount": 450.00, "desc": "Late Night Takeout"},
        {"date": "2026-08-08", "category": "Health", "amount": 1500.00, "desc": "Gym Membership & Fitness Pass"},
        {"date": "2026-08-10", "category": "Shopping", "amount": 2400.00, "desc": "Work Desk Ergonomic Accessories"},
        {"date": "2026-08-12", "category": "Entertainment", "amount": 699.00, "desc": "Streaming Subscriptions & Movies"},
        {"date": "2026-08-15", "category": "Food", "amount": 1200.00, "desc": "Weekend Dinner with Friends"},
        {"date": "2026-08-17", "category": "Transport", "amount": 450.00, "desc": "City Transit Pass"},
        {"date": "2026-08-18", "category": "Other", "amount": 850.00, "desc": "Technical Books & Learning Material"},
        {"date": "2026-08-19", "category": "Food", "amount": 320.00, "desc": "Campus Cafe Lunch & Coffee"},
        {"date": "2026-08-20", "category": "Shopping", "amount": 1250.00, "desc": "Stationery & Project Supplies"},
        {"date": "2026-08-21", "category": "Entertainment", "amount": 450.00, "desc": "Weekend Cinema Ticket & Snacks"}
    ]

    execute_query("DELETE FROM expenses WHERE user_id = %s AND expense_date BETWEEN '2026-08-01' AND '2026-08-21'", (user_id,), commit=True)
    expenses_count = 0
    for e in august_expenses:
        ExpenseModel.add_expense(user_id, e['date'], e['category'], e['amount'], e['desc'])
        expenses_count += 1
    print(f"[OK] Expenses: Created {expenses_count} synthetic INR expenses across August 1-21.")

    # 4. August Tasks
    august_tasks = [
        ("Complete August ML Evaluation Metrics", "High", 2.5, "Completed"),
        ("Refine Behavior Clustering PCA Plot", "High", 3.0, "Completed"),
        ("Review Monthly Financial Expenses", "Medium", 1.5, "Completed"),
        ("Daily 30-min Cardio Workout", "Low", 0.5, "Completed"),
        ("Draft LifePilot AI Performance Summary", "High", 4.0, "Pending"),
        ("Organize Next Week's Sprint Tasks", "Medium", 1.0, "Pending"),
        ("Update User Preferences & Goals", "Low", 0.5, "Pending")
    ]

    execute_query("DELETE FROM tasks WHERE user_id = %s", (user_id,), commit=True)
    tasks_count = 0
    for title, priority, est, status in august_tasks:
        TaskModel.create_task(user_id, title, "August task item", priority, est)
        if status == "Completed":
            last_task = execute_query("SELECT id FROM tasks WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,), fetch_one=True)
            if last_task:
                TaskModel.update_status(last_task['id'], user_id, 'Completed')
        tasks_count += 1
    print(f"[OK] Tasks: Created {tasks_count} synthetic tasks (4 Completed, 3 Pending).")

    # 5. Execute ML Training & Evaluation
    print("\n--- Running ML Pipeline on August Dataset ---")
    user_records = DailyRecordModel.get_all_records_for_user(user_id)
    
    regressor = ProductivityRegressor()
    reg_ok, reg_msg = regressor.train(user_records)
    
    classifier = ProductivityClassifier()
    clf_ok, clf_msg = classifier.train(user_records)
    
    eval_metrics = ModelEvaluator.evaluate_models(user_records)
    
    clusterer = BehaviorClusterer(n_clusters=4)
    cluster_res = clusterer.fit_predict(user_records)

    print(f"[OK] ML Regression (RandomForestRegressor): {reg_ok} | MSE: {eval_metrics['regression_metrics']['mse']} | R2: {eval_metrics['regression_metrics']['r2_score']}")
    print(f"[OK] ML Classification (RandomForestClassifier): {clf_ok} | Accuracy: {eval_metrics['classification_metrics']['accuracy']} | Precision: {eval_metrics['classification_metrics']['precision']} | Recall: {eval_metrics['classification_metrics']['recall']} | F1: {eval_metrics['classification_metrics']['f1_score']}")
    print(f"[OK] Confusion Matrix Plot Generated: {eval_metrics['confusion_matrix_plot']}")
    print(f"[OK] K-Means Clustering & PCA Plot: {len(cluster_res['cluster_points'])} data points | Variance Explained: {cluster_res['total_variance_explained']:.2f}%")

    print("\n=== August Dataset Seeding & ML Pipeline Complete ===")

    return {
        "user_id": user_id,
        "daily_records_count": records_count,
        "expenses_count": expenses_count,
        "tasks_count": tasks_count,
        "date_range": "2026-08-01 through 2026-08-21",
        "reg_metrics": eval_metrics['regression_metrics'],
        "clf_metrics": eval_metrics['classification_metrics'],
        "cm_plot": eval_metrics['confusion_matrix_plot'],
        "pca_points": len(cluster_res['cluster_points'])
    }

if __name__ == '__main__':
    run_august_seeding()
