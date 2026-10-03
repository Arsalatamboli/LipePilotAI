from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from functools import wraps
from app.models.daily_record_model import DailyRecordModel
from app.models.task_model import TaskModel
from app.models.expense_model import ExpenseModel
from app.models.prediction_model import PredictionModel
from app.ml.clustering_model import BehaviorClusterer
from app.nlp.recommendation_engine import RecommendationEngine

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    # 1. Fetch user averages and summary stats
    averages = DailyRecordModel.get_user_averages(user_id) or {}
    task_summary = TaskModel.get_task_summary(user_id) or {}
    latest_prediction = PredictionModel.get_latest(user_id)
    recent_records = DailyRecordModel.get_user_history(user_id, limit=14)
    pending_tasks = TaskModel.get_by_user(user_id, status='Pending')[:5]
    expense_categories = ExpenseModel.get_category_breakdown(user_id)
    
    # 2. Get cluster persona if records exist
    cluster_persona = None
    if recent_records and len(recent_records) > 0:
        latest_r = recent_records[0]
        clusterer = BehaviorClusterer()
        cluster_persona = clusterer.predict_single(
            float(latest_r['sleep_hours']), float(latest_r['work_hours']),
            float(latest_r['screen_time']), int(latest_r['exercise_mins']),
            int(latest_r['stress_level'])
        )
        
    # 3. Generate AI recommendations summary
    ai_recs = RecommendationEngine.generate_response(user_id, intent='greeting')
    
    # Format trend chart data for Chart.js
    dates = [str(r['record_date']) for r in reversed(recent_records)]
    prod_scores = [float(r['productivity_score'] or 0) for r in reversed(recent_records)]
    work_hours = [float(r['work_hours']) for r in reversed(recent_records)]
    sleep_hours = [float(r['sleep_hours']) for r in reversed(recent_records)]
    
    chart_data = {
        "labels": dates,
        "productivity": prod_scores,
        "work": work_hours,
        "sleep": sleep_hours
    }

    return render_template(
        'dashboard/index.html',
        averages=averages,
        task_summary=task_summary,
        latest_prediction=latest_prediction,
        recent_records=recent_records,
        pending_tasks=pending_tasks,
        expense_categories=expense_categories,
        cluster_persona=cluster_persona,
        ai_recs=ai_recs['recommendations'],
        chart_data=chart_data
    )
