import json
from app.db import execute_query

class AIModel:
    @staticmethod
    def log_interaction(user_id, user_message, assistant_response, intent='general', recommendations_json=None):
        """Logs an AI assistant chat interaction."""
        rec_json_str = json.dumps(recommendations_json) if recommendations_json else None
        sql = """
        INSERT INTO ai_interactions (user_id, user_message, assistant_response, intent, recommendations_json)
        VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(sql, (user_id, user_message, assistant_response, intent, rec_json_str), commit=True)

    @staticmethod
    def get_recent_history(user_id, limit=20):
        """Fetches recent AI conversation history for a user."""
        sql = "SELECT * FROM ai_interactions WHERE user_id = %s ORDER BY created_at ASC LIMIT %s"
        return execute_query(sql, (user_id, limit), fetch_all=True)
