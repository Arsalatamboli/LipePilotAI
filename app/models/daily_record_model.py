from app.db import execute_query

class DailyRecordModel:
    @staticmethod
    def add_or_update(user_id, record_date, sleep_hours, work_hours, screen_time, 
                      exercise_mins, stress_level, mood, productivity_score=None, notes=''):
        """Inserts or updates a daily life record for a given date."""
        sql = """
        INSERT INTO daily_records 
            (user_id, record_date, sleep_hours, work_hours, screen_time, exercise_mins, stress_level, mood, productivity_score, notes)
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            sleep_hours = VALUES(sleep_hours),
            work_hours = VALUES(work_hours),
            screen_time = VALUES(screen_time),
            exercise_mins = VALUES(exercise_mins),
            stress_level = VALUES(stress_level),
            mood = VALUES(mood),
            productivity_score = VALUES(productivity_score),
            notes = VALUES(notes);
        """
        params = (user_id, record_date, sleep_hours, work_hours, screen_time, 
                  exercise_mins, stress_level, mood, productivity_score, notes)
        return execute_query(sql, params, commit=True)

    @staticmethod
    def get_by_date(user_id, record_date):
        """Fetches daily record for a specific user and date."""
        sql = "SELECT * FROM daily_records WHERE user_id = %s AND record_date = %s"
        return execute_query(sql, (user_id, record_date), fetch_one=True)

    @staticmethod
    def get_user_history(user_id, limit=30):
        """Fetches history of daily records for a user sorted by date descending."""
        sql = "SELECT * FROM daily_records WHERE user_id = %s ORDER BY record_date DESC LIMIT %s"
        return execute_query(sql, (user_id, limit), fetch_all=True)

    @staticmethod
    def get_all_records_for_user(user_id):
        """Fetches all daily records for a user for ML processing."""
        sql = "SELECT * FROM daily_records WHERE user_id = %s ORDER BY record_date ASC"
        return execute_query(sql, (user_id,), fetch_all=True)

    @staticmethod
    def get_all_global_records():
        """Fetches all records across system for general ML training."""
        sql = "SELECT * FROM daily_records ORDER BY record_date ASC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def get_user_averages(user_id):
        """Calculates 30-day average stats for a user."""
        sql = """
        SELECT 
            AVG(sleep_hours) as avg_sleep,
            AVG(work_hours) as avg_work,
            AVG(screen_time) as avg_screen,
            AVG(exercise_mins) as avg_exercise,
            AVG(stress_level) as avg_stress,
            AVG(productivity_score) as avg_productivity,
            COUNT(*) as total_days
        FROM daily_records 
        WHERE user_id = %s
        """
        return execute_query(sql, (user_id,), fetch_one=True)
