from datetime import datetime
from app.models.task_model import TaskModel
from app.models.daily_record_model import DailyRecordModel
from app.models.expense_model import ExpenseModel
from app.models.prediction_model import PredictionModel
from app.ml.clustering_model import BehaviorClusterer

class RecommendationEngine:
    @staticmethod
    def generate_response(user_id, intent, user_text=""):
        """Generates contextual AI response, recommendations, and structured daily plan for the given user."""
        # Gather user context
        tasks = TaskModel.get_by_user(user_id, status='Pending')
        user_avg = DailyRecordModel.get_user_averages(user_id) or {}
        latest_pred = PredictionModel.get_latest(user_id)
        expense_summary = ExpenseModel.get_category_breakdown(user_id)

        total_days = int(user_avg.get('total_days') or 0)
        recommendations = []
        schedule = []
        response_text = ""

        # Average metrics if user has logged data
        avg_sleep = float(user_avg.get('avg_sleep') or 0.0)
        avg_work = float(user_avg.get('avg_work') or 0.0)
        avg_screen = float(user_avg.get('avg_screen') or 0.0)
        avg_exercise = float(user_avg.get('avg_exercise') or 0.0)
        avg_stress = float(user_avg.get('avg_stress') or 0.0)

        # Behavioral Recommendations (ONLY if user has logged daily records)
        if total_days > 0:
            if avg_sleep < 6.5:
                recommendations.append("😴 **Sleep Recovery**: Your average sleep is below 6.5 hours. Aim for 7.5 hours tonight to boost cognitive performance and lower stress.")
            if avg_screen > 5.0:
                recommendations.append("📱 **Screen Time Limit**: Screen time is averaging over 5 hours. Take 5-minute eye breaks every 45 minutes.")
            if avg_exercise < 30:
                recommendations.append("🏃 **Physical Activity**: Incorporate a 25-minute brisk walk or cardio session to elevate focus and energy.")
            if avg_stress >= 7:
                recommendations.append("🧘 **Stress Management**: High stress detected. Schedule 10 minutes of deep breathing or meditation before starting work.")
        else:
            recommendations.append("📝 **Start Logging**: Log your daily metrics (sleep, work, exercise, stress) in the Daily Tracker to receive personalized AI recommendations.")

        # Pending high-priority task recommendation
        high_priority_tasks = [t for t in tasks if t.get('priority') == 'High'] if tasks else []
        if high_priority_tasks:
            top_task = high_priority_tasks[0]
            recommendations.append(f"🎯 **High Priority Task**: Focus your morning energy peak on: *{top_task['title']}* (Estimated: {top_task['estimated_hours']} hrs).")

        # Intent specific handling
        if intent == 'schedule_plan':
            response_text = "Here is your personalized daily schedule synthesized from your tasks, energy levels, and available time:"
            
            schedule = [
                {"time": "08:00 AM - 08:30 AM", "activity": "Morning Routine, Hydration & Light Exercise", "icon": "fa-sun"},
                {"time": "08:30 AM - 09:00 AM", "activity": "Review Daily Priorities & LifePilot Assistant Plan", "icon": "fa-list-check"}
            ]

            curr_hour = 9
            if high_priority_tasks:
                for hp_task in high_priority_tasks[:2]:
                    est = float(hp_task.get('estimated_hours', 1.5))
                    end_hour = curr_hour + int(est)
                    schedule.append({
                        "time": f"{curr_hour:02d}:00 AM - {end_hour:02d}:00 AM" if end_hour <= 12 else f"{curr_hour-12 if curr_hour>12 else curr_hour:02d}:00 PM - {end_hour-12 if end_hour>12 else end_hour:02d}:00 PM",
                        "activity": f"Deep Work: {hp_task['title']}",
                        "icon": "fa-brain"
                    })
                    curr_hour = end_hour

            schedule.extend([
                {"time": "12:30 PM - 01:30 PM", "activity": "Nutritious Lunch Break & Digital Screen Off", "icon": "fa-utensils"},
                {"time": "01:30 PM - 04:30 PM", "activity": "Secondary Tasks & Communication Review", "icon": "fa-laptop-code"},
                {"time": "04:30 PM - 05:30 PM", "activity": f"{'Physical Exercise Session' if avg_exercise < 30 else 'Light Evening Walk'}", "icon": "fa-running"},
                {"time": "05:30 PM - 07:00 PM", "activity": "Daily Log & Expense Tracker Update", "icon": "fa-pen-to-square"},
                {"time": "09:30 PM - 10:00 PM", "activity": "Wind Down, Screen Off & Reading", "icon": "fa-moon"}
            ])

        elif intent == 'productivity_inquiry':
            if latest_pred:
                pred_score = latest_pred['predicted_productivity_score']
                pred_level = latest_pred['predicted_productivity_level']
                response_text = f"Your latest predicted Productivity Score is **{pred_score}/100** ({pred_level} Level). Your average work time is {avg_work:.1f} hrs/day with {avg_sleep:.1f} hrs of sleep."
            elif total_days > 0:
                response_text = f"Your average work time is {avg_work:.1f} hrs/day with {avg_sleep:.1f} hrs of sleep. Run the Productivity Predictor to calculate your score!"
            else:
                response_text = "Prediction unavailable — log your daily metrics first so I can analyze your productivity trends."

        elif intent == 'expense_inquiry':
            total_exp = sum([float(e['total_amount']) for e in expense_summary]) if expense_summary else 0.0
            top_cat = expense_summary[0]['category'] if expense_summary else 'None'
            if total_exp > 0:
                response_text = f"You have logged total expenses of **₹{total_exp:,.2f}**. Your highest spending category is **{top_cat}**."
            else:
                response_text = "No expenses recorded yet. Log your spending entries in the Expense Manager to get category insights."

        elif intent == 'task_inquiry':
            task_count = len(tasks) if tasks else 0
            if task_count > 0:
                response_text = f"You currently have **{task_count} pending tasks**. You have {len(high_priority_tasks)} high-priority items waiting for completion."
            else:
                response_text = "You have no pending tasks! Add your to-do items in the Quick Task Planner."

        else: # Greeting / General
            if total_days > 0:
                response_text = "Hello! I am your LifePilot AI Assistant. I analyze your tasks, productivity trends, and expenses to optimize your day. How can I assist you today?"
            else:
                response_text = "Hello! I am your LifePilot AI Assistant. Start logging your daily metrics and tasks so I can provide personalized insights and schedule routines."

        return {
            "response_text": response_text,
            "recommendations": recommendations,
            "schedule": schedule
        }
