from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.routes.main_routes import login_required
from app.models.daily_record_model import DailyRecordModel
from app.ml.regression_model import ProductivityRegressor
from app.ml.classification_model import ProductivityClassifier
from app.ml.model_evaluator import ModelEvaluator
from app.models.prediction_model import PredictionModel

productivity_bp = Blueprint('productivity', __name__, url_prefix='/productivity')

@productivity_bp.route('/analysis')
@login_required
def analysis():
    user_id = session['user_id']
    records = DailyRecordModel.get_user_history(user_id, limit=60)
    averages = DailyRecordModel.get_user_averages(user_id) or {}
    
    # Evaluate models ONLY using current authenticated user's records
    user_records = DailyRecordModel.get_all_records_for_user(user_id)
    if user_records and len(user_records) >= 10:
        eval_results = ModelEvaluator.evaluate_models(user_records)
    else:
        eval_results = {
            "status": "warning",
            "message": "Prediction evaluation requires at least 10 logged daily records. Start logging your daily metrics!"
        }
    
    return render_template('productivity/analysis.html', records=records, averages=averages, eval_results=eval_results)

@productivity_bp.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction():
    user_id = session['user_id']
    latest_prediction = PredictionModel.get_latest(user_id)
    
    result = None
    if request.method == 'POST':
        sleep_hours = float(request.form.get('sleep_hours', 7.0))
        work_hours = float(request.form.get('work_hours', 8.0))
        screen_time = float(request.form.get('screen_time', 4.0))
        exercise_mins = int(request.form.get('exercise_mins', 30))
        stress_level = int(request.form.get('stress_level', 5))

        regressor = ProductivityRegressor()
        classifier = ProductivityClassifier()
        
        predicted_score = regressor.predict(sleep_hours, work_hours, screen_time, exercise_mins, stress_level)
        predicted_level = classifier.predict(sleep_hours, work_hours, screen_time, exercise_mins, stress_level)

        result = {
            "sleep_hours": sleep_hours,
            "work_hours": work_hours,
            "screen_time": screen_time,
            "exercise_mins": exercise_mins,
            "stress_level": stress_level,
            "predicted_score": predicted_score,
            "predicted_level": predicted_level
        }

    return render_template('productivity/prediction.html', latest_prediction=latest_prediction, result=result)

@productivity_bp.route('/train', methods=['POST'])
@login_required
def train_models():
    """Triggers retraining of ML regression and classification models for the current user."""
    user_id = session['user_id']
    user_records = DailyRecordModel.get_all_records_for_user(user_id)
    
    if not user_records or len(user_records) < 5:
        flash("Insufficient daily records for training (at least 5 records required). Start logging your daily metrics!", "warning")
        return redirect(url_for('productivity.analysis'))

    regressor = ProductivityRegressor()
    reg_success, reg_msg = regressor.train(user_records)
    
    classifier = ProductivityClassifier()
    clf_success, clf_msg = classifier.train(user_records)
    
    if reg_success and clf_success:
        flash("ML Productivity models retrained and serialized successfully for your account!", "success")
    else:
        flash(f"Model training notice: {reg_msg} / {clf_msg}", "warning")
        
    return redirect(url_for('productivity.analysis'))
