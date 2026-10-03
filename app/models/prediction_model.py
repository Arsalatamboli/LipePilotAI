from app.db import execute_query

class PredictionModel:
    @staticmethod
    def save_prediction(user_id, record_date, predicted_score, predicted_level, reg_ver='v1.0', clf_ver='v1.0'):
        """Saves a model prediction result to MySQL."""
        sql = """
        INSERT INTO predictions 
            (user_id, record_date, predicted_productivity_score, predicted_productivity_level, regression_model_version, classification_model_version)
        VALUES 
            (%s, %s, %s, %s, %s, %s)
        """
        return execute_query(sql, (user_id, record_date, predicted_score, predicted_level, reg_ver, clf_ver), commit=True)

    @staticmethod
    def get_latest(user_id):
        """Fetches latest prediction for a user."""
        sql = "SELECT * FROM predictions WHERE user_id = %s ORDER BY created_at DESC LIMIT 1"
        return execute_query(sql, (user_id,), fetch_one=True)

    @staticmethod
    def get_history(user_id, limit=30):
        """Fetches history of predictions for a user."""
        sql = "SELECT * FROM predictions WHERE user_id = %s ORDER BY record_date DESC LIMIT %s"
        return execute_query(sql, (user_id, limit), fetch_all=True)
