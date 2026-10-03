from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from app.routes.main_routes import login_required
from app.models.daily_record_model import DailyRecordModel
from app.ml.regression_model import ProductivityRegressor
from app.ml.classification_model import ProductivityClassifier
from app.models.prediction_model import PredictionModel

tracker_bp = Blueprint('tracker', __name__, url_prefix='/tracker')

@tracker_bp.route('/', methods=['GET', 'POST'])
@login_required
def daily_form():
    user_id = session['user_id']
    today_str = datetime.now().strftime('%Y-%m-%d')
    existing_record = DailyRecordModel.get_by_date(user_id, today_str)

    if request.method == 'POST':
        record_date = request.form.get('record_date', today_str)
        sleep_hours = float(request.form.get('sleep_hours', 7.0))
        work_hours = float(request.form.get('work_hours', 8.0))
        screen_time = float(request.form.get('screen_time', 4.0))
        exercise_mins = int(request.form.get('exercise_mins', 0))
        stress_level = int(request.form.get('stress_level', 5))
        mood = request.form.get('mood', 'Neutral')
        notes = request.form.get('notes', '').strip()

        # Compute productivity score via regression or formula
        regressor = ProductivityRegressor()
        classifier = ProductivityClassifier()
        
        prod_score = regressor.predict(sleep_hours, work_hours, screen_time, exercise_mins, stress_level)
        prod_level = classifier.predict(sleep_hours, work_hours, screen_time, exercise_mins, stress_level)

        # Add or update daily record
        DailyRecordModel.add_or_update(
            user_id, record_date, sleep_hours, work_hours, screen_time,
            exercise_mins, stress_level, mood, prod_score, notes
        )

        # Log prediction to DB
        PredictionModel.save_prediction(user_id, record_date, prod_score, prod_level)

        flash(f'Daily record for {record_date} saved successfully! Predicted Productivity: {prod_score} ({prod_level} Level).', 'success')
        return redirect(url_for('tracker.history'))

    return render_template('tracker/daily_form.html', today_str=today_str, existing_record=existing_record)

@tracker_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    records = DailyRecordModel.get_user_history(user_id, limit=30)
    return render_template('tracker/history.html', records=records)
