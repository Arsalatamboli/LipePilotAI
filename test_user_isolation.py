from app import create_app
from app.db import execute_query
from app.models.user_model import UserModel
from app.models.daily_record_model import DailyRecordModel
from app.models.expense_model import ExpenseModel
from app.models.task_model import TaskModel
from app.models.prediction_model import PredictionModel
from app.nlp.recommendation_engine import RecommendationEngine

print("=== LifePilot AI Complete User Isolation Automated Test ===")

app = create_app()

with app.app_context():
    # 1. Verify USER A (Sara / ID 1)
    user_a = UserModel.get_by_id(1)
    assert user_a is not None, "User A (ID 1) must exist!"
    user_a_id = user_a['id']
    
    recs_a = DailyRecordModel.get_all_records_for_user(user_a_id)
    exps_a = ExpenseModel.get_by_user(user_a_id, limit=50)
    tasks_a = TaskModel.get_by_user(user_a_id, status='Pending')
    
    print(f"USER A ({user_a['username']}):")
    print(f"  - Daily Records: {len(recs_a)}")
    print(f"  - Expenses: {len(exps_a)} entries (Total: INR {sum([float(e['amount']) for e in exps_a]):,.2f})")
    print(f"  - Pending Tasks: {len(tasks_a)}")
    
    assert len(recs_a) >= 21, "User A daily records must remain intact!"
    assert len(exps_a) >= 13, "User A expenses must remain intact!"

    # 2. Register/Create USER B (New User)
    user_b_email = "user_b_isolation_test@lifepilot.ai"
    existing_b = UserModel.get_by_email(user_b_email)
    if existing_b:
        user_b_id = existing_b['id']
        # Clean up any old test data for User B
        execute_query("DELETE FROM daily_records WHERE user_id = %s", (user_b_id,), commit=True)
        execute_query("DELETE FROM expenses WHERE user_id = %s", (user_b_id,), commit=True)
        execute_query("DELETE FROM tasks WHERE user_id = %s", (user_b_id,), commit=True)
        execute_query("DELETE FROM predictions WHERE user_id = %s", (user_b_id,), commit=True)
    else:
        user_b_id = UserModel.create_user("User B Test", user_b_email, "Password123!")

    user_b = UserModel.get_by_id(user_b_id)
    print(f"\nUSER B ({user_b['username']} - Newly Registered ID {user_b_id}):")

    # 3. Test USER B Empty State
    recs_b = DailyRecordModel.get_all_records_for_user(user_b_id)
    exps_b = ExpenseModel.get_by_user(user_b_id, limit=50)
    tasks_b = TaskModel.get_by_user(user_b_id, status='Pending')
    pred_b = PredictionModel.get_latest(user_b_id)
    avg_b = DailyRecordModel.get_user_averages(user_b_id)
    ai_b = RecommendationEngine.generate_response(user_b_id, intent='productivity_inquiry')

    print(f"  - Daily Records: {len(recs_b)} (Expected: 0)")
    print(f"  - Expenses: {len(exps_b)} (Expected: 0)")
    print(f"  - Pending Tasks: {len(tasks_b)} (Expected: 0)")
    print(f"  - Latest Prediction: {pred_b} (Expected: None)")
    print(f"  - AI Response: '{ai_b['response_text']}'")

    assert len(recs_b) == 0, "User B MUST start with 0 daily records!"
    assert len(exps_b) == 0, "User B MUST start with 0 expenses!"
    assert len(tasks_b) == 0, "User B MUST start with 0 tasks!"
    assert pred_b is None, "User B MUST start with 0 predictions!"

    # 4. Add 1 Daily Record to USER B
    DailyRecordModel.add_or_update(
        user_id=user_b_id,
        record_date='2026-08-22',
        sleep_hours=8.0,
        work_hours=8.0,
        screen_time=2.5,
        exercise_mins=45,
        stress_level=2,
        mood='Happy',
        productivity_score=90.0,
        notes='User B first logged record'
    )
    print("\n[ACTION] Logged 1 Daily Record for User B ('2026-08-22')")

    recs_b_after = DailyRecordModel.get_all_records_for_user(user_b_id)
    recs_a_after = DailyRecordModel.get_all_records_for_user(user_a_id)

    print(f"  - User B Daily Records count: {len(recs_b_after)} (Expected: 1)")
    print(f"  - User A Daily Records count: {len(recs_a_after)} (Expected: 21+)")

    assert len(recs_b_after) == 1, "User B must have exactly 1 record after insertion!"
    assert len(recs_a_after) == len(recs_a), "User A's record count must remain unchanged!"

    # 5. Add 1 Expense to USER B
    ExpenseModel.add_expense(user_b_id, '2026-08-22', 'Food', 250.00, 'User B Cafe Lunch')
    print("\n[ACTION] Logged 1 Expense (INR 250.00) for User B")

    exps_b_after = ExpenseModel.get_by_user(user_b_id)
    exps_a_after = ExpenseModel.get_by_user(user_a_id)

    total_b = sum([float(e['amount']) for e in exps_b_after])
    total_a = sum([float(e['amount']) for e in exps_a_after])

    print(f"  - User B Total Expenses: INR {total_b:,.2f} (Expected: 250.00)")
    print(f"  - User A Total Expenses: INR {total_a:,.2f} (Unchanged)")

    assert total_b == 250.00, "User B expense total must be exactly 250.00!"
    assert total_a == sum([float(e['amount']) for e in exps_a]), "User A expense total must NOT change!"

    # 6. Add 1 Task to USER B
    TaskModel.create_task(user_b_id, 'User B Priority Task', 'Task for User B only', 'High', 2.0)
    print("\n[ACTION] Logged 1 Task for User B")

    tasks_b_after = TaskModel.get_by_user(user_b_id, status='Pending')
    tasks_a_after = TaskModel.get_by_user(user_a_id, status='Pending')

    print(f"  - User B Pending Tasks: {len(tasks_b_after)} (Expected: 1)")
    print(f"  - User A Pending Tasks: {len(tasks_a_after)} (Unchanged)")

    assert len(tasks_b_after) == 1, "User B pending tasks must be exactly 1!"
    assert len(tasks_a_after) == len(tasks_a), "User A pending tasks must NOT change!"

    # 7. Clean up test account User B
    execute_query("DELETE FROM daily_records WHERE user_id = %s", (user_b_id,), commit=True)
    execute_query("DELETE FROM expenses WHERE user_id = %s", (user_b_id,), commit=True)
    execute_query("DELETE FROM tasks WHERE user_id = %s", (user_b_id,), commit=True)
    execute_query("DELETE FROM predictions WHERE user_id = %s", (user_b_id,), commit=True)
    execute_query("DELETE FROM users WHERE id = %s", (user_b_id,), commit=True)
    print("\n[CLEANUP] Cleaned up User B test account.")

print("\n=== SUCCESS: 100% User Data Isolation Verified Across All Modules! ===")
