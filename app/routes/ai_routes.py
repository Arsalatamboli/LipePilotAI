from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from app.routes.main_routes import login_required
from app.nlp.intent_parser import IntentParser
from app.nlp.recommendation_engine import RecommendationEngine
from app.models.ai_model import AIModel
from app.models.task_model import TaskModel

ai_bp = Blueprint('ai', __name__, url_prefix='/ai-assistant')

@ai_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    chat_history = AIModel.get_recent_history(user_id, limit=20)
    pending_tasks = TaskModel.get_by_user(user_id, status='Pending')
    
    # Generate initial greeting and recommendations
    initial_recs = RecommendationEngine.generate_response(user_id, intent='schedule_plan')

    return render_template(
        'ai_assistant/index.html',
        chat_history=chat_history,
        pending_tasks=pending_tasks,
        initial_recs=initial_recs
    )

@ai_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    user_id = session['user_id']
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({"status": "error", "message": "Empty message."}), 400

    # Parse NLP Intent
    intent, tokens = IntentParser.parse_intent(user_message)

    # Generate Recommendation & Daily Plan
    response_data = RecommendationEngine.generate_response(user_id, intent, user_text=user_message)

    # Log interaction to database
    AIModel.log_interaction(
        user_id, 
        user_message, 
        response_data['response_text'], 
        intent, 
        response_data.get('recommendations')
    )

    return jsonify({
        "status": "success",
        "intent": intent,
        "response_text": response_data['response_text'],
        "recommendations": response_data.get('recommendations', []),
        "schedule": response_data.get('schedule', [])
    })

@ai_bp.route('/task/add', methods=['POST'])
@login_required
def add_task():
    user_id = session['user_id']
    title = request.form.get('title', '').strip()
    priority = request.form.get('priority', 'Medium')
    estimated_hours = float(request.form.get('estimated_hours', 1.0))
    due_date = request.form.get('due_date') or None

    if title:
        TaskModel.create_task(user_id, title, '', priority, estimated_hours, due_date)
        flash(f'Task "{title}" added to your planning list!', 'success')
    else:
        flash('Task title is required.', 'warning')
        
    return redirect(url_for('ai.index'))

@ai_bp.route('/task/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    user_id = session['user_id']
    TaskModel.update_status(task_id, user_id, 'Completed')
    flash('Task marked as completed!', 'success')
    return redirect(url_for('ai.index'))
